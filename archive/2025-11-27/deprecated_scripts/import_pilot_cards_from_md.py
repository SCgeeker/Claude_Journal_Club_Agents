#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
從 Markdown 文件導入 Pilot 論文的 Zettelkasten 卡片到資料庫
"""

import os
import re
import sqlite3
from pathlib import Path

def parse_frontmatter(content):
    """解析 YAML frontmatter"""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return {}, content

    frontmatter_text = match.group(1)
    body = content[match.end():]

    frontmatter = {}
    current_key = None
    current_value = []

    for line in frontmatter_text.split('\n'):
        if ':' in line and not line.startswith(' '):
            if current_key:
                frontmatter[current_key] = '\n'.join(current_value).strip()
            key, value = line.split(':', 1)
            current_key = key.strip()
            current_value = [value.strip().strip('"').strip("'").strip('|-')]
        elif current_key:
            current_value.append(line.strip().strip('"').strip("'"))

    if current_key:
        frontmatter[current_key] = '\n'.join(current_value).strip()

    return frontmatter, body

def extract_sections(body):
    """提取各個區塊的內容"""
    sections = {}
    current_section = None
    current_content = []

    for line in body.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections

# 連接資料庫
conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()

# 所有 12 篇 Pilot 論文
paper_configs = [
    ('Adams-2020', 7),  # Test 1
    ('Baruch-2016', 8),  # Test 2
    ('Créquit-2018', 9),  # Test 2 (特殊字符)
    ('Hosseini-2015', 10),  # Test 2
    ('Peer-2017', 11),
    ('Liao-2021', 12),
    ('Leckel-2025', 13),
    ('Shapiro-2013', 14),
    ('Stewart-2017', 15),
    ('Strickland-2019', 16),
    ('Strickland-2022', 17),
    ('Woodley-2025', 18)
]

total_imported = 0
total_failed = 0

for cite_key, paper_id in paper_configs:
    folder = f'zettel_{cite_key}_20251120'
    cards_dir = Path(f'output/zettelkasten_notes/{folder}/zettel_cards')

    if not cards_dir.exists():
        print(f'Directory not found: {folder}')
        continue

    # 讀取所有 Markdown 卡片
    card_files = sorted(cards_dir.glob(f'{cite_key}-*.md'))

    imported = 0
    failed = 0

    for card_file in card_files:
        try:
            with open(card_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析
            frontmatter, body = parse_frontmatter(content)
            sections = extract_sections(body)

            # 提取 zettel_id from filename
            zettel_id = card_file.stem

            # 準備數據
            title = frontmatter.get('title', '')
            description = sections.get('說明', '')
            source_info = sections.get('來源脈絡', '')
            ai_notes = sections.get('個人筆記', '')
            link_network = sections.get('連結網絡', '')

            # 從連結網絡提取 tags
            tags = []
            if link_network:
                for match in re.findall(r'\[\[([^\]]+)\]\]', link_network):
                    if match not in tags:
                        tags.append(match)

            # 插入資料庫
            cursor.execute('''
                INSERT OR REPLACE INTO zettel_cards (
                    zettel_id, title, content, core_concept, description,
                    card_type, domain, tags, paper_id, zettel_folder,
                    source_info, file_path, ai_notes, human_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                zettel_id,
                title,
                body,
                title,  # 使用 title 作為 core_concept
                description,
                'concept',  # 默認類型
                'Psycho Studies on crowdsourcing',
                ','.join(tags),
                paper_id,
                folder,
                source_info,
                str(card_file),
                ai_notes,
                ''  # human_notes 初始為空
            ))

            if cursor.rowcount > 0:
                imported += 1
        except Exception as e:
            print(f'Error importing {card_file.name}: {e}')
            failed += 1

    total_imported += imported
    total_failed += failed
    # Avoid encoding error with special characters
    try:
        print(f'{cite_key}: {imported} imported, {failed} failed')
    except:
        print(f'Paper: {imported} imported, {failed} failed')

conn.commit()
conn.close()

print(f'\nTotal: {total_imported} imported, {total_failed} failed')
print(f'\nVerifying...')

# 驗證
conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM zettel_cards')
print(f'Total cards in DB: {cursor.fetchone()[0]}')
conn.close()
