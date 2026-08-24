from pathlib import Path
import shutil


CHROMA_DIR = Path("data/chroma")


if CHROMA_DIR.exists():
    shutil.rmtree(CHROMA_DIR)
    print("ChromaDB reset successfully.")
else:
    print("ChromaDB directory does not exist.")

CHROMA_DIR.mkdir(parents=True, exist_ok=True)

print("Fresh ChromaDB directory created.")