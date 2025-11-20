#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Zettelkasten 卡片重新生成 - 优雅方案
绕过数据库，直接从 MD 文件生成

设计哲学：Simple, Direct, Elegant
"""

import shutil
from pathlib import Path
from datetime import datetime
from src.generators.zettel_maker import ZettelMaker
from src.generators.slide_maker import SlideMaker

def extract_paper_content(md_path):
    """从 MD 文件提取论文内容"""
    content = md_path.read_text(encoding='utf-8')

    # 提取基本信息
    lines = content.split('\n')
    title = "Unknown"
    authors = "Unknown"
    year = None

    # 从 frontmatter 提取
    import re
    title_match = re.search(r"title:\s*['\"]?(.+?)['\"]?\s*$", content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)

    authors_match = re.search(r"authors:\s*(.+?)$", content, re.MULTILINE)
    if authors_match:
        authors = authors_match.group(1)

    year_match = re.search(r"year:\s*(\d{4})", content)
    if year_match:
        year = int(year_match.group(1))

    # 提取完整内容部分（去除 frontmatter）
    content_start = content.find('---', content.find('---') + 3) + 3
    full_content = content[content_start:].strip()

    return {
        'title': title,
        'authors': authors,
        'year': year,
        'content': full_content[:15000],  # 限制长度
        'cite_key': md_path.stem  # Abbas-2022
    }

def generate_with_new_template(paper_data):
    """使用新 template 生成卡片"""
    print(f"\n{'='*70}")
    print(f"生成 Zettelkasten: {paper_data['cite_key']}")
    print(f"标题: {paper_data['title'][:60]}...")
    print(f"{'='*70}\n")

    # 1. 初始化 SlideMaker（重用成熟的 LLM 调用逻辑）
    slide_maker = SlideMaker(
        llm_provider='auto',
        selection_strategy='balanced'
    )

    print(f"LLM Provider: {slide_maker.llm_provider}")

    # 2. 准备 prompt
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

    print(f"Prompt 长度: {len(prompt)} 字符")
    print(f"生成 20 张卡片 (comprehensive 模式)\n")

    # 3. 调用 LLM
    print("正在调用 LLM...")
    result = slide_maker.call_llm(prompt)

    if not result:
        print("❌ LLM 返回空响应")
        return None

    # call_llm 返回 (response, provider) tuple
    response, provider = result
    print(f"✅ LLM 响应 ({provider}): {len(response)} 字符\n")

    # 4. 生成卡片文件
    output_dir = Path("output/zettelkasten_notes") / f"zettel_{paper_data['cite_key']}_{datetime.now().strftime('%Y%m%d')}"

    # 删除旧版本（已备份）
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

    print(f"✅ 生成 {result['card_count']} 张卡片")

    print(f"\n✅ 生成完成: {output_dir}\n")

    return output_dir

def main():
    """主函数"""
    print("\n" + "="*70)
    print("Zettelkasten 重新生成 - Elegant Solution")
    print("="*70 + "\n")

    # 1. 读取论文
    md_path = Path("knowledge_base/papers/Abbas-2022.md")
    if not md_path.exists():
        print(f"❌ 文件不存在: {md_path}")
        return

    print(f"📄 读取论文: {md_path}")
    paper_data = extract_paper_content(md_path)
    print(f"✅ 提取成功\n")

    # 2. 备份旧卡片
    old_dir = Path("output/zettelkasten_notes/zettel_Abbas-2022_20251104")
    if old_dir.exists():
        backup_dir = old_dir.parent / f"{old_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"💾 备份旧卡片: {backup_dir}")
        shutil.copytree(old_dir, backup_dir)
        print(f"✅ 备份完成\n")

    # 3. 生成新卡片
    output_dir = generate_with_new_template(paper_data)

    if output_dir:
        print("="*70)
        print("下一步:")
        print("="*70)
        print("1. 分析新卡片:")
        print("   python analyze_card_links.py")
        print("2. 对比结果:")
        print("   对比 card_link_analysis_before.txt 和新分析")

if __name__ == '__main__':
    main()
