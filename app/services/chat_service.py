from app.rag.vector_store import VectorStore
from app.services.llm_service import LLMService


class ChatService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_service = LLMService()

    def retrieve_context(
        self,
        question: str,
        top_k: int = 3
    ):
        results = self.vector_store.search_similar_chunks(
            query=question,
            top_k=top_k
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
        question: str,
        top_k: int = 3
    ):
        retrieved_chunks = self.retrieve_context(
            question=question,
            top_k=top_k
        )

        if not retrieved_chunks:
            return {
                "answer": "I could not find relevant information in the provided documents.",
                "sources": []
            }

        context_parts = []

        for chunk in retrieved_chunks:
            metadata = chunk["metadata"]

            source = (
                f"Document: {metadata.get('filename', 'Unknown')}, "
                f"Page: {metadata.get('page', 'Unknown')}"
            )

            context_parts.append(
                f"{source}\n"
                f"{chunk['text']}"
            )

        context = "\n\n---\n\n".join(context_parts)

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

        return {
            "answer": answer,
            "sources": sources
        }