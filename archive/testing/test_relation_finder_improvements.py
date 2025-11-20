#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RelationFinder Phase 2.3 改進測試腳本

測試項目:
1. 中文關鍵詞提取（_extract_chinese_keywords）
2. 增強版概念提取（_extract_concepts_enhanced）
3. 領域相似度計算（_calculate_multi_domain_similarity）
4. 完整信度計算（_calculate_confidence）
"""

import sys
from pathlib import Path

# 設置專案根目錄
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.analyzers.relation_finder import RelationFinder


def test_chinese_keywords():
    """測試中文關鍵詞提取"""
    print("\n" + "="*70)
    print("測試 1: 中文關鍵詞提取")
    print("="*70)

    finder = RelationFinder()

    test_texts = [
        "視覺注意機制在工作記憶中的作用",
        "深度學習應用於自然語言處理",
        "認知負荷理論與教學設計",
        "雙語者的語言切換機制研究",
    ]

    for text in test_texts:
        keywords = finder._extract_chinese_keywords(text, top_n=5)
        print(f"\n文本: {text}")
        print(f"提取關鍵詞: {keywords}")
        print(f"數量: {len(keywords)}")


def test_concept_extraction():
    """測試增強版概念提取"""
    print("\n" + "="*70)
    print("測試 2: 增強版概念提取（5個來源）")
    print("="*70)

    finder = RelationFinder()

    # 模擬 Wu-2020 類型的卡片
    sample_card = {
        'zettel_id': 'Wu-2020-001',
        'title': '視覺注意與字符識別',
        'core_concept': '注意機制在視覺處理中的調節作用',
        'description': '本研究探討選擇性注意如何影響字符識別的準確性和速度',
        'tags': '認知科學, 視覺處理, 注意力',
        'ai_notes': '這項研究揭示了注意力資源分配對認知負荷的影響',
        'domain': 'CogSci'
    }

    concepts = finder._extract_concepts_enhanced(sample_card)

    print(f"\n卡片: {sample_card['zettel_id']}")
    print(f"標題: {sample_card['title']}")
    print(f"\n提取概念（帶權重）:")

    # 按權重排序
    sorted_concepts = sorted(concepts.items(), key=lambda x: x[1], reverse=True)
    for concept, weight in sorted_concepts[:15]:  # 顯示前15個
        print(f"  {concept}: {weight:.2f}")

    print(f"\n總概念數: {len(concepts)}")


def test_domain_similarity():
    """測試領域相似度矩陣"""
    print("\n" + "="*70)
    print("測試 3: 領域相似度計算")
    print("="*70)

    finder = RelationFinder()

    test_cases = [
        ("CogSci", "CogSci"),          # 相同領域
        ("CogSci", "AI"),              # 高度相關
        ("CogSci", "Linguistics"),     # 高度相關
        ("AI", "Linguistics"),         # 中度相關
        ("CogSci", "Biology"),         # 未定義（默認）
        ("CogSci, AI", "Linguistics"), # 多領域
    ]

    for domain1_str, domain2_str in test_cases:
        domains1 = finder._parse_domain(domain1_str)
        domains2 = finder._parse_domain(domain2_str)
        similarity = finder._calculate_multi_domain_similarity(domains1, domains2)

        print(f"\n{domain1_str} ↔ {domain2_str}")
        print(f"  解析: {domains1} ↔ {domains2}")
        print(f"  相似度: {similarity:.2f}")


def test_multi_layer_link_detection():
    """測試多層次連結檢測"""
    print("\n" + "="*70)
    print("測試 4: 多層次連結檢測（Phase 3.3）")
    print("="*70)

    finder = RelationFinder()

    # 測試案例 1：連結網絡區段中的結構化連結
    card_with_network_link = {
        'zettel_id': 'Wu-2020-001',
        'content': '''## 說明
視覺注意機制的研究

## 連結網絡
基於 -> [[Wu-2020-002]]
導向 -> [[Wu-2020-003]]
相關 <-> [[Wu-2020-004]]

## 個人筆記
**[AI Agent]**: 此概念...
**[Human]**: (TODO)
'''
    }

    # 測試不同語義的連結
    test_cases = [
        ('Wu-2020-002', '基於', 0.8),   # 基礎關係
        ('Wu-2020-003', '導向', 0.75),  # 延伸關係
        ('Wu-2020-004', '相關', 0.7),   # 雙向關係
    ]

    print("\n測試案例 1: 連結網絡區段（結構化連結）")
    for target_id, relation, expected_score in test_cases:
        score = finder._check_explicit_link_enhanced(card_with_network_link, target_id)
        print(f"  {relation} -> [[{target_id}]]: {score:.2f} (預期: {expected_score})")

    # 測試案例 2：AI Agent 區段中的語境連結
    card_with_ai_link = {
        'zettel_id': 'Liu-2012-001',
        'content': '''## 說明
深度學習中的注意力機制

## 連結網絡
（無連結）

## 個人筆記
**[AI Agent]**: 這個概念是基於 [[Wu-2020-001]] 的視覺注意理論，並延伸到深度學習領域。相關的研究還包括 [[Liu-2012-002]]。
**[Human]**: (TODO)
'''
    }

    print("\n測試案例 2: [AI Agent] 區段（語境連結）")
    ai_test_cases = [
        ('Wu-2020-001', '基於', 1.0),   # 強關係詞
        ('Liu-2012-002', '相關', 0.6),  # 一般相關
    ]

    for target_id, relation, expected_score in ai_test_cases:
        score = finder._check_explicit_link_enhanced(card_with_ai_link, target_id)
        context = finder._extract_link_context(card_with_ai_link['content'], target_id)
        print(f"  {relation} [[{target_id}]]: {score:.2f} (預期: {expected_score})")
        print(f"    語境: {context[:60]}...")

    # 測試案例 3：來源脈絡區段
    card_with_source_link = {
        'zettel_id': 'Gao-2009a-001',
        'content': '''## 說明
字符識別研究

## 來源脈絡
本研究參考了 [[Wu-2020-001]] 的實驗設計。

## 個人筆記
**[AI Agent]**: ...
**[Human]**: (TODO)
'''
    }

    print("\n測試案例 3: 來源脈絡區段（脈絡關聯）")
    score = finder._check_explicit_link_enhanced(card_with_source_link, 'Wu-2020-001')
    print(f"  來源脈絡 [[Wu-2020-001]]: {score:.2f} (預期: 0.4)")

    # 測試案例 4：其他區段（弱關聯）
    card_with_weak_link = {
        'zettel_id': 'Abbas-2022-001',
        'content': '''## 說明
目標設定理論，參見 [[Locke-1990-001]]

## 連結網絡
（無連結）

## 個人筆記
**[AI Agent]**: ...
**[Human]**: (TODO)
'''
    }

    print("\n測試案例 4: 其他區段（說明區段，弱關聯）")
    score = finder._check_explicit_link_enhanced(card_with_weak_link, 'Locke-1990-001')
    print(f"  說明區段 [[Locke-1990-001]]: {score:.2f} (預期: 0.3)")

    # 測試案例 5：無連結
    card_without_link = {
        'zettel_id': 'Test-2024-001',
        'content': '## 說明\n無任何連結的卡片'
    }

    print("\n測試案例 5: 無連結")
    score = finder._check_explicit_link_enhanced(card_without_link, 'Wu-2020-001')
    print(f"  無連結: {score:.2f} (預期: 0.0)")


def test_confidence_calculation():
    """測試完整信度計算"""
    print("\n" + "="*70)
    print("測試 5: 完整信度計算（所有改進整合）")
    print("="*70)

    finder = RelationFinder()

    # 模擬兩張相關的卡片（跨領域：CogSci ↔ AI）
    # 現在加入明確連結來測試完整效果
    card1 = {
        'zettel_id': 'Wu-2020-001',
        'title': '視覺注意機制',
        'core_concept': '選擇性注意在視覺處理中的作用',
        'description': '研究注意力如何影響視覺信息的編碼和提取',
        'tags': '認知科學, 注意力, 視覺處理',
        'ai_notes': '注意機制涉及工作記憶和執行功能的協調',
        'domain': 'CogSci',
        'content': '''## 說明
選擇性注意在視覺處理中扮演關鍵角色。

## 連結網絡
導向 -> [[Liu-2012-003]]
相關 <-> [[Gao-2009a-001]]

## 個人筆記
**[AI Agent]**: 這個概念延伸到深度學習領域，特別是注意力機制。
**[Human]**: (TODO)
'''
    }

    card2 = {
        'zettel_id': 'Liu-2012-003',
        'title': '深度學習中的注意力機制',
        'core_concept': '注意力機制在神經網絡中的實現',
        'description': '探討如何在深度學習模型中引入選擇性注意',
        'tags': '人工智能, 深度學習, 注意力機制',
        'ai_notes': '注意力機制提升了模型的可解釋性和性能',
        'domain': 'AI',
        'content': '## 說明\n注意力機制...'
    }

    # 模擬向量相似度（假設中等）
    vector_similarity = 0.65

    # 計算信度（這將使用改進後的方法）
    confidence = finder._calculate_confidence(card1, card2, vector_similarity, "related")

    print(f"\n卡片1: {card1['zettel_id']} ({card1['domain']})")
    print(f"  標題: {card1['title']}")
    print(f"\n卡片2: {card2['zettel_id']} ({card2['domain']})")
    print(f"  標題: {card2['title']}")

    print(f"\n向量相似度: {vector_similarity:.2f}")
    print(f"信度評分: {confidence:.3f}")

    # 手動計算各維度貢獻（用於調試）
    print("\n各維度貢獻分析:")

    # 1. 語義相似度
    semantic_score = vector_similarity * 0.4
    print(f"  1. 語義相似度 (40%): {semantic_score:.3f}")

    # 2. 明確連結（這裡假設有連結）
    has_link = finder._check_explicit_link(card1, card2['zettel_id'])
    link_score = 0.3 if has_link else 0.0
    print(f"  2. 明確連結 (30%): {link_score:.3f} (存在: {has_link})")

    # 3. 共同概念（使用改進版）
    shared_concepts, weighted_similarity = finder._extract_shared_concepts_enhanced(card1, card2)
    co_occurrence_score = weighted_similarity * 0.2
    print(f"  3. 共同概念 (20%): {co_occurrence_score:.3f}")
    print(f"     共同概念: {shared_concepts[:5]}")  # 顯示前5個
    print(f"     加權相似度: {weighted_similarity:.3f}")

    # 4. 領域一致性（使用矩陣）
    domains1 = finder._parse_domain(card1['domain'])
    domains2 = finder._parse_domain(card2['domain'])
    domain_similarity = finder._calculate_multi_domain_similarity(domains1, domains2)
    domain_score = domain_similarity * 0.10
    print(f"  4. 領域相似度 (10%): {domain_score:.3f}")
    print(f"     CogSci ↔ AI 相似度: {domain_similarity:.2f}")

    print(f"\n總分: {semantic_score + link_score + co_occurrence_score + domain_score:.3f}")

    # 預期改進效果
    print("\n預期改進效果:")
    print("  改進前平均: 0.33")
    print(f"  改進後範例: {confidence:.3f}")
    if confidence >= 0.4:
        print("  ✅ 達到高信度閾值（≥ 0.4）")
    else:
        print(f"  ⚠️ 尚未達到閾值，差距: {0.4 - confidence:.3f}")


def main():
    """執行所有測試"""
    print("="*70)
    print("RelationFinder Phase 2.3 改進測試")
    print("="*70)

    try:
        test_chinese_keywords()
        test_concept_extraction()
        test_domain_similarity()
        test_multi_layer_link_detection()
        test_confidence_calculation()

        print("\n" + "="*70)
        print("✅ 所有測試完成")
        print("="*70)

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
