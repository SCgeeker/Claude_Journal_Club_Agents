#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
互動式 PDF 重新導入工具
用於修復缺失 cite_key 的論文
"""

import sqlite3
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

class InteractivePDFReimport:
    def __init__(self):
        self.conn = sqlite3.connect('knowledge_base/index.db')
        self.cursor = self.conn.cursor()
        self.results = {
            'processed': 0,
            'success': 0,
            'skipped': 0,
            'failed': 0,
            'errors': []
        }

    def get_missing_papers(self):
        """獲取缺失 cite_key 的論文"""
        self.cursor.execute('''
            SELECT id, title, file_path
            FROM papers
            WHERE cite_key IS NULL
            ORDER BY id
        ''')
        return self.cursor.fetchall()

    def show_paper_info(self, paper_id, title, md_path):
        """顯示論文信息"""
        print()
        print("=" * 80)
        print(f"📄 Paper {paper_id}")
        print("=" * 80)
        print(f"當前標題: {title}")
        print(f"Markdown 文件: {md_path}")
        print()

        # 嘗試從 Markdown 提取更多信息
        md_file = Path(md_path)
        if md_file.exists():
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取前幾行完整內容
            lines = content.split('\n')
            in_full = False
            preview_lines = []

            for line in lines:
                if '## 完整內容' in line:
                    in_full = True
                    continue
                if in_full and line.strip() and not line.startswith('#'):
                    preview_lines.append(line.strip())
                    if len(preview_lines) >= 5:
                        break

            if preview_lines:
                print("內容預覽:")
                for line in preview_lines[:5]:
                    print(f"  {line[:75]}")
                print()

    def analyze_pdf(self, pdf_path, paper_id):
        """重新分析 PDF 並更新知識庫"""
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            return False, f"PDF 文件不存在: {pdf_path}"

        print(f"  🔄 正在分析 PDF: {pdf_path.name}...")

        # 步驟 1: 從文件名提取可能的 cite_key
        pdf_stem = pdf_path.stem
        potential_cite_key = None

        # 嘗試匹配常見格式: Author-YYYY, AuthorYYYY
        import re
        patterns = [
            r'^([A-Z][a-z]+)-?(\d{4})[a-z]?$',  # Her-2012, Her2012a
            r'^([A-Z][a-z]+[A-Z][a-z]+)-?(\d{4})$',  # ChenYiRu-2020
        ]

        for pattern in patterns:
            match = re.match(pattern, pdf_stem)
            if match:
                author = match.group(1)
                year = match.group(2)
                potential_cite_key = f"{author}-{year}"
                break

        # 步驟 2: 使用 analyze_paper.py 分析 PDF (JSON 格式，不加入知識庫)
        temp_json = Path(f"temp_analysis_{paper_id}.json")

        cmd = [
            'python', 'analyze_paper.py',
            str(pdf_path),
            '--format', 'json',
            '--output-json', str(temp_json)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=180
            )

            if result.returncode == 0 and temp_json.exists():
                # 讀取分析結果
                with open(temp_json, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)

                # 提取元數據
                title = analysis.get('title', '')
                authors = analysis.get('authors', [])
                year = analysis.get('year')
                abstract = analysis.get('abstract', '')
                keywords = analysis.get('keywords', [])

                # 確定 cite_key
                cite_key = potential_cite_key  # 優先使用文件名
                if not cite_key and authors and year:
                    # 從作者和年份生成
                    first_author = authors[0].split()[-1] if authors else ''
                    cite_key = f"{first_author}-{year}" if first_author else None

                # 清理臨時文件
                temp_json.unlink()

                if cite_key:
                    # 步驟 3: 更新數據庫
                    # 檢查 cite_key 是否已被使用
                    self.cursor.execute('SELECT id FROM papers WHERE cite_key = ?', (cite_key,))
                    existing = self.cursor.fetchone()

                    if existing and existing[0] != paper_id:
                        # cite_key 衝突，添加後綴
                        suffix = 'a'
                        while True:
                            new_cite_key = f"{cite_key}{suffix}"
                            self.cursor.execute('SELECT id FROM papers WHERE cite_key = ?', (new_cite_key,))
                            if not self.cursor.fetchone():
                                cite_key = new_cite_key
                                break
                            suffix = chr(ord(suffix) + 1)
                        print(f"  ⚠️  cite_key 衝突，使用: {cite_key}")

                    # 更新記錄
                    update_fields = []
                    update_values = []

                    if cite_key:
                        update_fields.append('cite_key = ?')
                        update_values.append(cite_key)

                    if title and title != 'Untitled':
                        update_fields.append('title = ?')
                        update_values.append(title)

                    if year:
                        update_fields.append('year = ?')
                        update_values.append(year)

                    if authors:
                        authors_str = ', '.join(authors)
                        update_fields.append('authors = ?')
                        update_values.append(authors_str)

                    if abstract:
                        update_fields.append('abstract = ?')
                        update_values.append(abstract)

                    if keywords:
                        keywords_str = ', '.join(keywords)
                        update_fields.append('keywords = ?')
                        update_values.append(keywords_str)

                    if update_fields:
                        update_values.append(paper_id)
                        sql = f"UPDATE papers SET {', '.join(update_fields)} WHERE id = ?"
                        self.cursor.execute(sql, update_values)
                        self.conn.commit()

                        print(f"  ✅ 成功更新!")
                        print(f"     cite_key: {cite_key}")
                        print(f"     year: {year if year else 'N/A'}")
                        print(f"     authors: {', '.join(authors[:2]) if authors else 'N/A'}")
                        return True, None
                    else:
                        return False, "未提取到有效的元數據"
                else:
                    return False, "無法確定 cite_key"
            else:
                # 清理臨時文件
                if temp_json.exists():
                    temp_json.unlink()
                error_msg = result.stderr[:200] if result.stderr else "未知錯誤"
                return False, f"分析失敗: {error_msg}"

        except subprocess.TimeoutExpired:
            if temp_json.exists():
                temp_json.unlink()
            return False, "處理超時 (180秒)"
        except Exception as e:
            if temp_json.exists():
                temp_json.unlink()
            return False, f"異常: {str(e)}"

    def process_paper(self, paper_id, title, md_path):
        """處理單篇論文"""
        self.show_paper_info(paper_id, title, md_path)
        self.results['processed'] += 1

        print("請提供選項:")
        print("  1. 提供 PDF 路徑 (絕對路徑或相對路徑)")
        print("  2. 跳過此論文 (s)")
        print("  3. 退出程式 (q)")
        print()

        choice = input("您的選擇: ").strip()

        if choice.lower() == 'q':
            return 'quit'
        elif choice.lower() == 's':
            print("  ⏭️  已跳過")
            self.results['skipped'] += 1
            return 'continue'
        elif choice:
            # 使用者提供了路徑
            pdf_path = choice.strip('"').strip("'")  # 移除引號
            success, error = self.analyze_pdf(pdf_path, paper_id)

            if success:
                self.results['success'] += 1
            else:
                print(f"  ❌ 失敗: {error}")
                self.results['failed'] += 1
                self.results['errors'].append({
                    'paper_id': paper_id,
                    'title': title,
                    'error': error,
                    'pdf_path': pdf_path
                })

            return 'continue'
        else:
            print("  ⚠️  無效輸入，已跳過")
            self.results['skipped'] += 1
            return 'continue'

    def run(self):
        """執行互動式處理"""
        missing_papers = self.get_missing_papers()

        print()
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "互動式 PDF 重新導入工具" + " " * 34 + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        print(f"發現 {len(missing_papers)} 篇論文缺少 cite_key")
        print()
        print("說明:")
        print("  - 每篇論文會顯示當前標題和內容預覽")
        print("  - 請提供對應的 PDF 文件路徑")
        print("  - 系統會重新分析 PDF 並更新元數據")
        print("  - 輸入 's' 跳過，'q' 退出")
        print()

        input("按 Enter 開始...")

        for paper_id, title, md_path in missing_papers:
            action = self.process_paper(paper_id, title, md_path)

            if action == 'quit':
                print()
                print("使用者退出處理")
                break

        # 顯示總結
        self.show_summary()

        # 保存日誌
        self.save_log()

    def show_summary(self):
        """顯示處理總結"""
        print()
        print("=" * 80)
        print("處理總結")
        print("=" * 80)
        print(f"處理論文數: {self.results['processed']}")
        print(f"成功更新: {self.results['success']}")
        print(f"跳過: {self.results['skipped']}")
        print(f"失敗: {self.results['failed']}")
        print()

        if self.results['failed'] > 0:
            print("失敗的論文:")
            for error in self.results['errors']:
                print(f"  Paper {error['paper_id']}: {error['error']}")
            print()

        # 檢查當前狀態
        self.cursor.execute('SELECT COUNT(*) FROM papers WHERE cite_key IS NULL')
        remaining = self.cursor.fetchone()[0]

        print(f"剩餘缺失 cite_key: {remaining} 篇")

        if remaining == 0:
            print()
            print("🎉 所有論文都已有 cite_key！")
            print("可以進行下一步：重新生成 Zettel 卡片")

    def save_log(self):
        """保存處理日誌"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = Path(f"pdf_reimport_log_{timestamp}.json")

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"日誌已保存: {log_file}")

    def close(self):
        """關閉數據庫連接"""
        self.conn.commit()
        self.conn.close()

def main():
    reimporter = InteractivePDFReimport()
    try:
        reimporter.run()
    except KeyboardInterrupt:
        print()
        print("使用者中斷處理")
    finally:
        reimporter.close()

if __name__ == '__main__':
    main()
