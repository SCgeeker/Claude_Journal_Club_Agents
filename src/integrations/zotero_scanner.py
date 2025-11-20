#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero PDF目錄掃描器
掃描Zotero管理的PDF文件，識別新論文
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher

# 條件式導入（支援直接執行和模組導入）
try:
    from .bibtex_parser import BibTeXEntry
except ImportError:
    from src.integrations.bibtex_parser import BibTeXEntry


@dataclass
class PDFFile:
    """PDF文件信息"""
    file_path: Path
    file_name: str
    file_size: int  # bytes

    # 從檔名提取的信息
    extracted_authors: List[str]
    extracted_year: Optional[int]
    extracted_title: Optional[str]

    # 匹配結果
    matched_bibtex_entry: Optional[BibTeXEntry] = None
    match_score: float = 0.0
    match_method: str = ""  # cite_key, title, filename

    def __post_init__(self):
        """驗證文件存在"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {self.file_path}")


class ZoteroScanner:
    """
    Zotero PDF目錄掃描器
    掃描PDF文件並匹配到BibTeX條目
    """

    def __init__(self, pdf_directory: str):
        """
        初始化掃描器

        Args:
            pdf_directory: PDF文件目錄路徑
        """
        self.pdf_dir = Path(pdf_directory)

        if not self.pdf_dir.exists():
            raise FileNotFoundError(f"PDF目錄不存在: {pdf_directory}")

    def scan_pdfs(self) -> List[PDFFile]:
        """
        掃描PDF目錄

        Returns:
            PDFFile對象列表
        """
        pdf_files = []

        # 遞歸搜索所有PDF文件
        for pdf_path in self.pdf_dir.rglob("*.pdf"):
            try:
                pdf_info = self._extract_pdf_info(pdf_path)
                pdf_files.append(pdf_info)
            except Exception as e:
                print(f"⚠️  跳過文件 {pdf_path.name}: {e}")
                continue

        return pdf_files

    def _extract_pdf_info(self, pdf_path: Path) -> PDFFile:
        """
        從PDF文件提取信息

        Args:
            pdf_path: PDF文件路徑

        Returns:
            PDFFile對象
        """
        file_name = pdf_path.stem  # 不含副檔名
        file_size = pdf_path.stat().st_size

        # 從檔名提取作者、年份、標題
        authors, year, title = self._parse_filename(file_name)

        return PDFFile(
            file_path=pdf_path,
            file_name=file_name,
            file_size=file_size,
            extracted_authors=authors,
            extracted_year=year,
            extracted_title=title
        )

    def _parse_filename(self, filename: str) -> Tuple[List[str], Optional[int], Optional[str]]:
        """
        解析PDF檔名

        常見格式：
        - "Author1_Author2_2024_Title"
        - "Author1-2024-Title"
        - "Author et al. (2024) Title"
        - "Title - Author (2024)"

        Args:
            filename: 檔名（不含副檔名）

        Returns:
            (作者列表, 年份, 標題)
        """
        authors = []
        year = None
        title = None

        # 提取年份（4位數字）
        year_match = re.search(r'\b(19|20)\d{2}\b', filename)
        if year_match:
            year = int(year_match.group(0))

        # 嘗試匹配 "Author_Year_Title" 格式
        pattern1 = re.match(r'^([A-Z][a-z]+(?:[_-][A-Z][a-z]+)*)(?:[_-])(\d{4})(?:[_-])(.+)$', filename)
        if pattern1:
            author_str, year_str, title_str = pattern1.groups()
            authors = re.split(r'[_-]', author_str)
            year = int(year_str)
            title = title_str.replace('_', ' ').replace('-', ' ')
            return authors, year, title

        # 嘗試匹配 "Author et al (Year) Title" 格式
        pattern2 = re.match(r'^(.+?)\s+et\s+al\.?\s*\((\d{4})\)\s*(.+)$', filename, re.IGNORECASE)
        if pattern2:
            author_str, year_str, title_str = pattern2.groups()
            authors = [author_str.strip()]
            year = int(year_str)
            title = title_str.strip()
            return authors, year, title

        # 嘗試匹配 "Title - Author (Year)" 格式
        pattern3 = re.match(r'^(.+?)\s*[-–—]\s*(.+?)\s*\((\d{4})\)$', filename)
        if pattern3:
            title_str, author_str, year_str = pattern3.groups()
            title = title_str.strip()
            authors = [author_str.strip()]
            year = int(year_str)
            return authors, year, title

        # 無法識別格式，返回檔名作為標題
        title = filename.replace('_', ' ').replace('-', ' ')

        return authors, year, title

    def match_to_bibtex(
        self,
        pdf_files: List[PDFFile],
        bibtex_entries: List[BibTeXEntry],
        threshold: float = 0.7
    ) -> List[PDFFile]:
        """
        將PDF文件匹配到BibTeX條目

        Args:
            pdf_files: PDFFile列表
            bibtex_entries: BibTeXEntry列表
            threshold: 標題相似度閾值（0-1）

        Returns:
            已匹配的PDFFile列表
        """
        matched_files = []

        # 建立cite_key索引（快速查找）
        cite_key_index = {entry.cite_key.lower(): entry for entry in bibtex_entries}

        for pdf in pdf_files:
            # 方法1: 嘗試通過cite_key匹配（檔名可能就是cite_key）
            cite_key_lower = pdf.file_name.lower()
            if cite_key_lower in cite_key_index:
                pdf.matched_bibtex_entry = cite_key_index[cite_key_lower]
                pdf.match_score = 1.0
                pdf.match_method = "cite_key"
                matched_files.append(pdf)
                continue

            # 方法2: 通過標題模糊匹配
            if pdf.extracted_title:
                best_match = self._find_best_title_match(
                    pdf.extracted_title,
                    bibtex_entries,
                    threshold
                )

                if best_match:
                    entry, score = best_match
                    pdf.matched_bibtex_entry = entry
                    pdf.match_score = score
                    pdf.match_method = "title"
                    matched_files.append(pdf)
                    continue

            # 方法3: 通過作者+年份匹配
            if pdf.extracted_authors and pdf.extracted_year:
                best_match = self._find_by_author_year(
                    pdf.extracted_authors,
                    pdf.extracted_year,
                    bibtex_entries
                )

                if best_match:
                    entry, score = best_match
                    pdf.matched_bibtex_entry = entry
                    pdf.match_score = score
                    pdf.match_method = "author_year"
                    matched_files.append(pdf)
                    continue

        return matched_files

    def _find_best_title_match(
        self,
        title: str,
        entries: List[BibTeXEntry],
        threshold: float
    ) -> Optional[Tuple[BibTeXEntry, float]]:
        """
        通過標題查找最佳匹配

        Args:
            title: 目標標題
            entries: BibTeX條目列表
            threshold: 相似度閾值

        Returns:
            (匹配的條目, 相似度分數) 或 None
        """
        title_lower = title.lower().strip()

        best_match = None
        best_score = 0

        for entry in entries:
            entry_title = entry.title.lower().strip()

            # 計算相似度
            score = SequenceMatcher(None, title_lower, entry_title).ratio()

            if score > best_score and score >= threshold:
                best_score = score
                best_match = entry

        if best_match:
            return (best_match, best_score)

        return None

    def _find_by_author_year(
        self,
        authors: List[str],
        year: int,
        entries: List[BibTeXEntry]
    ) -> Optional[Tuple[BibTeXEntry, float]]:
        """
        通過作者和年份查找匹配

        Args:
            authors: 作者列表
            year: 年份
            entries: BibTeX條目列表

        Returns:
            (匹配的條目, 相似度分數) 或 None
        """
        candidates = []

        for entry in entries:
            # 年份必須匹配
            if entry.year != year:
                continue

            # 檢查作者重疊
            if not entry.authors:
                continue

            # 計算作者重疊度
            author_overlap = self._calculate_author_overlap(authors, entry.authors)

            if author_overlap > 0:
                candidates.append((entry, author_overlap))

        # 返回作者重疊度最高的
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0]

        return None

    def _calculate_author_overlap(
        self,
        authors1: List[str],
        authors2: List[str]
    ) -> float:
        """
        計算作者列表的重疊度

        Args:
            authors1: 作者列表1
            authors2: 作者列表2

        Returns:
            重疊度（0-1）
        """
        # 提取姓氏（假設格式為 "Last, First" 或 "First Last"）
        def extract_last_name(author: str) -> str:
            # 移除空白並轉小寫
            author = author.strip().lower()

            # 格式 "Last, First"
            if ',' in author:
                return author.split(',')[0].strip()

            # 格式 "First Last"
            parts = author.split()
            if parts:
                return parts[-1].strip()

            return author

        last_names1 = set(extract_last_name(a) for a in authors1)
        last_names2 = set(extract_last_name(a) for a in authors2)

        if not last_names1 or not last_names2:
            return 0.0

        # Jaccard相似度
        intersection = len(last_names1 & last_names2)
        union = len(last_names1 | last_names2)

        return intersection / union if union > 0 else 0.0

    def filter_new_pdfs(
        self,
        matched_pdfs: List[PDFFile],
        existing_papers: List[Dict]
    ) -> List[PDFFile]:
        """
        過濾出新PDF（不在知識庫中的）

        Args:
            matched_pdfs: 已匹配的PDF列表
            existing_papers: 知識庫中已有的論文（字典列表，包含title和file_path）

        Returns:
            新PDF列表
        """
        # 建立已有論文的標題索引
        existing_titles = set()
        existing_paths = set()

        for paper in existing_papers:
            if paper.get('title'):
                existing_titles.add(paper['title'].lower().strip())
            if paper.get('file_path'):
                existing_paths.add(str(Path(paper['file_path']).resolve()))

        # 過濾
        new_pdfs = []

        for pdf in matched_pdfs:
            # 檢查路徑
            pdf_path_str = str(pdf.file_path.resolve())
            if pdf_path_str in existing_paths:
                continue

            # 檢查標題（如果有匹配的BibTeX條目）
            if pdf.matched_bibtex_entry:
                title = pdf.matched_bibtex_entry.title.lower().strip()
                if title in existing_titles:
                    continue

            new_pdfs.append(pdf)

        return new_pdfs

    def get_statistics(
        self,
        pdf_files: List[PDFFile]
    ) -> Dict:
        """
        生成統計信息

        Args:
            pdf_files: PDF文件列表

        Returns:
            統計字典
        """
        total = len(pdf_files)
        matched = sum(1 for pdf in pdf_files if pdf.matched_bibtex_entry)
        unmatched = total - matched

        # 匹配方法分布
        match_methods = {}
        for pdf in pdf_files:
            if pdf.match_method:
                match_methods[pdf.match_method] = match_methods.get(pdf.match_method, 0) + 1

        # 平均匹配分數
        matched_pdfs = [pdf for pdf in pdf_files if pdf.matched_bibtex_entry]
        avg_score = sum(pdf.match_score for pdf in matched_pdfs) / len(matched_pdfs) if matched_pdfs else 0

        return {
            'total_pdfs': total,
            'matched': matched,
            'unmatched': unmatched,
            'match_rate': (matched / total * 100) if total > 0 else 0,
            'match_methods': match_methods,
            'average_match_score': avg_score
        }


def main():
    """測試Zotero掃描器"""
    import sys
    import io

    # 修復Windows終端UTF-8編碼
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 3:
        print("使用方式: python zotero_scanner.py <pdf_directory> <bib_file>")
        sys.exit(1)

    pdf_dir = sys.argv[1]
    bib_file = sys.argv[2]

    # 解析BibTeX（絕對導入）
    from src.integrations.bibtex_parser import BibTeXParser

    print(f"📚 解析BibTeX: {bib_file}")
    parser = BibTeXParser()
    bibtex_entries = parser.parse_file(bib_file)
    print(f"   找到 {len(bibtex_entries)} 個BibTeX條目\n")

    # 掃描PDF
    print(f"📁 掃描PDF目錄: {pdf_dir}")
    scanner = ZoteroScanner(pdf_dir)
    pdf_files = scanner.scan_pdfs()
    print(f"   找到 {len(pdf_files)} 個PDF文件\n")

    # 匹配
    print("🔗 匹配PDF到BibTeX...")
    matched_pdfs = scanner.match_to_bibtex(pdf_files, bibtex_entries, threshold=0.7)

    # 統計
    stats = scanner.get_statistics(pdf_files)
    print(f"✅ 匹配完成\n")
    print(f"📊 統計:")
    print(f"   總PDF數: {stats['total_pdfs']}")
    print(f"   已匹配: {stats['matched']} ({stats['match_rate']:.1f}%)")
    print(f"   未匹配: {stats['unmatched']}")
    print(f"   平均匹配分數: {stats['average_match_score']:.2f}")
    print(f"\n   匹配方法:")
    for method, count in stats['match_methods'].items():
        print(f"     - {method}: {count}")

    # 顯示前5個匹配結果
    print(f"\n📄 範例匹配（前5個）:")
    for i, pdf in enumerate(matched_pdfs[:5], 1):
        print(f"\n   [{i}] {pdf.file_name}")
        if pdf.matched_bibtex_entry:
            print(f"       → {pdf.matched_bibtex_entry.cite_key}")
            print(f"       標題: {pdf.matched_bibtex_entry.title[:80]}...")
            print(f"       方法: {pdf.match_method} (分數: {pdf.match_score:.2f})")


if __name__ == "__main__":
    main()
