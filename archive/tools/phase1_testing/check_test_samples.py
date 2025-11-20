#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查測試樣本"""

import sys
import io
import sqlite3
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()

# 1. 檢查低質量論文
cursor.execute('''
    SELECT id, title, file_path, keywords, abstract
    FROM papers
    WHERE (keywords IS NULL OR keywords = "[]")
       OR (abstract IS NULL OR abstract = "None" OR LENGTH(abstract) < 50)
    LIMIT 10
''')

papers = cursor.fetchall()

print(f"📊 低質量論文（可用於測試 metadata-fix）: {len(papers)} 篇\n")
print("=" * 60)

for p in papers:
    paper_id, title, file_path, keywords, abstract = p

    print(f"\nID {paper_id}: {title[:50]}")
    print(f"  檔案: {Path(file_path).name}")
    print(f"  關鍵詞: {keywords if keywords and keywords != '[]' else '❌ 缺失'}")

    if not abstract or abstract == 'None' or len(abstract) < 50:
        print(f"  摘要: ❌ 缺失或過短 ({len(abstract) if abstract and abstract != 'None' else 0} 字元)")
    else:
        print(f"  摘要: ✅ {len(abstract)} 字元")

# 2. 檢查是否有未記錄的 Markdown
print(f"\n\n{'=' * 60}")
print("📥 檢查未記錄的 Markdown 檔案")
print("=" * 60)

actual_files = set(f.name for f in Path("knowledge_base/papers").glob("*.md"))
cursor.execute('SELECT file_path FROM papers')
db_files = set(Path(row[0]).name for row in cursor.fetchall())

unrecorded = actual_files - db_files

if unrecorded:
    print(f"\n找到 {len(unrecorded)} 個未記錄的檔案:")
    for f in sorted(unrecorded)[:5]:
        print(f"  - {f}")
    if len(unrecorded) > 5:
        print(f"  ... 還有 {len(unrecorded) - 5} 個")
else:
    print("\n✅ 沒有未記錄的檔案")

# 3. 檢查孤立記錄
print(f"\n\n{'=' * 60}")
print("🗑️ 檢查孤立記錄")
print("=" * 60)

cursor.execute('SELECT id, title, file_path FROM papers')
all_papers = cursor.fetchall()

orphans = []
for pid, title, file_path in all_papers:
    if not Path(file_path).exists():
        orphans.append((pid, title, file_path))

if orphans:
    print(f"\n找到 {len(orphans)} 筆孤立記錄:")
    for pid, title, file_path in orphans[:5]:
        print(f"  ID {pid}: {title[:50]}")
        print(f"    檔案: {file_path}")
    if len(orphans) > 5:
        print(f"  ... 還有 {len(orphans) - 5} 筆")
else:
    print("\n✅ 沒有孤立記錄")

conn.close()

# 4. 建議測試策略
print(f"\n\n{'=' * 60}")
print("💡 測試建議")
print("=" * 60)

print("""
基於當前狀況，建議以下測試策略:

1. **測試 metadata-fix**（有 26 篇低質量論文）
   ```bash
   # 預覽模式
   python kb_manage.py metadata-fix --field keywords --dry-run

   # 實際執行（修復關鍵詞）
   python kb_manage.py metadata-fix --field keywords --batch

   # 修復所有字段
   python kb_manage.py metadata-fix --field all --batch
   ```

2. **測試 analyze_paper.py --validate**（需要原始 PDF）
   選項 A: 使用外部 PDF
   ```bash
   # 下載一篇新論文 PDF
   python analyze_paper.py new_paper.pdf --validate
   ```

   選項 B: 創建測試樣本（模擬低質量 PDF）
   - 手動修改某篇論文的 Markdown，移除摘要和關鍵詞
   - 重新導入測試

3. **壓力測試 cleanup 和 import-papers**（需要創建樣本）
   ```bash
   # 創建測試樣本:
   # 1. 複製一個 Markdown 檔案，改名為 test_import.md
   # 2. 暫時刪除某篇論文的 Markdown（測試孤立記錄）
   ```

推薦順序:
  1️⃣ 先測試 metadata-fix（有真實樣本）
  2️⃣ 測試 analyze_paper.py --validate（用新 PDF）
  3️⃣ 壓力測試其他功能（創建樣本）
""")
