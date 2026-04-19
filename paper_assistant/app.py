import streamlit as st
import asyncio
import os
import logging
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
import ollama
import numpy as np

try:
    from lightrag.kg.shared_storage import initialize_pipeline_status
except Exception:
    initialize_pipeline_status = None

try:
    from .config import (
        CHUNK_TOKEN_SIZE,
        EMBEDDING_DIM,
        EMBEDDING_MODEL_NAME,
        LLM_MODEL_MAX_ASYNC,
        LLM_MODEL_NAME,
        MAX_TOKEN_SIZE,
        OLLAMA_CTX,
        PDF_DIR,
        WORKING_DIR,
    )
except ImportError:
    from config import (
        CHUNK_TOKEN_SIZE,
        EMBEDDING_DIM,
        EMBEDDING_MODEL_NAME,
        LLM_MODEL_MAX_ASYNC,
        LLM_MODEL_NAME,
        MAX_TOKEN_SIZE,
        OLLAMA_CTX,
        PDF_DIR,
        WORKING_DIR,
    )

# 设置日志级别，减少干扰
logging.basicConfig(level=logging.INFO)

# --- 页面配置 ---
st.set_page_config(
    page_title="Paper Chat", 
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 侧边栏状态 ---
with st.sidebar:
    st.title("🎓 知识库控制台")
    
    # 检查数据目录
    if os.path.exists(WORKING_DIR) and len(os.listdir(WORKING_DIR)) > 0:
        st.success(f"✅ 知识库数据就绪")
        
        # 显示已索引文件
        if os.path.exists(PDF_DIR):
            files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
            with st.expander(f"📚 已索引论文 ({len(files)})", expanded=True):
                for f in files:
                    st.caption(f"📄 {f}")
    else:
        st.error("❌ 未检测到数据！请先运行 main.py 构建知识库")
        st.stop()

    st.markdown("---")
    st.info("💡 提示：'Global' 模式适合做总结，'Local' 模式适合问细节。")

# --- 核心逻辑 ---
st.title("Paper Chat (Graph RAG)")
st.caption("🚀 基于 LightRAG：不仅仅是搜索，更是深度理解")

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- RAG 初始化函数 (核心修复版) ---
@st.cache_resource
def get_rag_engine():
    # 定义 Ollama 适配器
    async def llm_func(prompt, system_prompt=None, history_messages=None, **kwargs):
        messages = []
        if system_prompt: messages.append({"role": "system", "content": system_prompt})
        if history_messages: messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await asyncio.to_thread(
                ollama.chat, 
                model=LLM_MODEL_NAME,
                messages=messages, 
                options={"num_ctx": OLLAMA_CTX, "temperature": 0.3}
            )
            return response["message"]["content"]
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Error generating response."

    async def embed_func(texts):
        if isinstance(texts, str): texts = [texts]
        embeddings = []
        for text in texts:
            try:
                res = await asyncio.to_thread(ollama.embeddings, model=EMBEDDING_MODEL_NAME, prompt=text)
                embeddings.append(res["embedding"])
            except Exception as e:
                print(f"Embedding Error: {e}")
                embeddings.append([0.0] * EMBEDDING_DIM)
        return np.array(embeddings)

    # 创建实例
    rag = LightRAG(
        working_dir=str(WORKING_DIR),
        llm_model_func=llm_func,
        embedding_func=EmbeddingFunc(func=embed_func, embedding_dim=EMBEDDING_DIM, max_token_size=MAX_TOKEN_SIZE),
        llm_model_max_async=LLM_MODEL_MAX_ASYNC,
        chunk_token_size=CHUNK_TOKEN_SIZE
    )

    # 【关键修复】手动创建循环来初始化存储
    # Streamlit 的缓存函数是同步运行的，必须在这里显式运行 async 初始化
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("⚙️ 正在加载知识库数据 (Initialize Storages)...")
        loop.run_until_complete(rag.initialize_storages())
        if initialize_pipeline_status is not None:
            loop.run_until_complete(initialize_pipeline_status())
        print("✅ 知识库加载完成！")
        loop.close()
    except Exception as e:
        st.error(f"知识库加载失败: {e}")
    
    return rag

# --- 处理用户输入 ---
if prompt := st.chat_input("向你的论文知识库提问..."):
    # 1. 显示用户问题
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. 生成回答
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("🧠 _正在调动图谱神经元进行思考..._")
        
        try:
            # 获取引擎
            rag = get_rag_engine()
            
            # 使用 asyncio.run 运行查询
            # 注意：Streamlit 内部可能已有 Loop，这里使用 safe_run 策略
            async def run_query():
                return await rag.aquery(prompt, param=QueryParam(mode="global"))
            
            # 简单的运行方式
            response = asyncio.run(run_query())
            
            if not response or response == "None":
                response = "⚠️ 模型似乎没有找到相关信息，或者生成了空内容。请尝试换个问法。"

            placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            placeholder.error(f"🚫 系统错误: {str(e)}")
