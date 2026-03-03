# Paper Assistant (基于知识图谱的论文问答助手)

## 项目简介

**Paper Assistant** 是一个本地化的知识库问答系统，专为学术论文设计。它不仅仅是一个简单的文档检索工具，而是通过构建 **知识图谱 (Knowledge Graph)** 来理解论文中的实体（Entities）及其关系（Relations），提供更深度的上下文理解和可视化展示。

该项目基于 LightRAG 架构，支持从非结构化 PDF 文本到结构化图谱的自动构建、本地化存储以及交互式可视化。

## 核心功能

* **PDF 论文解析与索引**：自动处理 `pdfs/` 目录下的学术论文，提取文本内容。
* **知识图谱构建**：利用 LLM 提取论文中的关键概念（如技术术语、架构名称）及其相互关系，构建本地知识图谱。
* **混合检索 (Hybrid RAG)**：结合向量检索（Vector Search）和图谱检索（Graph Search）来回答用户问题。
* **量化评估 (Advanced)**：引入 Ragas 评估指标，从 Faithfulness 和 Context Precision 角度对 RAG 效果进行科学量化。
* **交互式可视化**：生成 HTML 格式的知识图谱可视化文件，支持离线查看。
* **本地化部署**：支持完全离线运行（依赖本地 LLM 和 Embedding 模型）。

## 文件结构说明

项目主要文件如下：

```text
paper_assistant/
├── app.py                  # [Web 应用入口] 基于 Streamlit 的交互式前端
├── main.py                 # [核心逻辑] 主程序入口，执行索引构建
├── eval_ragas.py           # [量化评估] 针对召回精度和回答质量的评估脚本
├── DEBUG_REPORT.md         # [故障报告] 针对 360s 超时死锁的深度溯源分析报告
├── visualize.py            # [可视化脚本] 用于读取索引数据并生成可视化 HTML
├── pdfs/                   # [数据源] 存放待处理的 PDF 论文
├── index_data/             # [持久化存储] 存放构建好的索引、向量库和图谱数据
```

## 快速开始

### 1. 环境准备
确保已安装 Python 及 `lightrag`, `ragas`, `streamlit` 等依赖。

### 2. 构建与运行
1. 将 PDF 放入 `pdfs/`。
2. 运行 `python main.py` 构建索引。
3. 运行 `python eval_ragas.py` 进行效果评估。
4. 启动应用：`streamlit run app.py`。

## 注意事项

* 如果遇到系统挂起或超时问题，请务必阅读 `DEBUG_REPORT.md`。
* 评估模块 `eval_ragas.py` 需要安装 `ragas` 库。
