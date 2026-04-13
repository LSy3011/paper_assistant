import re
from loguru import logger

class SpecializedParser:
    """
    语义级 PDF 解析器
    底层依赖: docling (由 IBM 开源，擅长表格与公式提取)
    """
    def __init__(self):
        self.converter = None
        try:
            from docling.document_converter import DocumentConverter
            self.converter = DocumentConverter()
            logger.info("✅ Docling 解析引擎加载成功")
        except ImportError:
            logger.warning("⚠️ 未检测到 docling 库，请在服务器上运行: pip install docling")

    def parse(self, file_path: str) -> str:
        """
        解析 PDF 并转换为增强型 Markdown
        """
        if not self.converter:
            return ""

        try:
            logger.info(f"正在使用 Docling 解析: {file_path}")
            # 1. 语义化转换
            result = self.converter.convert(file_path)
            markdown_text = result.document.export_to_markdown()

            # 2. 继承并增强原有的清洗逻辑
            # A. 修复断词 (如 continuous-\nly -> continuously)
            markdown_text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', markdown_text)
            # B. 修复带空格的断词
            markdown_text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', markdown_text)
            # C. 移除 3 个及以上的连续换行，保持布局整洁
            markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
            
            # D. (可选) 针对 LaTeX 特殊处理
            # Docling 默认输出标准的 Markdown 表格和 LaTeX 公式
            
            return markdown_text
        except Exception as e:
            logger.error(f"Docling 解析失败 {file_path}: {e}")
            return ""

# 单例模式
specialized_parser = SpecializedParser()
