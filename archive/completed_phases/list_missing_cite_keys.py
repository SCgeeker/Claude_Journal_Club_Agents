#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
列出所有缺少 cite_key 的論文
"""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def main():
    conn = sqlite3.connect('knowledge_base/index.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, file_path
        FROM papers
        WHERE cite_key IS NULL
        ORDER BY id
    ''')

    missing_papers = cursor.fetchall()

    print()
    print("=" * 80)
    print(f"缺少 cite_key 的論文清單 (共 {len(missing_papers)} 篇)")
    print("=" * 80)
    print()

    if not missing_papers:
        print("🎉 所有論文都已有 cite_key！")
        conn.close()
        return

    for paper_id, title, md_path in missing_papers:
        print(f"Paper {paper_id:2d}")
        print(f"  標題: {title[:65]}")

        # 嘗試顯示內容預覽
        md_file = Path(md_path)
        if md_file.exists():
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')
                in_full = False
                preview = []

                for line in lines:
                    if '## 完整內容' in line:
                        in_full = True
                        continue
                    if in_full and line.strip() and not line.startswith('#'):
                        preview.append(line.strip())
                        if len(preview) >= 2:
                            break

                if preview:
                    print(f"  預覽: {preview[0][:65]}")
                    if len(preview) > 1:
                        print(f"        {preview[1][:65]}")
            except:
                pass

        print()

    print()
    print("使用方法:")
    print("=" * 80)
    print()
    print("方法 1: 單個處理")
    print("  python fix_single_paper.py <paper_id> <pdf_path>")
    print()
    print("  範例:")
    print('    python fix_single_paper.py 1 "D:\\PDFs\\Her-2012.pdf"')
    print()
    print("方法 2: 批量處理")
    print("  1. 創建 pdf_path_mapping.txt 文件")
    print("  2. 格式: paper_id|pdf_path (每行一個)")
    print("  3. 執行: python batch_fix_cite_keys.py")
    print()
    print("  範例 pdf_path_mapping.txt:")
    print("    1|D:\\PDFs\\Her-2012.pdf")
    print("    3|D:\\PDFs\\Zwaan-2002.pdf")
    print("    4|D:\\PDFs\\Concepts-Brain.pdf")
    print()

    conn.close()

if __name__ == '__main__':
    main()
