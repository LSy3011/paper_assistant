# Paper Assistant Server Fast Mode

## Why A10 May Not Be Used During PDF Parsing

The A10 GPU is mainly useful for local LLM inference and embedding workloads.
In this project those workloads are handled by Ollama.

PDF parsing is different:

- The fast parser, PyMuPDF, is CPU-oriented but very quick for text-based PDFs.
- The high-fidelity parser, Docling, can load layout/OCR models and may download
  HuggingFace model files on first run.
- If PyTorch CUDA cannot initialize because the installed PyTorch build does not
  match the server NVIDIA driver, Docling/RapidOCR will fall back to CPU.

The server log showed:

```text
CUDA initialization: The NVIDIA driver on your system is too old
Accelerator device: 'cpu'
```

So the slow behavior was caused by Docling/RapidOCR running on CPU plus first-run
model initialization/downloads, not by LightRAG itself.

## Recommended Demo Configuration

Create or update `.env` in the repository root:

```env
PAPER_ASSISTANT_PARSE_BACKEND=pymupdf
PAPER_ASSISTANT_ENABLE_OCR=0
PAPER_ASSISTANT_INGEST_MODE=auto
```

Meaning:

- `pymupdf`: fast text extraction, best for server validation and interview demos.
- `docling`: slower high-fidelity parsing for layout/table-heavy PDFs.
- `auto`: try Docling first, then fall back to PyMuPDF.
- `PAPER_ASSISTANT_INGEST_MODE=auto`: skip PDF parsing when an existing LightRAG
  graph index is already present.

## Rebuild Index When Needed

To force a full rebuild:

```bash
export PAPER_ASSISTANT_INGEST_MODE=always
python paper_assistant/main.py
```

To only query an existing index:

```bash
export PAPER_ASSISTANT_INGEST_MODE=skip
python paper_assistant/main.py
```

## Server Run

```bash
cd /mnt/workspace/paper_assistant/paper_assistant
source venv/bin/activate
python paper_assistant/health_check.py
python paper_assistant/main.py
```
