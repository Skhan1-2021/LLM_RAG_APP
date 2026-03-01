from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw text content to index")
    source: str = Field(default="manual", min_length=1, description="Document source name")


class IngestResponse(BaseModel):
    status: str
    chunks: int
    source: str


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)


class QueryResponse(BaseModel):
    answer: str
    context: list[str]
    source_count: int
