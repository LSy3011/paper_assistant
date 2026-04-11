import os
import asyncio
import fitz
import numpy as np
import ollama
import re
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc

# 1. 基础配置
WORKING_DIR = "./index_data"
PDF_DIR = "./pdfs"
CORPUS_DIR = "./corpus"
# 自动创建 corpus 目录以防报错
if not os.path.exists(CORPUS_DIR):
    os.makedirs(CORPUS_DIR)
    print(f"✅ 已为您自动创建论文存放目录: {CORPUS_DIR}")

LLM_MODEL_NAME = "qwen2.5:7b"
EMBEDDING_MODEL_NAME = "bge-m3:latest"
OLLAMA_CTX = 32000

from specialized_parser import specialized_parser

# 2. 增强型 PDF 解析函数 (NLP 简历亮点：语义化与 Markdown 转换)
def parse_pdf_structured(file_path):
    """
    调用高性能 Docling 引擎进行语义化解析，
    自动处理表格、公式，并集成后置清洗逻辑。
    """
    return specialized_parser.parse(file_path)

# 3. 推理函数 (增加 Rerank 逻辑说明)
async def ollama_llm_func(prompt, system_prompt=None, history_messages=None, **kwargs):
    # 此处可以预留给 Reranker，如果检索出的 context 太多，先在这里做一次 Cross-Encoder 评分
    messages = []
    if system_prompt: messages.append({"role": "system", "content": system_prompt})
    if history_messages: messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    try:
        response = await asyncio.to_thread(
            ollama.chat,
            model=LLM_MODEL_NAME,
            messages=messages,
            options={"num_ctx": OLLAMA_CTX, "temperature": 0.1}
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"⚠️ LLM 调用失败: {e}")
        return ""

async def ollama_embedding_func(texts):
    if isinstance(texts, str): texts = [texts]
    embeddings = []
    for text in texts:
        try:
            response = await asyncio.to_thread(
                ollama.embeddings, model=EMBEDDING_MODEL_NAME, prompt=text
            )
            embeddings.append(response["embedding"])
        except:
            embeddings.append([0.0] * 1024)
    return np.array(embeddings)

# 4. 主流程
async def main():
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(WORKING_DIR, exist_ok=True)

    print("🔧 启动 LightRAG (优化版)...")
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=ollama_llm_func,
        embedding_func=EmbeddingFunc(
            func=ollama_embedding_func,
            embedding_dim=1024,
            max_token_size=8192,
        ),
        # NLP 优化建议：学术论文分块不宜过小，1024 Token 能保留更多语义上下文
        chunk_token_size=1024, 
        chunk_overlap_token_size=128,
        # 提高实体的提取覆盖率，默认是 100，这里可以微调
        # entity_extract_max_gleaning=1 
    )

    files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    
    for f in files:
        print(f"\n📄 结构化处理并注入: {f}")
        content = parse_pdf_structured(os.path.join(PDF_DIR, f))
        if content:
            await rag.ainsert(content)
            print(f"✅ 完成")

    # 5. 带有思考链的查询示例
    query = "请分析这些论文对于 CGRA 编译效率的改进方法，并给出推理理由。"
    print(f"\n❓ 复杂查询: {query}")
    # 使用混合检索 (Vector + Graph) 以获得最佳效果
    result = await rag.aquery(query, param=QueryParam(mode="hybrid"))
    print(f"\n✨ 生成回答:\n{result}")

if __name__ == "__main__":
    asyncio.run(main())