#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan B Migration Script: content → ai_notes + human_notes

This script migrates Zettelkasten cards from the mixed content model
to the separated model with dedicated ai_notes and human_notes fields.

Author: Claude Code Agent
Date: 2025-11-05
Phase: 2.1 System Testing - Day 3
"""

import sys
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# UTF-8 encoding for Windows (safer approach)
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from src.utils.content_filter import extract_ai_content, get_human_notes


class PlanBMigrator:
    """Migrate zettel_cards from content → ai_notes + human_notes"""

    def __init__(self, db_path: str = "knowledge_base/index.db"):
        """
        Initialize migrator

        Args:
            db_path: Path to knowledge base database
        """
        self.db_path = db_path
        self.conn = None

        # Statistics
        self.total_cards = 0
        self.migrated_cards = 0
        self.cards_with_ai_only = 0
        self.cards_with_human = 0
        self.failed_cards = []

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()

    def verify_schema(self) -> bool:
        """
        Verify that ai_notes and human_notes fields exist

        Returns:
            True if schema is correct
        """
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(zettel_cards)")
        columns = {row['name'] for row in cursor.fetchall()}

        required = {'ai_notes', 'human_notes', 'content'}
        missing = required - columns

        if missing:
            print(f"❌ 缺少欄位: {missing}")
            return False

        return True

    def preview_migration(self, limit: int = 5) -> List[Dict]:
        """
        Preview migration for a few cards

        Args:
            limit: Number of cards to preview

        Returns:
            List of preview results
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT zettel_id, content
            FROM zettel_cards
            LIMIT ?
        """, (limit,))

        previews = []
        for row in cursor.fetchall():
            zettel_id = row['zettel_id']
            content = row['content']

            ai_content = extract_ai_content(content)
            human_content = get_human_notes(content)

            previews.append({
                'zettel_id': zettel_id,
                'original_length': len(content),
                'ai_length': len(ai_content) if ai_content else 0,
                'human_length': len(human_content) if human_content else 0,
                'has_human': human_content is not None
            })

        return previews

    def migrate_all_cards(self, dry_run: bool = False) -> Dict:
        """
        Migrate all cards from content to ai_notes + human_notes

        Args:
            dry_run: If True, only simulate without writing

        Returns:
            Migration statistics
        """
        print("\n" + "=" * 70)
        print("🚀 開始遷移 Zettelkasten 卡片")
        print("=" * 70)

        if dry_run:
            print("⚠️  DRY RUN 模式：不會修改資料庫")
            print()

        # Get all cards
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT card_id, zettel_id, content, ai_notes, human_notes
            FROM zettel_cards
        """)
        cards = cursor.fetchall()

        self.total_cards = len(cards)
        print(f"找到 {self.total_cards} 張卡片\n")

        # Migrate each card
        for i, card in enumerate(cards, 1):
            card_id = card['card_id']
            zettel_id = card['zettel_id']
            content = card['content']
            existing_ai = card['ai_notes']
            existing_human = card['human_notes']

            # Skip if already migrated (ai_notes is not NULL)
            if existing_ai is not None:
                print(f"  [{i}/{self.total_cards}] ⏭️  {zettel_id} - 已遷移，跳過")
                continue

            # Extract AI and human content
            try:
                ai_content = extract_ai_content(content)
                human_content = get_human_notes(content)

                # Update statistics
                self.migrated_cards += 1
                if human_content:
                    self.cards_with_human += 1
                else:
                    self.cards_with_ai_only += 1

                # Update database (if not dry run)
                if not dry_run:
                    cursor.execute("""
                        UPDATE zettel_cards
                        SET ai_notes = ?,
                            human_notes = ?
                        WHERE card_id = ?
                    """, (ai_content, human_content, card_id))

                # Progress indicator
                status = "👤" if human_content else "🤖"
                print(f"  [{i}/{self.total_cards}] {status} {zettel_id} - "
                      f"AI: {len(ai_content)} 字元, "
                      f"Human: {len(human_content) if human_content else 0} 字元")

            except Exception as e:
                print(f"  [{i}/{self.total_cards}] ❌ {zettel_id} - 錯誤: {e}")
                self.failed_cards.append({
                    'zettel_id': zettel_id,
                    'error': str(e)
                })

        # Commit changes
        if not dry_run:
            self.conn.commit()
            print("\n✅ 資料庫已更新")
        else:
            print("\n⚠️  DRY RUN：未修改資料庫")

        return self.get_statistics()

    def verify_migration(self) -> Dict:
        """
        Verify migration success

        Returns:
            Verification results
        """
        cursor = self.conn.cursor()

        # Count cards with ai_notes populated
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM zettel_cards
            WHERE ai_notes IS NOT NULL AND ai_notes != ''
        """)
        ai_populated = cursor.fetchone()['count']

        # Count cards with human_notes populated
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM zettel_cards
            WHERE human_notes IS NOT NULL AND human_notes != ''
        """)
        human_populated = cursor.fetchone()['count']

        # Count cards still with NULL ai_notes
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM zettel_cards
            WHERE ai_notes IS NULL
        """)
        null_ai = cursor.fetchone()['count']

        return {
            'ai_populated': ai_populated,
            'human_populated': human_populated,
            'null_ai': null_ai,
            'success_rate': (ai_populated / self.total_cards * 100) if self.total_cards > 0 else 0
        }

    def get_statistics(self) -> Dict:
        """Get migration statistics"""
        return {
            'total_cards': self.total_cards,
            'migrated_cards': self.migrated_cards,
            'cards_with_ai_only': self.cards_with_ai_only,
            'cards_with_human': self.cards_with_human,
            'failed_cards': len(self.failed_cards),
            'failed_details': self.failed_cards
        }

    def print_report(self, stats: Dict):
        """Print migration report"""
        print("\n" + "=" * 70)
        print("📊 遷移報告")
        print("=" * 70)

        print(f"\n總卡片數: {stats['total_cards']}")
        print(f"已遷移: {stats['migrated_cards']}")
        print(f"  - 僅 AI 內容: {stats['cards_with_ai_only']}")
        print(f"  - 包含人類筆記: {stats['cards_with_human']}")
        print(f"失敗: {stats['failed_cards']}")

        if stats['failed_details']:
            print("\n失敗詳情:")
            for fail in stats['failed_details']:
                print(f"  - {fail['zettel_id']}: {fail['error']}")

        # Verification
        if self.conn:
            verify = self.verify_migration()
            print(f"\n驗證結果:")
            print(f"  - ai_notes 已填充: {verify['ai_populated']}")
            print(f"  - human_notes 已填充: {verify['human_populated']}")
            print(f"  - ai_notes 仍為 NULL: {verify['null_ai']}")
            print(f"  - 成功率: {verify['success_rate']:.1f}%")

            if verify['null_ai'] > 0:
                print(f"\n⚠️  警告: {verify['null_ai']} 張卡片的 ai_notes 仍為 NULL")
            else:
                print("\n✅ 所有卡片遷移成功！")


def main():
    """Main migration script"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate zettel_cards from content to ai_notes + human_notes"
    )

    parser.add_argument(
        "--db-path",
        default="knowledge_base/index.db",
        help="Path to knowledge base database"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate migration without writing to database"
    )

    parser.add_argument(
        "--preview",
        type=int,
        metavar="N",
        help="Preview N cards before migration"
    )

    args = parser.parse_args()

    # Initialize migrator
    migrator = PlanBMigrator(args.db_path)

    try:
        # Connect
        migrator.connect()

        # Verify schema
        print("檢查資料庫結構...")
        if not migrator.verify_schema():
            print("❌ 資料庫結構不正確，中止遷移")
            return 1
        print("✅ 資料庫結構正確\n")

        # Preview (if requested)
        if args.preview:
            print(f"預覽前 {args.preview} 張卡片:")
            print("-" * 70)
            previews = migrator.preview_migration(args.preview)
            for p in previews:
                status = "👤" if p['has_human'] else "🤖"
                print(f"{status} {p['zettel_id']}: "
                      f"{p['original_length']} → "
                      f"AI {p['ai_length']} + Human {p['human_length']}")
            print()

            confirm = input("是否繼續完整遷移？(y/n): ")
            if confirm.lower() != 'y':
                print("已取消")
                return 0

        # Migrate
        stats = migrator.migrate_all_cards(dry_run=args.dry_run)

        # Print report
        migrator.print_report(stats)

        if stats['failed_cards'] > 0:
            return 1

        return 0

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        migrator.disconnect()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷")
        sys.exit(1)
