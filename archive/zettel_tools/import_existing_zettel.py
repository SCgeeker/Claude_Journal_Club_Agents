#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手動導入現有的 Zettelkasten 卡片到知識庫

用途：
- 將已生成但未加入數據庫的卡片批次導入
- 修復 batch_process.py 未正確導入卡片的問題

使用：
    python import_existing_zettel.py
"""

import sys
from pathlib import Path
import re

# 添加專案根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.knowledge_base import KnowledgeBaseManager


def parse_zettel_card(card_file: Path) -> dict:
    """解析 Zettelkasten 卡片文件"""
    try:
        content = card_file.read_text(encoding='utf-8')

        # 提取卡片 ID（從檔名）
        card_id = card_file.stem  # 例如：Crockett-2025-001

        # 提取標題（第一個 # 標題）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else card_id

        # 提取類型
        type_match = re.search(r'\*\*類型\*\*:\s*(.+)', content)
        card_type = type_match.group(1).strip() if type_match else 'concept'

        # 提取核心內容
        core_match = re.search(r'\*\*核心\*\*:\s*(.+)', content)
        core_concept = core_match.group(1).strip() if core_match else ''

        # 提取標籤
        tags_match = re.search(r'\*\*標籤\*\*:\s*(.+)', content)
        tags = []
        if tags_match:
            tags_text = tags_match.group(1)
            tags = [t.strip() for t in tags_text.split(',')]

        # 提取說明（在「說明」和「連結網絡」之間）
        description_match = re.search(
            r'\*\*說明\*\*:\s*\n(.*?)\n\*\*連結網絡\*\*:',
            content,
            re.DOTALL
        )
        description = description_match.group(1).strip() if description_match else ''

        return {
            'id': card_id,
            'title': title,
            'type': card_type,
            'core_concept': core_concept,
            'description': description,
            'tags': tags,
            'content': content
        }
    except Exception as e:
        print(f"  [WARN] 解析失敗: {card_file.name} - {e}")
        return None


def import_zettel_cards():
    """導入所有 Zettelkasten 卡片"""

    print("=" * 70)
    print("[IMPORT] 導入現有 Zettelkasten 卡片到知識庫")
    print("=" * 70)
    print()

    # 初始化知識庫
    kb = KnowledgeBaseManager()

    # Papers 對應（從數據庫查詢）
    import sqlite3
    conn = sqlite3.connect('knowledge_base/index.db')
    cursor = conn.cursor()

    # 查詢所有論文的 ID 和 file_path
    cursor.execute("SELECT id, file_path FROM papers")
    papers = cursor.fetchall()

    # 建立 cite_key 到 paper_id 的映射
    paper_mapping = {}
    for paper_id, file_path in papers:
        # 從 file_path 提取 cite_key（檔名去除 .md）
        cite_key = Path(file_path).stem

        # 嘗試匹配常見的命名模式
        # 例如：TICS2778NoofPages13 -> Crockett-2025
        # 或者直接使用檔名的一部分

        # 簡化的映射（根據實際情況）
        if paper_id == 1:
            paper_mapping['Crockett-2025'] = paper_id
        elif paper_id == 2:
            paper_mapping['Guest-2025 2'] = paper_id
        elif paper_id == 3:
            paper_mapping['Guest-2025a'] = paper_id
        elif paper_id == 4:
            paper_mapping['Günther-2025a'] = paper_id
        elif paper_id == 5:
            paper_mapping['vanRooij-2025'] = paper_id
        elif paper_id == 6:
            paper_mapping['Vigly-2025'] = paper_id

    conn.close()

    print(f"找到 {len(paper_mapping)} 篇論文的映射")
    print()

    # 掃描 Zettelkasten 目錄
    zettel_base = Path('output/zettelkasten_notes')
    zettel_dirs = list(zettel_base.glob('zettel_*_20251119'))

    print(f"找到 {len(zettel_dirs)} 個 Zettelkasten 目錄")
    print()

    total_imported = 0
    total_failed = 0

    for zettel_dir in sorted(zettel_dirs):
        # 提取 cite_key
        dir_name = zettel_dir.name
        cite_key = dir_name.replace('zettel_', '').replace('_20251119', '')

        try:
            print(f"Processing: {cite_key}")
        except UnicodeEncodeError:
            print(f"Processing: {cite_key.encode('ascii', 'replace').decode('ascii')}")

        # 查找對應的 paper_id
        paper_id = paper_mapping.get(cite_key)

        if not paper_id:
            print(f"  [WARN] Cannot find paper ID, skipping")
            print()
            continue

        print(f"  Paper ID: {paper_id}")

        # 讀取卡片
        cards_dir = zettel_dir / 'zettel_cards'

        if not cards_dir.exists():
            print(f"  [WARN] 找不到 zettel_cards 目錄，跳過")
            print()
            continue

        card_files = list(cards_dir.glob('*.md'))
        print(f"  找到 {len(card_files)} 張卡片")

        # 導入每張卡片
        imported = 0
        failed = 0

        for card_file in sorted(card_files):
            card_data = parse_zettel_card(card_file)

            if not card_data:
                failed += 1
                continue

            try:
                # 準備卡片數據（符合 add_zettel_card 的格式）
                zettel_data = {
                    'zettel_id': card_data['id'],
                    'title': card_data['title'],
                    'content': card_data['content'],
                    'core_concept': card_data['core_concept'],
                    'description': card_data['description'],
                    'card_type': card_data['type'],
                    'domain': 'AI_literacy',  # 使用批次處理時的 domain
                    'tags': card_data['tags'],
                    'file_path': str(card_file.resolve()),
                    'source_info': None,
                    'ai_notes': None,
                    'human_notes': None,
                    'created_at': None,
                    'links': []
                }

                # 加入知識庫 - 使用結構化回傳
                result = kb.add_zettel_card(zettel_data)

                # 手動關聯到論文（因為 add_zettel_card 不會自動關聯）
                if result['status'] == 'inserted':
                    kb.link_zettel_to_paper(result['card_id'], paper_id)
                    imported += 1
                elif result['status'] == 'duplicate':
                    # 重複卡片也嘗試關聯
                    if result['card_id'] > 0:
                        kb.link_zettel_to_paper(result['card_id'], paper_id)
                    print(f"    [DUPLICATE] {card_file.name}")
                else:
                    failed += 1
                    print(f"    [ERROR] {result['message']}")
            except Exception as e:
                print(f"    [ERROR] {card_file.name}: {e}")
                failed += 1

        total_imported += imported
        total_failed += failed

        print(f"  [OK] 成功導入: {imported} 張")
        if failed > 0:
            print(f"  [FAIL] 失敗: {failed} 張")
        print()

    # 最終統計
    print("=" * 70)
    print("[STATS] 導入完成")
    print("=" * 70)
    print(f"總計導入: {total_imported} 張卡片")
    if total_failed > 0:
        print(f"失敗: {total_failed} 張")
    print()

    # 驗證知識庫統計
    stats = kb.get_stats()
    print("知識庫統計:")
    print(f"  論文: {stats['total_papers']} 篇")
    print(f"  Zettelkasten 卡片: {stats.get('total_zettel_cards', 0)} 張")
    print()


if __name__ == '__main__':
    import_zettel_cards()
