#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新ID 23的cite_key"""

import sys
import io
import sqlite3

# Windows UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()

# 更新ID 23的cite_key和year
cursor.execute('UPDATE papers SET cite_key = ?, year = ? WHERE id = ?', ('Zwaan-2002', 2002, 23))
conn.commit()

# 驗證更新
cursor.execute('SELECT id, title, cite_key, year FROM papers WHERE id = 23')
result = cursor.fetchone()

print(f'✅ 已更新論文 ID {result[0]}:')
print(f'   標題: {result[1]}')
print(f'   cite_key: {result[2]}')
print(f'   年份: {result[3]}')

conn.close()
