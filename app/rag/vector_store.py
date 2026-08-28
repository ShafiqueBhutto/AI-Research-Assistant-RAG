from pathlib import Path

import chromadb

from app.rag.embeddings import EmbeddingService


class VectorStore:
    def __init__(self):
        database_path = Path("data/chroma")
        database_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(database_path)
        )

        self.collection = self.client.get_or_create_collection(
            name="research_documents"
        )

        self.embedding_service = EmbeddingService()

    def add_document_chunks(
        self,
        chunks: list[str],
        metadatas: list[dict],
        ids: list[str]
    ):
        embeddings = self.embedding_service.generate_embeddings(chunks)

        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def search_similar_chunks(
        self,
        query: str,
        top_k: int = 3,
        document_id: str | None = None
    ):
        query_embedding = (
            self.embedding_service.generate_query_embedding(query)
        )

        if document_id:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={
                    "document_id": document_id
                }
            )
        else:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

        return results

    def delete_document(
        self,
        document_id: str
    ):
        self.collection.delete(
            where={
                "document_id": document_id
            }
        )