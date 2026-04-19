import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR.parent / ".env")
except ImportError:
    pass

def resolve_path(value, default):
    path = Path(os.getenv(value, default))
    return path if path.is_absolute() else BASE_DIR.parent / path


PDF_DIR = resolve_path("PAPER_ASSISTANT_PDF_DIR", BASE_DIR / "pdfs")
WORKING_DIR = resolve_path("PAPER_ASSISTANT_WORKING_DIR", BASE_DIR / "index_data")

LLM_MODEL_NAME = os.getenv("OLLAMA_LLM_MODEL", "qwen2.5:7b")
EMBEDDING_MODEL_NAME = os.getenv("OLLAMA_EMBED_MODEL", "bge-m3:latest")
OLLAMA_CTX = int(os.getenv("OLLAMA_CTX", "32000"))
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))

EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))
MAX_TOKEN_SIZE = int(os.getenv("MAX_TOKEN_SIZE", "8192"))
CHUNK_TOKEN_SIZE = int(os.getenv("CHUNK_TOKEN_SIZE", "1024"))
CHUNK_OVERLAP_TOKEN_SIZE = int(os.getenv("CHUNK_OVERLAP_TOKEN_SIZE", "128"))
LLM_MODEL_MAX_ASYNC = int(os.getenv("LLM_MODEL_MAX_ASYNC", "1"))
