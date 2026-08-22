from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pymupdf

app = FastAPI()

class ChatRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "AI Research Assistant API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat")
def chat(request: ChatRequest):
    return {
        "question": request.question,
        "answer": "This is a dummy response."
    }


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    contents = await file.read()

    document = pymupdf.open(stream=contents, filetype="pdf")

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        pages.append({
            "page": page_number,
            "text": text
        })

    document.close()

    return {
        "filename": file.filename,
        "pages": len(pages),
        "content": pages
    }