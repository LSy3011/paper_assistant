# Paper Assistant 使用指南

## 1. 服务器启动

```bash
cd /mnt/workspace/paper_assistant/paper_assistant
source venv/bin/activate
```

确认环境：

```bash
python paper_assistant/health_check.py
```

## 2. 查询已有知识库

推荐演示模式：

```bash
export PAPER_ASSISTANT_INGEST_MODE=skip
python paper_assistant/main.py
```

该模式会跳过 PDF 解析，直接加载 `paper_assistant/index_data/` 中的 LightRAG 索引。

## 3. 重建索引

如果新增 PDF 或需要重新构建索引：

```bash
export PAPER_ASSISTANT_INGEST_MODE=always
python paper_assistant/main.py
```

推荐默认解析器：

```bash
export PAPER_ASSISTANT_PARSE_BACKEND=pymupdf
```

高精度解析：

```bash
export PAPER_ASSISTANT_PARSE_BACKEND=docling
export PAPER_ASSISTANT_ENABLE_OCR=0
```

## 4. Web 问答

```bash
streamlit run paper_assistant/app.py --server.address 0.0.0.0 --server.port 8501
```

打开 Streamlit 输出的外部地址后，可以直接向论文知识库提问。

## 5. MCP/CLI 工具

```bash
python paper_assistant/mcp_server.py list_papers
python paper_assistant/mcp_server.py paper_ask "Only based on the indexed papers, compare ML-CGRA, VecPAC and DRIPS." --mode hybrid
python paper_assistant/mcp_server.py graph_neighbors CGRA --depth 1
```

如果安装了 MCP SDK，`mcp_server.py` 会优先作为 MCP 服务启动；否则退化为 CLI 工具，便于服务器验证。

## 6. 图谱可视化

```bash
python paper_assistant/visualize.py
```

输出文件：

```text
paper_assistant/knowledge_graph_offline.html
```

## 7. 常见问题

### 为什么 A10 没有被 PDF 解析使用？

PDF 解析默认使用 PyMuPDF 快速模式，主要走 CPU。Docling/RapidOCR 可能使用 PyTorch，但如果 PyTorch CUDA 构建版本与服务器 NVIDIA 驱动不匹配，会自动回退 CPU。项目主链路依赖 Ollama 运行本地 LLM 和 embedding。

### 为什么默认跳过 PDF 解析？

服务器演示时已有索引，重复解析 PDF 会浪费时间。`PAPER_ASSISTANT_INGEST_MODE=skip` 或 `auto` 可以让系统直接加载已有索引并查询。

### 什么时候使用 Docling？

当 PDF 中表格、公式、版式结构对结果很重要时，可以切换到 Docling。日常演示和快速验证推荐使用 PyMuPDF。
