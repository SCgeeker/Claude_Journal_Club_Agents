#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修復缺失的 cite_key
從 Markdown 文件內容提取完整標題和作者，然後與 bib 文件匹配
"""

import sqlite3
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# 手動映射：基於 Markdown 內容和已知信息
MANUAL_MAPPINGS = {
    1: "Her-2012",  # Taxonomy of Numeral Classifiers - Her, Wu
    3: None,  # 待查找
    4: None,  # Concepts in the Brain
    8: None,  # LinguisticsVanguard
    10: None,  # Huang
    13: None,  # 待查找
    14: None,  # Journal of Cognitive Psychology
    15: None,  # Psychonomic Bulletin
    16: None,  # 待查找
    18: None,  # Memory&Cognition
    19: None,  # Cognitive Processing
    20: None,  # Cognition
    22: None,  # JVLVB
    25: None,  # Memory & Cognition
    26: None,  # Educational Psychology
    27: None,  # Journal Pre-proof
    28: None,  # Revisiting Mental Simulation
    29: None,  # PsychonBullRev
}

def extract_info_from_markdown(md_path):
    """從 Markdown 文件提取標題和作者信息"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取前幾行的標題
    lines = content.split('\n')
    title_lines = []
    authors_lines = []

    # 查找完整標題（在 ## 完整內容 後）
    in_full_content = False
    for line in lines:
        if '## 完整內容' in line or '## Full Content' in line:
            in_full_content = True
            continue

        if in_full_content and line.strip() and not line.startswith('#'):
            title_lines.append(line.strip())
            if len(title_lines) >= 3:  # 取前幾行
                break

    full_title = ' '.join(title_lines[:3])

    # 查找作者（通常在標題後）
    if len(title_lines) > 3:
        authors_lines = title_lines[3:5]

    return {
        'full_title': full_title,
        'authors': ' '.join(authors_lines) if authors_lines else None
    }

def search_in_bib(bib_file, search_terms):
    """在 bib 文件中搜索條目"""
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 搜索包含搜索詞的條目
    entries = re.split(r'\n@', content)
    matches = []

    for entry in entries:
        entry_lower = entry.lower()
        if all(term.lower() in entry_lower for term in search_terms):
            # 提取 cite_key
            cite_key_match = re.search(r'^\s*(\w+)\s*\{([^,]+),', entry)
            if cite_key_match:
                entry_type = cite_key_match.group(1)
                cite_key = cite_key_match.group(2)
                matches.append({
                    'cite_key': cite_key,
                    'type': entry_type,
                    'preview': entry[:200]
                })

    return matches

def main():
    conn = sqlite3.connect('knowledge_base/index.db')
    cursor = conn.cursor()

    # 讀取缺失 cite_key 的論文
    cursor.execute('''
        SELECT id, title, file_path
        FROM papers
        WHERE cite_key IS NULL
        ORDER BY id
    ''')

    missing_papers = cursor.fetchall()

    print(f'發現 {len(missing_papers)} 篇論文缺少 cite_key')
    print('=' * 80)

    # 處理 Paper 1 (已知)
    if MANUAL_MAPPINGS.get(1):
        paper_id = 1
        cite_key = MANUAL_MAPPINGS[1]

        # 檢查 cite_key 是否已存在
        cursor.execute('SELECT id FROM papers WHERE cite_key = ?', (cite_key,))
        existing = cursor.fetchone()

        if existing:
            print(f'⚠️  Paper {paper_id}: cite_key "{cite_key}" 已被 Paper {existing[0]} 使用')
        else:
            # 更新
            cursor.execute('UPDATE papers SET cite_key = ? WHERE id = ?', (cite_key, paper_id))
            print(f'✅ Paper {paper_id}: 已更新 cite_key = "{cite_key}"')

    # 顯示需要手動處理的論文
    print()
    print('需要手動查找的論文:')
    print('=' * 80)

    for paper_id, title, file_path in missing_papers:
        if MANUAL_MAPPINGS.get(paper_id) is None:
            # 嘗試從 Markdown 提取信息
            md_path = Path(file_path)
            if md_path.exists():
                info = extract_info_from_markdown(md_path)
                print(f'Paper {paper_id:2d}: {title[:50]}')
                if info['full_title']:
                    print(f'  完整標題: {info["full_title"][:80]}')
                if info['authors']:
                    print(f'  作者信息: {info["authors"][:80]}')
                print()

    # 提交變更
    conn.commit()
    conn.close()

    print()
    print('處理完成！')
    print('建議：手動檢查剩餘論文的 Markdown 文件，從 bib 文件中查找對應的 cite_key')

if __name__ == '__main__':
    main()
