import subprocess
import os
import sys

def run_command(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
    else:
        print(f"✅ Success: {result.stdout.strip()}")

def main():
    print("🚀 开始为服务器环境进行【cdfdcca 版本】还原配置...")
    
    # 1. 安装核心依赖
    # 注意：cdfdcca 版本底层默认使用 PyMuPDF (fitz)
    run_command("pip install lightrag-hku pymupdf streamlit pyvis loguru")
    
    # 2. 运行物理补丁脚本
    if os.path.exists("paper_assistant/final_fix.py"):
        run_command(f"{sys.executable} paper_assistant/final_fix.py")
    
    # 3. 清理全量缓存
    if os.path.exists("paper_assistant/wipe_cache.py"):
        run_command(f"{sys.executable} paper_assistant/wipe_cache.py")
    
    print("\n" + "="*50)
    print("🎉 cdfdcca 版本还原完成！")
    print("👉 运行 main.py 开始构建知识图谱: python paper_assistant/main.py")
    print("👉 运行 app.py 启动 Streamlit 界面: streamlit run paper_assistant/app.py")
    print("="*50)

if __name__ == "__main__":
    main()
