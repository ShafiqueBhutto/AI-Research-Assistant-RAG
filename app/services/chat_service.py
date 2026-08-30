from sqlalchemy.orm import Session

from app.rag.vector_store import VectorStore
from app.services.llm_service import LLMService

from app.db.repository import (
    create_chat_session,
    create_chat_message,
    get_chat_session,
    get_chat_messages
)


class ChatService:

    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_service = LLMService()

    # ============================================================
    # RETRIEVE RELEVANT DOCUMENT CHUNKS
    # ============================================================

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

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        retrieved_chunks = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            retrieved_chunks.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance
                }
            )

        return retrieved_chunks

    # ============================================================
    # BUILD CONVERSATION HISTORY
    # ============================================================

    def build_conversation_history(
        self,
        messages
    ):

        if not messages:
            return ""

        history_parts = []

        for message in messages:

            history_parts.append(
                f"User: {message.question}\n"
                f"Assistant: {message.answer}"
            )

        return "\n\n".join(history_parts)

    # ============================================================
    # ANSWER QUESTION
    # ============================================================

    def answer_question(
        self,
        db: Session,
        question: str,
        top_k: int = 3,
        document_id: str | None = None,
        session_id: str | None = None
    ):

        # --------------------------------------------------------
        # 1. Get existing chat session OR create a new one
        # --------------------------------------------------------

        if session_id:

            chat_session = get_chat_session(
                db=db,
                session_id=session_id
            )

            if not chat_session:
                raise ValueError(
                    "Chat session not found."
                )

            # ----------------------------------------------------
            # IMPORTANT:
            # Always use the document associated with the
            # existing chat session.
            # ----------------------------------------------------

            if chat_session.document_id:

                document_id = chat_session.document_id

        else:

            chat_session = create_chat_session(
                db=db,
                document_id=document_id
            )

        # --------------------------------------------------------
        # 2. Get previous conversation
        # --------------------------------------------------------

        previous_messages = get_chat_messages(
            db=db,
            session_id=chat_session.session_id
        )

        conversation_history = (
            self.build_conversation_history(
                previous_messages
            )
        )

        # --------------------------------------------------------
        # 3. Retrieve relevant document chunks
        # --------------------------------------------------------

        retrieved_chunks = self.retrieve_context(
            question=question,
            top_k=top_k,
            document_id=document_id
        )

        # --------------------------------------------------------
        # 4. Handle no relevant information
        # --------------------------------------------------------

        if not retrieved_chunks:

            answer = (
                "I could not find relevant information "
                "in the provided document."
            )

            create_chat_message(
                db=db,
                session_id=chat_session.session_id,
                question=question,
                answer=answer,
                sources=[]
            )

            return {
                "session_id": chat_session.session_id,
                "answer": answer,
                "sources": []
            }

        # --------------------------------------------------------
        # 5. Build RAG context
        # --------------------------------------------------------

        context_parts = []

        for index, chunk in enumerate(
            retrieved_chunks,
            start=1
        ):

            metadata = chunk["metadata"]

            filename = metadata.get(
                "filename",
                "Unknown file"
            )

            page = metadata.get(
                "page",
                "Unknown"
            )

            context_parts.append(
                f"""
SOURCE {index}
File: {filename}
Page: {page}

{chunk["text"]}
"""
            )

        context = "\n\n".join(
            context_parts
        )

        # --------------------------------------------------------
        # 6. Generate answer using LLM
        # --------------------------------------------------------

        answer = self.llm_service.generate_answer(
            question=question,
            context=context,
            conversation_history=conversation_history
        )

        # --------------------------------------------------------
        # 7. Prepare sources
        # --------------------------------------------------------

        sources = []

        for chunk in retrieved_chunks:

            metadata = chunk["metadata"]

            sources.append(
                {
                    "document_id": metadata.get(
                        "document_id"
                    ),
                    "filename": metadata.get(
                        "filename"
                    ),
                    "page": metadata.get(
                        "page"
                    ),
                    "distance": chunk["distance"]
                }
            )

        # --------------------------------------------------------
        # 8. Save message
        # --------------------------------------------------------

        create_chat_message(
            db=db,
            session_id=chat_session.session_id,
            question=question,
            answer=answer,
            sources=sources
        )

        # --------------------------------------------------------
        # 9. Return response
        # --------------------------------------------------------

        return {
            "session_id": chat_session.session_id,
            "answer": answer,
            "sources": sources
        }

    # ============================================================
    # GET CONVERSATION HISTORY
    # ============================================================

    def get_conversation_history(
        self,
        db: Session,
        session_id: str
    ):

        chat_session = get_chat_session(
            db=db,
            session_id=session_id
        )

        if not chat_session:
            raise ValueError(
                "Chat session not found."
            )

        messages = get_chat_messages(
            db=db,
            session_id=session_id
        )

        history = []

        for message in messages:

            history.append(
                {
                    "id": message.id,
                    "question": message.question,
                    "answer": message.answer,
                    "sources": message.sources,
                    "created_at": message.created_at
                }
            )

        return {
            "session_id": session_id,
            "document_id": chat_session.document_id,
            "messages": history
        }

    # ============================================================
    # GET CHAT HISTORY
    # ============================================================

    def get_chat_history(
        self,
        db: Session,
        session_id: str
    ):

        chat_session = get_chat_session(
            db=db,
            session_id=session_id
        )

        if not chat_session:
            return None

        messages = get_chat_messages(
            db=db,
            session_id=session_id
        )

        return {
            "session_id": session_id,
            "document_id": chat_session.document_id,
            "messages": [
                {
                    "question": message.question,
                    "answer": message.answer,
                    "sources": message.sources,
                    "created_at": message.created_at
                }
                for message in messages
            ]
        }