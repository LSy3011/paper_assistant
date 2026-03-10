# -*- coding: utf-8 -*-
import numpy as np
import ollama
import re
import json

# ================= 1. 模拟实验数据源 =================
# 模拟从某篇论文中提取出的真实带噪声文本 vs 清洗后的文本
test_cases = [
    {
        "query": "What is the purpose of MLIR in compiler design?",
        "raw": "The multi-level intermediate rep-\nresentation (MLIR) is a frame-\nwork for build-ing domain-specific com-\npilers. [Page 12]",
        "cleaned": "The multi-level intermediate representation (MLIR) is a framework for building domain-specific compilers."
    },
    {
        "query": "How does VecPAC handle precision-aware vectorization?",
        "raw": "VecPAC architecture supports precision-\naware vectorization by intro-ducing custom ISA.\n99 | IEEE Conference",
        "cleaned": "VecPAC architecture supports precision-aware vectorization by introducing custom ISA."
    },
    {
        "query": "What are the optimization goals for SODA-OPT?",
        "raw": "SODA-OPT aims to minimize energy con-\nsumption while maintain-ing high through-\nput in CGRA systems.",
        "cleaned": "SODA-OPT aims to minimize energy consumption while maintaining high throughput in CGRA systems."
    }
]

def get_embedding(text, model="bge-m3:latest"):
    """调用 Ollama 获取向量"""
    try:
        response = ollama.embeddings(model=model, prompt=text)
        return np.array(response["embedding"])
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def cosine_similarity(v1, v2):
    """计算余弦相似度"""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def run_experiment():
    print("🧪 启动 Embedding 质量对比实验...")
    print("模型: bge-m3:latest | 场景: 学术论文断词修复\n")
    
    results = []
    
    for i, case in enumerate(test_cases):
        print(f"--- Case {i+1} ---")
        q_emb = get_embedding(case["query"])
        r_emb = get_embedding(case["raw"])
        c_emb = get_embedding(case["cleaned"])
        
        if q_emb is None or r_emb is None or c_emb is None:
            continue
            
        sim_raw = cosine_similarity(q_emb, r_emb)
        sim_clean = cosine_similarity(q_emb, c_emb)
        gain = (sim_clean - sim_raw) / sim_raw * 100
        
        results.append({
            "case": i + 1,
            "sim_raw": float(sim_raw),
            "sim_clean": float(sim_clean),
            "gain_percent": float(gain)
        })
        
        print(f"Query: {case['query']}")
        print(f"相似度 (Raw):   {sim_raw:.4f}")
        print(f"相似度 (Cleaned): {sim_clean:.4f}")
        print(f"提升幅度: {gain:+.2f}%\n")

    # 保存实验结论
    avg_gain = sum([r["gain_percent"] for r in results]) / len(results)
    final_report = {
        "detail": results,
        "average_gain_percent": avg_gain,
        "conclusion": f"通过结构化解析，Embedding 语义匹配质量平均提升了 {avg_gain:.2f}%"
    }
    
    with open("embedding_experiment_results.json", "w") as f:
        json.dump(final_report, f, indent=4)
        
    print(f"✅ 实验完成！平均提升效率: {avg_gain:.2f}%")
    print("数据结论已保存至 embedding_experiment_results.json")

if __name__ == "__main__":
    run_experiment()
