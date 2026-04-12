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
        尝试使用 Docling，失败或不可用时降级到 PyMuPDF (fitz)
        """
        # 1. 尝试使用 Docling
        if self.converter:
            try:
                logger.info(f"正在使用 Docling 解析: {file_path}")
                result = self.converter.convert(file_path)
                markdown_text = result.document.export_to_markdown()
                
                # 增强清洗逻辑
                markdown_text = self._clean_text(markdown_text)
                return markdown_text
            except Exception as e:
                logger.error(f"Docling 解析过程中出错，准备切换备选引擎: {e}")

        # 2. 兜底法：使用 PyMuPDF (fitz)
        return self.parse_with_fitz(file_path)

    def parse_with_fitz(self, file_path: str) -> str:
        """
        备选解析引擎：基于 PyMuPDF 提取纯文本
        优点：无需模型，离线稳健
        """
        try:
            import fitz
            logger.info(f"🚀 正在使用 PyMuPDF (fitz) 备选引擎解析: {file_path}")
            doc = fitz.open(file_path)
            full_text = ""
            for i, page in enumerate(doc):
                # 提取带布局的文本
                text = page.get_text("text")
                full_text += f"\n\n### Page {i+1}\n\n" + text
            
            doc.close()
            return self._clean_text(full_text)
        except Exception as e:
            logger.error(f"PyMuPDF 解析也失败了: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        """集中处理文本清洗逻辑"""
        import re
        # A. 修复断词 (如 continuous-\nly -> continuously)
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        # B. 修复带空格的断词
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        # C. 移除 3 个及以上的连续换行
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

# 单例模式
specialized_parser = SpecializedParser()
