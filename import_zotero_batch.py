#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero 批量導入工具
使用 ZoteroSync 框架將 Zotero 論文批量導入知識庫
"""

import sys
import io
import json
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime

# 修復 Windows 終端 UTF-8 編碼
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 導入 ZoteroSync
try:
    from src.integrations.zotero_sync import ZoteroSync, SyncResult
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from src.integrations.zotero_sync import ZoteroSync, SyncResult


class ZoteroImporter:
    """Zotero 批量導入管理器"""

    def __init__(self, kb_path: str = "knowledge_base"):
        """
        初始化導入器

        Args:
            kb_path: 知識庫路徑
        """
        self.kb_path = Path(kb_path)
        self.db_path = self.kb_path / "index.db"
        self.sync = ZoteroSync(kb_path=kb_path)

    def import_batch(
        self,
        bib_file: str,
        batch_name: str = "batch_1",
        conflict_strategy: str = 'skip',
        dry_run: bool = False,
        update_kb: bool = True
    ) -> SyncResult:
        """
        執行批量導入

        Args:
            bib_file: Zotero BibTeX 文件
            batch_name: 批次名稱
            conflict_strategy: 衝突解決策略
            dry_run: 模擬運行
            update_kb: 是否實際更新知識庫

        Returns:
            SyncResult 對象
        """
        print(f"\n{'=' * 70}")
        print(f"📦 Zotero 批量導入 - {batch_name}")
        print(f"{'=' * 70}")

        # 執行同步
        result = self.sync.sync(
            bib_file=bib_file,
            conflict_strategy=conflict_strategy,
            dry_run=dry_run or not update_kb,
            output_file=f"output/{batch_name}_sync_result.json"
        )

        # 如果不是 dry_run，更新知識庫
        if update_kb and not dry_run:
            self._update_knowledge_base(result, batch_name)

        # 生成批次報告
        self._generate_batch_report(result, batch_name)

        return result

    def _update_knowledge_base(self, result: SyncResult, batch_name: str):
        """將同步結果導入知識庫"""
        print(f"\n📥 更新知識庫...")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            imported_count = 0

            for paper in result.import_list:
                try:
                    # 生成虛擬文件路徑
                    cite_key = paper.get('cite_key', paper.get('title', '').replace(' ', '_')[:20])
                    file_path = f"zotero_sync/{cite_key}.md"

                    # 插入或更新論文
                    cursor.execute("""
                        INSERT INTO papers (
                            file_path, title, authors, year, abstract, keywords,
                            source, doi, url, cite_key,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file_path,
                        paper.get('title'),
                        json.dumps(paper.get('authors', [])) if paper.get('authors') else None,
                        paper.get('year'),
                        paper.get('abstract'),
                        json.dumps(paper.get('keywords', [])) if paper.get('keywords') else None,
                        paper.get('source', 'zotero_sync'),
                        paper.get('doi'),
                        paper.get('url'),
                        cite_key,
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))

                    imported_count += 1

                except Exception as e:
                    print(f"   ⚠️  無法導入 {paper.get('title', 'Unknown')}: {e}")
                    continue

            conn.commit()
            conn.close()

            print(f"✅ 成功導入 {imported_count} 篇論文到知識庫")

        except Exception as e:
            print(f"❌ 知識庫更新失敗: {e}")
            raise

    def _generate_batch_report(self, result: SyncResult, batch_name: str):
        """生成批次報告"""
        report_path = Path("output") / f"{batch_name}_report.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Zotero 批量導入報告 - {batch_name}\n")
            f.write("=" * 60 + "\n")
            f.write(f"時間戳: {result.timestamp}\n\n")

            f.write("📊 統計:\n")
            f.write(f"  - BibTeX 條目總數: {result.total_bibtex_entries}\n")
            f.write(f"  - 成功導入: {result.successful_imports}\n")
            f.write(f"  - 跳過（重複）: {result.skipped_duplicates}\n")
            f.write(f"  - 導入失敗: {len(result.errors)}\n")
            f.write(f"  - 衝突數: {len(result.conflicts)}\n\n")

            if result.errors:
                f.write("❌ 導入失敗列表:\n")
                for cite_key, error_msg in result.errors:
                    f.write(f"  - {cite_key}: {error_msg}\n")
                f.write("\n")

            f.write(f"✅ 成功導入論文清單 ({result.successful_imports} 篇):\n")
            for i, paper in enumerate(result.import_list, 1):
                f.write(f"  [{i}] {paper.get('title', 'Unknown')}\n")
                if paper.get('authors'):
                    authors_str = '; '.join(paper['authors'][:3])
                    f.write(f"      作者: {authors_str}\n")
                if paper.get('year'):
                    f.write(f"      年份: {paper['year']}\n")
                f.write("\n")

        print(f"📄 報告已保存: {report_path}")


def main():
    """主程序"""
    parser = argparse.ArgumentParser(
        description='Zotero 批量導入工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例使用:
  # Batch B1 導入（前 40 篇）
  python import_zotero_batch.py --batch B1 \\
    --bib-file "D:\\zotero\\My Library.bib" \\
    --strategy skip

  # 模擬運行（驗證但不導入）
  python import_zotero_batch.py --batch B1 \\
    --bib-file "D:\\zotero\\My Library.bib" \\
    --dry-run
        """
    )

    parser.add_argument(
        '--batch',
        default='batch_1',
        help='批次名稱 (預設: batch_1)'
    )
    parser.add_argument(
        '--bib-file',
        required=True,
        help='Zotero 導出的 .bib 文件路徑'
    )
    parser.add_argument(
        '--kb-path',
        default='knowledge_base',
        help='知識庫路徑 (預設: knowledge_base)'
    )
    parser.add_argument(
        '--strategy',
        choices=['skip', 'replace', 'merge'],
        default='skip',
        help='衝突解決策略 (預設: skip)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='模擬運行（驗證但不導入到知識庫）'
    )
    parser.add_argument(
        '--no-update-kb',
        action='store_true',
        help='只生成導入清單，不更新知識庫'
    )

    args = parser.parse_args()

    try:
        importer = ZoteroImporter(kb_path=args.kb_path)

        result = importer.import_batch(
            bib_file=args.bib_file,
            batch_name=args.batch,
            conflict_strategy=args.strategy,
            dry_run=args.dry_run,
            update_kb=not args.no_update_kb
        )

        # 打印最終統計
        print(f"\n{'=' * 70}")
        print(f"✅ 批量導入完成")
        print(f"{'=' * 70}")
        print(f"成功導入: {result.successful_imports}/{result.total_bibtex_entries}")
        print(f"成功率: {result.successful_imports/result.total_bibtex_entries*100:.1f}%")

        return 0 if result.successful_imports > 0 else 1

    except Exception as e:
        print(f"\n❌ 導入失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
