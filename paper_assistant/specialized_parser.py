import re

from loguru import logger

try:
    from .config import PARSER_BACKEND, PARSER_ENABLE_OCR
except ImportError:
    from config import PARSER_BACKEND, PARSER_ENABLE_OCR


class SpecializedParser:
    """PDF parser with a fast default path and an optional high-fidelity Docling path."""

    def __init__(self, backend=PARSER_BACKEND):
        self.backend = backend if backend in {"pymupdf", "docling", "auto"} else "pymupdf"
        self.converter = None

        if self.backend in {"docling", "auto"}:
            self.converter = self._build_docling_converter()

        logger.info(
            "PDF parser backend: {}{}",
            self.backend,
            " (OCR enabled)" if PARSER_ENABLE_OCR else "",
        )

    def _build_docling_converter(self):
        try:
            if not PARSER_ENABLE_OCR:
                return self._build_docling_without_ocr()

            from docling.document_converter import DocumentConverter

            logger.info("Docling parser loaded with default OCR/layout options")
            return DocumentConverter()
        except ImportError:
            logger.warning("Docling is not installed; falling back to PyMuPDF")
            return None
        except Exception as exc:
            logger.warning("Docling initialization failed; falling back to PyMuPDF: {}", exc)
            return None

    @staticmethod
    def _build_docling_without_ocr():
        try:
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import DocumentConverter, PdfFormatOption

            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = False

            logger.info("Docling parser loaded with OCR disabled")
            return DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                }
            )
        except Exception:
            from docling.document_converter import DocumentConverter

            logger.warning("Docling no-OCR options unavailable; using default converter")
            return DocumentConverter()

    def parse(self, file_path: str) -> str:
        if self.backend == "pymupdf" or self.converter is None:
            logger.info("Parsing with fast PyMuPDF: {}", file_path)
            return self._parse_with_pymupdf(file_path)

        try:
            logger.info("Parsing with Docling: {}", file_path)
            result = self.converter.convert(file_path)
            return self._clean_text(result.document.export_to_markdown())
        except Exception as exc:
            logger.error("Docling parse failed; falling back to PyMuPDF: {}", exc)
            return self._parse_with_pymupdf(file_path)

    def _parse_with_pymupdf(self, file_path: str) -> str:
        try:
            import fitz

            text_parts = []
            with fitz.open(file_path) as doc:
                for page in doc:
                    text_parts.append(page.get_text("text"))
            return self._clean_text("\n".join(text_parts))
        except Exception as exc:
            logger.error("PyMuPDF parse failed for {}: {}", file_path, exc)
            return ""

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


specialized_parser = SpecializedParser()
