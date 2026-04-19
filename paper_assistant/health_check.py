import importlib.util
import json
from pathlib import Path

import ollama

try:
    from .config import EMBEDDING_MODEL_NAME, INGEST_MODE, LLM_MODEL_NAME, PARSER_BACKEND, PDF_DIR, WORKING_DIR
except ImportError:
    from config import EMBEDDING_MODEL_NAME, INGEST_MODE, LLM_MODEL_NAME, PARSER_BACKEND, PDF_DIR, WORKING_DIR


def check_import(module_name):
    return importlib.util.find_spec(module_name) is not None


def check_ollama_models():
    try:
        response = ollama.list()
        raw_models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
        names = set()
        for model in raw_models:
            if isinstance(model, dict):
                names.add(model.get("name") or model.get("model"))
            else:
                names.add(getattr(model, "name", None) or getattr(model, "model", None))
        names.discard(None)
        return {
            "ok": True,
            "models": sorted(names),
            "has_llm": LLM_MODEL_NAME in names,
            "has_embedding": EMBEDDING_MODEL_NAME in names,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def check_torch_cuda():
    if not check_import("torch"):
        return {"torch_installed": False}
    try:
        import torch

        return {
            "torch_installed": True,
            "cuda_available": bool(torch.cuda.is_available()),
            "torch_version": torch.__version__,
            "cuda_build": getattr(torch.version, "cuda", None),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }
    except Exception as exc:
        return {
            "torch_installed": True,
            "cuda_available": False,
            "error": str(exc),
            "hint": "Docling/RapidOCR will use CPU when PyTorch CUDA cannot initialize.",
        }


def main():
    checks = {
        "paths": {
            "pdf_dir": str(PDF_DIR),
            "pdf_dir_exists": PDF_DIR.exists(),
            "pdf_count": len(list(PDF_DIR.glob("*.pdf"))) if PDF_DIR.exists() else 0,
            "working_dir": str(WORKING_DIR),
            "working_dir_exists": WORKING_DIR.exists(),
            "graph_exists": (WORKING_DIR / "graph_chunk_entity_relation.graphml").exists(),
        },
        "config": {
            "parser_backend": PARSER_BACKEND,
            "ingest_mode": INGEST_MODE,
        },
        "imports": {
            "lightrag": check_import("lightrag"),
            "docling": check_import("docling"),
            "fitz": check_import("fitz"),
            "streamlit": check_import("streamlit"),
            "dotenv": check_import("dotenv"),
        },
        "torch_cuda": check_torch_cuda(),
        "ollama": check_ollama_models(),
    }
    print(json.dumps(checks, ensure_ascii=False, indent=2))

    critical_ok = (
        checks["paths"]["pdf_dir_exists"]
        and checks["imports"]["lightrag"]
        and checks["imports"]["fitz"]
        and checks["ollama"]["ok"]
        and checks["ollama"].get("has_llm", False)
        and checks["ollama"].get("has_embedding", False)
    )
    raise SystemExit(0 if critical_ok else 1)


if __name__ == "__main__":
    main()
