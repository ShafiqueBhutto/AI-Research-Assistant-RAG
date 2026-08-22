def chunk_text(text, chunk_size=100, overlap=20):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks


pages = [
    {
        "page": 1,
        "text": "This is page one containing information about artificial intelligence."
    },
    {
        "page": 2,
        "text": "This is page two containing information about machine learning."
    }
]

document_id = "doc-001"

all_chunks = []

for page in pages:
    chunks = chunk_text(page["text"])

    for chunk_number, chunk in enumerate(chunks, start=1):
        all_chunks.append({
            "document_id": document_id,
            "chunk_id": f"{document_id}-p{page['page']}-c{chunk_number}",
            "page": page["page"],
            "text": chunk
        })


for chunk in all_chunks:
    print(chunk)