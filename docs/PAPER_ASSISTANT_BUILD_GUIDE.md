# Paper Assistant 项目搭建与架构说明文档

## 1. 项目定位

Paper Assistant 可以包装成一个“企业私有知识服务平台”的底层模块：面向科研论文、技术报告、研发文档、产品资料、行业分析和内部知识库等非结构化内容，把长期积累的资料转成可检索、可解释、可复用、可被 Agent 调用的知识资产。当前代码以 CGRA/MLIR 科研论文为样例场景，核心是把 PDF 论文解析成结构化文本，再交给 LightRAG 建立向量索引与知识图谱，最后支持问答、跨文档对比、知识图谱可视化和 RAG 效果评估。

简历定位建议：

> 基于 LightRAG + Ollama + BGE-M3 构建本地化科研与企业文档知识服务平台，以 CGRA/MLIR 论文为验证数据，实现 PDF 解析、GraphRAG 混合检索、知识图谱可视化、MCP 工具化暴露和 RAG 评估闭环，并针对长文档处理中的异步超时、模型下载和本地推理稳定性问题完成工程化排查与优化。

这个项目更适合体现知识工程与 AI 应用工程能力：文档解析、索引构建、检索增强生成、评估指标、工具协议暴露、工程排障。公司层面可以服务研发知识库、技术调研、售前支持、企业内训、投研资料分析和内部文档问答等“私有知识密集 + 需要可信引用”的场景。

## 2. 与 Second Agent 的差异

Paper Assistant 解决的是“专业文档如何被系统理解并检索”的问题，输入是论文 PDF，核心链路是文档解析、索引构建、图谱检索、问答评估。

Second Agent 解决的是“Agent 如何拥有长期记忆并做工具化推理”的问题，输入是用户记忆和任务，核心链路是 Mem0 向量记忆、Neo4j 图谱记忆、ReAct 工具选择、推理轨迹记录。

面试时可以这样区分：

- Paper Assistant：偏 RAG 基础设施和知识库构建。
- Second Agent：偏 Agent runtime、记忆系统和工具调用决策。
- 两者连接：Paper Assistant 可以作为高质量知识源，Second Agent 可以作为调用知识源的上层智能体。
- 商业化连接：Paper Assistant 沉淀企业/领域知识，Second Agent 沉淀用户上下文和任务流程，组合后可以做面向研发、售前、培训和运营的企业知识工作流 Agent。

## 3. 当前代码结构

主要目录：

```text
paper_assistant/
├── main.py                         # 构建 LightRAG 索引和执行示例查询
├── app.py                          # Streamlit 论文问答界面
├── specialized_parser.py           # Docling PDF 语义解析器
├── visualize.py                    # GraphML 图谱转离线 HTML
├── eval_ragas.py                   # RAG 评估样例输出
├── experiment_embedding_quality.py # 清洗前后 Embedding 质量对比实验
├── pdfs/                           # 待处理论文
├── index_data/                     # LightRAG 索引、图谱和缓存数据
└── knowledge_graph_offline.html    # 离线知识图谱可视化结果
```

根目录关键文件：

```text
requirements.txt     # 服务器依赖
DEBUG_REPORT.md      # LightRAG 超时/死锁问题排查记录
README.md            # 项目概览
USAGE_GUIDE.md       # 脚本运行说明
```

建议新增或规划的扩展文件：

```text
docs/MCP_AND_SKILL_EXTENSION_PLAN.md # MCP/Skill 扩展设计与项目表达
paper_assistant/mcp_server.py        # 可选：将论文知识库暴露为 MCP Server
```

## 4. 服务器部署步骤

建议在服务器上使用 Python 3.11 或 3.12，优先 Python 3.11。

### 4.1 DSW 服务器现有环境

你当前服务器上已经有 Paper Assistant 的独立虚拟环境，可以直接复用：

```bash
cd /mnt/workspace/paper_assistant/paper_assistant/
source venv/bin/activate
```

如果仓库代码在该目录下的 `paper_assistant/` 子目录中，运行入口可以这样执行：

```bash
cd /mnt/workspace/paper_assistant/paper_assistant/
source venv/bin/activate
cd paper_assistant
python main.py
```

如果你重新拉取后的目录结构是仓库根目录直接包含 `paper_assistant/` 包目录，更推荐在仓库根目录运行：

```bash
cd /mnt/workspace/paper_assistant/paper_assistant/
source venv/bin/activate
python paper_assistant/health_check.py
python paper_assistant/main.py
```

