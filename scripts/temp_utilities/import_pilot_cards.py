#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手動導入 Pilot 論文的 Zettelkasten 卡片到資料庫
"""

import os
import json
import sqlite3
from pathlib import Path

# 連接資料庫
conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()

# 今天生成的 8 個 Zettelkasten 目錄
folders = [
    'zettel_Peer-2017_20251120',
    'zettel_Liao-2021_20251120',
    'zettel_Leckel-2025_20251120',
    'zettel_Shapiro-2013_20251120',
    'zettel_Stewart-2017_20251120',
    'zettel_Strickland-2019_20251120',
    'zettel_Strickland-2022_20251120',
    'zettel_Woodley-2025_20251120'
]

paper_id_map = {
    'Peer-2017': 11,
    'Liao-2021': 12,
    'Leckel-2025': 13,
    'Shapiro-2013': 14,
    'Stewart-2017': 15,
    'Strickland-2019': 16,
    'Strickland-2022': 17,
    'Woodley-2025': 18
}

total_imported = 0
total_failed = 0

for folder in folders:
    cite_key = folder.replace('zettel_', '').replace('_20251120', '')
    paper_id = paper_id_map.get(cite_key)

    if not paper_id:
        print(f'Unknown paper: {cite_key}')
        continue

    # 讀取 zettel_index.json
    index_path = Path(f'output/zettelkasten_notes/{folder}/zettel_index.json')
    if not index_path.exists():
        print(f'Index not found: {folder}')
        continue

    with open(index_path, 'r', encoding='utf-8') as f:
        cards_data = json.load(f)

    # 導入每張卡片
    imported = 0
    failed = 0
    for card in cards_data:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO zettel_cards (
                    zettel_id, title, content, core_concept, description,
                    card_type, domain, tags, paper_id, zettel_folder,
                    source_info, file_path, ai_notes, human_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                card.get('zettel_id', ''),
                card.get('title', ''),
                card.get('content', ''),
                card.get('core_concept', ''),
                card.get('description', ''),
                card.get('card_type', ''),
                card.get('domain', ''),
                ','.join(card.get('tags', [])),
                paper_id,
                folder,
                card.get('source_info', ''),
                card.get('file_path', ''),
                card.get('ai_notes', ''),
                card.get('human_notes', '')
            ))
            if cursor.rowcount > 0:
                imported += 1
            else:
                failed += 1
        except Exception as e:
            print(f'Error importing {card.get("zettel_id")}: {e}')
            failed += 1

    total_imported += imported
    total_failed += failed
    print(f'{cite_key}: {imported} imported, {failed} skipped')

conn.commit()
conn.close()

print(f'\nTotal: {total_imported} imported, {total_failed} failed')
