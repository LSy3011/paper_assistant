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

# PDF parsing and ingestion controls.
# PAPER_ASSISTANT_PARSE_BACKEND:
#   pymupdf  -> fast text extraction, best for demos and server validation
#   docling  -> high-fidelity layout/table parsing, slower and may download HF models
#   auto     -> try docling first, then fallback to pymupdf
PARSER_BACKEND = os.getenv("PAPER_ASSISTANT_PARSE_BACKEND", "pymupdf").strip().lower()
PARSER_ENABLE_OCR = os.getenv("PAPER_ASSISTANT_ENABLE_OCR", "0").strip().lower() in {"1", "true", "yes"}

# PAPER_ASSISTANT_INGEST_MODE:
#   auto   -> ingest PDFs only when no existing LightRAG graph is present
#   always -> parse and ingest PDFs every run
#   skip   -> never ingest PDFs, only query the existing index
INGEST_MODE = os.getenv("PAPER_ASSISTANT_INGEST_MODE", "auto").strip().lower()
