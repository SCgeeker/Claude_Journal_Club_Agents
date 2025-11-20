#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4: 完整網絡測試（704 張卡片）

測試 RelationFinder Phase 2.3 改進在實際知識庫的效果
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 設置專案根目錄
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import sqlite3

from src.analyzers.relation_finder import RelationFinder


def test_full_network():
    """執行完整網絡關係識別"""
    print("="*70)
    print("Phase 4: 完整網絡測試（704 張卡片）")
    print("="*70)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 初始化
    print("\n初始化 RelationFinder...")
    finder = RelationFinder()

    # 獲取所有卡片
    print("載入所有 Zettelkasten 卡片...")
    db_path = project_root / "knowledge_base" / "index.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            zettel_id, title, core_concept, description,
            tags, domain, ai_notes, content,
            created_at
        FROM zettel_cards
        ORDER BY zettel_id
    """)

    all_cards = []
    for row in cursor.fetchall():
        card = {
            'zettel_id': row[0],
            'title': row[1],
            'core_concept': row[2],
            'description': row[3],
            'tags': row[4],
            'domain': row[5],
            'ai_notes': row[6],
            'content': row[7],
            'created_at': row[8]
        }
        all_cards.append(card)

    print(f"載入卡片數: {len(all_cards)}")

    # 執行關係識別
    print("\n開始關係識別...")
    print("(這可能需要 3-5 分鐘)")

    relations = finder.find_concept_relations(
        min_similarity=0.3,  # 降低閾值以包含更多關係
        relation_types=None  # 所有類型
    )

    print(f"\n識別關係總數: {len(relations)}")

    # 統計信度分佈
    print("\n" + "="*70)
    print("信度分佈統計")
    print("="*70)

    confidence_bins = {
        '≥ 0.8 (極高)': 0,
        '0.6-0.8 (高)': 0,
        '0.4-0.6 (中)': 0,
        '0.3-0.4 (低)': 0,
        '< 0.3 (極低)': 0
    }

    total_confidence = 0.0
    high_confidence_relations = []  # ≥ 0.4

    for rel in relations:
        conf = rel.confidence_score
        total_confidence += conf

        if conf >= 0.8:
            confidence_bins['≥ 0.8 (極高)'] += 1
            high_confidence_relations.append(rel)
        elif conf >= 0.6:
            confidence_bins['0.6-0.8 (高)'] += 1
            high_confidence_relations.append(rel)
        elif conf >= 0.4:
            confidence_bins['0.4-0.6 (中)'] += 1
            high_confidence_relations.append(rel)
        elif conf >= 0.3:
            confidence_bins['0.3-0.4 (低)'] += 1
        else:
            confidence_bins['< 0.3 (極低)'] += 1

    avg_confidence = total_confidence / len(relations) if relations else 0.0

    # 顯示統計結果
    for bin_name, count in confidence_bins.items():
        percentage = (count / len(relations) * 100) if relations else 0
        print(f"{bin_name}: {count:,} ({percentage:.1f}%)")

    print(f"\n平均信度: {avg_confidence:.3f}")
    print(f"高信度關係數 (≥ 0.4): {len(high_confidence_relations):,}")

    # 對比基準測試
    print("\n" + "="*70)
    print("與基準測試對比")
    print("="*70)

    baseline = {
        'total_relations': 56436,
        'avg_confidence': 0.33,
        'high_confidence': 0,
        'very_high': 0,
        'high': 0,
        'medium': 0
    }

    print(f"\n基準測試（改進前）:")
    print(f"  總關係數: {baseline['total_relations']:,}")
    print(f"  平均信度: {baseline['avg_confidence']:.3f}")
    print(f"  高信度關係 (≥ 0.4): {baseline['high_confidence']}")

    print(f"\n改進後測試:")
    print(f"  總關係數: {len(relations):,}")
    print(f"  平均信度: {avg_confidence:.3f}")
    print(f"  高信度關係 (≥ 0.4): {len(high_confidence_relations):,}")

    if len(relations) > 0 and baseline['total_relations'] > 0:
        relations_change = (len(relations) - baseline['total_relations']) / baseline['total_relations'] * 100
        confidence_change = (avg_confidence - baseline['avg_confidence']) / baseline['avg_confidence'] * 100

        print(f"\n改進幅度:")
        print(f"  關係數變化: {relations_change:+.1f}%")
        print(f"  平均信度提升: {confidence_change:+.1f}%")
        print(f"  高信度關係增加: {len(high_confidence_relations) - baseline['high_confidence']:,} (+∞)")

    # 顯示前 20 個高信度關係範例
    if high_confidence_relations:
        print("\n" + "="*70)
        print("高信度關係範例 (前 20 個)")
        print("="*70)

        # 按信度排序
        high_confidence_relations.sort(key=lambda r: r.confidence_score, reverse=True)

        for i, rel in enumerate(high_confidence_relations[:20], 1):
            print(f"\n{i}. [{rel.confidence_score:.3f}] {rel.relation_type}")
            print(f"   卡片1: {rel.card_id_1} - {rel.card_title_1}")
            print(f"   卡片2: {rel.card_id_2} - {rel.card_title_2}")

    # 保存結果到文件
    output_dir = Path("output/relation_finder_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存統計數據
    stats = {
        'test_time': datetime.now().isoformat(),
        'total_cards': len(all_cards),
        'total_relations': len(relations),
        'avg_confidence': avg_confidence,
        'confidence_distribution': confidence_bins,
        'high_confidence_count': len(high_confidence_relations),
        'baseline_comparison': {
            'baseline_total': baseline['total_relations'],
            'baseline_avg_confidence': baseline['avg_confidence'],
            'baseline_high_confidence': baseline['high_confidence'],
            'relations_change_pct': relations_change if len(relations) > 0 else 0,
            'confidence_change_pct': confidence_change if len(relations) > 0 else 0
        }
    }

    stats_file = output_dir / 'test_statistics.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"\n統計數據已保存到: {stats_file}")

    # 保存高信度關係列表
    if high_confidence_relations:
        high_conf_file = output_dir / 'high_confidence_relations.txt'
        with open(high_conf_file, 'w', encoding='utf-8') as f:
            f.write("高信度關係列表 (≥ 0.4)\n")
            f.write("="*70 + "\n\n")

            for rel in high_confidence_relations:
                f.write(f"信度: {rel.confidence_score:.3f} | 類型: {rel.relation_type}\n")
                f.write(f"  卡片1: {rel.card_id_1} - {rel.card_title_1}\n")
                f.write(f"  卡片2: {rel.card_id_2} - {rel.card_title_2}\n")
                f.write("\n")

        print(f"高信度關係已保存到: {high_conf_file}")

    print("\n" + "="*70)
    print("✅ Phase 4 測試完成")
    print("="*70)

    # 評估成功與否
    if len(high_confidence_relations) > 0:
        print("\n🎉 成功：產生了高信度關係！")
        print(f"   Obsidian 建議連結功能現在可用")
    else:
        print("\n⚠️  警告：仍無高信度關係")
        print(f"   可能需要進一步調整參數")

    return stats


if __name__ == "__main__":
    try:
        stats = test_full_network()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
