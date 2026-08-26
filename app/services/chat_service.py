from sqlalchemy.orm import Session

from app.rag.vector_store import VectorStore
from app.services.llm_service import LLMService
from app.db.repository import (
    create_chat_session,
    create_chat_message,
    get_chat_session
)


class ChatService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_service = LLMService()

    def retrieve_context(
        self,
        question: str,
        top_k: int = 3,
        document_id: str | None = None
    ):
        results = self.vector_store.search_similar_chunks(
            query=question,
            top_k=top_k,
            document_id=document_id
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved_chunks = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):
            retrieved_chunks.append({
                "text": document,
                "metadata": metadata,
                "distance": distance
            })

        return retrieved_chunks

    def answer_question(
        self,
        db: Session,
        question: str,
        top_k: int = 3,
        document_id: str | None = None
    ):
        retrieved_chunks = self.retrieve_context(
            question=question,
            top_k=top_k,
            document_id=document_id
        )

        if not retrieved_chunks:
            return {
                "answer": (
                    "I could not find relevant information "
                    "in the provided document."
                ),
                "sources": []
            }

        context = "\n\n".join(
            chunk["text"]
            for chunk in retrieved_chunks
        )

        answer = self.llm_service.generate_answer(
            question=question,
            context=context
        )

        sources = []

        for chunk in retrieved_chunks:
            metadata = chunk["metadata"]

            sources.append({
                "filename": metadata.get("filename"),
                "page": metadata.get("page"),
                "distance": chunk["distance"]
            })

        # Create a new chat session
        chat_session = create_chat_session(
            db=db,
            document_id=document_id
        )

        # Save the question, answer and sources
        create_chat_message(
            db=db,
            session_id=chat_session.session_id,
            question=question,
            answer=answer,
            sources=sources
        )

        return {
            "session_id": chat_session.session_id,
            "answer": answer,
            "sources": sources
        }
