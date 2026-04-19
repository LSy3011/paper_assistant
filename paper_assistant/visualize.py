import networkx as nx
from pyvis.network import Network
import os
import json
from pathlib import Path

# ===========================
# 配置路径
# ===========================
BASE_DIR = Path(__file__).resolve().parent
GRAPH_FILE = BASE_DIR / "index_data" / "graph_chunk_entity_relation.graphml"
OUTPUT_FILE = BASE_DIR / "knowledge_graph_offline.html"

def main():
    # 1. 检查文件是否存在
    if not os.path.exists(GRAPH_FILE):
        print(f"❌ 错误：找不到图文件: {GRAPH_FILE}")
        print("💡 请先运行 main.py 生成数据")
        return

    print(f"🚀 正在加载图谱数据: {GRAPH_FILE} ...")
    # NetworkX 读取 GraphML
    G = nx.read_graphml(GRAPH_FILE)
    print(f"📊 图谱统计: 节点数 {len(G.nodes())}, 边数 {len(G.edges())}")

    # 2. 创建 PyVis 网络对象
    # cdn_resources="in_line" 是核心：它把所有 JS 库直接写进 HTML，不再依赖网络
    net = Network(
        height="100vh",              # 全屏高度
        width="100%", 
        bgcolor="#1a1a1a",           # 深灰色背景，护眼
        font_color="#ffffff",        # 白色字体
        select_menu=True,            # 开启节点搜索下拉框
        filter_menu=False,           # 过滤器（节点多时建议关掉，否则卡顿）
        cdn_resources="in_line"      # 【关键】完全离线模式
    )

    # 3. 将 NetworkX 数据转入 PyVis
    net.from_nx(G)

    # 4. 高级性能优化配置 (通过 JSON 配置物理引擎)
    # 针对 1000+ 节点的大图进行特殊优化
    options = {
        "nodes": {
            "shape": "dot",
            "size": 10,
            "font": {
                "size": 12,
                "face": "Tahoma"
            },
            "borderWidth": 0.5
        },
        "edges": {
            "width": 0.5,
            "color": {
                "inherit": True,
                "opacity": 0.5
            },
            "smooth": False  # 【关键】关闭曲线平滑，改用直线。这对性能提升巨大！
        },
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 100,
                "springStrength": 0.08,
                "damping": 0.4,
                "avoidOverlap": 0
            },
            "maxVelocity": 50,
            "minVelocity": 0.1,
            "solver": "forceAtlas2Based", # 适合大图的算法
            "stabilization": {
                "enabled": True,
                "iterations": 1000,       # 打开前先在后台计算 1000 次布局
                "updateInterval": 25,
                "onlyDynamicEdges": False,
                "fit": True
            }
        },
        "interaction": {
            "hover": True,
            "navigationButtons": True,
            "keyboard": True
        }
    }
    
    # 应用配置
    net.set_options(json.dumps(options))

    # 5. 保存并生成
    print(f"💾 正在生成离线 HTML 文件: {OUTPUT_FILE} ...")
    try:
        net.save_graph(str(OUTPUT_FILE))
        print(f"\n✅ 成功！文件已生成: {os.path.abspath(OUTPUT_FILE)}")
        print("👉 请在左侧文件浏览器中，右键点击 'knowledge_graph_offline.html' -> 下载 (Download)")
        print("👉 然后在本地浏览器双击打开，即可秒开且无需联网。")
    except Exception as e:
        print(f"❌ 保存失败: {e}")

if __name__ == "__main__":
    main()
