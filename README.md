# Paper Assistant (基于知识图谱的论文问答助手)

## 项目简介

**Paper Assistant** 是一个本地化的知识库问答系统，专为学术论文（特别是 CGRA、编译器设计、机器学习加速等领域）设计。它不仅仅是一个简单的文档检索工具，而是通过构建 **知识图谱 (Knowledge Graph)** 来理解论文中的实体（Entities）及其关系（Relations），提供更深度的上下文理解和可视化展示。

该项目基于 LightRAG（推测）架构，支持从非结构化 PDF 文本到结构化图谱的自动构建、本地化存储以及交互式可视化。

## 核心功能

* **PDF 论文解析与索引**：自动处理 `pdfs/` 目录下的学术论文，提取文本内容。
* **知识图谱构建**：利用 LLM 提取论文中的关键概念（如技术术语、架构名称）及其相互关系，构建本地知识图谱。
* **混合检索 (Hybrid RAG)**：结合向量检索（Vector Search）和图谱检索（Graph Search）来回答用户问题。
* **交互式可视化**：生成 HTML 格式的知识图谱可视化文件，支持离线查看（利用本地 `lib/` 资源）。
* **本地化部署**：支持完全离线运行（依赖本地 LLM 和 Embedding 模型）。

## 文件结构说明

项目根目录结构如下：

```text
paper_assistant/
├── app.py                  # [Web 应用入口] 可能是一个基于 Streamlit 的交互式前端，用于对话和展示
├── main.py                 # [核心逻辑] 主程序入口，通常用于执行索引构建、数据处理管线
├── visualize.py            # [可视化脚本] 用于读取索引数据并生成 knowledge_graph.html
├── final_fix.py            # [工具脚本] 可能用于修复某些特定的数据格式或索引问题
│
├── pdfs/                   # [数据源] 存放待处理的 PDF 论文
│   ├── AnMLIR-based Compiler Flow for System-Level Design and.pdf
│   ├── DRIPS_Dynamic_Rebalancing_of_Pipelined_Streaming_Applications_on_CGRAs.pdf
│   ├── ML-CGRA_An_Integrated_Compilation_Framework_to_Enable_Efficient_Machine_Learning_Acceleration_on_CGRAs.pdf
│   └── VecPAC_A_Vectorizable_and_Precision-Aware_CGRA.pdf
│
├── index_data/             # [持久化存储] 存放构建好的索引、向量库和图谱数据
│   ├── graph_chunk_entity_relation.graphml  # GraphML 格式的图谱数据，可导入 Gephi 等工具
│   ├── kv_store_*.json                      # Key-Value 存储 (文档、实体、关系、文本块)
│   ├── vdb_*.json                           # 向量数据库文件 (Chunks, Entities, Relationships)
│   └── processed_*.txt                      # 解析后的纯文本缓存
│
├── lib/                    # [前端依赖] 包含 vis.js 等库，支持离线渲染图谱
│   ├── vis-9.1.2/          # 网络可视化库
│   ├── tom-select/         # 下拉选择组件
│   └── bindings/           # 数据绑定工具
│
├── knowledge_graph.html         # [输出] 生成的知识图谱可视化页面
└── knowledge_graph_offline.html # [输出] 离线版可视化页面 (直接引用 lib/ 下的资源)
```

## 快速开始

### 1. 环境准备

确保已安装 Python 及项目所需的依赖库（如 `lightrag`, `networkx`, `streamlit` 等，具体参考 `requirements.txt`，如果未提供则需根据 import 报错安装）。

### 2. 数据准备

将需要分析的 PDF 论文放入 `pdfs/` 文件夹中。目前示例中包含关于 CGRA 和编译器流的论文。

### 3. 构建索引

运行主程序以处理 PDF 并构建知识图谱索引：

```bash
python main.py

```

*此步骤会读取 `pdfs/` 中的文件，调用 LLM 进行提取，并将结果保存到 `index_data/` 目录中。*

### 4. 生成可视化

构建完成后，运行可视化脚本生成 HTML 文件：

```bash
python visualize.py

```

运行后将生成 `knowledge_graph.html` 和 `knowledge_graph_offline.html`。

### 5. 启动应用

如需使用对话问答功能，启动 Web 界面（假设是 Streamlit）：

```bash
streamlit run app.py

```

或者直接运行 Python 脚本（视具体实现而定）：

```bash
python app.py

```

## 数据说明

`index_data/` 目录包含了系统的“大脑”：

* **kv_store_full_docs.json**: 原始文档的元数据。
* **kv_store_full_entities.json**: 提取出的所有实体（如 "CGRA", "LLVM", "Data Flow"）。
* **kv_store_full_relations.json**: 实体之间的关系（如 "CGRA" --[uses]--> "Compiler"）。
* **vdb_*.json**: 用于向量检索的 Embedding 数据，支持语义搜索。

## 注意事项

* `knowledge_graph_offline.html` 是完全本地化的，不依赖 CDN，适合在无外网环境演示。
* 如果遇到索引错误或需要清理缓存，请检查 `final_fix.py` 中的逻辑。请将这个部分的内容写成.md的格式
