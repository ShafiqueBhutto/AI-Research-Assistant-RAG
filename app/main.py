from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pathlib import Path
import shutil
import uuid

from sqlalchemy.orm import Session

from app.db.models import Document
from app.schemas.chat import ChatRequest
from app.services.document_service import DocumentService
from app.services.chat_service import ChatService

from app.db.database import get_db
from app.db.repository import (
    create_document,
    get_documents,
    get_document,
    create_chat_session,
    delete_document,
    create_chat_message,
    get_chat_sessions
)

app = FastAPI(
    title="AI Research Assistant",
    description="RAG-based document question answering system",
    version="1.0.0"
)


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

document_service = DocumentService()
chat_service = ChatService()


@app.get("/")
def root():
    return {
        "message": "AI Research Assistant API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/documents")
def list_documents(
    db: Session = Depends(get_db)
):
    documents = get_documents(db=db)

    return [
        {
            "document_id": document.document_id,
            "filename": document.filename,
            "file_path": document.file_path,
            "chunks_stored": document.chunks_stored,
            "created_at": document.created_at
        }
        for document in documents
    ]




@app.get("/documents/{document_id}")
def get_document_by_id(
    document_id: str,
    db: Session = Depends(get_db)
):
    document = get_document(
        db=db,
        document_id=document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "document_id": document.document_id,
        "filename": document.filename,
        "file_path": document.file_path,
        "chunks_stored": document.chunks_stored,
        "created_at": document.created_at
    }



@app.delete("/documents/{document_id}")
def delete_document_by_id(
    document_id: str,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(
            Document.document_id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    file_path = Path(document.file_path)

    try:
        # Delete chunks from ChromaDB
        document_service.delete_document(
            document_id=document_id
        )

        # Delete metadata from PostgreSQL
        delete_document(
            db=db,
            document_id=document_id
        )

        # Delete actual PDF file
        if file_path.exists():
            file_path.unlink()

        return {
            "message": "Document deleted successfully.",
            "document_id": document_id
        }

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Document deletion failed: {str(e)}"
        )




@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    document_id = str(uuid.uuid4())

    file_path = UPLOAD_DIR / f"{document_id}_{file.filename}"

    try:

        # Save uploaded PDF
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process PDF and store chunks in ChromaDB
        result = document_service.process_pdf(
            pdf_path=str(file_path),
            document_id=document_id
        )

        # Save document metadata in PostgreSQL
        create_document(
            db=db,
            document_id=document_id,
            filename=result["filename"],
            file_path=str(file_path),
            chunks_stored=result["chunks_stored"]
        )

        return {
            "message": "Document uploaded and processed successfully.",
            **result
        }

    except Exception as e:

        if file_path.exists():
            file_path.unlink()

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

    finally:
        await file.close()


@app.get("/chat")
def list_chat_sessions(
    db: Session = Depends(get_db)
):
    return get_chat_sessions(db=db)


@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        result = chat_service.answer_question(
            db=db,
            question=request.question,
            top_k=request.top_k,
            document_id=request.document_id,
             session_id=request.session_id
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Question processing failed: {str(e)}"
        )


@app.get("/chat/{session_id}")
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    history = chat_service.get_chat_history(
        db=db,
        session_id=session_id
    )

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found."
        )

    return history

    

