#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新 Template 的卡片生成效果
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

def analyze_existing_cards():
    """分析现有卡片的连结情况"""
    print("=" * 70)
    print("分析现有 Zettelkasten 卡片")
    print("=" * 70)

    zettel_dir = Path("output/zettelkasten_notes")
    if not zettel_dir.exists():
        print(f"Error: {zettel_dir} 不存在")
        return None

    stats = {
        'total_papers': 0,
        'total_cards': 0,
        'cards_with_explicit_links': 0,
        'ai_notes_with_links': 0,
        'total_ai_notes': 0,
        'link_counts': [],
        'papers': []
    }

    # Wiki Link 模式
    wiki_link_pattern = re.compile(r'\[\[([^\]]+)\]\]')

    for paper_dir in sorted(zettel_dir.iterdir()):
        if not paper_dir.is_dir() or not paper_dir.name.startswith('zettel_'):
            continue

        stats['total_papers'] += 1
        paper_info = {
            'name': paper_dir.name,
            'cards': 0,
            'cards_with_links': 0,
            'ai_notes_links': []
        }

        cards_dir = paper_dir / "zettel_cards"
        if not cards_dir.exists():
            continue

        for card_file in sorted(cards_dir.glob("*.md")):
            stats['total_cards'] += 1
            paper_info['cards'] += 1

            content = card_file.read_text(encoding='utf-8')

            # 检查是否有明确连结
            links = wiki_link_pattern.findall(content)
            if links:
                stats['cards_with_explicit_links'] += 1
                paper_info['cards_with_links'] += 1

            # 检查 AI notes 区块
            ai_notes_match = re.search(r'## 個人筆記\s*\n\s*🤖\s*\*\*AI\*\*:\s*(.*?)(?=\n\n|✍️|\Z)', content, re.DOTALL)
            if ai_notes_match:
                stats['total_ai_notes'] += 1
                ai_notes = ai_notes_match.group(1)
                ai_links = wiki_link_pattern.findall(ai_notes)

                if ai_links:
                    stats['ai_notes_with_links'] += 1
                    stats['link_counts'].append(len(ai_links))
                    paper_info['ai_notes_links'].append({
                        'card': card_file.name,
                        'count': len(ai_links),
                        'links': ai_links
                    })
                else:
                    stats['link_counts'].append(0)

        stats['papers'].append(paper_info)

    return stats

def print_stats(stats):
    """打印统计结果"""
    print(f"\n📊 统计摘要:")
    print(f"   - 论文总数: {stats['total_papers']}")
    print(f"   - 卡片总数: {stats['total_cards']}")
    print(f"   - 有明确连结的卡片: {stats['cards_with_explicit_links']} ({stats['cards_with_explicit_links']/stats['total_cards']*100:.1f}%)")
    print(f"   - AI notes 总数: {stats['total_ai_notes']}")
    print(f"   - 有连结的 AI notes: {stats['ai_notes_with_links']} ({stats['ai_notes_with_links']/stats['total_ai_notes']*100:.1f}%)" if stats['total_ai_notes'] > 0 else "   - 有连结的 AI notes: 0")

    if stats['link_counts']:
        avg_links = sum(stats['link_counts']) / len(stats['link_counts'])
        print(f"   - AI notes 平均连结数: {avg_links:.2f}")
        print(f"   - 连结数分布: min={min(stats['link_counts'])}, max={max(stats['link_counts'])}")
    else:
        print(f"   - AI notes 平均连结数: 0.00")

    # 显示前 5 篇论文的详细信息
    print(f"\n📄 前 5 篇论文详情:")
    for i, paper in enumerate(stats['papers'][:5], 1):
        print(f"\n{i}. {paper['name']}")
        print(f"   - 卡片数: {paper['cards']}")
        print(f"   - 有连结的卡片: {paper['cards_with_links']}")
        if paper['ai_notes_links']:
            print(f"   - AI notes 有连结的卡片:")
            for link_info in paper['ai_notes_links'][:3]:  # 只显示前3个
                print(f"     • {link_info['card']}: {link_info['count']} 个连结")
                print(f"       {link_info['links'][:2]}")  # 显示前2个连结

def select_test_paper(stats):
    """选择测试论文"""
    print("\n" + "=" * 70)
    print("选择测试论文")
    print("=" * 70)

    # 选择一篇有一定卡片数量的论文
    candidates = [p for p in stats['papers'] if p['cards'] >= 5 and p['cards'] <= 15]

    if not candidates:
        candidates = stats['papers'][:5]

    print("\n推荐的测试论文:")
    for i, paper in enumerate(candidates[:5], 1):
        print(f"{i}. {paper['name']} ({paper['cards']} 张卡片, {paper['cards_with_links']} 张有连结)")

    return candidates[0] if candidates else None

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("Zettelkasten 卡片生成测试 - Phase 2.3")
    print("=" * 70)

    # 分析现有卡片
    stats = analyze_existing_cards()
    if not stats:
        return

    print_stats(stats)

    # 选择测试论文
    test_paper = select_test_paper(stats)

    if test_paper:
        print(f"\n✅ 推荐测试论文: {test_paper['name']}")
        print(f"   这篇论文有 {test_paper['cards']} 张卡片")
        print(f"\n下一步:")
        print(f"   1. 从知识库找到对应的 paper_id")
        print(f"   2. 重新生成 Zettelkasten 卡片")
        print(f"   3. 比较前后差异")

    # 保存统计数据
    output_file = Path("output/card_generation_test_baseline.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\n💾 统计数据已保存到: {output_file}")

if __name__ == '__main__':
    main()
