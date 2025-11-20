#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查修復結果"""

import sys
import io
import sqlite3
import json
from pathlib import Path

# Windows UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()

# 檢查修復的5篇論文
paper_ids = [2, 5, 6, 9, 40]

print('\n📊 修復後的論文狀態:\n')
print(f"{'ID':<4} | {'cite_key':<20} | {'Year':<6} | {'Keywords':<10} | {'Abstract':<10}")
print('-' * 70)

for pid in paper_ids:
    cursor.execute('''
        SELECT id, cite_key, year, keywords, abstract
        FROM papers
        WHERE id = ?
    ''', (pid,))

    row = cursor.fetchone()
    if row:
        pid, cite_key, year, keywords, abstract = row

        cite_key_display = cite_key if cite_key else '❌ 缺失'
        year_display = str(year) if year else '❌ 缺失'

        # 檢查keywords
        if keywords and keywords != '[]':
            try:
                kw_list = json.loads(keywords)
                kw_display = f'✅ {len(kw_list)}個'
            except:
                kw_display = '❌ 格式錯誤'
        else:
            kw_display = '❌ 缺失'

        # 檢查abstract
        if abstract and abstract != 'None' and len(abstract) >= 50:
            abstract_display = f'✅ {len(abstract)}字元'
        else:
            abstract_display = f'❌ {len(abstract) if abstract and abstract != "None" else 0}字元'

        print(f'{pid:<4} | {cite_key_display:<20} | {year_display:<6} | {kw_display:<10} | {abstract_display:<10}')

# 統計所有論文的cite_key狀態
cursor.execute('SELECT COUNT(*) FROM papers WHERE cite_key IS NOT NULL AND cite_key != ""')
has_cite_key = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM papers')
total = cursor.fetchone()[0]

print(f'\n📈 cite_key 更新統計:')
print(f'  總論文數: {total}')
print(f'  有 cite_key: {has_cite_key} ({has_cite_key*100//total}%)')
print(f'  進步: 2 → {has_cite_key} (+{has_cite_key-2})')

conn.close()
