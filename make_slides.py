#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投影片生成命令行工具
基於Journal Club架構的多風格學術簡報生成
"""

import sys
import argparse
from pathlib import Path

# 設置UTF-8編碼（Windows相容性）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加src到路徑
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generators import SlideMaker
from extractors import PDFExtractor
from knowledge_base import KnowledgeBaseManager
import subprocess
import json


# 可用的學術風格（8種）
AVAILABLE_STYLES = {
    'classic_academic': '經典學術 - 傳統學術語言，強調理論和研究方法',
    'modern_academic': '現代學術 - 結合視覺化和數據，清晰易懂',
    'clinical': '臨床導向 - 強調臨床應用和病例分析',
    'research_methods': '研究方法 - 著重研究設計和統計分析',
    'literature_review': '文獻回顧 - 系統性文獻整理，比較不同研究',
    'case_analysis': '案例分析 - 以具體案例為主，深入分析個案',
    'teaching': '教學導向 - 循序漸進易懂，適合學習者',
    'zettelkasten': 'Zettelkasten卡片盒 - 原子化筆記，每張投影片為獨立知識單元'
}

# 可用的詳細程度（5種）
AVAILABLE_DETAILS = {
    'minimal': '極簡 - 2-3個重點/張，1句話/點',
    'brief': '簡要 - 3-4個重點/張，1-2句話/點',
    'standard': '標準 - 4-5個重點/張，2-3句話/點（Journal Club格式）',
    'detailed': '詳細 - 5-6個重點/張，3-4句話/點',
    'comprehensive': '完整 - 6-8個重點/張，4-5句話/點'
}

# 可用的語言（3種）
AVAILABLE_LANGUAGES = {
    'chinese': '繁體中文',
    'english': 'English',
    'bilingual': '中英雙語'
}


def print_available_options():
    """顯示所有可用選項"""
    print("\n📚 可用的學術風格：")
    for key, desc in AVAILABLE_STYLES.items():
        print(f"   • {key:20s} - {desc}")

    print("\n📊 可用的詳細程度：")
    for key, desc in AVAILABLE_DETAILS.items():
        print(f"   • {key:15s} - {desc}")

    print("\n🌐 可用的語言模式：")
    for key, desc in AVAILABLE_LANGUAGES.items():
        print(f"   • {key:15s} - {desc}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='投影片生成工具 - 支援8種學術風格、5種詳細程度、3種語言',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法：
  # 基本用法：生成現代學術風格的投影片
  python make_slides.py "深度學習應用" --style modern_academic --slides 15

  # 從PDF生成投影片（直接提取文字）
  python make_slides.py "論文摘要" --pdf paper.pdf --style research_methods

  # 先分析PDF並加入知識庫，再從結構化內容生成投影片
  python make_slides.py "論文摘要" --pdf paper.pdf --analyze-first --style research_methods

  # 從知識庫已有的論文生成投影片
  python make_slides.py "論文簡報" --from-kb 1 --style modern_academic

  # 使用Zettelkasten原子筆記風格生成Markdown（自動強制）
  python make_slides.py "知識管理系統" --pdf paper.pdf --style zettelkasten --domain AI

  # 生成雙語教學投影片
  python make_slides.py "機器學習入門" --style teaching --language bilingual --slides 20

  # 生成Markdown簡報格式（支援Marp/reveal.js）
  python make_slides.py "深度學習" --pdf paper.pdf --format markdown --style modern_academic

  # 同時生成PPTX和Markdown
  python make_slides.py "研究方法" --pdf paper.pdf --format both --style research_methods

  # 列出所有可用選項
  python make_slides.py --list-options
        """
    )

    parser.add_argument('topic', nargs='?', help='簡報主題')
    parser.add_argument('--pdf', type=str, help='PDF文件路徑（可選）')
    parser.add_argument('--analyze-first', action='store_true',
                       help='先分析PDF並加入知識庫，再從結構化內容生成投影片')
    parser.add_argument('--from-kb', type=int, metavar='PAPER_ID',
                       help='從知識庫中已有的論文ID生成投影片（不需要--pdf）')
    parser.add_argument('--style', type=str, default='modern_academic',
                       choices=AVAILABLE_STYLES.keys(),
                       help='學術風格（預設：modern_academic）')
    parser.add_argument('--detail', type=str, default='standard',
                       choices=AVAILABLE_DETAILS.keys(),
                       help='詳細程度（預設：standard）')
    parser.add_argument('--language', type=str, default='chinese',
                       choices=AVAILABLE_LANGUAGES.keys(),
                       help='語言模式（預設：chinese）')
    parser.add_argument('--slides', type=int, default=15,
                       help='投影片數量（預設：15）')
    parser.add_argument('--output', type=str, help='輸出路徑（可選）')
    parser.add_argument('--format', type=str, default='pptx',
                       choices=['pptx', 'markdown', 'both'],
                       help='輸出格式：pptx(PowerPoint)、markdown或both（預設：pptx）')
    parser.add_argument('--domain', type=str, default='Research',
                       help='領域代碼（Zettelkasten用，如NeuroPsy、AI、CompBio等，預設：Research）')
    parser.add_argument('--model', type=str, default='gpt-oss:20b-cloud',
                       help='LLM模型名稱（預設：gpt-oss:20b-cloud for Ollama Cloud）')
    parser.add_argument('--llm-provider', type=str, default='auto',
                       choices=['auto', 'ollama', 'google', 'openai', 'anthropic'],
                       help='LLM提供者（預設：auto自動選擇）')
    parser.add_argument('--api-key', type=str,
                       help='API金鑰（Google/OpenAI/Anthropic用，或設置環境變數）')
    parser.add_argument('--ollama-url', type=str, default='http://localhost:11434',
                       help='Ollama API地址（預設：http://localhost:11434）')
    parser.add_argument('--custom', type=str, help='自訂要求（可選）')
    parser.add_argument('--list-options', action='store_true',
                       help='列出所有可用的風格、詳細程度和語言選項')

    # 自動模型選擇參數
    parser.add_argument('--selection-strategy', type=str, default='balanced',
                       choices=['balanced', 'quality_first', 'cost_first', 'speed_first'],
                       help='模型選擇策略：balanced(平衡)、quality_first(品質優先)、cost_first(成本優先)、speed_first(速度優先)，預設：balanced')
    parser.add_argument('--max-cost', type=float,
                       help='單次會話最高成本限制（美元），超過後自動切換到免費模型')
    parser.add_argument('--usage-report', action='store_true',
                       help='生成使用報告（每日和週報）')
    parser.add_argument('--monitor', action='store_true',
                       help='啟用詳細的模型監控和成本追蹤')

    args = parser.parse_args()

    # 如果只是列出選項
    if args.list_options:
        print_available_options()
        return 0

    # 檢查參數邏輯
    if not args.topic and not args.from_kb:
        parser.print_help()
        print("\n❌ 錯誤：請提供簡報主題或使用 --from-kb 從知識庫生成")
        print("💡 提示：使用 --list-options 查看所有可用選項")
        return 1

    if args.from_kb and args.pdf:
        print("\n❌ 錯誤：--from-kb 和 --pdf 不能同時使用")
        print("💡 提示：--from-kb 會從知識庫讀取論文內容")
        return 1

    if args.analyze_first and not args.pdf:
        print("\n❌ 錯誤：--analyze-first 需要配合 --pdf 使用")
        return 1

    print("=" * 70)
    print("📊 投影片生成工具")
    print("=" * 70)
    print(f"\n主題：{args.topic or '（從知識庫論文標題）'}")
    print(f"風格：{args.style} - {AVAILABLE_STYLES[args.style]}")
    print(f"詳細程度：{args.detail} - {AVAILABLE_DETAILS[args.detail]}")
    print(f"語言：{args.language} - {AVAILABLE_LANGUAGES[args.language]}")
    print(f"投影片數：{args.slides}")
    print(f"LLM模型：{args.model}")
    print(f"LLM提供者：{args.llm_provider}")
    if args.llm_provider == 'auto':
        print(f"選擇策略：{args.selection_strategy}")
    if args.max_cost:
        print(f"成本限制：${args.max_cost:.2f}")
    if args.monitor:
        print(f"監控模式：已啟用")

    if args.from_kb:
        print(f"知識庫來源：論文ID {args.from_kb}")
    elif args.pdf:
        print(f"PDF來源：{args.pdf}")
        if args.analyze_first:
            print(f"工作流：先分析並加入知識庫 → 從結構化內容生成投影片")

    if args.custom:
        print(f"自訂要求：{args.custom}")

    print("\n" + "=" * 70)

    try:
        # 初始化投影片生成器
        maker = SlideMaker(
            llm_provider=args.llm_provider,
            ollama_url=args.ollama_url,
            api_key=args.api_key,
            selection_strategy=args.selection_strategy,
            max_cost=args.max_cost,
            enable_monitoring=args.monitor
        )

        # 準備內容和主題
        pdf_content = None
        effective_topic = args.topic

        # 情況1：從知識庫讀取論文
        if args.from_kb:
            print(f"\n📚 正在從知識庫讀取論文 ID {args.from_kb}...")
            kb = KnowledgeBaseManager()

            # 查詢論文資訊
            paper = kb.get_paper_by_id(args.from_kb)
            if not paper:
                print(f"\n❌ 錯誤：找不到論文ID {args.from_kb}")
                print("💡 提示：使用 'python kb_manage.py list' 查看所有論文")
                return 1

            effective_topic = paper['title']

            # 讀取 Markdown 筆記內容（結構化）
            md_path = Path(paper['file_path'])
            if md_path.exists():
                with open(md_path, 'r', encoding='utf-8') as f:
                    pdf_content = f.read()
                print(f"✅ 成功讀取論文：{effective_topic}")
                print(f"   作者：{', '.join(paper['authors']) if paper['authors'] else '未知'}")
                print(f"   年份：{paper['year'] or '未知'}")
            else:
                print(f"⚠️  警告：找不到Markdown筆記，使用資料庫內容")
                authors_str = ', '.join(paper['authors']) if paper['authors'] else '未知'
                abstract = paper['abstract'] or '無摘要'
                pdf_content = f"# {paper['title']}\n\n作者：{authors_str}\n年份：{paper['year'] or '未知'}\n\n## 摘要\n{abstract}"

        # 情況2：先分析PDF並加入知識庫
        elif args.analyze_first and args.pdf:
            pdf_path = Path(args.pdf)
            if not pdf_path.exists():
                print(f"\n❌ 錯誤：找不到PDF文件：{args.pdf}")
                return 1

            print(f"\n📄 步驟1：分析PDF並加入知識庫...")
            # 調用 analyze_paper.py
            result = subprocess.run(
                [sys.executable, 'analyze_paper.py', str(pdf_path), '--add-to-kb', '--format', 'json'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode != 0:
                print(f"❌ analyze_paper.py 執行失敗：")
                print(result.stderr)
                return 1

            print(f"✅ 論文已加入知識庫")

            # 從輸出中提取 paper_id 和 file_hash
            output_lines = result.stdout.strip().split('\n')
            paper_id = None
            file_hash = None

            for line in output_lines:
                if 'paper_id' in line.lower() or '論文ID' in line:
                    # 嘗試提取數字
                    import re
                    match = re.search(r'(\d+)', line)
                    if match:
                        paper_id = int(match.group(1))
                elif 'file_hash' in line.lower() or '文件雜湊' in line:
                    match = re.search(r'([a-f0-9]{32})', line)
                    if match:
                        file_hash = match.group(1)

            print(f"\n📚 步驟2：從結構化內容生成投影片...")

            # 讀取生成的 Markdown 筆記
            if file_hash:
                md_path = Path('knowledge_base') / 'papers' / f"{file_hash}.md"
                if md_path.exists():
                    with open(md_path, 'r', encoding='utf-8') as f:
                        pdf_content = f.read()
                    print(f"✅ 使用結構化Markdown內容")
                else:
                    print(f"⚠️  找不到Markdown，回退到直接提取")
                    extractor = PDFExtractor(max_chars=10000)
                    pdf_result = extractor.extract(str(pdf_path))
                    pdf_content = pdf_result['full_text']
            else:
                # 回退方案：直接提取
                print(f"⚠️  無法獲取file_hash，回退到直接提取")
                extractor = PDFExtractor(max_chars=10000)
                pdf_result = extractor.extract(str(pdf_path))
                pdf_content = pdf_result['full_text']

        # 情況3：直接從PDF提取（原有流程）
        elif args.pdf:
            pdf_path = Path(args.pdf)
            if not pdf_path.exists():
                print(f"\n❌ 錯誤：找不到PDF文件：{args.pdf}")
                return 1

            print(f"\n📄 正在提取PDF內容：{pdf_path.name}...")
            extractor = PDFExtractor(max_chars=10000)  # Journal Club限制
            pdf_result = extractor.extract(str(pdf_path))
            pdf_content = pdf_result['full_text']

            if pdf_result['truncated']:
                print(f"⚠️  警告：PDF內容已截斷（{pdf_result['char_count']} 字元 -> 10000 字元）")
            else:
                print(f"✅ 成功提取 {pdf_result['char_count']} 字元")

        # Zettelkasten模式：使用專用生成器
        if args.style == 'zettelkasten':
            print("\n🗂️  啟用Zettelkasten原子筆記模式...")
            from generators.zettel_maker import ZettelMaker
            from jinja2 import Template
            from datetime import datetime

            zettel_maker = ZettelMaker()

            # 載入Zettelkasten prompt模板
            zettel_template_path = Path(__file__).parent / "templates" / "prompts" / "zettelkasten_template.jinja2"
            with open(zettel_template_path, 'r', encoding='utf-8') as f:
                zettel_template = Template(f.read())

            # 決定卡片數量
            style_config = zettel_maker.styles_config['styles']['zettelkasten']
            card_count = style_config['default_card_count'].get(args.detail, 12)

            # 生成prompt
            date_str = datetime.now().strftime("%Y%m%d")
            zettel_prompt = zettel_template.render(
                topic=effective_topic,
                pdf_content=pdf_content,
                card_count=card_count,
                domain=args.domain,
                date=date_str,
                language=args.language
            )

            # 調用LLM
            print(f"🤖 正在生成{card_count}張原子筆記卡片...")
            llm_output, used_provider = maker.call_llm(zettel_prompt, model=args.model)
            print(f"✅ 使用 {used_provider} 生成完成")

            # 解析並生成卡片
            # 使用PDF檔名而非domain來命名資料夾（每篇PDF獨立）
            if args.output:
                output_dir = Path(args.output)
            elif args.pdf:
                pdf_stem = Path(args.pdf).stem
                output_dir = Path(f"output/zettelkasten_notes/zettel_{pdf_stem}_{date_str}")
            else:
                # 回退：沒有PDF時使用domain
                output_dir = Path(f"output/zettelkasten_notes/zettel_{args.domain}_{date_str}")
            paper_info = {
                'title': effective_topic,
                'authors': '',
                'year': datetime.now().year,
                'paper_id': args.from_kb if args.from_kb else '',
                'citation': effective_topic
            }

            result = zettel_maker.generate_zettelkasten(
                llm_output=llm_output,
                output_dir=output_dir,
                paper_info=paper_info
            )

            # 添加額外信息
            result['style'] = args.style
            result['detail_level'] = args.detail
            result['language'] = args.language
            result['llm_provider'] = used_provider
            result['output_format'] = 'zettelkasten_markdown'

        # 一般模式：投影片生成
        else:
            # 決定輸出格式（Zettelkasten強制Markdown）
            output_format = args.format
            if args.style == 'zettelkasten' and output_format == 'pptx':
                output_format = 'markdown'
                print("ℹ️  Zettelkasten風格自動切換為Markdown輸出")

            result = maker.generate_slides(
                topic=effective_topic,
                style=args.style,
                detail_level=args.detail,
                language=args.language,
                slide_count=args.slides,
                output_path=args.output,
                output_format=output_format,
                pdf_content=pdf_content,
                custom_requirements=args.custom,
                model=args.model
            )

        # 顯示結果
        print("\n" + "=" * 70)

        if args.style == 'zettelkasten':
            print("✅ Zettelkasten原子筆記生成完成！")
            print("=" * 70)
            print(f"\n📁 輸出目錄：{result['output_dir']}")
            print(f"📄 索引文件：{result['index_file']}")
            print(f"🗂️  卡片數量：{result['card_count']}")
            print(f"🎨 學術風格：{result['style']}")
            print(f"📝 詳細程度：{result['detail_level']}")
            print(f"🌐 語言模式：{result['language']}")
            print(f"🤖 使用LLM：{result.get('llm_provider', '未知')}")

            print("\n📚 生成的卡片文件：")
            for i, card_file in enumerate(result['card_files'][:5], 1):
                print(f"   {i}. {Path(card_file).name}")
            if len(result['card_files']) > 5:
                print(f"   ... 以及其他 {len(result['card_files']) - 5} 張卡片")

        else:
            print("✅ 投影片生成完成！")
            print("=" * 70)

            # 顯示輸出文件
            if isinstance(result.get('output_files'), list):
                print(f"\n📁 輸出文件：")
                for file in result['output_files']:
                    file_type = "PPTX" if file.endswith('.pptx') else "Markdown"
                    print(f"   • {file_type}: {file}")
            else:
                print(f"\n📁 輸出文件：{result['output_path']}")

            print(f"📊 投影片數量：{result.get('slide_count', '未知')}")
            print(f"🎨 學術風格：{result['style']}")
            print(f"📝 詳細程度：{result['detail_level']}")
            print(f"🌐 語言模式：{result['language']}")
            print(f"📄 輸出格式：{result.get('output_format', args.format)}")
            print(f"🤖 使用LLM：{result.get('llm_provider', '未知')}")

            if result.get('llm_output'):
                print("\n💡 LLM輸出預覽：")
                print("-" * 70)
                print(result['llm_output'][:300] + "...")
                print("-" * 70)

        # 生成使用報告（如果請求）
        if args.usage_report:
            print("\n" + "=" * 70)
            print("📊 生成使用報告...")
            print("=" * 70)

            from utils.usage_reporter import UsageReporter
            reporter = UsageReporter()

            # 生成今日報告
            daily_report = reporter.generate_daily_report()
            print("\n今日使用報告：")
            print("-" * 70)
            print(daily_report)

            # 保存報告
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            reporter.save_report(daily_report, f"daily_{date_str}.md")

            # 生成週報告
            weekly_report = reporter.generate_weekly_report()
            reporter.save_report(weekly_report, f"weekly_{date_str}.md")
            print("\n✅ 報告已保存到 logs/model_usage/reports/ 目錄")

        # 顯示監控摘要（如果啟用）
        if args.monitor and hasattr(maker, 'model_monitor') and maker.model_monitor:
            print("\n" + "=" * 70)
            print("📊 模型使用監控摘要")
            print("=" * 70)

            cost_status = maker.model_monitor.check_cost_status()
            if cost_status.get('controlled'):
                session_info = cost_status['session']
                daily_info = cost_status['daily']

                print(f"\n💰 成本追蹤：")
                print(f"   • 會話成本: ${session_info['cost']:.4f} / ${session_info['limit']:.2f}")
                print(f"   • 今日成本: ${daily_info['cost']:.4f} / ${daily_info['limit']:.2f}")

                if session_info.get('warning'):
                    print("   ⚠️  會話成本接近限制！")
                if daily_info.get('warning'):
                    print("   ⚠️  今日成本接近限制！")

            # 顯示模型切換建議
            if hasattr(maker, 'last_provider') and hasattr(maker, 'last_model'):
                suggestion = maker.model_monitor.suggest_model_switch(
                    maker.last_model,
                    maker.last_provider,
                    task_type='academic_slides'
                )
                if suggestion:
                    print(f"\n💡 模型切換建議：")
                    print(f"   {suggestion['suggestion']}")

        return 0

    except ImportError as e:
        print(f"\n❌ 缺少必要的套件：{e}")
        print("💡 提示：請運行 pip install -r requirements.txt")
        return 1

    except FileNotFoundError as e:
        print(f"\n❌ 找不到文件：{e}")
        return 1

    except ValueError as e:
        print(f"\n❌ 參數錯誤：{e}")
        return 1

    except RuntimeError as e:
        print(f"\n❌ 執行錯誤：{e}")
        print("💡 提示：請確認Ollama服務正在運行（http://localhost:11434）")
        print("   或使用 --ollama-url 指定正確的API地址")
        return 1

    except Exception as e:
        print(f"\n❌ 未預期的錯誤：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
