from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str
    top_k: int = Field(default=3, ge=1, le=5)
    document_id: str | None = None
    session_id: str | None = None

class Source(BaseModel):
    document_id: str
    filename: str
    page: int


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[Source]