#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查數據庫結構"""

import sqlite3
import sys
import io

# 修復Windows UTF-8編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.knowledge_base.kb_manager import KnowledgeBaseManager

# 初始化知識庫（會執行ALTER TABLE）
kb = KnowledgeBaseManager()

# 查詢papers表結構
conn = sqlite3.connect(kb.db_path)
cursor = conn.cursor()

print("📊 Papers表結構:\n")
cursor.execute("PRAGMA table_info(papers)")
columns = cursor.fetchall()

for col in columns:
    cid, name, type_, not_null, default, pk = col
    print(f"   [{cid}] {name:15} {type_:10} ", end="")
    if pk:
        print("PRIMARY KEY", end="")
    if not_null:
        print(" NOT NULL", end="")
    if default:
        print(f" DEFAULT {default}", end="")
    print()

print(f"\n   總欄位數: {len(columns)}")

# 查詢索引
print("\n📑 索引:")
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='papers'")
indexes = cursor.fetchall()

for idx_name, idx_sql in indexes:
    if idx_sql:  # 跳過自動創建的索引
        print(f"\n   {idx_name}:")
        print(f"   {idx_sql}")

conn.close()

print("\n✅ 數據庫schema檢查完成！")
