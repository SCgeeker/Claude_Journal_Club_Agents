#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加 public 欄位到 papers 表，並標記當前 6 篇論文為公開範例
"""

import sys
import io
import sqlite3
from pathlib import Path

# 強制 UTF-8 輸出（Windows 相容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

def add_public_column():
    """添加 public 欄位並標記範例論文"""

    db_path = Path('knowledge_base/index.db')

    if not db_path.exists():
        print(f"❌ 數據庫不存在: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Step 1: 檢查 public 欄位是否已存在
        cursor.execute("PRAGMA table_info(papers)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'public' in columns:
            print("ℹ️  'public' 欄位已存在，跳過添加")
        else:
            # Step 2: 添加 public 欄位
            print("\n[1/3] 添加 'public' 欄位到 papers 表...")
            cursor.execute('''
                ALTER TABLE papers
                ADD COLUMN public INTEGER DEFAULT 0
            ''')
            print("  ✅ 欄位添加成功")

        # Step 3: 查詢當前論文
        print("\n[2/3] 查詢當前論文...")
        cursor.execute('''
            SELECT id, title, cite_key
            FROM papers
            ORDER BY id
        ''')
        papers = cursor.fetchall()

        print(f"  找到 {len(papers)} 篇論文:")
        for paper_id, title, cite_key in papers:
            print(f"    - Paper {paper_id}: {cite_key or 'N/A'} - {title[:50]}")

        # Step 4: 標記前 6 篇為公開
        if len(papers) >= 6:
            print("\n[3/3] 標記前 6 篇論文為公開範例...")
            cursor.execute('''
                UPDATE papers
                SET public = 1
                WHERE id IN (1, 2, 3, 4, 5, 6)
            ''')

            affected = cursor.rowcount
            print(f"  ✅ 已標記 {affected} 篇論文為公開（public=1）")

            # 驗證
            cursor.execute('''
                SELECT id, cite_key, title, public
                FROM papers
                ORDER BY id
            ''')
            all_papers = cursor.fetchall()

            print("\n📊 論文狀態:")
            print("=" * 80)
            for paper_id, cite_key, title, is_public in all_papers:
                status = "🌐 公開" if is_public else "🔒 Embargo"
                print(f"  {status} | Paper {paper_id} | {cite_key or 'N/A':20s} | {title[:40]}")
            print("=" * 80)
        else:
            print(f"\n⚠️  警告: 只有 {len(papers)} 篇論文，少於 6 篇")

        # 提交變更
        conn.commit()
        print("\n✅ 數據庫修改成功！")

        return True

    except sqlite3.Error as e:
        print(f"\n❌ 數據庫錯誤: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 80)
    print("添加 Public 標記到知識庫")
    print("=" * 80)

    success = add_public_column()

    if success:
        print("\n🎉 完成！當前 6 篇論文已設為公開範例")
        print("\n下一步:")
        print("  1. 檢查論文狀態: python check_db.py")
        print("  2. 導出公開數據庫: python export_public_db.py")
        print("  3. 之後匯入的論文將默認為 embargo (public=0)")
    else:
        print("\n❌ 失敗，請檢查錯誤訊息")
