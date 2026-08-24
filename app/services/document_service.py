from pathlib import Path

import pymupdf

from app.rag.vector_store import VectorStore


class DocumentService:
    def __init__(self):
        self.vector_store = VectorStore()

    def process_pdf(self, pdf_path: str, document_id: str):
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        chunks = []
        metadatas = []
        ids = []

        document = pymupdf.open(pdf_file)

        chunk_number = 1

        for page_number, page in enumerate(document, start=1):
            text = page.get_text().strip()

            if not text:
                continue

            page_chunks = self._create_chunks(text)

            for chunk in page_chunks:
                chunks.append(chunk)

                metadatas.append({
                    "document_id": document_id,
                    "filename": pdf_file.name,
                    "page": page_number
                })

                ids.append(
                    f"{document_id}_chunk_{chunk_number}"
                )

                chunk_number += 1

        document.close()

        if not chunks:
            raise ValueError("No text could be extracted from the PDF.")

        self.vector_store.add_document_chunks(
            chunks=chunks,
            metadatas=metadatas,
            ids=ids
        )

        return {
            "document_id": document_id,
            "filename": pdf_file.name,
            "chunks_stored": len(chunks)
        }

    def _create_chunks(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ):
        words = text.split()

        chunks = []

        start = 0

        while start < len(words):
            end = start + chunk_size

            chunk = " ".join(words[start:end])

            if chunk.strip():
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks