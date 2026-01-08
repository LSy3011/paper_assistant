import os
import re

# 目标目录：你 LightRAG 源码的真实位置
TARGET_DIR = "/mnt/workspace/LightRAG/lightrag"

def search_and_destroy():
    print(f"🚀 开始扫描目录: {TARGET_DIR} ...")
    modified_files = 0
    
    # 遍历所有 .py 文件
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue
                
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # --- 规则 1: 修改常量定义 ---
                # 查找 TIMEOUT_LLM_MODEL_WORKER = 360
                content = re.sub(
                    r'(TIMEOUT_LLM_MODEL_WORKER\s*=\s*)360', 
                    r'\g<1>3600', 
                    content
                )
                
                # 查找 TIMEOUT_LLM_MODEL_FUNC = 180
                content = re.sub(
                    r'(TIMEOUT_LLM_MODEL_FUNC\s*=\s*)180', 
                    r'\g<1>3600', 
                    content
                )

                # --- 规则 2: 修改函数参数默认值 ---
                # 查找 llm_timeout=180 (常见于 ollama.py 或 openai.py)
                content = re.sub(
                    r'(llm_timeout\s*=\s*)180', 
                    r'\g<1>3600', 
                    content
                )
                
                # 查找 max_execution_timeout=360
                content = re.sub(
                    r'(max_execution_timeout\s*=\s*)360', 
                    r'\g<1>3600', 
                    content
                )

                # --- 规则 3: 修改特定硬编码 (针对旧版本) ---
                # 有些版本直接写死在 decorator 里
                content = content.replace("max_execution_timeout=360", "max_execution_timeout=3600")

                # 如果内容发生了变化，写入文件
                if content != original_content:
                    print(f"🔧 正在修复: {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    modified_files += 1
                    
                    # 打印出改了哪里，让你放心
                    if "TIMEOUT" in content:
                        print("   -> 已将超时常量修改为 3600s")
                    if "llm_timeout" in content:
                        print("   -> 已将 llm_timeout 参数修改为 3600s")

            except Exception as e:
                print(f"⚠️ 无法读取 {file_path}: {e}")

    print("="*40)
    if modified_files > 0:
        print(f"🎉 成功修复了 {modified_files} 个文件！超时限制已解除。")
    else:
        print("🤔 没有发现需要修改的文件。可能已经修改过了，或者数字不是 360/180。")
        print("建议检查 lightrag/constants.py 文件。")

if __name__ == "__main__":
    search_and_destroy()
