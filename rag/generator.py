from groq import Groq

from rag.config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPT = (
    "You are Scheme Saathi, an assistant that answers questions about Indian "
    "government welfare schemes using ONLY the context provided below. "
    "If the answer is not contained in the context, say clearly that you "
    "don't have information on that in the current knowledge base — do not "
    "guess or use outside knowledge. Cite the scheme name(s) your answer is "
    "based on."
)

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set — copy .env.example to .env and add your key."
            )
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def generate(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(chunk["text"] for chunk in chunks)
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
