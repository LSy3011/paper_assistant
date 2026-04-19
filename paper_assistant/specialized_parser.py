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
        try:
            if self.converter:
                logger.info(f"正在使用 Docling 解析: {file_path}")
                result = self.converter.convert(file_path)
                return self._clean_text(result.document.export_to_markdown())

            logger.warning(f"Docling 不可用，改用 PyMuPDF 兜底解析: {file_path}")
            return self._parse_with_pymupdf(file_path)
        except Exception as e:
            logger.error(f"Docling 解析失败，改用 PyMuPDF 兜底 {file_path}: {e}")
            return self._parse_with_pymupdf(file_path)

    def _parse_with_pymupdf(self, file_path: str) -> str:
        try:
            import fitz

            text_parts = []
            with fitz.open(file_path) as doc:
                for page in doc:
                    text_parts.append(page.get_text("text"))
            return self._clean_text("\n".join(text_parts))
        except Exception as e:
            logger.error(f"PyMuPDF 兜底解析失败 {file_path}: {e}")
            return ""

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

# 单例模式
specialized_parser = SpecializedParser()
