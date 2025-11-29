#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zettel 卡片匯入模組

用於將現有的 Zettelkasten 卡片匯入知識庫。
支援單一資料夾或批次匯入。
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ImportResult:
    """匯入結果"""
    folder: str
    total_cards: int
    imported: int
    skipped: int
    errors: int
    paper_id: Optional[int] = None
    cite_key: Optional[str] = None


def parse_zettel_index(index_path: Path) -> Optional[Dict]:
    """
    解析 zettel_index.md 檔案

    Args:
        index_path: 索引檔案路徑

    Returns:
        解析結果字典，包含 cite_key、paper_title、authors、year、card_count
    """
    try:
        content = index_path.read_text(encoding='utf-8')

        # 提取 YAML front matter
        yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not yaml_match:
            return None

        metadata = yaml.safe_load(yaml_match.group(1))

        return {
            'cite_key': metadata.get('title', ''),  # title 欄位存的是 cite_key
            'paper_title': metadata.get('paper_title', ''),
            'authors': metadata.get('authors', ''),
            'year': metadata.get('year'),
            'card_count': metadata.get('card_count', 0),
            'generated_date': metadata.get('generated_date', '')
        }

    except Exception as e:
        print(f"  [ERROR] 解析索引檔案失敗：{e}")
        return None


def find_paper_by_citekey(kb, cite_key: str) -> Optional[int]:
    """
    在知識庫中查找對應的論文

    Args:
        kb: KnowledgeBaseManager 實例
        cite_key: 論文 cite_key

    Returns:
        paper_id 或 None
    """
    try:
        paper = kb.get_paper_by_citekey(cite_key)
        if paper:
            return paper['id']

        # 嘗試模糊匹配（移除年份後綴）
        base_key = re.sub(r'-\d{4}[a-z]?$', '', cite_key)
        papers = kb.search_papers(base_key, limit=5)
        for p in papers:
            if p.get('cite_key') and base_key.lower() in p['cite_key'].lower():
                return p['id']

        return None

    except Exception:
        return None


def _find_bib_entry(cite_key: str, bib_entries: Dict):
    """
    在 bib_entries 中查找對應的條目（支援 Unicode 正規化比對）

    Args:
        cite_key: 要查找的 cite_key
        bib_entries: BibTeX 條目字典 {cite_key: BibTeXEntry}

    Returns:
        匹配的 BibTeXEntry 或 None
    """
    from src.utils.citekey_resolver import normalize_citekey

    # 1. 精確匹配
    if cite_key in bib_entries:
        return bib_entries[cite_key]

    # 2. 忽略大小寫匹配
    cite_key_lower = cite_key.lower()
    for key, entry in bib_entries.items():
        if key.lower() == cite_key_lower:
            return entry

    # 3. Unicode 正規化匹配（處理 é→e, ü→ue 等）
    cite_key_normalized = normalize_citekey(cite_key).lower()
    for key, entry in bib_entries.items():
        if normalize_citekey(key).lower() == cite_key_normalized:
            return entry

    return None


def add_paper_from_bib(kb, cite_key: str, bib_entries: Dict) -> Optional[int]:
    """
    從 BibTeX 資料新增論文到知識庫

    Args:
        kb: KnowledgeBaseManager 實例
        cite_key: 論文 cite_key
        bib_entries: BibTeX 條目字典 {cite_key: BibTeXEntry}

    Returns:
        新增的 paper_id 或 None
    """
    entry = _find_bib_entry(cite_key, bib_entries)
    if entry is None:
        return None

    try:
        # 建立論文 Markdown 檔案路徑
        from pathlib import Path
        papers_dir = Path("knowledge_base/papers")
        papers_dir.mkdir(parents=True, exist_ok=True)

        # 建立檔案名稱
        safe_key = re.sub(r'[^\w\-]', '_', cite_key)
        file_path = papers_dir / f"{safe_key}.md"

        # 建立基本 Markdown 內容
        authors_str = ', '.join(entry.authors) if entry.authors else ''
        keywords_str = ', '.join(entry.keywords) if entry.keywords else ''

        content = f"""---
title: "{entry.title}"
authors: "{authors_str}"
year: {entry.year or ''}
keywords: [{keywords_str}]
doi: "{entry.doi or ''}"
cite_key: "{entry.cite_key}"
---

# {entry.title}

## 摘要

{entry.abstract or '（無摘要）'}

## 來源

- DOI: {entry.doi or 'N/A'}
- 期刊: {entry.journal or entry.booktitle or 'N/A'}
"""

        # 寫入檔案
        file_path.write_text(content, encoding='utf-8')

        # 新增到知識庫
        paper_id = kb.add_paper(
            file_path=str(file_path),
            title=entry.title,
            authors=entry.authors,
            year=entry.year,
            keywords=entry.keywords,
            doi=entry.doi,
            cite_key=entry.cite_key,
            abstract=entry.abstract,
            source='bib_import'
        )

        return paper_id

    except Exception as e:
        print(f"  [ERROR] 從 bib 新增論文失敗: {e}")
        return None


