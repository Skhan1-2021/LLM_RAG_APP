from fastapi import FastAPI, HTTPException

from app.config import settings
from app.rag_service import RAGService
from app.schemas import IngestRequest, IngestResponse, QueryRequest, QueryResponse

app = FastAPI(title=settings.app_name)
rag = RAGService()


@app.get("/health")
def health() -> dict[str, str | int]:
    return {
        "status": "ok",
        "provider": settings.llm_provider,
        "documents": rag.stats()["documents"],
    }


@app.post("/ingest", response_model=IngestResponse)
def ingest(payload: IngestRequest) -> IngestResponse:
    chunks = rag.ingest(text=payload.text, source=payload.source)
    return IngestResponse(status="ingested", chunks=chunks, source=payload.source)


@app.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    try:
        answer, context = rag.answer(payload.question, top_k=payload.top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return QueryResponse(answer=answer, context=context, source_count=len(context))
