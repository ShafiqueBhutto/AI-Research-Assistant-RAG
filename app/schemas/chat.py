from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    document_id: str
    filename: str
    page: int


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]