def import_zettel_folder(
    folder_path: Path,
    kb,
    embed: bool = False,
    dry_run: bool = False,
    bib_entries: Dict = None
) -> ImportResult:
    """
    匯入單一 Zettelkasten 資料夾

    Args:
        folder_path: Zettel 資料夾路徑
        kb: KnowledgeBaseManager 實例
        embed: 是否生成向量嵌入
        dry_run: 預覽模式（不實際寫入）
        bib_entries: BibTeX 條目字典（用於自動新增缺失論文）

    Returns:
        ImportResult
    """
    folder_name = folder_path.name
    result = ImportResult(
        folder=folder_name,
        total_cards=0,
        imported=0,
        skipped=0,
        errors=0
    )

    # 1. 解析索引檔案
    index_path = folder_path / 'zettel_index.md'
    if not index_path.exists():
        print(f"  ⚠️  找不到索引檔案：{index_path}")
        result.errors = 1
        return result

    index_data = parse_zettel_index(index_path)
    if not index_data:
        result.errors = 1
        return result

    result.cite_key = index_data['cite_key']

    # 2. 查找對應論文
    paper_id = find_paper_by_citekey(kb, index_data['cite_key'])

    # 2.1 如果找不到且有 bib_entries，嘗試從 bib 新增
    if not paper_id and bib_entries and not dry_run:
        paper_id = add_paper_from_bib(kb, index_data['cite_key'], bib_entries)
        if paper_id:
            print(f"  📥 從 bib 新增論文 ID: {paper_id}")

    result.paper_id = paper_id

    if paper_id:
        print(f"  📄 關聯論文 ID: {paper_id}")
    elif bib_entries and _find_bib_entry(index_data['cite_key'], bib_entries):
        print(f"  📋 [DRY RUN] 將從 bib 新增論文（cite_key: {index_data['cite_key']}）")
    else:
        print(f"  ⚠️  未找到對應論文（cite_key: {index_data['cite_key']}）")

    # 3. 掃描卡片資料夾
    cards_folder = folder_path / 'zettel_cards'
    if not cards_folder.exists():
        print(f"  ⚠️  找不到卡片資料夾：{cards_folder}")
        result.errors = 1
        return result

    card_files = list(cards_folder.glob('*.md'))
    result.total_cards = len(card_files)

    if dry_run:
        print(f"  [DRY RUN] 將匯入 {result.total_cards} 張卡片")
        return result

    # 4. 匯入卡片
    for card_file in card_files:
        card_data = kb.parse_zettel_card(str(card_file))
        if not card_data:
            result.errors += 1
            continue

        add_result = kb.add_zettel_card(card_data)

        if add_result['status'] == 'inserted':
            result.imported += 1
        elif add_result['status'] == 'duplicate':
            result.skipped += 1
        else:
            result.errors += 1
            continue

        # 建立論文-卡片關聯（無論是新增或重複都嘗試建立）
        if paper_id and add_result['card_id'] > 0:
            kb.link_paper_to_zettel(paper_id, add_result['card_id'], 1.0)

    # 5. 向量嵌入（可選）
    if embed and result.imported > 0:
        try:
            from integrations.vector_db import VectorDatabase
            from integrations.embedder import get_embedder

            vector_db = VectorDatabase()
            embedder = get_embedder(provider='google')

            for card_file in card_files:
                card_data = kb.parse_zettel_card(str(card_file))
                if card_data and card_data.get('content'):
                    embedding = embedder.embed(
                        card_data['content'][:2000],
                        task_type="retrieval_document"
                    )
                    vector_db.upsert_zettel(
                        embeddings=[embedding],
                        documents=[card_data['content'][:2000]],
                        ids=[card_data['zettel_id']],
                        metadatas=[{
                            'title': card_data.get('title', ''),
                            'core_concept': card_data.get('core_concept', ''),
                            'card_type': card_data.get('card_type', 'concept'),
                            'cite_key': result.cite_key
                        }]
                    )

        except Exception as e:
            print(f"  ⚠️  向量嵌入失敗：{e}")

    return result


def import_all_zettel_folders(
    base_path: Path,
    kb,
    embed: bool = False,
    dry_run: bool = False,
    bib_entries: Dict = None
) -> List[ImportResult]:
    """
    批次匯入所有 Zettelkasten 資料夾

    Args:
        base_path: 基礎路徑（通常是 output/zettelkasten_notes/）
        kb: KnowledgeBaseManager 實例
        embed: 是否生成向量嵌入
        dry_run: 預覽模式
        bib_entries: BibTeX 條目字典（用於自動新增缺失論文）

    Returns:
        所有匯入結果列表
    """
    results = []

    # 掃描所有 zettel_ 開頭的資料夾
    zettel_folders = sorted(base_path.glob('zettel_*'))

    print(f"\n找到 {len(zettel_folders)} 個 Zettel 資料夾")

    if bib_entries:
        print(f"📚 已載入 {len(bib_entries)} 筆 BibTeX 條目")

    for folder in zettel_folders:
        if not folder.is_dir():
            continue

        print(f"\n📁 處理：{folder.name}")
        result = import_zettel_folder(folder, kb, embed=embed, dry_run=dry_run, bib_entries=bib_entries)
        results.append(result)

        # 顯示結果
        if not dry_run:
            print(f"   ✅ 匯入 {result.imported} / {result.total_cards} 張")
            if result.skipped > 0:
                print(f"   ⏭️  跳過 {result.skipped} 張重複")
            if result.errors > 0:
                print(f"   ❌ 錯誤 {result.errors} 張")

    return results


def summarize_import_results(results: List[ImportResult]) -> Dict:
    """
    統計匯入結果

    Args:
        results: 匯入結果列表

    Returns:
        統計摘要
    """
    total_folders = len(results)
    total_cards = sum(r.total_cards for r in results)
    total_imported = sum(r.imported for r in results)
    total_skipped = sum(r.skipped for r in results)
    total_errors = sum(r.errors for r in results)
    linked_papers = sum(1 for r in results if r.paper_id)

    return {
        'folders': total_folders,
        'total_cards': total_cards,
        'imported': total_imported,
        'skipped': total_skipped,
        'errors': total_errors,
        'linked_papers': linked_papers
    }
