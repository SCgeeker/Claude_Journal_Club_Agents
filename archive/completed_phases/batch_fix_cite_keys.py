#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量修復 cite_key
讀取映射文件，批量更新論文元數據
"""

import sqlite3
import sys
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def analyze_pdf_and_extract_metadata(pdf_path, paper_id):
    """分析 PDF 並提取元數據"""
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        return None, f"PDF 文件不存在: {pdf_path}"

    print(f"  🔄 正在分析: {pdf_path.name}...")

    # 步驟 1: 從文件名提取可能的 cite_key
    pdf_stem = pdf_path.stem
    potential_cite_key = None

    # 嘗試匹配常見格式
    patterns = [
        r'^([A-Z][a-z]+)-?(\d{4})[a-z]?$',  # Her-2012, Her2012a
        r'^([A-Z][a-z]+[A-Z][a-z]+)-?(\d{4})$',  # ChenYiRu-2020
        r'^([A-Z][a-z]+)_([A-Z][a-z]+)-?(\d{4})$',  # Glenberg_Kaschak-2002
    ]

    for pattern in patterns:
        match = re.match(pattern, pdf_stem)
        if match:
            if len(match.groups()) == 2:
                author = match.group(1)
                year = match.group(2)
            else:
                author = match.group(1) + match.group(2)
                year = match.group(3)
            potential_cite_key = f"{author}-{year}"
            print(f"     從文件名提取: {potential_cite_key}")
            break

    # 步驟 2: 使用 analyze_paper.py 分析 PDF
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

        if result.returncode == 0 and temp_json.exists():
            with open(temp_json, 'r', encoding='utf-8') as f:
                analysis = json.load(f)

            # 提取元數據
            metadata = {
                'cite_key': potential_cite_key,
                'title': analysis.get('title', ''),
                'authors': analysis.get('authors', []),
                'year': analysis.get('year'),
                'abstract': analysis.get('abstract', ''),
                'keywords': analysis.get('keywords', [])
            }

            # 如果沒有從文件名提取到 cite_key，嘗試從元數據生成
            if not metadata['cite_key'] and metadata['authors'] and metadata['year']:
                first_author = metadata['authors'][0].split()[-1] if metadata['authors'] else ''
                if first_author:
                    metadata['cite_key'] = f"{first_author}-{metadata['year']}"

            temp_json.unlink()
            return metadata, None
        else:
            if temp_json.exists():
                temp_json.unlink()
            error_msg = result.stderr[:200] if result.stderr else "未知錯誤"
            return None, f"分析失敗: {error_msg}"

    except subprocess.TimeoutExpired:
        if temp_json.exists():
            temp_json.unlink()
        return None, "處理超時 (180秒)"
    except Exception as e:
        if temp_json.exists():
            temp_json.unlink()
        return None, f"異常: {str(e)}"

def update_paper_metadata(conn, paper_id, metadata):
    """更新論文元數據"""
    cursor = conn.cursor()

    cite_key = metadata['cite_key']

    if not cite_key:
        return False, "缺少 cite_key"

    # 檢查 cite_key 衝突
    cursor.execute('SELECT id FROM papers WHERE cite_key = ?', (cite_key,))
    existing = cursor.fetchone()

    if existing and existing[0] != paper_id:
        # 添加後綴
        suffix = 'a'
        while True:
            new_cite_key = f"{cite_key}{suffix}"
            cursor.execute('SELECT id FROM papers WHERE cite_key = ?', (new_cite_key,))
            if not cursor.fetchone():
                cite_key = new_cite_key
                metadata['cite_key'] = cite_key
                print(f"     ⚠️  cite_key 衝突，使用: {cite_key}")
                break
            suffix = chr(ord(suffix) + 1)

    # 構建更新語句
    update_fields = []
    update_values = []

    if cite_key:
        update_fields.append('cite_key = ?')
        update_values.append(cite_key)

    if metadata['title'] and metadata['title'] != 'Untitled':
        update_fields.append('title = ?')
        update_values.append(metadata['title'])

    if metadata['year']:
        update_fields.append('year = ?')
        update_values.append(metadata['year'])

    if metadata['authors']:
        authors_str = ', '.join(metadata['authors'])
        update_fields.append('authors = ?')
        update_values.append(authors_str)

    if metadata['abstract']:
        update_fields.append('abstract = ?')
        update_values.append(metadata['abstract'])

    if metadata['keywords']:
        keywords_str = ', '.join(metadata['keywords'])
        update_fields.append('keywords = ?')
        update_values.append(keywords_str)

    if update_fields:
        update_values.append(paper_id)
        sql = f"UPDATE papers SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, update_values)
        conn.commit()
        return True, None
    else:
        return False, "沒有可更新的字段"

def main():
    # 映射文件格式：paper_id: pdf_path
    mapping_file = Path("pdf_path_mapping.txt")

    if not mapping_file.exists():
        print("請創建 pdf_path_mapping.txt 文件")
        print("格式：每行一個映射，格式為: paper_id|pdf_path")
        print()
        print("範例:")
        print("1|D:\\PDFs\\Her-2012.pdf")
        print("3|D:\\PDFs\\Zwaan-2002.pdf")
        print()
        print("或者輸入 'q' 跳過批處理，改用單個處理")
        return

    # 讀取映射
    mappings = []
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('|')
            if len(parts) == 2:
                paper_id = int(parts[0].strip())
                pdf_path = parts[1].strip().strip('"').strip("'")
                mappings.append((paper_id, pdf_path))

    if not mappings:
        print("映射文件為空")
        return

    print("=" * 80)
    print(f"批量修復 cite_key - 共 {len(mappings)} 篇論文")
    print("=" * 80)
    print()

    conn = sqlite3.connect('knowledge_base/index.db')
    results = {
        'success': 0,
        'failed': 0,
        'errors': []
    }

    for paper_id, pdf_path in mappings:
        print(f"[{results['success'] + results['failed'] + 1}/{len(mappings)}] Paper {paper_id}")

        # 分析 PDF
        metadata, error = analyze_pdf_and_extract_metadata(pdf_path, paper_id)

        if error:
            print(f"  ❌ {error}")
            results['failed'] += 1
            results['errors'].append({
                'paper_id': paper_id,
                'pdf_path': pdf_path,
                'error': error
            })
            continue

        # 更新數據庫
        success, error = update_paper_metadata(conn, paper_id, metadata)

        if success:
            print(f"  ✅ 成功更新")
            print(f"     cite_key: {metadata['cite_key']}")
            print(f"     year: {metadata['year'] if metadata['year'] else 'N/A'}")
            results['success'] += 1
        else:
            print(f"  ❌ {error}")
            results['failed'] += 1
            results['errors'].append({
                'paper_id': paper_id,
                'pdf_path': pdf_path,
                'error': error
            })

        print()

    conn.close()

    # 顯示總結
    print("=" * 80)
    print("處理總結")
    print("=" * 80)
    print(f"成功: {results['success']}")
    print(f"失敗: {results['failed']}")

    if results['failed'] > 0:
        print()
        print("失敗的論文:")
        for error in results['errors']:
            print(f"  Paper {error['paper_id']}: {error['error']}")

    # 保存日誌
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(f"batch_fix_log_{timestamp}.json")
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print()
    print(f"日誌已保存: {log_file}")

if __name__ == '__main__':
    main()
