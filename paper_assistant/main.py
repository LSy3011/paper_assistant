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
    
    if not files:
        print(f"⚠️ 在 {PDF_DIR} 目录下没有找到 PDF 文件。请确认你的论文存放在该位置。")
    
    for f in files:
        print(f"\n📄 处理中: {f}")
        content = parse_pdf_structured(os.path.join(PDF_DIR, f))
        if content and len(content.strip()) > 50: # 过滤掉解析太短的内容
            await rag.ainsert(content)
            print(f"✅ 内容已注入知识图谱")
        else:
            print(f"⚠️ 解析内容过短或为空，跳过注入。")

    # 5. 带有思考链的查询示例
    query = "请分析这些论文对于 CGRA 编译效率的改进方法，并给出推理理由。"
    print(f"\n❓ 综合查询: {query}")
    
    try:
        # 增加防御性：如果知识图谱完全为空，aquery 可能会触发内部错误
        # 使用 hybrid 模式获得最佳效果
        result = await rag.aquery(query, param=QueryParam(mode="hybrid"))
        
        if not result or result == "I am sorry, but I don't have the message history yet":
            print("\n✨ 回答: 抱歉，当前知识库中没有足够的背景信息来回答该问题。请确保 PDF 已成功解析并注入。")
        else:
            print(f"\n✨ 生成回答:\n{result}")
            
    except Exception as e:
        print(f"\n❌ 查询失败: {e}")
        print("💡 提示: 这通常是因为知识库中没有有效数据，或者 LLM 返回了不符合预期的响应。")

if __name__ == "__main__":
    asyncio.run(main())