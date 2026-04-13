import os
import shutil

def wipe_pycache(target_dir="."):
    """
    递归删除目标目录下的所有 __pycache__ 文件夹
    """
    print(f"🧹 正在清理目录下的 Python 字节码缓存: {os.path.abspath(target_dir)}")
    count = 0
    for root, dirs, files in os.walk(target_dir):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_path)
                print(f"✅ 已删除: {pycache_path}")
                count += 1
            except Exception as e:
                print(f"⚠️ 无法删除 {pycache_path}: {e}")
    
    print("-" * 30)
    if count > 0:
        print(f"🎉 清理完成！共删除了 {count} 个缓存目录。")
    else:
        print("✨ 未发现 __pycache__ 目录，环境很整洁。")

if __name__ == "__main__":
    # 清理当前目录（项目目录）
    wipe_pycache()
    
    # 尝试清理库目录（由于库可能在 site-packages，需要通过 import 找）
    try:
        import lightrag
        lib_dir = os.path.dirname(lightrag.__file__)
        wipe_pycache(lib_dir)
    except:
        pass
