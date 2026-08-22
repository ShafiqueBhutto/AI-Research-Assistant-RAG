from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "Machine learning is a subset of artificial intelligence.",
    "AI includes machine learning techniques.",
    "I cooked dinner yesterday."
]

embeddings = model.encode(sentences)

print("Embedding shape:", embeddings.shape)

similarity = cosine_similarity(embeddings)

print("\nSimilarity Matrix:")
print(similarity)