#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
導入未被記錄的 Markdown 檔案到知識庫
"""

import sqlite3
import sys
import io
from pathlib import Path
from typing import List, Dict
import re

# Windows UTF-8 支援
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

def find_unrecorded_files(papers_dir: str = "knowledge_base/papers", db_path: str = "knowledge_base/index.db") -> List[Path]:
    """找出未被記錄的 Markdown 檔案"""

    # 獲取所有實際檔案
    actual_files = set(f.name for f in Path(papers_dir).glob("*.md"))

    # 獲取資料庫中的檔案
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT file_path FROM papers')
    db_files = set(Path(row[0]).name for row in cursor.fetchall())
    conn.close()

    # 找出差異
    unrecorded = actual_files - db_files

    return [Path(papers_dir) / f for f in sorted(unrecorded)]

def extract_metadata_from_file(md_path: Path) -> Dict:
    """從 Markdown 檔案提取元數據"""

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 YAML front matter
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

    metadata = {
        'title': md_path.stem,  # 預設使用檔名
        'authors': None,
        'year': None,
        'keywords': None,
        'abstract': None
    }

    if yaml_match:
        import yaml
        try:
            yaml_data = yaml.safe_load(yaml_match.group(1))
            if yaml_data:
                metadata['title'] = yaml_data.get('title', metadata['title'])
                metadata['year'] = yaml_data.get('year')
                metadata['keywords'] = yaml_data.get('keywords')
                metadata['abstract'] = yaml_data.get('abstract')

                # 處理作者
                authors = yaml_data.get('authors')
                if authors:
                    if isinstance(authors, list):
                        metadata['authors'] = ', '.join(str(a) for a in authors)
                    else:
                        metadata['authors'] = str(authors)
        except yaml.YAMLError:
            pass

    # 過濾 None 字串
    if metadata['abstract'] in ['None', 'null']:
        metadata['abstract'] = None

    if metadata['year'] in ['N/A', 'null']:
        metadata['year'] = None

    return metadata

def import_file_to_kb(md_path: Path, db_path: str = "knowledge_base/index.db") -> bool:
    """導入單個檔案到知識庫"""

    # 提取元數據
    metadata = extract_metadata_from_file(md_path)

    # 插入到資料庫
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        import json

        # 準備關鍵詞（列表轉 JSON）
        keywords_json = None
        if metadata['keywords']:
            if isinstance(metadata['keywords'], list):
                keywords_json = json.dumps(metadata['keywords'], ensure_ascii=False)
            elif isinstance(metadata['keywords'], str):
                keywords_json = json.dumps([metadata['keywords']], ensure_ascii=False)

        cursor.execute("""
            INSERT INTO papers (title, authors, year, keywords, abstract, file_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            metadata['title'],
            metadata['authors'],
            metadata['year'],
            keywords_json,
            metadata['abstract'],
            str(md_path)
        ))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"  ❌ 失敗: {e}")
        conn.close()
        return False

def batch_import(papers_dir: str = "knowledge_base/papers", db_path: str = "knowledge_base/index.db"):
    """批次導入未被記錄的檔案"""

    unrecorded_files = find_unrecorded_files(papers_dir, db_path)

    print(f"找到 {len(unrecorded_files)} 個未被記錄的檔案")
    print("=" * 80)

    if not unrecorded_files:
        print("所有檔案都已記錄！")
        return

    success_count = 0
    failed_count = 0

    for i, md_file in enumerate(unrecorded_files, 1):
        print(f"[{i}/{len(unrecorded_files)}] {md_file.name}")

        # 提取並顯示元數據
        metadata = extract_metadata_from_file(md_file)
        print(f"  標題: {metadata['title']}")
        print(f"  作者: {metadata['authors'] or '未知'}")
        print(f"  年份: {metadata['year'] or '未知'}")

        # 導入
        success = import_file_to_kb(md_file, db_path)

        if success:
            print(f"  ✅ 導入成功")
            success_count += 1
        else:
            failed_count += 1

        print()

    print("=" * 80)
    print(f"導入完成:")
    print(f"  成功: {success_count}")
    print(f"  失敗: {failed_count}")
    print(f"  總計: {len(unrecorded_files)}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="導入未被記錄的 Markdown 檔案")
    parser.add_argument('--list', action='store_true', help='僅列出未被記錄的檔案')
    parser.add_argument('--import', dest='do_import', action='store_true', help='執行導入')

    args = parser.parse_args()

    if args.list:
        unrecorded = find_unrecorded_files()
        print(f"未被記錄的檔案 ({len(unrecorded)} 個):")
        for f in unrecorded:
            print(f"  - {f.name}")

    elif args.do_import:
        batch_import()

    else:
        parser.print_help()
