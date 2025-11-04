#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量为所有论文生成 Zettelkasten 卡片
执行选项 A：为所有 64 篇论文重新生成 Zettel（选项A）
"""

import sqlite3
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json
import time
import os

# 添加 src 到 Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

class ZettelBatchGenerator:
    def __init__(self, db_path: str = "knowledge_base/index.db"):
        self.db_path = Path(db_path)
        self.log_file = Path("batch_zettel_generation.log")
        self.start_time = datetime.now()
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

    def log(self, message: str):
        """记录消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')

    def get_all_papers(self) -> list:
        """获取所有论文信息"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Get papers with existing domain
        cursor.execute("""
            SELECT DISTINCT p.id, p.title, p.cite_key, z.domain
            FROM papers p
            LEFT JOIN zettel_cards z ON p.id = z.paper_id
            ORDER BY p.id
        """)

        papers = []
        seen_ids = set()

        for row in cursor.fetchall():
            pid, title, citekey, domain = row
            if pid not in seen_ids:
                papers.append({
                    'id': pid,
                    'title': title or f"Paper {pid}",
                    'cite_key': citekey or f'paper_{pid}',  # Fixed: use 'cite_key' instead of 'citekey'
                    'domain': domain or 'Research'
                })
                seen_ids.add(pid)

        conn.close()
        return papers

    def generate_zettel_for_paper(self, paper: dict, dry_run: bool = False) -> bool:
        """
        为单篇论文生成 Zettel

        Args:
            paper: 论文信息字典
            dry_run: 是否为模拟运行

        Returns:
            True if successful, False otherwise
        """
        pid = paper['id']
        title = paper['title'][:60]
        domain = paper['domain']

        # 构建命令 (添加 --detail comprehensive 参数)
        cmd = [
            'python',
            'make_slides.py',
            f'"{title}"',
            '--from-kb', str(pid),
            '--style', 'zettelkasten',
            '--domain', domain,
            '--detail', 'comprehensive'
        ]

        cmd_str = ' '.join(cmd)

        if dry_run:
            self.log(f"[DRY RUN] Paper {pid:2d} ({domain:10s}): {cmd_str}")
            return True

        try:
            self.log(f"[{self.stats['success'] + self.stats['failed'] + 1:3d}] "
                    f"Paper {pid:2d} ({domain:10s}): {title}")

            # 设置环境变量确保 src 目录在 PYTHONPATH 中
            env = os.environ.copy()
            src_path = str(project_root / "src")
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = src_path + os.pathsep + env['PYTHONPATH']
            else:
                env['PYTHONPATH'] = src_path

            result = subprocess.run(
                cmd_str,
                shell=True,
                capture_output=True,
                timeout=600,  # 10 minutes per paper
                text=True,
                env=env,
                cwd=str(project_root)  # 确保工作目录正确
            )

            if result.returncode == 0:
                self.log(f"      SUCCESS")
                return True
            else:
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                self.log(f"      FAILED: {error_msg}")
                self.stats['errors'].append({
                    'paper_id': pid,
                    'title': title,
                    'error': error_msg
                })
                return False

        except subprocess.TimeoutExpired:
            self.log(f"      TIMEOUT (exceeded 10 minutes)")
            self.stats['errors'].append({
                'paper_id': pid,
                'title': title,
                'error': 'Timeout'
            })
            return False
        except Exception as e:
            self.log(f"      ERROR: {str(e)}")
            self.stats['errors'].append({
                'paper_id': pid,
                'title': title,
                'error': str(e)
            })
            return False

    def run(self, dry_run: bool = False, limit: int = None):
        """
        执行批量生成

        Args:
            dry_run: 仅显示命令，不执行
            limit: 仅处理前 N 篇论文（用于测试）
        """
        papers = self.get_all_papers()
        if limit:
            papers = papers[:limit]

        # ⭐ Phase 3: 檢查所有論文是否有 cite_key
        missing_cite_keys = []
        for paper in papers:
            if not paper.get('cite_key'):
                missing_cite_keys.append(paper['id'])

        if missing_cite_keys:
            print(f"\n{'=' * 80}")
            print(f"[WARNING] 發現 {len(missing_cite_keys)} 篇論文缺少 cite_key")
            print(f"{'=' * 80}\n")
            print(f"論文ID: {missing_cite_keys[:20]}")
            if len(missing_cite_keys) > 20:
                print(f"... 以及其他 {len(missing_cite_keys) - 20} 篇")
            print(f"\n[SOLUTION] 解決步驟:")
            print(f"   1. 檢查缺少 cite_key 的論文：")
            print(f"      python kb_manage.py check-cite-keys")
            print(f"   2. 從 Zotero 導出 'My Library.bib' 文件")
            print(f"      （Zotero: File → Export Library → BibTeX）")
            print(f"   3. 更新 cite_key：")
            print(f"      python kb_manage.py update-from-bib 'My Library.bib'")
            print(f"   4. 重新執行批量生成\n")
            print(f"{'=' * 80}\n")
            import sys
            sys.exit(1)

        self.stats['total'] = len(papers)

        print("\n" + "=" * 80)
        print(f"BATCH ZETTEL GENERATION - Option A: All {self.stats['total']} Papers")
        print("=" * 80)
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if dry_run:
            print("MODE: DRY RUN (no files will be generated)")
        else:
            print("MODE: LIVE EXECUTION")
        print("=" * 80 + "\n")

        self.log(f"Starting batch generation for {self.stats['total']} papers")

        try:
            for i, paper in enumerate(papers, 1):
                success = self.generate_zettel_for_paper(paper, dry_run=dry_run)

                if success:
                    self.stats['success'] += 1
                else:
                    self.stats['failed'] += 1

                # Progress report every 10 papers
                if i % 10 == 0 or i == self.stats['total']:
                    progress = (i / self.stats['total']) * 100
                    self.log(f"Progress: {i}/{self.stats['total']} "
                            f"({progress:.1f}%) - Success: {self.stats['success']}, "
                            f"Failed: {self.stats['failed']}")

                # Brief pause between requests to avoid rate limiting
                if not dry_run and i < self.stats['total']:
                    time.sleep(2)

        except KeyboardInterrupt:
            self.log("Batch generation interrupted by user")

        finally:
            self.print_summary()

    def print_summary(self):
        """打印总结报告"""
        elapsed = datetime.now() - self.start_time

        print("\n" + "=" * 80)
        print("BATCH GENERATION SUMMARY")
        print("=" * 80)
        print(f"Total papers:   {self.stats['total']}")
        print(f"Success:        {self.stats['success']}")
        print(f"Failed:         {self.stats['failed']}")
        print(f"Skipped:        {self.stats['skipped']}")
        print(f"Success rate:   {self.stats['success']/self.stats['total']*100:.1f}%")
        print(f"Elapsed time:   {elapsed}")
        print(f"Avg per paper:  {elapsed.total_seconds()/max(1, self.stats['success']):.1f}s")

        if self.stats['errors']:
            print(f"\nFailed papers ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:10]:
                print(f"  Paper {error['paper_id']:2d}: {error['error'][:50]}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")

        print(f"\nLog file: {self.log_file}")
        print("=" * 80 + "\n")

        # Save stats to JSON
        stats_file = Path("batch_zettel_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        print(f"Stats saved to: {stats_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Batch generate Zettelkasten for all papers')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show commands without executing')
    parser.add_argument('--limit', type=int, default=None,
                       help='Only process first N papers (for testing)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: process only first 5 papers')

    args = parser.parse_args()

    if args.test:
        args.limit = 5
        args.dry_run = False

    generator = ZettelBatchGenerator()
    generator.run(dry_run=args.dry_run, limit=args.limit)


if __name__ == "__main__":
    main()
