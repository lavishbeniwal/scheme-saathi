from rag.generator import generate
from rag.retriever import retrieve


def answer_question(query: str) -> dict:
    chunks = retrieve(query)
    answer = generate(query, chunks)
    sources = sorted({chunk["scheme_name"] for chunk in chunks})
    return {"answer": answer, "sources": sources}
