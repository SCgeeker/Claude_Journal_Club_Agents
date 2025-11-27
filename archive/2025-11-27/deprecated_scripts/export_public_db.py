#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
導出公開數據庫（只包含 public=1 的論文及其相關數據）
"""

import sys
import io
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# 強制 UTF-8 輸出（Windows 相容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

def export_public_database(output_path: str = None) -> bool:
    """
    導出公開數據庫，只包含 public=1 的論文及其關聯數據

    Args:
        output_path: 輸出路徑（默認：knowledge_base/index_public.db）

    Returns:
        bool: 是否成功
    """

    source_db = Path('knowledge_base/index.db')
    if output_path is None:
        output_path = Path('knowledge_base/index_public.db')
    else:
        output_path = Path(output_path)

    if not source_db.exists():
        print(f"❌ 源數據庫不存在: {source_db}")
        return False

    # 備份舊的公開數據庫
    if output_path.exists():
        backup_path = output_path.with_suffix(f'.backup_{datetime.now():%Y%m%d_%H%M%S}.db')
        print(f"📦 備份舊數據庫: {backup_path.name}")
        shutil.copy2(output_path, backup_path)
        output_path.unlink()

    # 複製完整數據庫
    print(f"\n[1/4] 複製源數據庫...")
    shutil.copy2(source_db, output_path)
    print(f"  ✅ 已複製到: {output_path}")

    # 連接到新數據庫並刪除非公開數據
    conn = sqlite3.connect(output_path)
    cursor = conn.cursor()

    try:
        # 1. 獲取非公開論文ID列表
        print("\n[2/4] 識別非公開論文...")
        cursor.execute('''
            SELECT id, title
            FROM papers
            WHERE public = 0 OR public IS NULL
        ''')
        embargo_papers = cursor.fetchall()
        embargo_ids = [p[0] for p in embargo_papers]

        print(f"  找到 {len(embargo_papers)} 篇 embargo 論文:")
        for paper_id, title in embargo_papers:
            print(f"    - Paper {paper_id}: {title[:50]}")

        if embargo_ids:
            # 2. 刪除關聯的 Zettelkasten 卡片
            print("\n[3/4] 刪除 embargo 論文的關聯數據...")

            placeholders = ','.join('?' for _ in embargo_ids)

            # 2a. 獲取要刪除的卡片數量
            cursor.execute(f'''
                SELECT COUNT(*), GROUP_CONCAT(zettel_id, ', ')
                FROM zettel_cards
                WHERE paper_id IN ({placeholders})
            ''', embargo_ids)
            count_result = cursor.fetchone()
            card_count = count_result[0] if count_result[0] else 0

            print(f"  - 找到 {card_count} 張關聯卡片")

            # 2b. 刪除 paper_zettel_links (如果有使用)
            cursor.execute(f'''
                DELETE FROM paper_zettel_links
                WHERE paper_id IN ({placeholders})
            ''', embargo_ids)
            if cursor.rowcount > 0:
                print(f"  ✅ 刪除 {cursor.rowcount} 條 paper_zettel_links")

            # 2c. 刪除 zettel_cards
            cursor.execute(f'''
                DELETE FROM zettel_cards
                WHERE paper_id IN ({placeholders})
            ''', embargo_ids)
            print(f"  ✅ 刪除 {cursor.rowcount} 張 zettel_cards")

            # 2d. 刪除 paper_topics
            cursor.execute(f'''
                DELETE FROM paper_topics
                WHERE paper_id IN ({placeholders})
            ''', embargo_ids)
            print(f"  ✅ 刪除 {cursor.rowcount} 條 paper_topics")

            # 2e. 刪除 citations
            cursor.execute(f'''
                DELETE FROM citations
                WHERE citing_paper_id IN ({placeholders})
                   OR cited_paper_id IN ({placeholders})
            ''', embargo_ids + embargo_ids)
            print(f"  ✅ 刪除 {cursor.rowcount} 條 citations")

            # 3. 刪除 papers 表中的 embargo 論文
            cursor.execute(f'''
                DELETE FROM papers
                WHERE id IN ({placeholders})
            ''', embargo_ids)
            print(f"  ✅ 刪除 {cursor.rowcount} 篇論文")
        else:
            print("\n[3/4] 無需刪除，所有論文皆為公開")

        # 4. 驗證結果
        print("\n[4/4] 驗證公開數據庫...")
        cursor.execute('SELECT COUNT(*) FROM papers')
        paper_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM zettel_cards')
        card_count = cursor.fetchone()[0]

        cursor.execute('''
            SELECT id, title, public
            FROM papers
            ORDER BY id
        ''')
        public_papers = cursor.fetchall()

        print(f"\n📊 公開數據庫統計:")
        print(f"  - 論文數: {paper_count}")
        print(f"  - Zettelkasten 卡片數: {card_count}")
        print(f"\n公開論文列表:")
        for paper_id, title, is_public in public_papers:
            print(f"  ✅ Paper {paper_id}: {title[:60]}")

        # 提交變更
        conn.commit()
        print(f"\n✅ 公開數據庫導出成功: {output_path}")
        print(f"   大小: {output_path.stat().st_size / 1024:.1f} KB")

        return True

    except sqlite3.Error as e:
        print(f"\n❌ 數據庫錯誤: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="導出公開數據庫（僅包含 public=1 的論文）")
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='輸出路徑（默認：knowledge_base/index_public.db）'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("導出公開數據庫（Public Examples）")
    print("=" * 80)

    success = export_public_database(output_path=args.output)

    if success:
        print("\n🎉 完成！")
        print("\n下一步:")
        print("  1. 檢查公開數據庫: python check_db.py")
        print("  2. 更新 .gitignore（排除完整數據庫 index.db）")
        print("  3. 提交到 git（只包含 index_public.db）")
        print("  4. 未來匯入的論文將默認為 embargo（public=0）")
    else:
        print("\n❌ 失敗，請檢查錯誤訊息")

    sys.exit(0 if success else 1)
