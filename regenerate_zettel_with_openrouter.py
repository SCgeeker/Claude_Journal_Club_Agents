#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Zettelkasten 卡片重新生成 - OpenRouter 支持版本
支持多种 LLM provider，特别优化 OpenRouter 集成
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from src.generators.zettel_maker import ZettelMaker
from src.generators.slide_maker import SlideMaker

def extract_paper_content(md_path):
    """从 MD 文件提取论文内容"""
    content = md_path.read_text(encoding='utf-8')

    import re
    title_match = re.search(r"title:\s*['\"]?(.+?)['\"]?\s*$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Unknown"

    authors_match = re.search(r"authors:\s*(.+?)$", content, re.MULTILINE)
    authors = authors_match.group(1) if authors_match else "Unknown"

    year_match = re.search(r"year:\s*(\d{4})", content)
    year = int(year_match.group(1)) if year_match else None

    content_start = content.find('---', content.find('---') + 3) + 3
    full_content = content[content_start:].strip()

    return {
        'title': title,
        'authors': authors,
        'year': year,
        'content': full_content[:15000],
        'cite_key': md_path.stem
    }

def generate_with_llm(paper_data, llm_provider='auto', model=None, temperature=0.3):
    """使用指定 LLM 生成卡片"""
    print(f"\n{'='*70}")
    print(f"生成 Zettelkasten: {paper_data['cite_key']}")
    print(f"标题: {paper_data['title'][:60]}...")
    print(f"{'='*70}\n")

    # 初始化 SlideMaker
    print(f"初始化 LLM...")
    print(f"  Provider: {llm_provider}")
    if model:
        print(f"  Model: {model}")
    print(f"  Temperature: {temperature}\n")

    slide_maker = SlideMaker(
        llm_provider=llm_provider,
        selection_strategy='balanced'
    )

    # 准备 prompt
    from jinja2 import Template
    template_path = Path("templates/prompts/zettelkasten_template.jinja2")
    template = Template(template_path.read_text(encoding='utf-8'))

    prompt = template.render(
        topic=paper_data['title'],
        card_count=20,
        detail_level="comprehensive",
        paper_content=paper_data['content'],
        cite_key=paper_data['cite_key'],
        language="chinese"  # 修復 Gemini 語言設置失效問題
    )

    print(f"Prompt 长度: {len(prompt)} 字符")
    print(f"生成 20 张卡片 (comprehensive 模式)\n")

    # 调用 LLM
    print("正在调用 LLM...")
    # DeepSeek 和 Llama 需要更大的 max_tokens 以生成完整卡片
    max_tokens = 16000 if ('deepseek' in model.lower() or 'llama' in model.lower()) else 4096
    print(f"使用 max_tokens: {max_tokens}")
    result = slide_maker.call_llm(prompt, model=model, max_tokens=max_tokens)

    if not result:
        print("❌ LLM 返回空响应")
        return None

    response, provider = result
    print(f"✅ LLM 响应 ({provider}): {len(response)} 字符\n")

    # 生成卡片文件（添加模型標記）
    model_name = model.split('/')[-1].replace('-', '_')  # deepseek-r1 -> deepseek_r1

    # 保存原始輸出用於調試
    debug_file = Path("output") / f"debug_llm_output_{paper_data['cite_key']}_{model_name}.txt"
    debug_file.write_text(response, encoding='utf-8')
    print(f"🐛 調試輸出已保存: {debug_file}\n")

    output_dir = Path("output/zettelkasten_notes") / f"zettel_{paper_data['cite_key']}_{datetime.now().strftime('%Y%m%d')}_{model_name}"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    print(f"生成卡片到: {output_dir}")

    zettel_maker = ZettelMaker()

    # 構建引用格式
    authors_short = paper_data['authors'].split(',')[0].split()[0] if paper_data['authors'] else "Unknown"
    citation = f"[[{paper_data['cite_key']}.pdf|{authors_short} et al. ({paper_data['year']})]]"

    result = zettel_maker.generate_zettelkasten(
        llm_output=response,
        output_dir=output_dir,
        paper_info={
            'cite_key': paper_data['cite_key'],
            'title': paper_data['title'],
            'authors': paper_data['authors'],
            'year': paper_data['year'],
            'citation': citation
        }
    )

    print(f"✅ 生成 {result['card_count']} 张卡片\n")
    print(f"✅ 生成完成: {output_dir}\n")

    return output_dir

def test_multiple_llms(paper_data):
    """测试多个 LLM 的生成效果"""
    print("\n" + "="*70)
    print("多 LLM 对比测试")
    print("="*70 + "\n")

    # 测试配置
    test_configs = []

    # 检查哪些 LLM 可用
    import os
    from dotenv import load_dotenv
    load_dotenv()

    if os.getenv('OPENROUTER_API_KEY'):
        test_configs.extend([
            ('openrouter', 'anthropic/claude-3.5-sonnet', 0.3, '最佳格式遵循'),
            ('openrouter', 'anthropic/claude-3-haiku', 0.3, '快速经济'),
        ])

    if os.getenv('ANTHROPIC_API_KEY'):
        test_configs.append(('anthropic', 'claude-3-sonnet-20240229', 0.3, '直接 Anthropic'))

    if os.getenv('GOOGLE_API_KEY'):
        test_configs.append(('google', 'gemini-2.0-flash-exp', 0.5, 'Google Gemini'))

    if not test_configs:
        print("❌ 没有可用的 LLM API key")
        print("请配置至少一个 API key:")
        print("  - OPENROUTER_API_KEY (推荐)")
        print("  - GOOGLE_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        return

    print(f"将测试 {len(test_configs)} 个配置:\n")
    for i, (provider, model, temp, desc) in enumerate(test_configs, 1):
        print(f"{i}. {desc}")
        print(f"   Provider: {provider}")
        print(f"   Model: {model}\n")

    results = {}
    for provider, model, temp, desc in test_configs:
        print("\n" + "="*70)
        print(f"测试: {desc}")
        print("="*70)

        try:
            output_dir = generate_with_llm(paper_data, provider, model, temp)
            if output_dir:
                results[desc] = {
                    'provider': provider,
                    'model': model,
                    'output_dir': output_dir,
                    'status': '成功'
                }
        except Exception as e:
            print(f"❌ 失败: {e}")
            results[desc] = {
                'provider': provider,
                'model': model,
                'status': f'失败: {e}'
            }

    # 生成对比报告
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70 + "\n")

    for desc, result in results.items():
        print(f"{desc}:")
        print(f"  状态: {result['status']}")
        if result['status'] == '成功':
            print(f"  输出: {result['output_dir']}")
        print()

    print("下一步: 使用 analyze_card_links.py 分析每个版本的连结数量")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Zettelkasten 重新生成 - 多 LLM 支持')
    parser.add_argument('--provider', default='auto',
                        choices=['auto', 'openrouter', 'google', 'anthropic', 'openai', 'ollama'],
                        help='LLM provider')
    parser.add_argument('--model', help='Model name')
    parser.add_argument('--temperature', type=float, default=0.3, help='Temperature')
    parser.add_argument('--test-all', action='store_true', help='测试所有可用的 LLM')

    args = parser.parse_args()

    print("\n" + "="*70)
    print("Zettelkasten 重新生成 - OpenRouter & 多 LLM 支持")
    print("="*70 + "\n")

    # 读取论文
    md_path = Path("knowledge_base/papers/Jones-2024.md")
    if not md_path.exists():
        print(f"❌ 文件不存在: {md_path}")
        return

    print(f"📄 读取论文: {md_path}")
    paper_data = extract_paper_content(md_path)
    print(f"✅ 提取成功\n")

    # 备份旧卡片
    old_dir = Path("output/zettelkasten_notes/zettel_Jones-2024_20251110_deepseek")
    if old_dir.exists() and not args.test_all:
        backup_dir = old_dir.parent / f"{old_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"💾 备份旧卡片: {backup_dir}")
        shutil.copytree(old_dir, backup_dir)
        print(f"✅ 备份完成\n")

    # 生成新卡片
    if args.test_all:
        test_multiple_llms(paper_data)
    else:
        output_dir = generate_with_llm(
            paper_data,
            llm_provider=args.provider,
            model=args.model,
            temperature=args.temperature
        )

        if output_dir:
            print("="*70)
            print("下一步:")
            print("="*70)
            print("1. 分析新卡片:")
            print("   python analyze_card_links.py")
            print("2. 查看报告:")
            print("   cat output/card_link_analysis_after.txt")

if __name__ == '__main__':
    main()
