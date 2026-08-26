import uuid

from sqlalchemy.orm import Session

from app.db.models import Document, ChatSession, ChatMessage


def create_document(
    db: Session,
    document_id: str,
    filename: str,
    file_path: str,
    chunks_stored: int
):
    document = Document(
        document_id=document_id,
        filename=filename,
        file_path=file_path,
        chunks_stored=chunks_stored
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def create_chat_session(
    db: Session,
    document_id: str | None = None
):
    session_id = str(uuid.uuid4())

    chat_session = ChatSession(
        session_id=session_id,
        document_id=document_id
    )

    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)

    return chat_session


def create_chat_message(
    db: Session,
    session_id: str,
    question: str,
    answer: str,
    sources: list
):
    message = ChatMessage(
        session_id=session_id,
        question=question,
        answer=answer,
        sources=sources
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message

def get_chat_session(
    db: Session,
    session_id: str
):
    return (
        db.query(ChatSession)
        .filter(
            ChatSession.session_id == session_id
        )
        .first()
    )

def get_chat_messages(
    db: Session,
    session_id: str
):
    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id
        )
        .order_by(ChatMessage.created_at.asc())
        .all()
    )