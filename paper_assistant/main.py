import asyncio
import os

import numpy as np
import ollama
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc

try:
    from lightrag.kg.shared_storage import initialize_pipeline_status
except Exception:
    initialize_pipeline_status = None

try:
    from .config import (
        CHUNK_OVERLAP_TOKEN_SIZE,
        CHUNK_TOKEN_SIZE,
        EMBEDDING_DIM,
        EMBEDDING_MODEL_NAME,
        INGEST_MODE,
        LLM_MODEL_MAX_ASYNC,
        LLM_MODEL_NAME,
        MAX_TOKEN_SIZE,
        OLLAMA_CTX,
        OLLAMA_TEMPERATURE,
        PARSER_BACKEND,
        PDF_DIR,
        WORKING_DIR,
    )
    from .specialized_parser import specialized_parser
except ImportError:
    from config import (
        CHUNK_OVERLAP_TOKEN_SIZE,
        CHUNK_TOKEN_SIZE,
        EMBEDDING_DIM,
        EMBEDDING_MODEL_NAME,
        INGEST_MODE,
        LLM_MODEL_MAX_ASYNC,
        LLM_MODEL_NAME,
        MAX_TOKEN_SIZE,
        OLLAMA_CTX,
        OLLAMA_TEMPERATURE,
        PARSER_BACKEND,
        PDF_DIR,
        WORKING_DIR,
    )
    from specialized_parser import specialized_parser


def parse_pdf_structured(file_path):
    return specialized_parser.parse(file_path)


async def initialize_lightrag(rag):
    """Initialize LightRAG storage lifecycle for current and older releases."""
    await rag.initialize_storages()
    if initialize_pipeline_status is not None:
        try:
            await initialize_pipeline_status()
        except TypeError:
            # Some LightRAG versions expose the symbol but do not need explicit args.
            pass
    return rag


async def finalize_lightrag(rag):
    finalize = getattr(rag, "finalize_storages", None)
    if callable(finalize):
        await finalize()


async def ollama_llm_func(prompt, system_prompt=None, history_messages=None, **kwargs):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    try:
        response = await asyncio.to_thread(
            ollama.chat,
            model=LLM_MODEL_NAME,
            messages=messages,
            options={"num_ctx": OLLAMA_CTX, "temperature": OLLAMA_TEMPERATURE},
        )
        return response["message"]["content"]
    except Exception as exc:
        print(f"LLM call failed: {exc}")
        return ""


async def ollama_embedding_func(texts):
    if isinstance(texts, str):
        texts = [texts]

    embeddings = []
    for text in texts:
        try:
            response = await asyncio.to_thread(
                ollama.embeddings,
                model=EMBEDDING_MODEL_NAME,
                prompt=text,
            )
            embeddings.append(response["embedding"])
        except Exception as exc:
            print(f"Embedding call failed; using zero vector fallback: {exc}")
            embeddings.append([0.0] * EMBEDDING_DIM)
    return np.array(embeddings)


def should_ingest_pdfs():
    graph_file = WORKING_DIR / "graph_chunk_entity_relation.graphml"

    if INGEST_MODE == "skip":
        return False
    if INGEST_MODE == "always":
        return True
    return not graph_file.exists()


async def ingest_pdfs(rag):
    files = sorted(f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf"))
    if not files:
        print(f"No PDF files found in {PDF_DIR}.")
        return

    for filename in files:
        pdf_path = PDF_DIR / filename
        print(f"\nParsing and ingesting: {filename}")
        content = parse_pdf_structured(str(pdf_path))
        if not content:
            print("Parser returned empty content; skipping.")
            continue
        await rag.ainsert(content)
        print("Ingestion complete.")


async def main():
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(WORKING_DIR, exist_ok=True)

    print("=== Paper Assistant LightRAG Demo ===")
    print(f"PDF parser backend: {PARSER_BACKEND}")
    print(f"Ingest mode: {INGEST_MODE}")
    print(f"PDF dir: {PDF_DIR}")
    print(f"Index dir: {WORKING_DIR}")

    rag = None
    try:
        rag = LightRAG(
            working_dir=str(WORKING_DIR),
            llm_model_func=ollama_llm_func,
            embedding_func=EmbeddingFunc(
                func=ollama_embedding_func,
                embedding_dim=EMBEDDING_DIM,
                max_token_size=MAX_TOKEN_SIZE,
            ),
            chunk_token_size=CHUNK_TOKEN_SIZE,
            chunk_overlap_token_size=CHUNK_OVERLAP_TOKEN_SIZE,
            llm_model_max_async=LLM_MODEL_MAX_ASYNC,
        )
        await initialize_lightrag(rag)

        if should_ingest_pdfs():
            await ingest_pdfs(rag)
        else:
            print("Existing LightRAG index detected; skipping PDF ingestion.")
            print("Set PAPER_ASSISTANT_INGEST_MODE=always to rebuild, or skip to force query-only mode.")

        query = "Please analyze how these papers improve CGRA compilation efficiency and give the reasoning."
        print(f"\nQuery: {query}")
        result = await rag.aquery(query, param=QueryParam(mode="hybrid"))
        print(f"\nAnswer:\n{result}")
    finally:
        if rag is not None:
            await finalize_lightrag(rag)


if __name__ == "__main__":
    asyncio.run(main())
