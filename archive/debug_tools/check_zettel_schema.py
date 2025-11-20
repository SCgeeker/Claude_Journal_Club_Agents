#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查Zettelkasten數據庫結構"""

import sqlite3
import sys
import io

# 修復Windows UTF-8編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.knowledge_base.kb_manager import KnowledgeBaseManager

# 初始化知識庫（會創建Zettelkasten表）
kb = KnowledgeBaseManager()

conn = sqlite3.connect(kb.db_path)
cursor = conn.cursor()

# 查詢zettel_cards表結構
print("📊 Zettelkasten Cards表結構:\n")
cursor.execute("PRAGMA table_info(zettel_cards)")
columns = cursor.fetchall()

for col in columns:
    cid, name, type_, not_null, default, pk = col
    print(f"   [{cid}] {name:20} {type_:10} ", end="")
    if pk:
        print("PRIMARY KEY", end="")
    if not_null:
        print(" NOT NULL", end="")
    if default:
        print(f" DEFAULT {default}", end="")
    print()

print(f"\n   總欄位數: {len(columns)}")

# 查詢zettel_links表結構
print("\n📊 Zettelkasten Links表結構:\n")
cursor.execute("PRAGMA table_info(zettel_links)")
columns = cursor.fetchall()

for col in columns:
    cid, name, type_, not_null, default, pk = col
    print(f"   [{cid}] {name:20} {type_:10} ", end="")
    if pk:
        print("PRIMARY KEY", end="")
    if not_null:
        print(" NOT NULL", end="")
    if default:
        print(f" DEFAULT {default}", end="")
    print()

print(f"\n   總欄位數: {len(columns)}")

# 查詢索引
print("\n📑 Zettelkasten索引:")
cursor.execute("""
    SELECT name, sql FROM sqlite_master
    WHERE type='index' AND (tbl_name='zettel_cards' OR tbl_name='zettel_links')
    ORDER BY tbl_name, name
""")
indexes = cursor.fetchall()

for idx_name, idx_sql in indexes:
    if idx_sql:  # 跳過自動創建的索引
        print(f"\n   {idx_name}")

# 檢查FTS5表
print("\n🔍 全文搜索表:")
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table' AND name LIKE '%_fts'
""")
fts_tables = cursor.fetchall()

for (table_name,) in fts_tables:
    print(f"   - {table_name}")

# 檢查觸發器
print("\n⚡ 觸發器:")
cursor.execute("""
    SELECT name, tbl_name FROM sqlite_master
    WHERE type='trigger' AND tbl_name='zettel_cards'
""")
triggers = cursor.fetchall()

for trigger_name, table_name in triggers:
    print(f"   - {trigger_name} (on {table_name})")

conn.close()

print("\n✅ Zettelkasten schema檢查完成！")
