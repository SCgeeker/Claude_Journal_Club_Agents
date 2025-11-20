#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Zotero掃描器
"""

import sys
import io
from pathlib import Path

# 添加src到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.integrations.bibtex_parser import BibTeXParser
from src.integrations.zotero_scanner import ZoteroScanner

# 修復Windows終端UTF-8編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    if len(sys.argv) < 3:
        print("使用方式: python test_zotero_scanner.py <pdf_directory> <bib_file>")
        sys.exit(1)

    pdf_dir = sys.argv[1]
    bib_file = sys.argv[2]

    # 解析BibTeX
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
        print(f"\n   [{i}] {pdf.file_name[:60]}...")
        if pdf.matched_bibtex_entry:
            print(f"       → {pdf.matched_bibtex_entry.cite_key}")
            print(f"       標題: {pdf.matched_bibtex_entry.title[:80]}...")
            print(f"       方法: {pdf.match_method} (分數: {pdf.match_score:.2f})")


if __name__ == "__main__":
    main()
