#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試解析器修復（使用已保存的 LLM 輸出）
"""

from pathlib import Path
from src.generators.zettel_maker import ZettelMaker
import shutil
from datetime import datetime

def test_parser():
    print("\n" + "="*70)
    print("測試解析器修復")
    print("="*70 + "\n")

    # 讀取已保存的 LLM 輸出
    llm_output_path = Path("llm_raw_output_jones2024.txt")
    if not llm_output_path.exists():
        print(f"❌ LLM 輸出文件不存在: {llm_output_path}")
        return

    print(f"📄 讀取 LLM 原始輸出: {llm_output_path}")
    llm_output = llm_output_path.read_text(encoding='utf-8')
    print(f"✅ LLM 輸出長度: {len(llm_output)} 字符\n")

    # 初始化 ZettelMaker
    zettel_maker = ZettelMaker()

    # 解析卡片
    print("🔄 解析卡片...")
    cards = zettel_maker.parse_llm_output(llm_output)
    print(f"✅ 解析到 {len(cards)} 張卡片\n")

    # 統計連結數量
    total_foundation = 0
    total_derived = 0
    total_related = 0
    total_contrast = 0

    for card in cards:
        total_foundation += len(card.get('foundation_links', []))
        total_derived += len(card.get('derived_links', []))
        total_related += len(card.get('related_links', []))
        total_contrast += len(card.get('contrast_links', []))

    print("="*70)
    print("連結統計")
    print("="*70)
    print(f"基於 (foundation): {total_foundation}")
    print(f"導向 (derived): {total_derived}")
    print(f"相關 (related): {total_related}")
    print(f"對比 (contrast): {total_contrast}")
    print(f"總連結數: {total_foundation + total_derived + total_related + total_contrast}")
    print()

    # 檢查有連結的卡片數量
    cards_with_links = 0
    for card in cards:
        total_links = (len(card.get('foundation_links', [])) +
                      len(card.get('derived_links', [])) +
                      len(card.get('related_links', [])) +
                      len(card.get('contrast_links', [])))
        if total_links > 0:
            cards_with_links += 1

    coverage = (cards_with_links / len(cards) * 100) if cards else 0
    print(f"有連結的卡片: {cards_with_links}/{len(cards)} ({coverage:.1f}%)")
    print()

    # 生成卡片文件
    output_dir = Path("output/zettelkasten_notes") / f"zettel_Jones-2024_{datetime.now().strftime('%Y%m%d')}_gemini_fixed"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    print(f"📝 生成卡片到: {output_dir}")
    result = zettel_maker.generate_zettelkasten(
        llm_output=llm_output,
        output_dir=output_dir,
        paper_info={
            'cite_key': 'Jones-2024',
            'title': 'Multimodal Language Models Show Evidence of Embodied Simulation',
            'authors': 'R. Jones, Sean Trott',
            'year': 2024
        }
    )

    print(f"✅ 生成 {result['card_count']} 張卡片\n")

    # 檢查第一張卡片的解析數據
    if cards:
        print("="*70)
        print(f"第一張卡片解析數據")
        print("="*70)
        print(f"標題: {cards[0]['title']}")
        print(f"personal_notes 長度: {len(cards[0].get('personal_notes', ''))}")
        print(f"personal_notes 內容:")
        print(cards[0].get('personal_notes', '(空)'))
        print()

    # 檢查第一張卡片
    first_card = output_dir / "zettel_cards" / "Jones-2024-001.md"
    if first_card.exists():
        print("="*70)
        print(f"第一張卡片預覽: {first_card}")
        print("="*70)
        content = first_card.read_text(encoding='utf-8')
        # 只顯示連結網絡區塊
        lines = content.split('\n')
        in_link_section = False
        for line in lines:
            if '## 連結網絡' in line:
                in_link_section = True
            if in_link_section:
                print(line)
                if line.startswith('## ') and '連結網絡' not in line:
                    break

    print("\n" + "="*70)
    print("✅ 測試完成")
    print("="*70)

if __name__ == '__main__':
    test_parser()
