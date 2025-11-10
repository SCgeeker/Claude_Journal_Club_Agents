#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
單模型測試腳本
測試單個 OpenRouter 免費模型生成 Zettelkasten 卡片
"""

import shutil
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from src.generators.zettel_maker import ZettelMaker
from src.generators.slide_maker import SlideMaker


def extract_paper_content(md_path):
    """從 MD 文件提取論文內容"""
    content = md_path.read_text(encoding='utf-8')

    import re
    title = "Unknown"
    authors = "Unknown"
    year = None

    title_match = re.search(r"title:\s*['\"]?(.+?)['\"]?\s*$", content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)

    authors_match = re.search(r"authors:\s*(.+?)$", content, re.MULTILINE)
    if authors_match:
        authors = authors_match.group(1)

    year_match = re.search(r"year:\s*(\d{4})", content)
    if year_match:
        year = int(year_match.group(1))

    content_start = content.find('---', content.find('---') + 3) + 3
    full_content = content[content_start:].strip()

    return {
        'title': title,
        'authors': authors,
        'year': year,
        'content': full_content[:15000],
        'cite_key': md_path.stem
    }


def main():
    parser = argparse.ArgumentParser(description='單模型測試')
    parser.add_argument('--cite-key', default='Jones-2024', help='論文 cite key')
    parser.add_argument('--model', default='google/gemini-2.0-flash-exp:free',
                       help='OpenRouter 模型 ID')
    parser.add_argument('--suffix', default='test', help='輸出目錄後綴')
    parser.add_argument('--max-tokens', type=int, default=4096,
                       help='最大生成 tokens 數（默認 4096）')
    args = parser.parse_args()

    print("\n" + "="*70)
    print("單模型測試 - OpenRouter")
    print("="*70 + "\n")

    # 1. 讀取論文
    md_path = Path(f"knowledge_base/papers/{args.cite_key}.md")
    if not md_path.exists():
        print(f"[ERROR] 文件不存在: {md_path}")
        return

    print(f"[INFO] 讀取論文: {md_path}")
    paper_data = extract_paper_content(md_path)
    print(f"[OK] 標題: {paper_data['title'][:60]}...")
    print(f"[OK] 作者: {paper_data['authors']}")
    print(f"[OK] 年份: {paper_data['year']}\n")

    # 2. 初始化 SlideMaker
    print(f"[INFO] 使用模型: {args.model}")
    slide_maker = SlideMaker(llm_provider='openrouter')

    # 3. 準備 prompt
    from jinja2 import Template
    template_path = Path("templates/prompts/zettelkasten_template.jinja2")
    template = Template(template_path.read_text(encoding='utf-8'))

    prompt = template.render(
        topic=paper_data['title'],
        card_count=20,
        detail_level="comprehensive",
        paper_content=paper_data['content'],
        cite_key=paper_data['cite_key']
    )

    print(f"[INFO] Prompt 長度: {len(prompt)} 字符\n")

    # 4. 調用 LLM
    print(f"[INFO] 正在調用 LLM...")
    print(f"[INFO] Max tokens: {args.max_tokens}")
    try:
        result = slide_maker.call_llm(
            prompt,
            provider='openrouter',
            model=args.model,
            timeout=600,
            max_tokens=args.max_tokens
        )

        if not result:
            print(f"[ERROR] LLM 返回空響應")
            return

        response, provider = result
        print(f"[OK] LLM 響應: {len(response)} 字符\n")

    except Exception as e:
        print(f"[ERROR] LLM 調用失敗: {e}")
        return

    # 5. 生成卡片文件
    output_dir = Path("output/zettelkasten_notes") / f"zettel_{paper_data['cite_key']}_{datetime.now().strftime('%Y%m%d')}_{args.suffix}"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    print(f"[INFO] 生成卡片到: {output_dir}")

    zettel_maker = ZettelMaker()
    result = zettel_maker.generate_zettelkasten(
        llm_output=response,
        output_dir=output_dir,
        paper_info={
            'cite_key': paper_data['cite_key'],
            'title': paper_data['title'],
            'authors': paper_data['authors'],
            'year': paper_data['year']
        }
    )

    print(f"\n[SUCCESS] 生成 {result['card_count']} 張卡片")

    # 6. 分析輸出
    print(f"\n" + "="*70)
    print("輸出分析")
    print("="*70)

    cards_dir = output_dir / "zettel_cards"
    if cards_dir.exists():
        card_files = list(cards_dir.glob("*.md"))
        print(f"卡片數量: {len(card_files)}")

        # 分析 AI notes 中的連結
        total_links = 0
        cards_with_links = 0

        for card_file in card_files:
            content = card_file.read_text(encoding='utf-8')

            if '🤖 **AI**:' in content:
                ai_section = content.split('🤖 **AI**:')[1].split('✍️ **Human**:')[0]
                links = ai_section.count('[[')
                if links > 0:
                    cards_with_links += 1
                    total_links += links

        print(f"AI notes 包含連結的卡片: {cards_with_links}/{len(card_files)} ({cards_with_links/len(card_files)*100:.1f}%)")
        print(f"AI notes 總連結數: {total_links}")
        print(f"平均每張卡片連結數: {total_links/len(card_files):.2f}")

        # 顯示前 3 張卡片的 AI notes（示例）
        print(f"\n前 3 張卡片 AI notes 示例:")
        print("-" * 70)
        for i, card_file in enumerate(sorted(card_files)[:3], 1):
            content = card_file.read_text(encoding='utf-8')
            if '🤖 **AI**:' in content:
                ai_section = content.split('🤖 **AI**:')[1].split('✍️ **Human**:')[0].strip()
                print(f"\n卡片 {i} ({card_file.name}):")
                print(f"  {ai_section[:150]}...")

    print(f"\n[SUCCESS] 完成！輸出: {output_dir}")


if __name__ == '__main__':
    main()
