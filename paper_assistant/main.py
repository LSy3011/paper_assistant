import os
import asyncio
import fitz
import numpy as np
import ollama
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

# 1. 基础配置
WORKING_DIR = "./index_data"
PDF_DIR = "./pdfs"
LLM_MODEL_NAME = "qwen2.5:7b"
EMBEDDING_MODEL_NAME = "bge-m3:latest"
OLLAMA_CTX = 32000

# 2. Ollama 函数
async def ollama_llm_func(prompt, system_prompt=None, history_messages=None, **kwargs):
    messages = []
    if system_prompt: messages.append({"role": "system", "content": system_prompt})
    if history_messages: messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    try:
        # 应用层超时设为 500s (比底层 600s 略短，以便先捕获)
        response = await asyncio.wait_for(
            asyncio.to_thread(
                ollama.chat,
                model=LLM_MODEL_NAME,
                messages=messages,
                options={
                    "num_ctx": OLLAMA_CTX, 
                    "temperature": 0.1, # 低温度减少死循环概率
                    "num_predict": 2048 # 强制限制最大生成长度，防止无限输出
                }
            ),
            timeout=500.0 
        )
        return response["message"]["content"]
    except asyncio.TimeoutError:
        print(f"⚠️  LLM 任务超过 500s，可能陷入死循环，跳过此块。")
        return ""
    except Exception as e:
        print(f"⚠️  LLM 调用失败: {e}")
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

def parse_pdf(file_path):
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc: text += page.get_text()
        return text
    except: return None

# 3. 主流程
async def main():
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(WORKING_DIR, exist_ok=True)

    print("🔧 启动 LightRAG (超时: 600s, 模式: 单线程稳定版)...")
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=ollama_llm_func,
        embedding_func=EmbeddingFunc(
            func=ollama_embedding_func,
            embedding_dim=1024,
            max_token_size=8192,
        ),
        # 核心：单并发 + 1024块大小
        # 这是本地单卡运行的最优解
        llm_model_max_async=1, 
        chunk_token_size=1024, 
        chunk_overlap_token_size=100,
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    print(f"📚 发现 {len(files)} 篇论文")

    for f in files:
        print(f"\n📄 处理: {f}")
        content = parse_pdf(os.path.join(PDF_DIR, f))
        if content:
            print(f"🚀 注入中 (长度: {len(content)})...")
            try:
                await rag.ainsert(content)
                print(f"✅ 完成")
            except Exception as e:
                print(f"❌ 失败: {e}")

    print("\n" + "="*30)
    query = "请总结这些论文中提出的核心算法创新点。"
    print(f"❓ 提问: {query}")
    try:
        print(await rag.aquery(query, param=QueryParam(mode="global")))
    except Exception as e:
        print(f"查询出错: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass