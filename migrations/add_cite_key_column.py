#!/usr/bin/env python3
"""
數據庫遷移：為 papers 表添加 cite_key 欄位

Purpose:
- 添加 cite_key 欄位（UNIQUE）用於論文精確匹配
- 創建索引優化查詢性能
- 從 BibTeX 文件填充 cite_key
- 使用 cite_key 替代 zotero_key 作為主要識別符

Background:
- zotero_key: Zotero內部ID（格式: ABCD1234）
- cite_key: BibTeX引用鍵（格式: Author2024a，可讀性高）
- cite_key 更適合用於 Zettelkasten 卡片關聯

Usage:
    python migrations/add_cite_key_column.py

Author: Claude Code (Sonnet 4.5)
Date: 2025-10-30
"""

import sys
import sqlite3
from pathlib import Path

# 添加項目根目錄到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.bibtex_parser import BibTeXParser


def add_cite_key_column(db_path: str = "knowledge_base/index.db") -> bool:
    """
    為 papers 表添加 cite_key 欄位

    Args:
        db_path: 數據庫文件路徑

    Returns:
        成功返回 True
    """
    print("=" * 70)
    print("數據庫遷移：添加 cite_key 欄位")
    print("=" * 70)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 檢查欄位是否已存在
        cursor.execute("PRAGMA table_info(papers)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'cite_key' in columns:
            print("\n[SKIP] cite_key 欄位已存在，跳過創建")
            return True

        # 添加欄位（不加 UNIQUE，SQLite 限制）
        print("\n[CREATE] 添加 cite_key 欄位...")
        cursor.execute("""
            ALTER TABLE papers
            ADD COLUMN cite_key TEXT
        """)

        # 創建 UNIQUE 索引（實現 UNIQUE 約束）
        print("[CREATE] 創建 UNIQUE 索引...")
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_papers_cite_key
            ON papers(cite_key)
        """)

        conn.commit()
        print("[OK] cite_key 欄位和索引創建成功")

        return True

    except Exception as e:
        print(f"[ERROR] 遷移失敗: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def populate_cite_keys_from_bibtex(
    db_path: str = "knowledge_base/index.db",
    bib_file: str = r"D:\core\research\Program_verse\+\My Library.bib"
) -> dict:
    """
    從 BibTeX 文件填充 cite_key

    Args:
        db_path: 數據庫文件路徑
        bib_file: BibTeX 文件路徑

    Returns:
        統計結果字典
    """
    print("\n" + "=" * 70)
    print("填充 cite_key 欄位（從 BibTeX）")
    print("=" * 70)

    stats = {
        'total_papers': 0,
        'matched': 0,
        'unmatched': 0,
        'updated': 0
    }

    # 檢查 BibTeX 文件是否存在
    if not Path(bib_file).exists():
        print(f"\n[SKIP] BibTeX 文件不存在: {bib_file}")
        print("跳過 cite_key 填充")
        return stats

    # 解析 BibTeX 文件
    print(f"\n[PARSE] 解析 BibTeX 文件: {bib_file}")
    parser = BibTeXParser()
    entries = parser.parse_file(bib_file)
    print(f"[OK] 找到 {len(entries)} 個 BibTeX 條目")

    # 建立 cite_key 映射（標題 → cite_key）
    print("\n[BUILD] 建立 cite_key 映射...")
    title_to_cite_key = {}
    for entry in entries:
        if entry.title:
            # 清理標題（移除多餘空白）
            clean_title = ' '.join(entry.title.lower().split())
            title_to_cite_key[clean_title] = entry.cite_key

    print(f"[OK] 建立 {len(title_to_cite_key)} 個標題映射")

    # 連接數據庫並更新
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 獲取所有論文
        cursor.execute("""
            SELECT id, title, cite_key
            FROM papers
        """)
        papers = cursor.fetchall()
        stats['total_papers'] = len(papers)

        print(f"\n[UPDATE] 更新 {len(papers)} 篇論文的 cite_key...")

        for paper_id, title, existing_cite_key in papers:
            if existing_cite_key:
                # 已有 cite_key，跳過
                continue

            if not title:
                # 無標題，跳過
                stats['unmatched'] += 1
                continue

            # 清理標題進行匹配
            clean_title = ' '.join(title.lower().split())

            # 查找匹配的 cite_key
            if clean_title in title_to_cite_key:
                cite_key = title_to_cite_key[clean_title]

                # 更新數據庫
                try:
                    cursor.execute("""
                        UPDATE papers
                        SET cite_key = ?
                        WHERE id = ?
                    """, (cite_key, paper_id))

                    stats['matched'] += 1
                    stats['updated'] += 1

                    print(f"  [{paper_id}] {title[:50]}... → {cite_key}")

                except sqlite3.IntegrityError:
                    # cite_key 重複，跳過
                    print(f"  [WARNING] [{paper_id}] cite_key 重複: {cite_key}")
                    stats['unmatched'] += 1

            else:
                stats['unmatched'] += 1

        conn.commit()

        # 顯示統計
        print("\n" + "=" * 70)
        print("[STATS] 填充統計")
        print("=" * 70)
        print(f"總論文數: {stats['total_papers']}")
        print(f"成功匹配: {stats['matched']} ({stats['matched']/stats['total_papers']*100:.1f}%)")
        print(f"未匹配: {stats['unmatched']}")
        print(f"已更新: {stats['updated']}")

        return stats

    except Exception as e:
        print(f"\n[ERROR] 填充失敗: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return stats

    finally:
        conn.close()


def verify_migration(db_path: str = "knowledge_base/index.db"):
    """
    驗證遷移結果

    Args:
        db_path: 數據庫文件路徑
    """
    print("\n" + "=" * 70)
    print("[VERIFY] 驗證遷移結果")
    print("=" * 70)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 檢查欄位
        cursor.execute("PRAGMA table_info(papers)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'cite_key' in columns:
            print("[OK] cite_key 欄位存在")
        else:
            print("[ERROR] cite_key 欄位不存在")
            return False

        # 檢查索引
        cursor.execute("PRAGMA index_list(papers)")
        indexes = [row[1] for row in cursor.fetchall()]

        if 'idx_papers_cite_key' in indexes:
            print("[OK] cite_key 索引存在")
        else:
            print("[ERROR] cite_key 索引不存在")

        # 統計填充率
        cursor.execute("SELECT COUNT(*) FROM papers")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM papers WHERE cite_key IS NOT NULL")
        filled = cursor.fetchone()[0]

        print(f"\n[STATS] cite_key 填充率: {filled}/{total} ({filled/total*100:.1f}%)")

        # 顯示範例
        cursor.execute("""
            SELECT id, title, cite_key
            FROM papers
            WHERE cite_key IS NOT NULL
            LIMIT 5
        """)

        print("\n[EXAMPLES] 範例（前5筆）:")
        for paper_id, title, cite_key in cursor.fetchall():
            print(f"  [{paper_id}] {cite_key} - {title[:50]}...")

        return True

    except Exception as e:
        print(f"[ERROR] 驗證失敗: {e}")
        return False

    finally:
        conn.close()


def main():
    """主流程"""
    print("\n[START] 開始數據庫遷移")
    print(f"時間: 2025-10-30")
    print()

    # Step 1: 添加 cite_key 欄位
    success = add_cite_key_column()
    if not success:
        print("\n[ERROR] 遷移失敗")
        return 1

    # Step 2: 從 BibTeX 填充 cite_key
    stats = populate_cite_keys_from_bibtex()

    # Step 3: 驗證遷移結果
    verify_migration()

    # 總結
    print("\n" + "=" * 70)
    print("[SUCCESS] 數據庫遷移完成")
    print("=" * 70)

    if stats['matched'] == 0:
        print("\n[WARNING] 沒有論文成功匹配 cite_key")
        print("可能原因:")
        print("  1. BibTeX 文件路徑不正確")
        print("  2. 標題格式不匹配")
        print("  3. BibTeX 文件中沒有對應的論文")
        print("\n建議: 檢查 BibTeX 文件路徑和內容")

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] 遷移被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] 遷移失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
