from __future__ import annotations

from typing import Iterable

import chromadb
import httpx
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from openai import OpenAI

from app.config import settings
from app.text_utils import chunk_id, split_text


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
        ids = [chunk_id(source=source, idx=idx, chunk=chunk) for idx, chunk in enumerate(chunks)]
        metadatas = [{"source": source, "chunk": idx} for idx in range(len(chunks))]
        self.collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
        return len(chunks)

    def retrieve(self, question: str, k: int | None = None) -> list[str]:
        n_results = k or settings.retrieval_k
        results = self.collection.query(query_texts=[question], n_results=n_results)
        documents = results.get("documents", [[]])[0]
        return [doc for doc in documents if doc]

    def answer(self, question: str, top_k: int | None = None) -> tuple[str, list[str]]:
        context = self.retrieve(question=question, k=top_k)
        if not context:
            return "I do not know based on the indexed knowledge base.", []

        prompt = self._build_prompt(question, context)
        provider = settings.llm_provider.lower()

        if provider == "ollama":
            answer = self._generate_ollama(prompt)
        elif provider == "openai":
            answer = self._generate_openai(prompt)
        else:
            raise RuntimeError("Unsupported LLM_PROVIDER. Use 'openai' or 'ollama'.")

        return answer.strip(), context


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

    def stats(self) -> dict[str, int]:
        return {"documents": self.collection.count()}
