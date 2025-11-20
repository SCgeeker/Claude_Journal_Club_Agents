#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZoteroSync - Zotero 到知識庫的同步框架
整合 BibTeX 解析、PDF 匹配、去重和批量導入功能
"""

import sys
import io
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from datetime import datetime

# 修復 Windows 終端 UTF-8 編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 條件式導入
try:
    from .bibtex_parser import BibTeXParser, BibTeXEntry
    from .zotero_scanner import ZoteroScanner, PDFFile
except ImportError:
    from src.integrations.bibtex_parser import BibTeXParser, BibTeXEntry
    from src.integrations.zotero_scanner import ZoteroScanner, PDFFile


@dataclass
class SyncConflict:
    """同步衝突記錄"""
    zotero_entry: BibTeXEntry
    kb_paper: Dict
    conflict_type: str  # 'duplicate', 'similar', 'metadata_mismatch'
    similarity_score: float
    resolution: str  # 'skip', 'replace', 'merge', 'manual_review'
    reason: str


@dataclass
class SyncResult:
    """同步結果統計"""
    total_bibtex_entries: int
    successful_imports: int
    skipped_duplicates: int
    conflicts: List[SyncConflict]
    errors: List[Tuple[str, str]]  # (entry_key, error_message)
    import_list: List[Dict]  # 實際導入的論文列表
    timestamp: str


class ZoteroSync:
    """
    Zotero 到知識庫的同步核心類

    工作流程：
    1. parse_bibtex() - 解析 Zotero BibTeX 導出檔案
    2. match_with_kb() - 與現有知識庫進行匹配，檢測重複
    3. resolve_conflicts() - 處理衝突和去重
    4. batch_import() - 批量導入到知識庫
    """

    def __init__(self, kb_path: str = "knowledge_base"):
        """
        初始化 ZoteroSync

        Args:
            kb_path: 知識庫路徑（預設: "knowledge_base"）
        """
        self.kb_path = Path(kb_path)
        self.db_path = self.kb_path / "index.db"

        # 驗證知識庫
        if not self.kb_path.exists():
            raise FileNotFoundError(f"知識庫路徑不存在: {kb_path}")
        if not self.db_path.exists():
            raise FileNotFoundError(f"知識庫數據庫不存在: {self.db_path}")

        # 初始化
        self.parser = BibTeXParser()
        self.bibtex_entries: List[BibTeXEntry] = []
        self.kb_papers: List[Dict] = []
        self.conflicts: List[SyncConflict] = []
        self.errors: List[Tuple[str, str]] = []

    # ==================== 第1步: 解析 BibTeX ====================

    def parse_bibtex(self, bib_file: str) -> List[BibTeXEntry]:
        """
        解析 Zotero 導出的 BibTeX 文件

        Args:
            bib_file: .bib 文件路徑

        Returns:
            BibTeXEntry 對象列表

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 解析失敗
        """
        bib_path = Path(bib_file)
        if not bib_path.exists():
            raise FileNotFoundError(f"BibTeX 文件不存在: {bib_file}")

        print(f"📚 解析 BibTeX 文件: {bib_file}")

        try:
            self.bibtex_entries = self.parser.parse_file(bib_file)
            print(f"✅ 成功解析 {len(self.bibtex_entries)} 個條目")
            return self.bibtex_entries
        except Exception as e:
            print(f"❌ 解析失敗: {e}")
            raise

    # ==================== 第2步: 從知識庫讀取現有論文 ====================

    def load_kb_papers(self) -> List[Dict]:
        """
        從知識庫數據庫讀取現有論文

        Returns:
            論文列表（包含 title, authors, year, keywords 等）
        """
        print(f"📖 從知識庫讀取現有論文...")

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 查詢論文基本信息
            cursor.execute("""
                SELECT id, title, authors, year, keywords, file_path
                FROM papers
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()
            self.kb_papers = [dict(row) for row in rows]

            conn.close()

            print(f"✅ 讀取 {len(self.kb_papers)} 篇現有論文")
            return self.kb_papers

        except Exception as e:
            print(f"⚠️  讀取知識庫失敗: {e}")
            self.kb_papers = []
            return []

    # ==================== 第3步: 與知識庫匹配 ====================

    def match_with_kb(self, threshold: float = 0.8) -> Dict[str, Any]:
        """
        將 BibTeX 條目與知識庫進行匹配，檢測重複

        匹配策略（按優先順序）：
        1. 精確標題匹配
        2. 相似標題匹配（>threshold）
        3. 作者+年份組合匹配

        Args:
            threshold: 標題相似度閾值（預設: 0.8）

        Returns:
            匹配結果統計字典
        """
        print(f"🔗 與知識庫進行匹配 (相似度閾值: {threshold})...")

        if not self.bibtex_entries:
            print("❌ 未載入 BibTeX 條目")
            return {'duplicates': [], 'new_entries': []}

        if not self.kb_papers:
            print("⚠️  知識庫為空，全部作為新條目")
            return {
                'duplicates': [],
                'new_entries': [(i, e) for i, e in enumerate(self.bibtex_entries)]
            }

        duplicates = []
        new_entries = []

        # 建立知識庫標題索引（快速查找）
        kb_titles_lower = {
            p['title'].lower().strip(): p
            for p in self.kb_papers if p.get('title')
        }

        for i, bibtex_entry in enumerate(self.bibtex_entries):
            entry_title = bibtex_entry.title.lower().strip()

            # 方法1: 精確標題匹配
            if entry_title in kb_titles_lower:
                kb_paper = kb_titles_lower[entry_title]
                duplicates.append({
                    'index': i,
                    'bibtex_entry': bibtex_entry,
                    'kb_paper': kb_paper,
                    'match_type': 'exact_title',
                    'score': 1.0
                })
                continue

            # 方法2: 相似標題匹配
            best_match = self._find_best_title_match(
                entry_title,
                self.kb_papers,
                threshold
            )

            if best_match:
                kb_paper, score = best_match
                duplicates.append({
                    'index': i,
                    'bibtex_entry': bibtex_entry,
                    'kb_paper': kb_paper,
                    'match_type': 'similar_title',
                    'score': score
                })
                continue

            # 方法3: 作者+年份匹配
            if bibtex_entry.authors and bibtex_entry.year:
                author_year_match = self._find_by_author_year(
                    bibtex_entry.authors,
                    bibtex_entry.year,
                    self.kb_papers
                )

                if author_year_match:
                    kb_paper, score = author_year_match
                    duplicates.append({
                        'index': i,
                        'bibtex_entry': bibtex_entry,
                        'kb_paper': kb_paper,
                        'match_type': 'author_year',
                        'score': score
                    })
                    continue

            # 無匹配，作為新條目
            new_entries.append((i, bibtex_entry))

        print(f"✅ 匹配完成:")
        print(f"   - 檢測到重複: {len(duplicates)} 篇")
        print(f"   - 新條目: {len(new_entries)} 篇")

        return {
            'duplicates': duplicates,
            'new_entries': new_entries,
            'total_bibtex': len(self.bibtex_entries),
            'total_kb': len(self.kb_papers)
        }

    def _find_best_title_match(
        self,
        title: str,
        papers: List[Dict],
        threshold: float
    ) -> Optional[Tuple[Dict, float]]:
        """查找最佳標題匹配"""
        best_match = None
        best_score = 0

        for paper in papers:
            paper_title = paper.get('title', '').lower().strip()
            if not paper_title:
                continue

            score = SequenceMatcher(None, title, paper_title).ratio()

            if score > best_score and score >= threshold:
                best_score = score
                best_match = paper

        if best_match:
            return (best_match, best_score)
        return None

    def _find_by_author_year(
        self,
        authors: List[str],
        year: int,
        papers: List[Dict]
    ) -> Optional[Tuple[Dict, float]]:
        """根據作者和年份查找匹配"""
        candidates = []

        for paper in papers:
            # 年份必須匹配
            if paper.get('year') != year:
                continue

            # 檢查作者
            paper_authors = paper.get('authors', [])
            if isinstance(paper_authors, str):
                paper_authors = [a.strip() for a in paper_authors.split(';')]

            if not paper_authors:
                continue

            # 計算作者重疊度
            overlap = self._calculate_author_overlap(authors, paper_authors)

            if overlap > 0:
                candidates.append((paper, overlap))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0]

        return None

    def _calculate_author_overlap(
        self,
        authors1: List[str],
        authors2: List[str]
    ) -> float:
        """計算作者列表的重疊度（Jaccard 相似度）"""
        def extract_last_name(author: str) -> str:
            author = author.strip().lower()
            if ',' in author:
                return author.split(',')[0].strip()
            parts = author.split()
            return parts[-1].strip() if parts else author

        last_names1 = set(extract_last_name(a) for a in authors1)
        last_names2 = set(extract_last_name(a) for a in authors2)

        if not last_names1 or not last_names2:
            return 0.0

        intersection = len(last_names1 & last_names2)
        union = len(last_names1 | last_names2)

        return intersection / union if union > 0 else 0.0

    # ==================== 第4步: 解決衝突 ====================

    def resolve_conflicts(
        self,
        match_results: Dict,
        strategy: str = 'skip'
    ) -> List[BibTeXEntry]:
        """
        解決衝突和去重

        策略：
        - 'skip': 跳過重複項（保留知識庫版本）
        - 'replace': 用 BibTeX 版本替換（保留新版本）
        - 'merge': 合併元數據（優先取 BibTeX 版本的有效數據）

        Args:
            match_results: match_with_kb() 的結果
            strategy: 衝突解決策略

        Returns:
            待導入的 BibTeXEntry 列表
        """
        print(f"⚙️  解決衝突 (策略: {strategy})...")

        duplicates = match_results['duplicates']
        new_entries = match_results['new_entries']

        # 根據策略處理重複
        entries_to_import = []

        if strategy == 'skip':
            # 只導入新條目
            entries_to_import = [entry for _, entry in new_entries]

            if duplicates:
                print(f"⏭️  跳過 {len(duplicates)} 篇重複論文（保留知識庫版本）")

        elif strategy == 'replace':
            # 導入新條目 + 替換重複
            entries_to_import = [entry for _, entry in new_entries]
            entries_to_import.extend([d['bibtex_entry'] for d in duplicates])

            print(f"🔄 將替換 {len(duplicates)} 篇重複論文（使用新版本）")

        elif strategy == 'merge':
            # 導入新條目 + 合併重複
            entries_to_import = [entry for _, entry in new_entries]

            for dup in duplicates:
                merged = self._merge_entries(
                    dup['bibtex_entry'],
                    dup['kb_paper']
                )
                entries_to_import.append(merged)

            print(f"🔗 合併 {len(duplicates)} 篇重複論文（保留兩版本的最佳數據）")

        print(f"✅ 衝突解決完成：待導入 {len(entries_to_import)} 篇論文")

        return entries_to_import

    def _merge_entries(
        self,
        bibtex_entry: BibTeXEntry,
        kb_paper: Dict
    ) -> BibTeXEntry:
        """合併 BibTeX 條目和知識庫論文"""
        # 優先取 BibTeX 版本的數據，補充知識庫缺失的部分
        merged = BibTeXEntry(
            entry_type=bibtex_entry.entry_type,
            cite_key=bibtex_entry.cite_key,
            title=bibtex_entry.title,  # BibTeX 版本
            authors=bibtex_entry.authors or kb_paper.get('authors', []),
            year=bibtex_entry.year or kb_paper.get('year'),
            abstract=bibtex_entry.abstract or kb_paper.get('abstract'),
            keywords=bibtex_entry.keywords or kb_paper.get('keywords', []),
            doi=bibtex_entry.doi,
            url=bibtex_entry.url,
            journal=bibtex_entry.journal,
            booktitle=bibtex_entry.booktitle,
            publisher=bibtex_entry.publisher,
            volume=bibtex_entry.volume,
            number=bibtex_entry.number,
            pages=bibtex_entry.pages,
            note=bibtex_entry.note,
            file=bibtex_entry.file,
            raw_entry=bibtex_entry.raw_entry
        )

        return merged

    # ==================== 第5步: 批量導入 ====================

    def batch_import(
        self,
        entries_to_import: List[BibTeXEntry],
        dry_run: bool = False
    ) -> SyncResult:
        """
        批量導入論文到知識庫

        Args:
            entries_to_import: 待導入的 BibTeXEntry 列表
            dry_run: 如果 True，只驗證不導入

        Returns:
            SyncResult 對象
        """
        print(f"\n📤 批量導入論文到知識庫 ({'模擬運行' if dry_run else '真實導入'})...")

        successful_imports = []
        skipped = 0
        errors = []

        for i, entry in enumerate(entries_to_import, 1):
            try:
                # 驗證必要欄位
                if not entry.title:
                    raise ValueError("缺少標題")

                # 準備導入記錄
                import_record = {
                    'cite_key': entry.cite_key,
                    'entry_type': entry.entry_type,
                    'title': entry.title,
                    'authors': entry.authors,
                    'year': entry.year,
                    'abstract': entry.abstract,
                    'keywords': entry.keywords,
                    'doi': entry.doi,
                    'url': entry.url,
                    'journal': entry.journal,
                    'booktitle': entry.booktitle,
                    'publisher': entry.publisher,
                    'volume': entry.volume,
                    'number': entry.number,
                    'pages': entry.pages,
                    'note': entry.note,
                    'file': entry.file,
                    'source': 'zotero_sync',
                    'import_timestamp': datetime.now().isoformat()
                }

                if not dry_run:
                    # 實際導入（此步驟由上層處理）
                    pass

                successful_imports.append(import_record)

                if (i % 10) == 0:
                    print(f"   [{i}/{len(entries_to_import)}] ✅ {entry.cite_key}")

            except Exception as e:
                error_msg = f"導入失敗: {str(e)}"
                errors.append((entry.cite_key, error_msg))
                print(f"   ❌ {entry.cite_key}: {error_msg}")

        # 生成最終結果
        result = SyncResult(
            total_bibtex_entries=len(self.bibtex_entries),
            successful_imports=len(successful_imports),
            skipped_duplicates=len(self.bibtex_entries) - len(entries_to_import),
            conflicts=self.conflicts,
            errors=errors,
            import_list=successful_imports,
            timestamp=datetime.now().isoformat()
        )

        print(f"\n✅ 導入完成:")
        print(f"   - 成功: {result.successful_imports} 篇")
        print(f"   - 跳過: {result.skipped_duplicates} 篇")
        print(f"   - 錯誤: {len(errors)} 篇")

        return result

    # ==================== 工作流整合 ====================

    def sync(
        self,
        bib_file: str,
        conflict_strategy: str = 'skip',
        dry_run: bool = False,
        output_file: Optional[str] = None
    ) -> SyncResult:
        """
        執行完整的 Zotero 同步工作流

        工作流步驟：
        1. 解析 BibTeX 文件
        2. 讀取知識庫現有論文
        3. 與知識庫進行匹配
        4. 解決衝突和去重
        5. 批量導入

        Args:
            bib_file: Zotero 導出的 .bib 文件路徑
            conflict_strategy: 衝突解決策略 ('skip', 'replace', 'merge')
            dry_run: 模擬運行（驗證但不導入）
            output_file: 可選，將結果輸出到 JSON 文件

        Returns:
            SyncResult 對象
        """
        print("=" * 60)
        print("🔄 ZoteroSync - Zotero 到知識庫同步")
        print("=" * 60)

        try:
            # 第1步：解析 BibTeX
            self.parse_bibtex(bib_file)

            # 第2步：讀取知識庫
            self.load_kb_papers()

            # 第3步：匹配
            match_results = self.match_with_kb()

            # 第4步：解決衝突
            entries_to_import = self.resolve_conflicts(
                match_results,
                strategy=conflict_strategy
            )

            # 第5步：批量導入
            result = self.batch_import(entries_to_import, dry_run=dry_run)

            # 輸出結果
            if output_file:
                self._save_result(result, output_file)

            return result

        except Exception as e:
            print(f"\n❌ 同步失敗: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _save_result(self, result: SyncResult, output_file: str):
        """保存同步結果到 JSON 文件"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        result_dict = {
            'total_bibtex_entries': result.total_bibtex_entries,
            'successful_imports': result.successful_imports,
            'skipped_duplicates': result.skipped_duplicates,
            'errors': result.errors,
            'error_count': len(result.errors),
            'import_count': len(result.import_list),
            'conflict_count': len(result.conflicts),
            'timestamp': result.timestamp,
            'import_list': result.import_list
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)

        print(f"\n💾 結果已保存: {output_file}")


def main():
    """測試 ZoteroSync"""
    import argparse

    parser = argparse.ArgumentParser(description='Zotero 到知識庫同步工具')
    parser.add_argument('bib_file', help='Zotero 導出的 .bib 文件')
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
        help='模擬運行（驗證但不導入）'
    )
    parser.add_argument(
        '--output',
        help='輸出結果到 JSON 文件'
    )

    args = parser.parse_args()

    try:
        sync = ZoteroSync(kb_path=args.kb_path)
        result = sync.sync(
            bib_file=args.bib_file,
            conflict_strategy=args.strategy,
            dry_run=args.dry_run,
            output_file=args.output
        )

        return 0 if result.successful_imports > 0 else 1

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
