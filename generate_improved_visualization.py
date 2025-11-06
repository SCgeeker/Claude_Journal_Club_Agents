#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用改進後的 RelationFinder 生成概念網絡可視化
"""

import sys
from pathlib import Path

# 設置專案根目錄
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.analyzers.concept_mapper import ConceptMapper


def main():
    print("="*70)
    print("使用改進後的 RelationFinder 生成概念網絡可視化")
    print("="*70)

    # 初始化 ConceptMapper
    mapper = ConceptMapper()

    # 執行完整分析
    print("\n開始分析...")
    results = mapper.analyze_all(
        output_dir="output/concept_analysis_improved",
        visualize=True,           # 生成 D3.js + Graphviz
        obsidian_mode=True,       # 生成 Obsidian 格式
        obsidian_options={
            'suggested_links_min_confidence': 0.4,  # 使用新的閾值
            'suggested_links_top_n': 100,           # 增加建議連結數量
            'moc_top_n': 20,
            'max_communities': 10,
            'path_top_n': 10
        }
    )

    print("\n" + "="*70)
    print("✅ 可視化生成完成")
    print("="*70)

    print("\n輸出目錄: output/concept_analysis_improved/")
    print("\n生成的文件:")
    print("  - concept_network.html (D3.js 互動式網絡圖)")
    print("  - concept_network.dot (Graphviz 格式)")
    print("  - analysis_report.md (完整分析報告)")
    print("  - analysis_data.json (原始數據)")
    print("  - obsidian/ (Obsidian 友好格式)")
    print("    - suggested_links.md (智能連結建議)")
    print("    - key_concepts_moc.md (核心概念地圖)")
    print("    - community_summaries/ (社群摘要)")

    # 顯示關鍵統計
    if results:
        print("\n" + "="*70)
        print("關鍵統計")
        print("="*70)

        network_stats = results.get('network_stats', {})
        print(f"\n網絡統計:")
        print(f"  節點數: {network_stats.get('num_nodes', 0)}")
        print(f"  邊數: {network_stats.get('num_edges', 0)}")
        print(f"  平均度: {network_stats.get('avg_degree', 0):.2f}")
        print(f"  網絡密度: {network_stats.get('density', 0):.3f}")

        centralities = results.get('centrality_analysis', {})
        if centralities:
            print(f"\n核心概念 (Top 5):")
            top_nodes = sorted(
                centralities.items(),
                key=lambda x: x[1].get('pagerank', 0),
                reverse=True
            )[:5]

            for i, (node_id, metrics) in enumerate(top_nodes, 1):
                print(f"  {i}. {node_id}")
                print(f"     PageRank: {metrics.get('pagerank', 0):.4f}")
                print(f"     Degree: {metrics.get('degree_centrality', 0):.3f}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
