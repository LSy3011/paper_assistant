# 🎓 Paper Assistant: 语义化论文解析与知识治理系统

本项目是一款专为学术论文设计的 Agentic RAG 前置解析系统。它摒弃了传统的正则匹配，引入了 **Docling** 语义解析引擎，能够精准提取论文中的 LaTeX 公式、Markdown 表格及复杂的文档布局。

---

## 🚀 快速启动 (服务器/DSW 环境)

### 1. 环境准备
确保您已进入虚拟环境（如 `neo4j_agent_env`），并安装核心解析依赖：

```bash
# 进入项目目录
cd /mnt/workspace/neo4j_agent_env/paper_assistant

# 安装语义解析引擎 (Docling 需要一定时间下载模型)
pip install docling langchain-core langchain-community neo4j
```

### 2. 配置服务
- **Neo4j**: 确保端口 `7687` 已开启且 APOC 插件已安装。
- **Ollama**: 确保后台已启动并加载了 `qwen2.5:7b` 或类似模型。

### 3. 执行解析
将您的 PDF 论文放入 `corpus/` 文件夹下，然后运行：

```bash
python main.py
```

---

## ✨ 核心技术亮点 (简历必写)

1. **语义级文档拆解 (Semantic Chunking)**:
   - 集成 **Docling** 引擎，实现对 PDF 布局的深度感知，自动识别标题层级、表格及公式。
   - 解决了传统 PDF 解析中“表格乱码”和“行间公式断裂”的痛点。

2. **多模态数据清洗**:
   - 自动将论文中的 LaTeX 公式标准化，确保 RAG 检索时公式语义不丢失 ($E=mc^2$)。

3. **知识图谱无缝对接**:
   - 解析结果直接转化为 Markdown 格式并对接 Neo4j 图谱节点，构建具备学术语义关联的知识网络。

---

## 📂 项目结构
- `main.py`: 主程序入口，协调解析流。
- `specialized_parser.py`: 基于 Docling 的核心解析逻辑。
- `corpus/`: 存放待处理的 PDF 论文。
- `requirements.txt`: 依赖清单。

---
*注：本项目已适配 Python 3.11+ 生产环境。*
