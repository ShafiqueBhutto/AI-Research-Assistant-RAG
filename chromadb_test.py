import chromadb
from sentence_transformers import SentenceTransformer

# 1. Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Create ChromaDB client
client = chromadb.PersistentClient(path="./data/chroma")

# 3. Create/get collection
collection = client.get_or_create_collection(
    name="research_documents"
)

# 4. Sample documents
documents = [
    "Retrieval-Augmented Generation combines information retrieval with large language models.",
    "Machine learning is a field of artificial intelligence that allows computers to learn from data.",
    "Deep learning uses neural networks with multiple layers to learn complex patterns.",
    "FastAPI is a Python framework used to build high-performance APIs."
]

# 5. Generate embeddings
embeddings = model.encode(documents).tolist()

# 6. Store documents + embeddings in ChromaDB
collection.add(
    ids=["doc1", "doc2", "doc3", "doc4"],
    documents=documents,
    embeddings=embeddings
)

print("Documents successfully stored in ChromaDB!")

# 7. User query
query = "What is Retrieval-Augmented Generation?"

# 8. Create embedding for query
query_embedding = model.encode([query]).tolist()

# 9. Search ChromaDB
results = collection.query(
    query_embeddings=query_embedding,
    n_results=2
)

# 10. Display results
print("\nQuery:")
print(query)

print("\nMost Relevant Documents:")

for i, document in enumerate(results["documents"][0]):
    print(f"\nResult {i + 1}:")
    print(document)

print("\nDistances:")
print(results["distances"][0])