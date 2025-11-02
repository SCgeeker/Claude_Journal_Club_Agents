#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理資料庫中檔案不存在的論文記錄
"""

import sqlite3
import sys
import io
from pathlib import Path

# Windows UTF-8 支援
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def find_orphan_records(db_path: str = "knowledge_base/index.db"):
    """找出檔案不存在的論文記錄"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, file_path FROM papers")
    papers = cursor.fetchall()

    orphans = []
    for pid, title, file_path in papers:
        if not Path(file_path).exists():
            orphans.append((pid, title, file_path))

    conn.close()
    return orphans

def delete_orphan_records(orphan_ids: list, db_path: str = "knowledge_base/index.db", dry_run: bool = False):
    """刪除孤立記錄"""

    if dry_run:
        print("⚠️ 預覽模式（不會實際刪除）\n")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for pid in orphan_ids:
        if not dry_run:
            cursor.execute("DELETE FROM papers WHERE id = ?", (pid,))
            cursor.execute("DELETE FROM paper_topics WHERE paper_id = ?", (pid,))

    if not dry_run:
        conn.commit()

    conn.close()

def main():
    import argparse

    parser = argparse.ArgumentParser(description="清理檔案不存在的論文記錄")
    parser.add_argument('--list', action='store_true', help='列出孤立記錄')
    parser.add_argument('--delete', action='store_true', help='刪除孤立記錄')
    parser.add_argument('--dry-run', action='store_true', help='預覽模式')

    args = parser.parse_args()

    orphans = find_orphan_records()

    print(f"找到 {len(orphans)} 筆孤立記錄")
    print("=" * 80)

    if not orphans:
        print("資料庫與檔案完全一致！")
        return

    for pid, title, file_path in orphans:
        print(f"ID {pid}: {title[:60]}")
        print(f"  檔案: {file_path}")
        print()

    if args.delete:
        print("=" * 80)
        orphan_ids = [o[0] for o in orphans]
        delete_orphan_records(orphan_ids, dry_run=args.dry_run)

        if not args.dry_run:
            print(f"✅ 已刪除 {len(orphan_ids)} 筆記錄")
        else:
            print(f"預覽: 將刪除 {len(orphan_ids)} 筆記錄")

if __name__ == "__main__":
    main()
