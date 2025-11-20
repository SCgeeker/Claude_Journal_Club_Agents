#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成只包含 Pilot 論文 (12 篇 crowdsourcing) 的 Concept Network 和 MOC
"""

import sqlite3
import sys
from pathlib import Path

# Pilot 論文 cite keys
PILOT_CITE_KEYS = [
    'Adams-2020', 'Baruch-2016', 'Crequit-2018', 'Hosseini-2015',
    'Leckel-2025', 'Liao-2021', 'Peer-2017', 'Shapiro-2013',
    'Stewart-2017', 'Strickland-2019', 'Strickland-2022', 'Woodley-2025'
]

# 連接資料庫
conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()

# 統計今天生成的卡片（Pilot 論文）
print('Pilot papers (2025-11-20):')
pilot_folders = [f'zettel_{key}_20251120' for key in PILOT_CITE_KEYS]

# 找出 Pilot 論文的所有卡片
cursor.execute('''
    SELECT COUNT(*), zettel_folder
    FROM zettel_cards
    WHERE zettel_folder LIKE '%20251120'
    GROUP BY zettel_folder
''')

pilot_card_count = 0
for row in cursor.fetchall():
    print(f'  {row[1]}: {row[0]} cards')
    pilot_card_count += row[0]

print(f'\nTotal Pilot cards: {pilot_card_count}')

# 找出非 Pilot 論文的卡片（用於過濾）
cursor.execute('''
    SELECT zettel_id
    FROM zettel_cards
    WHERE zettel_folder NOT LIKE '%20251120' OR zettel_folder IS NULL
''')

non_pilot_ids = set(row[0] for row in cursor.fetchall())
print(f'Non-Pilot cards to filter: {len(non_pilot_ids)}')

conn.close()

print(f'\nTo generate Pilot-only MOC:')
print(f'1. Modify RelationFinder to filter out non-Pilot card IDs')
print(f'2. Re-run: python kb_manage.py visualize-network --obsidian --output output/pilot_only_moc')
