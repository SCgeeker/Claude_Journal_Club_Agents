#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析现有 Zettelkasten 卡片的连结分布
"""

import re
import json
from pathlib import Path
from collections import defaultdict

def extract_section(content, section_name):
    """提取指定区块的内容"""
    pattern = rf'##\s*{re.escape(section_name)}\s*\n(.*?)(?=\n##|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""

def count_wiki_links(text):
    """统计文本中的 Wiki Links"""
    pattern = r'\[\[([^\]]+)\]\]'
    return re.findall(pattern, text)

def analyze_card(card_path):
    """分析单张卡片"""
    content = card_path.read_text(encoding='utf-8')

    # 提取各区块
    link_network = extract_section(content, '連結網絡')
    ai_notes_section = extract_section(content, '個人筆記')

    # 从 AI notes 区块中提取 AI 部分
    ai_notes = ""
    ai_match = re.search(r'\*\*\[AI Agent\]\*\*:\s*\*\*\[AI Agent\]\*\*:\s*(.*?)(?=\n\n\*\*\[Human\]|\Z)', ai_notes_section, re.DOTALL)
    if ai_match:
        ai_notes = ai_match.group(1).strip()

    # 统计连结
    link_network_links = count_wiki_links(link_network)
    ai_notes_links = count_wiki_links(ai_notes)
    all_links = count_wiki_links(content)

    return {
        'card': card_path.name,
        'link_network_links': link_network_links,
        'link_network_count': len(link_network_links),
        'ai_notes_links': ai_notes_links,
        'ai_notes_count': len(ai_notes_links),
        'total_links': len(all_links)
    }

def analyze_paper_cards(paper_dir):
    """分析一篇论文的所有卡片"""
    cards_dir = paper_dir / "zettel_cards"
    if not cards_dir.exists():
        return None

    results = []
    for card_file in sorted(cards_dir.glob("*.md")):
        result = analyze_card(card_file)
        results.append(result)

    # 统计
    stats = {
        'paper': paper_dir.name,
        'total_cards': len(results),
        'cards_with_network_links': sum(1 for r in results if r['link_network_count'] > 0),
        'cards_with_ai_links': sum(1 for r in results if r['ai_notes_count'] > 0),
        'total_network_links': sum(r['link_network_count'] for r in results),
        'total_ai_links': sum(r['ai_notes_count'] for r in results),
        'avg_network_links': sum(r['link_network_count'] for r in results) / len(results) if results else 0,
        'avg_ai_links': sum(r['ai_notes_count'] for r in results) / len(results) if results else 0,
        'cards': results
    }

    return stats

def main():
    """主函数"""
    zettel_dir = Path("output/zettelkasten_notes")

    # 分析 Abbas-2022 论文（新生成的版本）
    paper_dir = zettel_dir / "zettel_Abbas-2022_20251109"

    if not paper_dir.exists():
        print(f"Error: {paper_dir} does not exist")
        return

    stats = analyze_paper_cards(paper_dir)

    if not stats:
        print("Error: No cards found")
        return

    # 输出到文件
    output_file = Path("output/card_link_analysis_after.json")
    output_file.parent.mkdir(exist_ok=True, parents=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    # 创建可读报告
    report_file = Path("output/card_link_analysis_after.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write(f"Zettelkasten Card Link Analysis - {stats['paper']}\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Total Cards: {stats['total_cards']}\n")
        f.write(f"Cards with Network Links: {stats['cards_with_network_links']} ({stats['cards_with_network_links']/stats['total_cards']*100:.1f}%)\n")
        f.write(f"Cards with AI Notes Links: {stats['cards_with_ai_links']} ({stats['cards_with_ai_links']/stats['total_cards']*100:.1f}%)\n\n")

        f.write(f"Total Network Links: {stats['total_network_links']}\n")
        f.write(f"Total AI Notes Links: {stats['total_ai_links']}\n\n")

        f.write(f"Average Network Links per Card: {stats['avg_network_links']:.2f}\n")
        f.write(f"Average AI Notes Links per Card: {stats['avg_ai_links']:.2f}\n\n")

        f.write("=" * 70 + "\n")
        f.write("Card Details (first 10):\n")
        f.write("=" * 70 + "\n\n")

        for card in stats['cards'][:10]:
            f.write(f"{card['card']}:\n")
            f.write(f"  - Link Network: {card['link_network_count']} links\n")
            if card['link_network_links']:
                f.write(f"    {card['link_network_links']}\n")
            f.write(f"  - AI Notes: {card['ai_notes_count']} links\n")
            if card['ai_notes_links']:
                f.write(f"    {card['ai_notes_links']}\n")
            f.write("\n")

    print(f"Analysis complete!")
    print(f"JSON output: {output_file}")
    print(f"Report: {report_file}")

    # 打印摘要
    print(f"\nSummary:")
    print(f"  Paper: {stats['paper']}")
    print(f"  Total Cards: {stats['total_cards']}")
    print(f"  Cards with AI Notes Links: {stats['cards_with_ai_links']} ({stats['cards_with_ai_links']/stats['total_cards']*100:.1f}%)")
    print(f"  Average AI Notes Links: {stats['avg_ai_links']:.2f}")

if __name__ == '__main__':
    main()
