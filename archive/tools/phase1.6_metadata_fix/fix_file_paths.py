#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復知識庫中檔案路徑不一致的問題
"""

import sqlite3
import sys
import io
from pathlib import Path
from difflib import SequenceMatcher

# Windows UTF-8 支援
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def find_best_match(title: str, files: list) -> Path:
    """根據標題找到最佳匹配的檔案"""
    best_match = None
    best_score = 0

    for file_path in files:
        # 移除副檔名和底線，轉小寫比較
        file_stem = file_path.stem.replace('_', ' ').replace('-', ' ').lower()
        title_clean = title.replace('_', ' ').lower()

        # 計算相似度
        score = SequenceMatcher(None, title_clean, file_stem).ratio()

        if score > best_score:
            best_score = score
            best_match = file_path

    return best_match if best_score > 0.5 else None

def fix_file_paths(db_path: str = "knowledge_base/index.db"):
    """修復所有檔案路徑"""

    # 獲取所有實際存在的 Markdown 檔案
    papers_dir = Path("knowledge_base/papers")
    actual_files = list(papers_dir.glob("*.md"))

    print(f"找到 {len(actual_files)} 個實際檔案")
    print()

    # 連接資料庫
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 獲取所有論文
    cursor.execute("SELECT id, title, file_path FROM papers")
    papers = cursor.fetchall()

    fixed_count = 0
    skipped_count = 0

    for pid, title, db_path_str in papers:
        db_path = Path(db_path_str)

        # 檢查檔案是否存在
        if db_path.exists():
            print(f"[OK] ID {pid}: {db_path.name}")
            skipped_count += 1
            continue

        # 找到最佳匹配的檔案
        matched_file = find_best_match(title, actual_files)

        if matched_file:
            new_path = str(matched_file)
            cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (new_path, pid))
            print(f"[FIXED] ID {pid}: {title[:40]}")
            print(f"  舊路徑: {db_path.name}")
            print(f"  新路徑: {matched_file.name}")
            print()
            fixed_count += 1
        else:
            print(f"[WARNING] ID {pid}: 找不到匹配檔案")
            print(f"  標題: {title}")
            print()

    conn.commit()
    conn.close()

    print("=" * 80)
    print(f"修復完成:")
    print(f"  修復: {fixed_count}")
    print(f"  跳過: {skipped_count}")
    print(f"  總計: {len(papers)}")

if __name__ == "__main__":
    fix_file_paths()
