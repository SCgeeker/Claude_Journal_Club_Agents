#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metadata 修復工具
提供多種方法修復論文的缺失元數據：年份、關鍵詞、摘要
"""

import sys
import sqlite3
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import io
import yaml

# Windows編碼支援
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.knowledge_base.kb_manager import KnowledgeBaseManager


class MetadataFixer:
    """Metadata 修復器"""

    def __init__(self, kb_root: str = "knowledge_base"):
        self.kb = KnowledgeBaseManager(kb_root=kb_root)
        self.db_path = self.kb.db_path

    def get_papers_needing_repair(self, field: Optional[str] = None) -> List[Dict]:
        """
        獲取需要修復的論文列表

        Args:
            field: 指定字段（year, keywords, abstract），None表示任意缺失

        Returns:
            論文列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if field == 'year':
            condition = "year IS NULL"
        elif field == 'keywords':
            condition = "(keywords IS NULL OR keywords = '' OR keywords = '[]')"
        elif field == 'abstract':
            condition = "(abstract IS NULL OR abstract = '' OR LENGTH(abstract) < 50)"
        else:
            # 任意缺失
            condition = """
                year IS NULL OR
                (keywords IS NULL OR keywords = '' OR keywords = '[]') OR
                (abstract IS NULL OR abstract = '' OR LENGTH(abstract) < 50)
            """

        cursor.execute(f"""
            SELECT id, title, authors, year, abstract, keywords, file_path
            FROM papers
            WHERE {condition}
            ORDER BY id
        """)

        papers = []
        for row in cursor.fetchall():
            papers.append({
                'id': row[0],
                'title': row[1],
                'authors': row[2],
                'year': row[3],
                'abstract': row[4],
                'keywords': row[5],
                'file_path': row[6]
            })

        conn.close()
        return papers

    def extract_metadata_from_yaml(self, md_path: str) -> Dict:
        """
        從 Markdown YAML front matter 提取元數據（最優先）

        Args:
            md_path: Markdown 檔案路徑

        Returns:
            元數據字典 {'year': int, 'keywords': list, 'abstract': str, 'authors': str}
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取 YAML front matter (--- 之間的內容)
            yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not yaml_match:
                return {}

            try:
                metadata = yaml.safe_load(yaml_match.group(1))
                if not metadata:
                    return {}

                result = {}

                # 提取年份
                if metadata.get('year'):
                    year = metadata['year']
                    if isinstance(year, int) and 1900 <= year <= 2030:
                        result['year'] = year
                    elif isinstance(year, str) and year.isdigit():
                        year_int = int(year)
                        if 1900 <= year_int <= 2030:
                            result['year'] = year_int

                # 提取關鍵詞
                if metadata.get('keywords'):
                    keywords = metadata['keywords']
                    if isinstance(keywords, list):
                        result['keywords'] = [str(kw).strip() for kw in keywords if kw]
                    elif isinstance(keywords, str):
                        # 處理逗號分隔的字串
                        result['keywords'] = [kw.strip() for kw in keywords.split(',') if kw.strip()]

                # 提取摘要（排除 None 字串）
                if metadata.get('abstract') and metadata['abstract'] not in ['None', 'null', None]:
                    abstract = str(metadata['abstract']).strip()
                    if len(abstract) >= 50:  # 至少 50 字元才算有效摘要
                        result['abstract'] = abstract

                # 提取作者（備用，可能用於未來改進）
                if metadata.get('authors'):
                    authors = metadata['authors']
                    if isinstance(authors, list):
                        result['authors'] = ', '.join(str(a) for a in authors if a)
                    elif isinstance(authors, str):
                        result['authors'] = authors.strip()

                return result

            except yaml.YAMLError as e:
                print(f"⚠️ YAML 解析失敗 {md_path}: {e}")
                return {}

        except Exception as e:
            print(f"⚠️ 讀取文件失敗 {md_path}: {e}")
            return {}

    def extract_year_from_markdown(self, md_path: str) -> Optional[int]:
        """
        從 Markdown 內容提取年份

        策略：
        1. 查找 "Year: YYYY" 格式
        2. 查找 (YYYY) 格式（括號內的四位數字）
        3. 查找版權聲明中的年份（© ... YYYY）
        4. 查找 YYYY 格式（獨立的四位數字，範圍 1900-2030）

        Args:
            md_path: Markdown 檔案路徑

        Returns:
            年份（整數）或 None
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 策略 1: "Year: YYYY" 或 "- 年份: YYYY"
            match = re.search(r'(?:Year|年份):\s*(\d{4})', content, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                if 1900 <= year <= 2030:
                    return year

            # 策略 2: 版權聲明（© ... YYYY）
            match = re.search(r'©.*?(\d{4})', content[:3000])
            if match:
                year = int(match.group(1))
                if 1900 <= year <= 2030:
                    return year

            # 策略 3: (YYYY) 在標題或作者附近
            match = re.search(r'\((\d{4})\)', content[:800])
            if match:
                year = int(match.group(1))
                if 1900 <= year <= 2030:
                    return year

            # 策略 4: 從標題提取（如 "Journal2022;8(1):151-164"）
            match = re.search(r'[A-Za-z]+(\d{4});', content[:500])
            if match:
                year = int(match.group(1))
                if 1900 <= year <= 2030:
                    return year

            # 策略 5: 獨立的 YYYY（前後有空白或標點）
            matches = re.findall(r'(?:^|\s|,|\.|\()(\d{4})(?:\s|,|\.|\)|$)', content[:1500])
            for match in matches:
                year = int(match)
                if 1950 <= year <= 2030:  # 更嚴格的範圍
                    return year

            return None

        except Exception as e:
            print(f"⚠️ 讀取文件失敗 {md_path}: {e}")
            return None

    def extract_keywords_from_markdown(self, md_path: str, max_keywords: int = 10) -> List[str]:
        """
        從 Markdown 內容提取關鍵詞

        策略：
        1. 查找 "Keywords:" 後的內容
        2. 提取加粗或斜體的術語
        3. 使用簡單 TF-IDF 提取重要詞彙（待實作）

        Args:
            md_path: Markdown 檔案路徑
            max_keywords: 最多關鍵詞數

        Returns:
            關鍵詞列表
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 移除 YAML front matter（避免提取到元數據）
            content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

            keywords = []

            # 策略 1: "Keywords:" 後的內容
            match = re.search(r'Keywords?:\s*(.+?)(?:\n\n|\Z)', content, re.IGNORECASE | re.DOTALL)
            if match:
                kw_text = match.group(1)
                # 分割（逗號、分號、換行）
                kw_list = re.split(r'[,;\n]', kw_text)
                for kw in kw_list:
                    kw = kw.strip()
                    # 過濾無效關鍵詞
                    if kw and 2 <= len(kw) <= 50 and not kw.startswith('created:') and not kw.startswith('---'):
                        keywords.append(kw)

            # 策略 2: 提取加粗術語（**term** 或 __term__）
            # 跳過前置 YAML 部分
            main_content = content[500:] if len(content) > 500 else content
            bold_terms = re.findall(r'\*\*(.+?)\*\*|__(.+?)__', main_content[:2000])
            for match in bold_terms:
                term = match[0] or match[1]
                if term and 2 <= len(term) <= 50:
                    # 過濾掉標題風格的文字（如 "AI Agent"、"Human"）
                    if not term.startswith('[') and ':' not in term:
                        keywords.append(term.strip())

            # 去重並限制數量
            keywords = list(dict.fromkeys(keywords))[:max_keywords]

            return keywords

        except Exception as e:
            print(f"⚠️ 讀取文件失敗 {md_path}: {e}")
            return []

    def extract_abstract_from_markdown(self, md_path: str, max_length: int = 2000) -> Optional[str]:
        """
        從 Markdown 內容提取摘要（增強版）

        策略：
        1. 查找 "Abstract" 標題後的內容
        2. 查找 "## 摘要" 標題後的內容
        3. 查找「完整內容」後的首段（新增！）
        4. 使用首段作為摘要（如果合理長度）

        Args:
            md_path: Markdown 檔案路徑
            max_length: 最大摘要長度

        Returns:
            摘要文本或 None
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 策略 1: "Abstract" 標題
            match = re.search(r'#+\s*Abstract\s*\n+(.+?)(?:\n#+|\Z)', content, re.IGNORECASE | re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                if 100 <= len(abstract) <= max_length:
                    return abstract

            # 策略 2: "摘要" 標題
            match = re.search(r'#+\s*摘要\s*\n+(.+?)(?:\n#+|\Z)', content, re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                if 100 <= len(abstract) <= max_length:
                    return abstract

            # 策略 3: 「完整內容」後的首段（新增！）
            match = re.search(r'#+\s*完整內容\s*\n+(.+?)(?:\n#+|\n\n\n|\Z)', content, re.DOTALL)
            if match:
                full_content = match.group(1).strip()
                # 提取首段（前500字元內的第一個段落）
                lines = full_content[:1500].split('\n')
                paragraph = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        paragraph.append(line)
                    elif paragraph and len(' '.join(paragraph)) >= 100:
                        # 已收集足夠長度的段落
                        break

                if paragraph:
                    abstract = ' '.join(paragraph)
                    if 100 <= len(abstract) <= max_length:
                        return abstract[:max_length]

            # 策略 4: 首段（在第一個 ## 標題之前）
            first_section = content.split('\n##')[0]
            # 跳過標題和元數據
            lines = first_section.split('\n')
            paragraphs = []
            current_para = []

            for line in lines[5:]:  # 跳過前5行（可能是標題/元數據）
                line = line.strip()
                if line and not line.startswith('#'):
                    current_para.append(line)
                elif current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []

            if current_para:
                paragraphs.append(' '.join(current_para))

            # 選擇最長的段落（可能是摘要）
            for para in paragraphs:
                if 100 <= len(para) <= max_length:
                    return para

            return None

        except Exception as e:
            print(f"⚠️ 讀取文件失敗 {md_path}: {e}")
            return None

    def update_paper_metadata(
        self,
        paper_id: int,
        year: Optional[int] = None,
        keywords: Optional[List[str]] = None,
        abstract: Optional[str] = None
    ) -> bool:
        """
        更新論文 metadata

        Args:
            paper_id: 論文 ID
            year: 年份
            keywords: 關鍵詞列表
            abstract: 摘要

        Returns:
            成功與否
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if year is not None:
            updates.append("year = ?")
            params.append(year)

        if keywords is not None:
            updates.append("keywords = ?")
            params.append(json.dumps(keywords, ensure_ascii=False))

        if abstract is not None:
            updates.append("abstract = ?")
            params.append(abstract)

        if not updates:
            return False

        params.append(paper_id)
        sql = f"UPDATE papers SET {', '.join(updates)} WHERE id = ?"

        try:
            cursor.execute(sql, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ 更新失敗: {e}")
            conn.close()
            return False

    def auto_fix_paper(self, paper_id: int, fields: List[str] = ['year', 'keywords', 'abstract']) -> Dict:
        """
        自動修復單篇論文的 metadata（優先使用 YAML front matter）

        Args:
            paper_id: 論文 ID
            fields: 要修復的字段列表

        Returns:
            修復結果字典
        """
        # 獲取論文信息
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, file_path, year, keywords, abstract
            FROM papers
            WHERE id = ?
        """, (paper_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {'success': False, 'error': f'論文 ID {paper_id} 不存在'}

        pid, title, file_path, current_year, current_keywords, current_abstract = row

        result = {
            'success': False,
            'paper_id': pid,
            'title': title,
            'updates': {},
            'source': {}  # 記錄數據來源（yaml 或 regex）
        }

        # 檢查檔案是否存在
        if not Path(file_path).exists():
            result['error'] = f'檔案不存在: {file_path}'
            return result

        # 策略：優先使用 YAML front matter，再使用正則表達式
        yaml_metadata = self.extract_metadata_from_yaml(file_path)

        # 修復年份
        if 'year' in fields and not current_year:
            if yaml_metadata.get('year'):
                result['updates']['year'] = yaml_metadata['year']
                result['source']['year'] = 'yaml'
            else:
                year = self.extract_year_from_markdown(file_path)
                if year:
                    result['updates']['year'] = year
                    result['source']['year'] = 'regex'

        # 修復關鍵詞
        if 'keywords' in fields and (not current_keywords or current_keywords == '[]'):
            if yaml_metadata.get('keywords'):
                result['updates']['keywords'] = yaml_metadata['keywords']
                result['source']['keywords'] = 'yaml'
            else:
                keywords = self.extract_keywords_from_markdown(file_path)
                if keywords:
                    result['updates']['keywords'] = keywords
                    result['source']['keywords'] = 'regex'

        # 修復摘要
        if 'abstract' in fields and (not current_abstract or len(current_abstract) < 50 or current_abstract == 'None'):
            if yaml_metadata.get('abstract'):
                result['updates']['abstract'] = yaml_metadata['abstract']
                result['source']['abstract'] = 'yaml'
            else:
                abstract = self.extract_abstract_from_markdown(file_path)
                if abstract:
                    result['updates']['abstract'] = abstract[:500] + '...' if len(abstract) > 500 else abstract
                    result['source']['abstract'] = 'regex'

        # 執行更新
        if result['updates']:
            success = self.update_paper_metadata(
                paper_id=pid,
                year=result['updates'].get('year'),
                keywords=result['updates'].get('keywords'),
                abstract=result['updates'].get('abstract')
            )
            result['success'] = success

        return result

    def batch_fix(self, field: Optional[str] = None, limit: Optional[int] = None, dry_run: bool = False) -> Dict:
        """
        批次修復所有需要修復的論文

        Args:
            field: 指定字段（year, keywords, abstract），None表示全部
            limit: 限制修復數量
            dry_run: 僅預覽，不實際修復

        Returns:
            修復結果統計
        """
        papers = self.get_papers_needing_repair(field)

        if limit:
            papers = papers[:limit]

        results = {
            'total': len(papers),
            'success': 0,
            'failed': 0,
            'no_update': 0,
            'details': []
        }

        print(f'\n找到 {len(papers)} 篇需要修復的論文')
        if dry_run:
            print('⚠️ 預覽模式（不會實際修改）\n')
        else:
            print()

        for i, paper in enumerate(papers, 1):
            print(f'[{i}/{len(papers)}] 論文 ID {paper["id"]}: {paper["title"][:50]}...')

            if dry_run:
                # 僅檢查，不修復
                year = self.extract_year_from_markdown(paper['file_path']) if not paper['year'] else None
                keywords = self.extract_keywords_from_markdown(paper['file_path']) if not paper['keywords'] or paper['keywords'] == '[]' else None
                abstract_preview = self.extract_abstract_from_markdown(paper['file_path'])

                if year:
                    print(f'  年份: None → {year}')
                if keywords:
                    print(f'  關鍵詞: None → {keywords[:3]}... ({len(keywords)} 個)')
                if abstract_preview:
                    print(f'  摘要: None → {abstract_preview[:80]}...')

                results['no_update'] += 1
            else:
                # 實際修復
                fields_to_fix = []
                if field:
                    fields_to_fix = [field]
                else:
                    fields_to_fix = ['year', 'keywords', 'abstract']

                result = self.auto_fix_paper(paper['id'], fields=fields_to_fix)

                if result.get('success'):
                    results['success'] += 1
                    print(f'  ✅ 修復成功')
                    for field_name, value in result.get('updates', {}).items():
                        source = result.get('source', {}).get(field_name, 'unknown')
                        if field_name == 'keywords':
                            print(f'    - {field_name}: {value[:3]}... ({len(value)} 個) [{source}]')
                        elif field_name == 'abstract':
                            print(f'    - {field_name}: {value[:60]}... [{source}]')
                        else:
                            print(f'    - {field_name}: {value} [{source}]')
                elif result.get('updates'):
                    results['no_update'] += 1
                    print(f'  ⚠️ 無更新')
                else:
                    results['failed'] += 1
                    print(f'  ❌ 失敗: {result.get("error", "未知錯誤")}')

                results['details'].append(result)

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="修復知識庫論文的缺失 metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 列出所有需要修復的論文
  python fix_metadata.py --list

  # 列出缺少年份的論文
  python fix_metadata.py --list --field year

  # 預覽修復（不實際執行）
  python fix_metadata.py --dry-run

  # 修復單篇論文
  python fix_metadata.py --paper-id 4

  # 批次修復所有論文
  python fix_metadata.py --batch

  # 只修復年份
  python fix_metadata.py --batch --field year

  # 限制修復數量
  python fix_metadata.py --batch --limit 10
        """
    )

    parser.add_argument('--list', action='store_true', help='列出需要修復的論文')
    parser.add_argument('--field', choices=['year', 'keywords', 'abstract'], help='指定字段')
    parser.add_argument('--paper-id', type=int, help='修復單篇論文')
    parser.add_argument('--batch', action='store_true', help='批次修復')
    parser.add_argument('--limit', type=int, help='限制修復數量')
    parser.add_argument('--dry-run', action='store_true', help='預覽模式（不實際修改）')

    args = parser.parse_args()

    fixer = MetadataFixer()

    if args.list:
        # 列出需要修復的論文
        papers = fixer.get_papers_needing_repair(field=args.field)

        print(f'\n找到 {len(papers)} 篇需要修復的論文')
        print('=' * 80)

        for paper in papers:
            print(f'\nID {paper["id"]}: {paper["title"]}')
            print(f'  年份: {paper["year"] if paper["year"] else "缺失"}')
            print(f'  關鍵詞: {paper["keywords"] if paper["keywords"] and paper["keywords"] != "[]" else "缺失"}')
            print(f'  摘要: {"有" if paper["abstract"] and len(paper["abstract"]) > 50 else "缺失"}')

    elif args.paper_id:
        # 修復單篇論文
        print(f'\n修復論文 ID {args.paper_id}...')
        result = fixer.auto_fix_paper(args.paper_id)

        if result.get('success'):
            print('\n✅ 修復成功!')
            print(f'論文: {result["title"]}')
            for field, value in result.get('updates', {}).items():
                if field == 'keywords':
                    print(f'  - {field}: {value[:5]} ({len(value)} 個)')
                elif field == 'abstract':
                    print(f'  - {field}: {value[:100]}...')
                else:
                    print(f'  - {field}: {value}')
        else:
            print(f'\n❌ 修復失敗: {result.get("error", "未知錯誤")}')

    elif args.batch:
        # 批次修復
        result = fixer.batch_fix(field=args.field, limit=args.limit, dry_run=args.dry_run)

        print('\n' + '=' * 80)
        print('批次修復結果')
        print('=' * 80)
        print(f'總計: {result["total"]}')
        print(f'成功: {result["success"]}')
        print(f'失敗: {result["failed"]}')
        print(f'無更新: {result["no_update"]}')

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
