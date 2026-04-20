# Paper Assistant

本项目是一个本地化论文知识库与 GraphRAG 问答系统，面向学术论文、行业报告和长文档知识管理场景。系统基于 LightRAG、Ollama 和 BGE-M3 构建向量索引与知识图谱索引，支持论文问答、跨论文比较、图谱邻居查询、Streamlit Web 交互和 MCP/CLI 工具化调用。

## 项目定位

Paper Assistant 解决的是“专业文档如何沉淀为可检索、可问答、可被 Agent 调用的知识服务”的问题。

它和 Second Agent 的分工是：

- Paper Assistant：知识库基础设施，负责 PDF 解析、索引构建、GraphRAG 查询和 MCP 工具暴露。
- Second Agent：上层 Agent runtime，负责长期记忆、Skill 调用、工具选择和推理轨迹。

组合后可以形成“企业私有知识库 + Agent 执行层”的架构，适用于研发知识助手、技术调研助手、售前知识支持、企业内训、行业研究和内部文档问答等场景。

## 已验证能力

服务器验证结果：

- 已加载论文知识图谱：约 1070 个节点、881 条关系。
- 已加载文本块：70 个 chunks。
- 支持 `hybrid` GraphRAG 查询并生成回答。
- 支持 Streamlit Web 页面问答。
- 支持 GraphML 离线可视化 HTML 生成。
- 支持 MCP/CLI fallback 工具：`list_papers`、`paper_ask`、`graph_neighbors`。

## 技术栈

- Python
- LightRAG-HKU
- Ollama
- Qwen2.5-7B
- BGE-M3
- PyMuPDF
- Docling
- Streamlit
- NetworkX / PyVis
- MCP/CLI

## 目录结构

```text
.
├── paper_assistant/
│   ├── main.py                 # CLI GraphRAG 查询与索引构建入口
│   ├── app.py                  # Streamlit Web 问答
│   ├── mcp_server.py           # MCP Server / CLI fallback
│   ├── health_check.py         # 环境与索引健康检查
│   ├── specialized_parser.py   # PyMuPDF / Docling 可切换 PDF 解析器
│   ├── visualize.py            # GraphML 离线可视化
│   ├── pdfs/                   # 示例论文 PDF
│   └── index_data/             # 已验证的 LightRAG 示例索引
├── docs/
│   ├── PAPER_ASSISTANT_BUILD_GUIDE.md
│   ├── PAPER_ASSISTANT_SERVER_FAST_MODE.md
│   ├── MCP_AND_SKILL_EXTENSION_PLAN.md
│   └── mcp_tool_contracts/
├── .env.example
├── requirements.txt
└── USAGE_GUIDE.md
```

## 快速运行

服务器已有虚拟环境时：

```bash
cd /mnt/workspace/paper_assistant/paper_assistant
source venv/bin/activate
```

健康检查：

```bash
python paper_assistant/health_check.py
```

查询已有索引：

```bash
export PAPER_ASSISTANT_INGEST_MODE=skip
python paper_assistant/main.py
```

启动 Web 页面：

```bash
streamlit run paper_assistant/app.py --server.address 0.0.0.0 --server.port 8501
```

生成图谱可视化：

```bash
python paper_assistant/visualize.py
```

## MCP/CLI 工具

列出论文：

```bash
python paper_assistant/mcp_server.py list_papers
```

论文问答：

```bash
python paper_assistant/mcp_server.py paper_ask "Only based on the indexed papers, compare ML-CGRA, VecPAC and DRIPS." --mode hybrid
```

图谱邻居查询：

```bash
python paper_assistant/mcp_server.py graph_neighbors CGRA --depth 1
```

## 关键配置

复制 `.env.example` 为 `.env` 后可调整：

```env
PAPER_ASSISTANT_PARSE_BACKEND=pymupdf
PAPER_ASSISTANT_ENABLE_OCR=0
PAPER_ASSISTANT_INGEST_MODE=auto
OLLAMA_LLM_MODEL=qwen2.5:7b
OLLAMA_EMBED_MODEL=bge-m3:latest
```

解析模式：

- `pymupdf`：默认快速模式，适合服务器演示。
- `docling`：高精度解析，适合表格/公式/版式要求高的 PDF，但首次运行可能较慢。
- `auto`：优先 Docling，失败后降级到 PyMuPDF。

索引模式：

- `auto`：有索引则跳过解析，没有索引才构建。
- `skip`：只查询已有索引。
- `always`：每次都解析 PDF 并写入索引。

## 项目表述

> 基于 LightRAG + Ollama + BGE-M3 构建本地化科研与企业文档 GraphRAG 知识服务，实现 PDF 解析、向量/图谱混合检索、Streamlit 问答、MCP/CLI 工具化调用与 GraphML 可视化；在 A10 服务器完成部署验证，成功加载约 1070 个图谱节点、881 条关系和 70 个文本块，支持 CGRA/MLIR 技术资料问答、跨文档比较与图谱邻居查询。
