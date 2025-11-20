#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
單論文 cite_key 修復工具
用法: python fix_single_paper.py <paper_id> <pdf_path>
"""

import sqlite3
import sys
import subprocess
import json
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def main():
    if len(sys.argv) < 3:
        print("用法: python fix_single_paper.py <paper_id> <pdf_path>")
        print()
        print("範例:")
        print('  python fix_single_paper.py 1 "D:\\PDFs\\Her-2012.pdf"')
        print()
        return

    paper_id = int(sys.argv[1])
    pdf_path = Path(sys.argv[2])

    if not pdf_path.exists():
        print(f"❌ PDF 文件不存在: {pdf_path}")
        return

    print(f"處理 Paper {paper_id}: {pdf_path.name}")
    print("=" * 80)

    # 從文件名提取 cite_key
    pdf_stem = pdf_path.stem
    potential_cite_key = None

    patterns = [
        r'^([A-Z][a-z]+)-?(\d{4})[a-z]?$',
        r'^([A-Z][a-z]+[A-Z][a-z]+)-?(\d{4})$',
    ]

    for pattern in patterns:
        match = re.match(pattern, pdf_stem)
        if match:
            author = match.group(1)
            year = match.group(2)
            potential_cite_key = f"{author}-{year}"
            print(f"從文件名提取 cite_key: {potential_cite_key}")
            break

    # 分析 PDF
    print("正在分析 PDF...")
    temp_json = Path(f"temp_analysis_{paper_id}.json")

    cmd = [
        'python', 'analyze_paper.py',
        str(pdf_path),
        '--format', 'json',
        '--output-json', str(temp_json)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=180,
            errors='replace'
        )

        if result.returncode != 0 or not temp_json.exists():
            print(f"❌ 分析失敗")
            if result.stderr:
                print(f"錯誤: {result.stderr[:200]}")
            return

        with open(temp_json, 'r', encoding='utf-8') as f:
            analysis = json.load(f)

        temp_json.unlink()

        # 提取元數據
        title = analysis.get('title', '')
        authors = analysis.get('authors', [])
        year = analysis.get('year')
        abstract = analysis.get('abstract', '')
        keywords = analysis.get('keywords', [])

        cite_key = potential_cite_key
        if not cite_key and authors and year:
            first_author = authors[0].split()[-1] if authors else ''
            cite_key = f"{first_author}-{year}" if first_author else None

        if not cite_key:
            print("❌ 無法確定 cite_key")
            return

        print()
        print("提取的元數據:")
        print(f"  cite_key: {cite_key}")
        print(f"  title: {title[:60]}")
        print(f"  authors: {', '.join(authors[:2])}")
        print(f"  year: {year}")
        print()

        # 更新數據庫
        conn = sqlite3.connect('knowledge_base/index.db')
        cursor = conn.cursor()

        # 檢查衝突
        cursor.execute('SELECT id FROM papers WHERE cite_key = ?', (cite_key,))
        existing = cursor.fetchone()

        if existing and existing[0] != paper_id:
            suffix = 'a'
            while True:
                new_cite_key = f"{cite_key}{suffix}"
                cursor.execute('SELECT id FROM papers WHERE cite_key = ?', (new_cite_key,))
                if not cursor.fetchone():
                    cite_key = new_cite_key
                    print(f"⚠️  cite_key 衝突，使用: {cite_key}")
                    break
                suffix = chr(ord(suffix) + 1)

        # 更新
        update_fields = []
        update_values = []

        if cite_key:
            update_fields.append('cite_key = ?')
            update_values.append(cite_key)

        if title and title != 'Untitled':
            update_fields.append('title = ?')
            update_values.append(title)

        if year:
            update_fields.append('year = ?')
            update_values.append(year)

        if authors:
            update_fields.append('authors = ?')
            update_values.append(', '.join(authors))

        if abstract:
            update_fields.append('abstract = ?')
            update_values.append(abstract)

        if keywords:
            update_fields.append('keywords = ?')
            update_values.append(', '.join(keywords))

        if update_fields:
            update_values.append(paper_id)
            sql = f"UPDATE papers SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(sql, update_values)
            conn.commit()

            print("✅ 成功更新!")
            print(f"   cite_key: {cite_key}")
            print(f"   year: {year if year else 'N/A'}")
        else:
            print("❌ 沒有可更新的字段")

        conn.close()

    except subprocess.TimeoutExpired:
        print("❌ 處理超時 (180秒)")
        if temp_json.exists():
            temp_json.unlink()
    except Exception as e:
        print(f"❌ 異常: {str(e)}")
        if temp_json.exists():
            temp_json.unlink()

if __name__ == '__main__':
    main()
