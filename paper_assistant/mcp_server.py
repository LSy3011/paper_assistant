import argparse
import asyncio
import json
from pathlib import Path

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc

try:
    from .config import (
        EMBEDDING_DIM,
        MAX_TOKEN_SIZE,
        PDF_DIR,
        WORKING_DIR,
    )
    from .main import ollama_embedding_func, ollama_llm_func
except ImportError:
    from config import (
        EMBEDDING_DIM,
        MAX_TOKEN_SIZE,
        PDF_DIR,
        WORKING_DIR,
    )
    from main import ollama_embedding_func, ollama_llm_func


def list_papers():
    if not PDF_DIR.exists():
        return {"papers": []}
    return {"papers": sorted(p.name for p in PDF_DIR.glob("*.pdf"))}


def paper_search(query, top_k=5):
    query_terms = [term.lower() for term in query.split() if term.strip()]
    results = []

    for path in WORKING_DIR.glob("processed_*.txt"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        score = sum(lowered.count(term) for term in query_terms)
        if score <= 0:
            continue

        first_hit = min(
            (lowered.find(term) for term in query_terms if lowered.find(term) >= 0),
            default=0,
        )
        start = max(first_hit - 240, 0)
        end = min(first_hit + 760, len(text))
        results.append(
            {
                "source": path.name,
                "score": score,
                "chunk": text[start:end].strip(),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return {"query": query, "results": results[:top_k]}


async def paper_ask(question, mode="hybrid"):
    rag = LightRAG(
        working_dir=str(WORKING_DIR),
        llm_model_func=ollama_llm_func,
        embedding_func=EmbeddingFunc(
            func=ollama_embedding_func,
            embedding_dim=EMBEDDING_DIM,
            max_token_size=MAX_TOKEN_SIZE,
        ),
    )
    await rag.initialize_storages()
    answer = await rag.aquery(question, param=QueryParam(mode=mode))
    return {"question": question, "mode": mode, "answer": answer}


def graph_neighbors(entity, depth=1):
    graph_file = WORKING_DIR / "graph_chunk_entity_relation.graphml"
    if not graph_file.exists():
        return {"entity": entity, "neighbors": [], "error": f"missing graph file: {graph_file}"}

    import networkx as nx

    graph = nx.read_graphml(graph_file)
    matches = [node for node in graph.nodes if entity.lower() in str(node).lower()]
    neighbors = []
    for node in matches[:5]:
        visited = {node}
        frontier = {node}
        for current_depth in range(1, depth + 1):
            next_frontier = set()
            for current in frontier:
                for neighbor in graph.neighbors(current):
                    if neighbor in visited:
                        continue
                    visited.add(neighbor)
                    next_frontier.add(neighbor)
                    neighbors.append(
                        {
                            "source": str(current),
                            "target": str(neighbor),
                            "depth": current_depth,
                        }
                    )
            frontier = next_frontier
    return {"entity": entity, "matches": [str(m) for m in matches[:5]], "neighbors": neighbors}


def run_cli():
    parser = argparse.ArgumentParser(description="Paper Assistant tool server fallback")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list_papers")

    search_parser = subparsers.add_parser("paper_search")
    search_parser.add_argument("query")
    search_parser.add_argument("--top-k", type=int, default=5)

    ask_parser = subparsers.add_parser("paper_ask")
    ask_parser.add_argument("question")
    ask_parser.add_argument("--mode", default="hybrid")

    graph_parser = subparsers.add_parser("graph_neighbors")
    graph_parser.add_argument("entity")
    graph_parser.add_argument("--depth", type=int, default=1)

    args = parser.parse_args()
    if args.command == "list_papers":
        payload = list_papers()
    elif args.command == "paper_search":
        payload = paper_search(args.query, args.top_k)
    elif args.command == "paper_ask":
        payload = asyncio.run(paper_ask(args.question, args.mode))
    else:
        payload = graph_neighbors(args.entity, args.depth)

    print(json.dumps(payload, ensure_ascii=False, indent=2))


def run_mcp():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        run_cli()
        return

    app = FastMCP("paper-assistant")
    app.tool()(list_papers)
    app.tool()(paper_search)
    app.tool()(paper_ask)
    app.tool()(graph_neighbors)
    app.run()


if __name__ == "__main__":
    run_mcp()
