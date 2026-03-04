# 项目运行与数据分析指南 (Paper Assistant)

## 1. 快速运行脚本清单

| 脚本名称 | 功能说明 | 运行命令 | 生成数据 |
| :--- | :--- | :--- | :--- |
| `main.py` | 全量论文索引构建 | `python main.py` | `index_data/` (GraphML & JSON) |
| `eval_ragas.py` | **核心量化评估** | `python eval_ragas.py` | `paper_assistant_eval.json` |
| `visualize.py` | 图谱 HTML 可视化 | `python visualize.py` | `knowledge_graph.html` |

## 2. 数据产出与分析步骤

### 步骤 A：生成评估数据
运行 `eval_ragas.py` 后，你会得到 `paper_assistant_eval.json`。这个文件记录了：
- **Faithfulness**: LLM 有没有在那瞎编？（1.0 为完美，低于 0.6 需要检查 Prompt）
- **Context Precision**: 检索到的 PDF 片段是否精准？（如果不精准，需减小 Chunk Size）

### 步骤 B：上传数据
请将 `paper_assistant_eval.json` 提交到 GitHub。这样在后续对话中，我可以读取该文件并为你提供具体的参数优化建议。

## 3. 常见问题
- **导入报错**：确保已安装 `lightrag-hku` 而不是 `lightrag`。
- **内存死锁**：如果脚本僵死，请检查 `DEBUG_REPORT.md` 中的超时调整建议。