关键原则：先激活 Paper Assistant 的 `venv`，再从仓库根目录执行 `python paper_assistant/...`，这样 `.env`、`pdfs/` 和 `index_data/` 路径最稳定。

### 4.2 通用新环境

```bash
cd /path/to/paper_assistant_backup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

复制配置模板并按服务器环境修改：

```bash
cp .env.example .env
```

常用配置项：

```text
OLLAMA_LLM_MODEL=qwen2.5:7b
OLLAMA_EMBED_MODEL=bge-m3:latest
PAPER_ASSISTANT_PDF_DIR=paper_assistant/pdfs
PAPER_ASSISTANT_WORKING_DIR=paper_assistant/index_data
LLM_MODEL_MAX_ASYNC=1
```

启动 Ollama 并准备模型：

```bash
ollama serve
ollama pull qwen2.5:7b
ollama pull bge-m3:latest
```

放入论文：

```bash
mkdir -p paper_assistant/pdfs
# 将 PDF 放入 paper_assistant/pdfs/
```

构建索引：

```bash
python paper_assistant/main.py
```

启动 Web 问答：

```bash
streamlit run paper_assistant/app.py
```

生成离线图谱：

```bash
python paper_assistant/visualize.py
```

生成评估样例：

```bash
python paper_assistant/eval_ragas.py
```

运行健康检查：

```bash
python paper_assistant/health_check.py
```

使用最小 MCP/工具入口：

```bash
python paper_assistant/mcp_server.py list_papers
python paper_assistant/mcp_server.py paper_search "CGRA vectorization" --top-k 3
python paper_assistant/mcp_server.py graph_neighbors CGRA --depth 1
```

如果服务器安装了 MCP SDK，`mcp_server.py` 会优先按 FastMCP 服务启动；未安装时会退化为 CLI 工具，方便先验证工具逻辑。

## 5. 本次修复点

这个项目之前容易“跑不通”的主要问题不是业务逻辑，而是入口和环境假设：

- `main.py` 使用包内相对导入，直接执行 `python paper_assistant/main.py` 时可能找不到 `specialized_parser`。
- `app.py`、`main.py`、`visualize.py` 使用相对当前工作目录的路径，服务器上从不同目录启动时会找不到 `index_data` 或 `pdfs`。
- `specialized_parser.py` 依赖 `docling` 和 `loguru`，但根目录 `requirements.txt` 里没有明确写入。
- 长论文处理时 LightRAG/本地 Ollama 容易触发异步超时或显存竞争，所以索引阶段需要保守设置 `llm_model_max_async=1`。

本次已做的代码修复：

- `paper_assistant/main.py`：使用 `Path(__file__).resolve().parent` 固定数据目录；增加相对导入失败后的普通导入兜底；恢复 `llm_model_max_async=1`。
- `paper_assistant/app.py`：Web 端使用脚本目录定位 `index_data` 和 `pdfs`。
- `paper_assistant/visualize.py`：图谱输入输出路径绑定到项目目录。
- `requirements.txt`：补充 `docling` 和 `loguru`。
- `paper_assistant/config.py`：集中管理模型、目录、chunk、embedding 维度和并发参数，支持 `.env` 覆盖。
- `paper_assistant/specialized_parser.py`：Docling 不可用或解析失败时自动降级到 PyMuPDF，减少服务器环境差异导致的空索引。
- `paper_assistant/health_check.py`：快速检查路径、依赖、Ollama 和模型状态。
- `paper_assistant/mcp_server.py`：提供 `list_papers`、`paper_search`、`paper_ask`、`graph_neighbors` 的最小工具入口，支持 CLI fallback。

## 6. 核心技术链路

完整链路：

```text
PDF 论文
  -> Docling 语义解析
  -> Markdown/文本清洗
  -> LightRAG chunking
  -> Ollama Embedding
  -> 向量索引 + 图谱关系抽取
  -> Hybrid/Global/Local Query
  -> Streamlit 问答 + PyVis 图谱可视化
  -> MCP Server 暴露 search/query/graph 工具
  -> RAG 评估和 Badcase 分析
