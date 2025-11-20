#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
互動式PDF元數據修復工具
列出有對應PDF的論文，讓使用者確認後使用現有CLI工具修復
"""

import sys
import io
import sqlite3
from pathlib import Path
import subprocess

# Windows UTF-8編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class InteractiveRepair:
    def __init__(self, pdf_folder="D:/core/research/Program_verse/+/pdf"):
        self.pdf_folder = Path(pdf_folder)
        self.db_path = "knowledge_base/index.db"
        self.repairable_papers = []

    def find_repairable_papers(self):
        """找出有對應PDF的論文"""
        # 掃描PDF資料夾
        pdf_files = {f.stem: str(f) for f in self.pdf_folder.glob('*.pdf')}

        # 查詢資料庫
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, cite_key, file_path, year, keywords, abstract
            FROM papers
            ORDER BY id
        ''')

        for row in cursor.fetchall():
            pid, title, cite_key, file_path, year, keywords, abstract = row

            if not file_path:
                continue

            md_stem = Path(file_path).stem
            pdf_path = None
            matched_bibkey = None

            # 策略1: Markdown檔名與PDF檔名一致
            if md_stem in pdf_files:
                pdf_path = pdf_files[md_stem]
                matched_bibkey = md_stem

            # 策略2: cite_key與PDF檔名一致
            elif cite_key and cite_key in pdf_files:
                pdf_path = pdf_files[cite_key]
                matched_bibkey = cite_key

            if pdf_path:
                # 檢查缺失的元數據
                missing = []
                if not year:
                    missing.append('year')
                if not keywords or keywords == '[]':
                    missing.append('keywords')
                if not abstract or abstract == 'None' or len(abstract) < 50:
                    missing.append('abstract')
                if not cite_key:
                    missing.append('cite_key')

                self.repairable_papers.append({
                    'id': pid,
                    'title': title,
                    'cite_key': cite_key,
                    'md_path': file_path,
                    'pdf_path': pdf_path,
                    'bibkey': matched_bibkey,
                    'missing': missing
                })

        conn.close()
        return len(self.repairable_papers)

    def display_papers(self):
        """顯示可修復的論文清單"""
        print(f"\n{'='*80}")
        print(f"📋 找到 {len(self.repairable_papers)} 篇有對應PDF的論文")
        print(f"{'='*80}\n")

        for i, paper in enumerate(self.repairable_papers, 1):
            print(f"{i}. [ID {paper['id']:2d}] {paper['title'][:60]}")
            print(f"   📄 PDF: {Path(paper['pdf_path']).name}")
            print(f"   🔑 BibKey: {paper['bibkey']}")
            print(f"   ❌ 缺失: {', '.join(paper['missing']) if paper['missing'] else '無（元數據完整）'}")
            print()

    def select_papers(self):
        """讓使用者選擇要修復的論文"""
        print(f"{'='*80}")
        print("請選擇要修復的論文:")
        print("  - 輸入論文編號（例如: 1,3,5）")
        print("  - 輸入範圍（例如: 1-5）")
        print("  - 輸入 'all' 修復全部")
        print("  - 輸入 'q' 退出")
        print(f"{'='*80}\n")

        while True:
            choice = input("➤ 您的選擇: ").strip()

            if choice.lower() == 'q':
                return []

            if choice.lower() == 'all':
                return list(range(len(self.repairable_papers)))

            # 解析選擇
            try:
                selected = []
                for part in choice.split(','):
                    part = part.strip()
                    if '-' in part:
                        # 範圍
                        start, end = map(int, part.split('-'))
                        selected.extend(range(start-1, end))
                    else:
                        # 單個編號
                        selected.append(int(part) - 1)

                # 驗證範圍
                if all(0 <= idx < len(self.repairable_papers) for idx in selected):
                    return selected
                else:
                    print("❌ 編號超出範圍，請重新輸入\n")
            except ValueError:
                print("❌ 格式錯誤，請重新輸入\n")

    def confirm_repair(self, selected_indices):
        """確認修復"""
        print(f"\n{'='*80}")
        print(f"📝 將修復以下 {len(selected_indices)} 篇論文:")
        print(f"{'='*80}\n")

        for idx in selected_indices:
            paper = self.repairable_papers[idx]
            print(f"  ✓ [ID {paper['id']}] {paper['title'][:60]}")
            print(f"    PDF: {Path(paper['pdf_path']).name}")
            print(f"    修復: {', '.join(paper['missing'])}")
            print()

        print(f"{'='*80}")
        confirm = input("➤ 確認執行修復？(y/N): ").strip().lower()
        return confirm == 'y'

    def repair_paper(self, paper, dry_run=False):
        """使用 analyze_paper.py 重新分析PDF並更新資料庫"""
        print(f"\n{'='*60}")
        print(f"🔧 修復論文 ID {paper['id']}: {paper['title'][:50]}")
        print(f"{'='*60}\n")

        pdf_path = paper['pdf_path']

        if dry_run:
            print(f"  [預覽] 將執行: python analyze_paper.py \"{pdf_path}\"")
            print(f"  [預覽] 然後更新資料庫:")
            print(f"    - 更新 cite_key: {paper['bibkey']}")
            print(f"    - 更新缺失的元數據: {', '.join(paper['missing'])}")
            return True

        # 實際執行
        try:
            # 步驟1: 使用 analyze_paper.py 分析PDF（不加入知識庫，僅提取）
            print(f"📄 正在分析PDF: {Path(pdf_path).name}")

            result = subprocess.run(
                ['python', 'analyze_paper.py', pdf_path, '--output-json', 'temp_analysis.json'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=120
            )

            if result.returncode != 0:
                print(f"  ❌ 分析失敗: {result.stderr}")
                return False

            print(f"  ✅ PDF分析完成")

            # 步驟2: 讀取分析結果
            import json
            with open('temp_analysis.json', 'r', encoding='utf-8') as f:
                analysis = json.load(f)

            structure = analysis.get('structure', {})

            # 步驟3: 更新資料庫
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            updates = []
            params = []

            # 更新cite_key（如果缺失）
            if not paper['cite_key']:
                updates.append("cite_key = ?")
                params.append(paper['bibkey'])
                print(f"  📝 設置 cite_key: {paper['bibkey']}")

            # 更新年份（從PDF或structure提取）
            if 'year' in paper['missing'] and structure.get('year'):
                updates.append("year = ?")
                params.append(structure['year'])
                print(f"  📅 更新 year: {structure['year']}")

            # 更新關鍵詞
            if 'keywords' in paper['missing'] and structure.get('keywords'):
                keywords_json = json.dumps(structure['keywords'], ensure_ascii=False)
                updates.append("keywords = ?")
                params.append(keywords_json)
                print(f"  🏷️  更新 keywords: {structure['keywords'][:5]}")

            # 更新摘要
            if 'abstract' in paper['missing'] and structure.get('abstract'):
                abstract = structure['abstract'][:2000]  # 限制長度
                updates.append("abstract = ?")
                params.append(abstract)
                print(f"  📝 更新 abstract: {abstract[:80]}...")

            if updates:
                params.append(paper['id'])
                sql = f"UPDATE papers SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, params)
                conn.commit()
                print(f"\n  ✅ 資料庫更新完成")
            else:
                print(f"\n  ⚠️  沒有需要更新的元數據")

            conn.close()

            # 清理臨時文件
            Path('temp_analysis.json').unlink(missing_ok=True)

            return True

        except subprocess.TimeoutExpired:
            print(f"  ❌ 處理超時（>120秒）")
            return False
        except Exception as e:
            print(f"  ❌ 處理失敗: {e}")
            return False

    def run(self):
        """執行互動式修復流程"""
        print(f"\n{'='*80}")
        print(f"🔧 互動式PDF元數據修復工具")
        print(f"{'='*80}\n")

        print(f"📁 PDF資料夾: {self.pdf_folder}")
        print(f"🗄️  資料庫: {self.db_path}\n")

        # 掃描可修復的論文
        print("🔍 正在掃描可修復的論文...")
        count = self.find_repairable_papers()

        if count == 0:
            print("\n❌ 找不到有對應PDF的論文")
            return

        # 顯示清單
        self.display_papers()

        # 選擇論文
        selected = self.select_papers()

        if not selected:
            print("\n👋 已取消修復")
            return

        # 確認修復
        if not self.confirm_repair(selected):
            print("\n👋 已取消修復")
            return

        # 執行修復
        print(f"\n{'='*80}")
        print(f"🚀 開始修復...")
        print(f"{'='*80}")

        success = 0
        failed = 0

        for idx in selected:
            paper = self.repairable_papers[idx]
            if self.repair_paper(paper, dry_run=False):
                success += 1
            else:
                failed += 1

        # 總結
        print(f"\n{'='*80}")
        print(f"📊 修復完成")
        print(f"{'='*80}")
        print(f"  ✅ 成功: {success}")
        print(f"  ❌ 失敗: {failed}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="互動式PDF元數據修復工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 互動模式
  python interactive_repair.py

  # 非互動模式（直接指定要修復的論文）
  python interactive_repair.py --select 1,2,3,4,9

  # 修復全部
  python interactive_repair.py --select all

  # 預覽模式
  python interactive_repair.py --select 1,2,3 --dry-run
        """
    )

    parser.add_argument('--select', help='直接選擇要修復的論文（例如: 1,2,3 或 all）')
    parser.add_argument('--dry-run', action='store_true', help='預覽模式（不實際修復）')

    args = parser.parse_args()

    repair = InteractiveRepair()

    # 非互動模式
    if args.select:
        print(f"\n{'='*80}")
        print(f"🔧 互動式PDF元數據修復工具（非互動模式）")
        print(f"{'='*80}\n")

        print(f"📁 PDF資料夾: {repair.pdf_folder}")
        print(f"🗄️  資料庫: {repair.db_path}\n")

        print("🔍 正在掃描可修復的論文...")
        count = repair.find_repairable_papers()

        if count == 0:
            print("\n❌ 找不到有對應PDF的論文")
            sys.exit(0)

        # 顯示清單
        repair.display_papers()

        # 解析選擇
        if args.select.lower() == 'all':
            selected = list(range(len(repair.repairable_papers)))
        else:
            selected = []
            for part in args.select.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    selected.extend(range(start-1, end))
                else:
                    selected.append(int(part) - 1)

        # 顯示將要修復的論文
        print(f"\n{'='*80}")
        print(f"📝 將修復以下 {len(selected)} 篇論文:")
        print(f"{'='*80}\n")

        for idx in selected:
            paper = repair.repairable_papers[idx]
            print(f"  ✓ [ID {paper['id']}] {paper['title'][:60]}")
            print(f"    PDF: {Path(paper['pdf_path']).name}")
            print(f"    修復: {', '.join(paper['missing'])}")
            print()

        if args.dry_run:
            print(f"{'='*80}")
            print("⚠️  預覽模式 - 不會實際修復")
            print(f"{'='*80}\n")
            sys.exit(0)

        # 執行修復
        print(f"{'='*80}")
        print(f"🚀 開始修復...")
        print(f"{'='*80}")

        success = 0
        failed = 0

        for idx in selected:
            paper = repair.repairable_papers[idx]
            if repair.repair_paper(paper, dry_run=False):
                success += 1
            else:
                failed += 1

        # 總結
        print(f"\n{'='*80}")
        print(f"📊 修復完成")
        print(f"{'='*80}")
        print(f"  ✅ 成功: {success}")
        print(f"  ❌ 失敗: {failed}")
        print(f"{'='*80}\n")
    else:
        # 互動模式
        repair.run()
