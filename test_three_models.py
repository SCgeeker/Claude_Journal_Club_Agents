#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
三模型對比測試腳本
使用三個免費 OpenRouter 模型重新生成 Zettelkasten 卡片並對比質量
"""

import shutil
import sys
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

from src.generators.zettel_maker import ZettelMaker
from src.generators.slide_maker import SlideMaker


def extract_paper_content(md_path):
    """從 MD 文件提取論文內容"""
    content = md_path.read_text(encoding='utf-8')

    # 提取基本信息
    import re
    title = "Unknown"
    authors = "Unknown"
    year = None

    # 從 frontmatter 提取
    title_match = re.search(r"title:\s*['\"]?(.+?)['\"]?\s*$", content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)

    authors_match = re.search(r"authors:\s*(.+?)$", content, re.MULTILINE)
    if authors_match:
        authors = authors_match.group(1)

    year_match = re.search(r"year:\s*(\d{4})", content)
    if year_match:
        year = int(year_match.group(1))

    # 提取完整內容部分（去除 frontmatter）
    content_start = content.find('---', content.find('---') + 3) + 3
    full_content = content[content_start:].strip()

    return {
        'title': title,
        'authors': authors,
        'year': year,
        'content': full_content[:15000],  # 限制長度
        'cite_key': md_path.stem
    }


def generate_with_model(paper_data, model_id, model_name, output_suffix):
    """使用指定模型生成卡片"""
    print(f"\n{'='*70}")
    print(f"[{model_name}] 生成 Zettelkasten: {paper_data['cite_key']}")
    print(f"模型: {model_id}")
    print(f"標題: {paper_data['title'][:60]}...")
    print(f"{'='*70}\n")

    # 1. 初始化 SlideMaker（指定 OpenRouter）
    slide_maker = SlideMaker(
        llm_provider='openrouter'
    )

    # 2. 準備 prompt
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

    print(f"Prompt 長度: {len(prompt)} 字符")
    print(f"生成 20 張卡片 (comprehensive 模式)\n")

    # 3. 調用 LLM
    print(f"正在調用 {model_name}...")

    try:
        result = slide_maker.call_llm(
            prompt,
            provider='openrouter',
            model=model_id,
            timeout=600  # 10 分鐘超時
        )

        if not result:
            print(f"[ERROR] {model_name} 返回空響應")
            return None

        response, provider = result
        print(f"[OK] {model_name} 響應: {len(response)} 字符\n")

    except Exception as e:
        print(f"[ERROR] {model_name} 調用失敗: {e}")
        return None

    # 4. 生成卡片文件
    output_dir = Path("output/zettelkasten_notes") / f"zettel_{paper_data['cite_key']}_{datetime.now().strftime('%Y%m%d')}_{output_suffix}"

    # 刪除舊版本
    if output_dir.exists():
        shutil.rmtree(output_dir)

    print(f"生成卡片到: {output_dir}")

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

    print(f"[OK] 生成 {result['card_count']} 張卡片")
    print(f"\n[SUCCESS] 完成: {output_dir}\n")

    return output_dir


def analyze_output(output_dir, model_name):
    """分析生成的卡片質量"""
    if not output_dir or not output_dir.exists():
        return None

    print(f"\n[ANALYZE] {model_name} 輸出分析:")
    print("-" * 70)

    # 統計卡片數
    cards_dir = output_dir / "zettel_cards"
    if cards_dir.exists():
        card_files = list(cards_dir.glob("*.md"))
        print(f"  卡片數量: {len(card_files)}")

        # 分析 AI notes 中的連結
        total_links = 0
        cards_with_links = 0

        for card_file in card_files:
            content = card_file.read_text(encoding='utf-8')

            # 檢查 AI notes 區塊
            if '🤖 **AI**:' in content:
                ai_section = content.split('🤖 **AI**:')[1].split('✍️ **Human**:')[0]
                # 統計 Wiki Links
                links = ai_section.count('[[')
                if links > 0:
                    cards_with_links += 1
                    total_links += links

        print(f"  AI notes 包含連結的卡片: {cards_with_links}/{len(card_files)} ({cards_with_links/len(card_files)*100:.1f}%)")
        print(f"  AI notes 總連結數: {total_links}")
        print(f"  平均每張卡片連結數: {total_links/len(card_files):.2f}")

    print("-" * 70)

    return {
        'card_count': len(card_files),
        'cards_with_links': cards_with_links,
        'total_links': total_links,
        'avg_links': total_links/len(card_files) if card_files else 0
    }


def main():
    parser = argparse.ArgumentParser(description='三模型對比測試')
    parser.add_argument('--cite-key', default='Jones-2024', help='論文 cite key')
    args = parser.parse_args()

    print("\n" + "="*70)
    print("三模型對比測試 - OpenRouter 免費模型")
    print("="*70 + "\n")

    # 1. 讀取論文
    md_path = Path(f"knowledge_base/papers/{args.cite_key}.md")
    if not md_path.exists():
        print(f"[ERROR] 文件不存在: {md_path}")
        return

    print(f"[INFO] 讀取論文: {md_path}")
    paper_data = extract_paper_content(md_path)
    print(f"[OK] 提取成功\n")

    # 2. 三個測試模型
    models = [
        {
            'id': 'google/gemini-2.0-flash-exp:free',
            'name': 'Gemini 2.0 Flash',
            'suffix': 'gemini'
        },
        {
            'id': 'deepseek/deepseek-r1:free',
            'name': 'DeepSeek R1',
            'suffix': 'deepseek'
        },
        {
            'id': 'meta-llama/llama-3.3-70b-instruct:free',
            'name': 'Llama 3.3 70B',
            'suffix': 'llama'
        }
    ]

    # 3. 依次使用三個模型生成
    results = {}
    import time

    for i, model in enumerate(models):
        # 在模型之間等待以避免 rate limiting
        if i > 0:
            print(f"\n[INFO] 等待 60 秒以避免 rate limiting...")
            time.sleep(60)

        output_dir = generate_with_model(
            paper_data,
            model['id'],
            model['name'],
            model['suffix']
        )

        if output_dir:
            analysis = analyze_output(output_dir, model['name'])
            results[model['name']] = {
                'output_dir': output_dir,
                'analysis': analysis
            }
        else:
            print(f"[WARNING] {model['name']} 生成失敗，等待 30 秒後繼續...")
            time.sleep(30)

    # 4. 對比結果
    print("\n" + "="*70)
    print("對比結果總結")
    print("="*70 + "\n")

    print(f"{'模型':<20} {'卡片數':<8} {'有連結卡片':<12} {'總連結數':<10} {'平均連結/卡片':<15}")
    print("-" * 70)

    for model in models:
        if model['name'] in results and results[model['name']]['analysis']:
            a = results[model['name']]['analysis']
            print(f"{model['name']:<20} {a['card_count']:<8} {a['cards_with_links']:<12} {a['total_links']:<10} {a['avg_links']:<15.2f}")
        else:
            print(f"{model['name']:<20} {'失敗':<8}")

    print("\n" + "="*70)
    print("測試完成！")
    print("="*70)

    # 5. 輸出詳細路徑
    print("\n生成的卡片目錄:")
    for model in models:
        if model['name'] in results:
            print(f"  [{model['name']}] {results[model['name']]['output_dir']}")


if __name__ == '__main__':
    main()
