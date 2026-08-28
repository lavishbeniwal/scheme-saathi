import re

import chromadb
from sentence_transformers import SentenceTransformer

from ingestion.chunker import chunk_schemes
from ingestion.loader import load_schemes
from rag.config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def build_index() -> int:
    schemes = load_schemes()
    if not schemes:
        raise RuntimeError("No scheme documents found in data/raw/")

    chunks = chunk_schemes(schemes)
    if not chunks:
        raise RuntimeError("No chunks produced from scheme documents")

    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode([chunk.text for chunk in chunks]).tolist()

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    client.delete_collection(COLLECTION_NAME) if COLLECTION_NAME in [
        c.name for c in client.list_collections()
    ] else None
    collection = client.create_collection(COLLECTION_NAME)

    ids = [
        f"{_slugify(chunk.scheme_name)}--{_slugify(chunk.section)}" for chunk in chunks
    ]
    documents = [chunk.text for chunk in chunks]
    metadatas = [
        {
            "scheme_name": chunk.scheme_name,
            "section": chunk.section,
            "source_url": chunk.source_url,
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
    )

    return len(chunks)


if __name__ == "__main__":
    count = build_index()
    print(f"Indexed {count} chunks into Chroma at {CHROMA_DIR}")
