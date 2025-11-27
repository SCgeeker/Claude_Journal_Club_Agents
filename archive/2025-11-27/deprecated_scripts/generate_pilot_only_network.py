#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成只包含 Pilot 論文的 Concept Network 和 MOC
使用臨時過濾策略：只從 Pilot 卡片開始關係識別
"""

import sys
import sqlite3
from pathlib import Path

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analyzers.concept_mapper import ConceptMapper

# Pilot 論文的 12 個資料夾（2025-11-20 生成）
PILOT_FOLDERS = [
    'zettel_Adams-2020_20251120',
    'zettel_Baruch-2016_20251120',
    'zettel_Créquit-2018_20251120',
    'zettel_Hosseini-2015_20251120',
    'zettel_Leckel-2025_20251120',
    'zettel_Liao-2021_20251120',
    'zettel_Peer-2017_20251120',
    'zettel_Shapiro-2013_20251120',
    'zettel_Stewart-2017_20251120',
    'zettel_Strickland-2019_20251120',
    'zettel_Strickland-2022_20251120',
    'zettel_Woodley-2025_20251120'
]

def get_pilot_card_ids():
    """獲取所有 Pilot 論文的卡片 IDs"""
    conn = sqlite3.connect('knowledge_base/index.db')
    cursor = conn.cursor()

    pilot_ids = []
    for folder in PILOT_FOLDERS:
        cursor.execute('SELECT zettel_id FROM zettel_cards WHERE zettel_folder = ?', (folder,))
        pilot_ids.extend([row[0] for row in cursor.fetchall()])

    conn.close()
    return set(pilot_ids)

def filter_relations_pilot_only(relations, pilot_ids):
    """過濾關係，只保留兩端都是 Pilot 卡片的關係"""
    filtered = []
    for rel in relations:
        # ConceptRelation 使用 card_id_1 和 card_id_2
        if rel.card_id_1 in pilot_ids and rel.card_id_2 in pilot_ids:
            filtered.append(rel)
    return filtered

if __name__ == '__main__':
    print('='*70)
    print('生成 Pilot-Only Concept Network (238 張卡片)')
    print('='*70)

    # 1. 獲取 Pilot 卡片 IDs
    print('\n[1] 讀取 Pilot 卡片列表...')
    pilot_ids = get_pilot_card_ids()
    print(f'   找到 {len(pilot_ids)} 張 Pilot 卡片')

    # 2. 執行關係識別（完整）
    print('\n[2] 執行關係識別（包含所有卡片）...')
    mapper = ConceptMapper()

    # 使用內部的 RelationFinder
    from analyzers.relation_finder import RelationFinder
    finder = RelationFinder()

    print('   讀取所有卡片...')
    all_relations = finder.find_concept_relations()
    print(f'   原始關係數: {len(all_relations)}')

    # 3. 過濾關係（只保留 Pilot 卡片間的關係）
    print('\n[3] 過濾關係（只保留 Pilot 卡片）...')
    pilot_relations = filter_relations_pilot_only(all_relations, pilot_ids)
    print(f'   Pilot 關係數: {len(pilot_relations)}')

    # 4. 手動建構只包含 Pilot 的網絡
    print('\n[4] 建構 Pilot-only 網絡...')
    import networkx as nx

    G = nx.Graph()

    # 添加節點（只有 Pilot 卡片）
    for card_id in pilot_ids:
        G.add_node(card_id, zettel_id=card_id)

    # 添加邊（只有 Pilot 關係）
    for rel in pilot_relations:
        if rel.confidence_score >= 0.3:  # 使用相同的信度閾值
            G.add_edge(
                rel.card_id_1,
                rel.card_id_2,
                weight=rel.confidence_score,
                relation_type=rel.relation_type
            )

    print(f'   節點數: {G.number_of_nodes()}')
    print(f'   邊數: {G.number_of_edges()}')
    print(f'   平均度: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}')

    # 5. 計算 PageRank
    print('\n[5] 計算 PageRank...')
    pagerank = nx.pagerank(G) if G.number_of_nodes() > 0 else {}

    # 6. Top 30 核心概念
    print('\n[6] Top 30 核心概念:')
    sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:30]

    # 獲取卡片標題
    conn = sqlite3.connect('knowledge_base/index.db')
    cursor = conn.cursor()

    print('\n   排名 | Zettel ID | PageRank | 標題')
    print('   ' + '-'*80)
    for i, (zettel_id, pr) in enumerate(sorted_nodes, 1):
        cursor.execute('SELECT title FROM zettel_cards WHERE zettel_id = ?', (zettel_id,))
        result = cursor.fetchone()
        title = result[0][:40] if result and result[0] else 'Unknown'
        try:
            print(f'   {i:2d}   {zettel_id:20s} {pr:.4f}   {title}')
        except:
            print(f'   {i:2d}   {zettel_id:20s} {pr:.4f}   (title with special chars)')

    conn.close()

    # 7. 生成完整的 Obsidian 輸出
    print('\n[7] 生成 Obsidian 格式輸出...')
    output_dir = Path('output/moc_pilot_only_238cards')
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f'   輸出目錄: {output_dir}')

    # 生成簡單的 MOC Markdown
    moc_file = output_dir / 'key_concepts_moc_pilot_only.md'
    with open(moc_file, 'w', encoding='utf-8') as f:
        f.write('# 🗺️ 關鍵概念地圖 (Pilot-Only, 238 Cards)\n\n')
        f.write('**生成時間**: 2025-11-20\n')
        f.write('**範圍**: 只包含 12 篇 Pilot 論文（Psycho Studies on crowdsourcing）\n\n')
        f.write('---\n\n')
        f.write('## 📊 網絡統計\n\n')
        f.write(f'- **卡片數**: {G.number_of_nodes()}\n')
        f.write(f'- **關係數**: {G.number_of_edges()}\n')
        f.write(f'- **平均度**: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}\n')
        f.write(f'- **網絡密度**: {nx.density(G):.4f}\n\n')
        f.write('## 📊 Top 30 核心概念\n\n')
        f.write('| 排名 | 概念 | PageRank |\n')
        f.write('|------|------|----------|\n')

        conn = sqlite3.connect('knowledge_base/index.db')
        cursor = conn.cursor()

        for i, (zettel_id, pr) in enumerate(sorted_nodes, 1):
            cursor.execute('SELECT title, zettel_folder FROM zettel_cards WHERE zettel_id = ?', (zettel_id,))
            result = cursor.fetchone()
            if result:
                title, folder = result
                # 生成 Wiki Link（表格中使用簡單格式，避免管道符號問題）
                link = f'[[{folder}/zettel_cards/{zettel_id}]]'
                f.write(f'| {i} | {link} | {pr:.4f} |\n')

        conn.close()

    print(f'   ✅ MOC 已生成: {moc_file}')

    print('\\n' + '='*70)
    print('✅ Pilot-Only 分析完成！')
    print('='*70)
    print(f'\\n輸出目錄: {output_dir}')
    print(f'查看: {moc_file}')
