from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return embeddings.tolist()

    def generate_query_embedding(self, query: str) -> list[float]:
        embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )

        return embedding.tolist()