from __future__ import annotations

from typing import Iterable

import chromadb
import httpx
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from openai import OpenAI

from app.config import settings
from app.text_utils import split_text



class RAGService:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=settings.persist_directory)
        embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model_name
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            embedding_function=embedding_fn,
        )
        self.openai_client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def ingest(self, text: str, source: str) -> int:
        chunks = split_text(text)
        ids = [f"{source}-{idx}" for idx, _ in enumerate(chunks)]
        metadatas = [{"source": source, "chunk": idx} for idx in range(len(chunks))]
        self.collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
        return len(chunks)

    def retrieve(self, question: str, k: int | None = None) -> list[str]:
        n_results = k or settings.retrieval_k
        results = self.collection.query(query_texts=[question], n_results=n_results)
        documents = results.get("documents", [[]])[0]
        return [doc for doc in documents if doc]

    def _build_prompt(self, question: str, context_chunks: Iterable[str]) -> str:
        context = "\n\n".join(context_chunks)
        return (
            "You are a concise assistant. Use only the context below to answer. "
            "If the answer is not present, say you do not know.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )

    def _generate_openai(self, prompt: str) -> str:
        if not self.openai_client:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        completion = self.openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return completion.choices[0].message.content or "No answer generated."

    def _generate_ollama(self, prompt: str) -> str:
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        response = httpx.post(
            f"{settings.ollama_base_url}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No answer generated.")

    def answer(self, question: str) -> tuple[str, list[str]]:
        context = self.retrieve(question)
        prompt = self._build_prompt(question, context)

        if settings.llm_provider.lower() == "ollama":
            answer = self._generate_ollama(prompt)
        else:
            answer = self._generate_openai(prompt)

        return answer.strip(), context
