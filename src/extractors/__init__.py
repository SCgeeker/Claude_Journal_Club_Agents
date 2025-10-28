"""
提取器模組
支援多種格式的文檔內容提取
"""

from .pdf_extractor import PDFExtractor, extract_pdf_text

__all__ = ['PDFExtractor', 'extract_pdf_text']
