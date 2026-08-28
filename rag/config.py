import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
CHROMA_DIR = ROOT_DIR / "chroma_db"

COLLECTION_NAME = "scheme_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = "openai/gpt-oss-120b"

TOP_K = 4
