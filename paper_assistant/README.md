# paper_assistant package

This directory contains the runnable Paper Assistant code.

For the full project overview, setup commands, and resume-ready description,
see the repository-level `README.md` and `USAGE_GUIDE.md`.

## Main Entrypoints

- `main.py`: command-line LightRAG demo for querying the indexed papers.
- `app.py`: Streamlit knowledge-base UI.
- `mcp_server.py`: MCP-style command-line tools for paper search, QA, and graph lookup.
- `health_check.py`: environment and model readiness check.
- `specialized_parser.py`: PDF parser wrapper with fast PyMuPDF mode and optional Docling mode.
- `visualize.py`: offline knowledge graph HTML generator.

## Runtime Data

- `pdfs/`: demo papers used by the local knowledge base.
- `index_data/`: demo LightRAG index for query-only startup.
- `knowledge_graph_offline.html`: offline graph visualization generated from the index.

These demo assets are intentionally kept so the project can run immediately on
the server with `PAPER_ASSISTANT_INGEST_MODE=skip`.