```

关键设计点：

- 文档解析：Docling 比普通 PyMuPDF 更适合论文，因为它能保留标题层级、表格、公式和布局语义。
- 混合检索：向量检索适合找语义相似片段，图谱检索适合找实体关系和跨论文关联。
- 本地模型：Ollama + Qwen2.5 + BGE-M3 降低 API 依赖，适合私有论文库。
- 可视化：GraphML 转 HTML，便于展示论文概念之间的关系网络。
- MCP 工具化：把论文问答、论文检索、图谱关系查询暴露成标准工具，让 IDE Agent、桌面 Agent 或 Second Agent 调用。
- 评估闭环：通过 faithfulness、answer relevancy、context precision 解释 RAG 质量，而不是只展示 demo。

## 7. MCP 扩展设计

MCP 更适合加在 Paper Assistant，而不是 Second Agent。原因是 Paper Assistant 已经有稳定知识库和查询能力，把它包装成 MCP Server 后，外部 Agent 可以像调用工具一样访问论文知识，而不需要直接关心 LightRAG 的索引目录和模型细节。

建议暴露三个工具：

```text
paper_search(query, top_k)
  输入：自然语言检索问题
  输出：相关论文片段、来源文件、相似度或排序理由

paper_ask(question, mode)
  输入：论文相关问题，mode 可选 local/global/hybrid
  输出：GraphRAG 生成的答案和引用上下文

graph_neighbors(entity, depth)
  输入：论文实体或技术关键词
  输出：相关实体、关系类型、邻居节点
```

工具输入输出契约模板见：

```text
docs/mcp_tool_contracts/paper_assistant_mcp_tools.md
```

项目讲法：

> 我没有把论文库只做成一个 Streamlit demo，而是进一步抽象成 MCP 工具服务。这样上层 Agent、IDE 插件或自动调研工作流都可以复用同一个论文知识库，形成“知识服务 + Agent 调用”的架构。

工程落地价值：

- 让知识库从单一 Web 应用变成可被多个 Agent 复用的工具服务。
- 把 LightRAG 查询细节封装在服务端，降低上层 Agent 的集成成本。
- 更接近企业内部知识库场景，例如研发知识助手、论文调研助手、技术路线分析助手。

## 8. 项目讲法

可以按“问题、方案、难点、结果”讲：

问题：

> 普通 PDF RAG 对学术论文效果不稳定，尤其是公式、表格、断词和跨论文关系很难处理。

方案：

> 我用 Docling 做语义解析，将 PDF 转成更稳定的 Markdown，再用 LightRAG 同时构建向量索引和实体关系图谱。上层提供两种入口：Streamlit 用于人工交互，MCP Server 用于被其他 Agent 和自动化工作流调用。

难点：

> 本地长论文处理时遇到过 360 秒左右的阻塞和 GPU 利用率归零。我从 LightRAG 的异步调用、进程通信超时、Ollama 并发和显存竞争几个方向排查，最后通过降低并发、固定超时策略、稳定工作目录解决。

结果：

> 项目形成了从 PDF 解析、知识图谱构建、GraphRAG 查询、MCP 工具化暴露、可视化到评估的完整闭环，可以用于本地私有论文库问答、技术调研和 Agent 自动化阅读。

## 9. 项目 bullet 建议

- 构建本地化论文知识服务平台，集成 Docling、LightRAG、Ollama 和 BGE-M3，实现 PDF 语义解析、向量检索、知识图谱检索与论文问答。
- 将系统抽象为企业私有知识服务层，可迁移到研发知识库、售前知识支持、企业内训、行业研究和内部文档问答等场景，为上层 Agent 提供可信知识调用能力。
- 针对学术 PDF 中的表格、公式、断词和多级标题结构，设计解析清洗链路，将论文内容转为结构化 Markdown，提升 Embedding 检索质量。
- 设计 MCP Server 扩展方案，将论文检索、GraphRAG 问答和图谱邻居查询封装为可被外部 Agent 调用的标准工具。
- 基于 GraphML 和 PyVis 实现离线知识图谱可视化，支持论文实体、方法、架构和实验结论之间的关系展示。
- 设计 RAG 评估样例，使用 faithfulness、answer relevancy、context precision 等指标分析回答质量和检索质量。
- 排查 LightRAG 在本地长论文处理中的异步超时与显存竞争问题，通过限制 LLM 并发、固定数据路径和完善依赖配置提升服务器运行稳定性。

## 10. 服务器验证清单

正式运行时建议按顺序检查：

- `python --version` 为 3.11 或 3.12。
- `ollama list` 中存在 `qwen2.5:7b` 和 `bge-m3:latest`。
- `python -c "import docling, lightrag, streamlit"` 能正常导入。
- `paper_assistant/pdfs/` 中至少有一个 PDF。
- `python paper_assistant/main.py` 能生成或更新 `paper_assistant/index_data/`。
- `streamlit run paper_assistant/app.py` 能识别已有知识库。
- `python paper_assistant/visualize.py` 能生成 `knowledge_graph_offline.html`。
