#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zettelkasten 卡片生成命令行工具

從論文生成原子化知識卡片，支援：
- 自動入庫（知識庫整合）
- 跨論文連結
- 自訂需求檔案
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generators import SlideMaker
from generators.zettel_maker import ZettelMaker
from extractors import PDFExtractor
from knowledge_base import KnowledgeBaseManager
from jinja2 import Template


# 可用的詳細程度（5 種）
AVAILABLE_DETAILS = {
    'minimal': '極簡 - 5 張卡片',
    'brief': '簡要 - 8 張卡片',
    'standard': '標準 - 12 張卡片（預設）',
    'detailed': '詳細 - 20 張卡片',
    'comprehensive': '完整 - 30+ 張卡片'
}

# 可用的語言（3 種）
AVAILABLE_LANGUAGES = {
    'chinese': '繁體中文',
    'english': 'English',
    'bilingual': '中英雙語'
}


def _query_related_cards(paper_content: str, cite_key: str, limit: int = 10) -> list:
    """
    查詢知識庫中與當前論文相關的卡片（用於跨論文連結）

    Args:
        paper_content: 論文內容（用於語義搜索）
        cite_key: 當前論文 cite_key（用於排除同一論文的卡片）
        limit: 返回數量上限

    Returns:
        相關卡片列表
    """
    try:
        from integrations.vector_db import VectorDatabase
        from integrations.embedder import get_embedder

        vector_db = VectorDatabase()

        # 提取論文摘要（前 1000 字）用於查詢
        query_text = paper_content[:1000] if paper_content else ""

        if not query_text:
            return []

        # 生成查詢嵌入
        embedder = get_embedder(provider='google')
        query_embedding = embedder.embed(query_text, task_type="retrieval_query")

        # 向量搜索相似卡片
        results = vector_db.semantic_search_zettel(
            query_embedding=query_embedding,
            n_results=limit * 2
        )

        if not results or not results.get('ids') or not results['ids'][0]:
            return []

        # 過濾並構建結果
        related_cards = []
        for i, zettel_id in enumerate(results['ids'][0]):
            # 排除同一 cite_key 的卡片
            if not zettel_id.startswith(cite_key):
                metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                card = {
                    'zettel_id': zettel_id,
                    'title': metadata.get('title', 'Unknown'),
                    'core_concept': metadata.get('core_concept', ''),
                    'card_type': metadata.get('card_type', 'concept'),
                    'source_paper': zettel_id.split('-')[0] if '-' in zettel_id else 'Unknown'
                }
                related_cards.append(card)
                if len(related_cards) >= limit:
                    break

        return related_cards

    except Exception as e:
        print(f"  [WARN] 無法查詢相關卡片: {e}")
        return []


def _get_cite_key_or_fallback(paper_data: dict) -> str:
    """
    獲取論文的 cite_key（嚴格模式）

    Args:
        paper_data: 論文資料字典

    Returns:
        cite_key 字串

    Raises:
        ValueError: 如果缺少 cite_key
    """
    if paper_data.get('cite_key') and paper_data['cite_key'].strip():
        return paper_data['cite_key'].strip()

    paper_id = paper_data.get('id', '未知')
    raise ValueError(
        f"\n論文 ID {paper_id} 缺少 cite_key。\n"
        f"請執行以下命令修正：\n"
        f"  1. uv run kb check-cite-keys\n"
        f"  2. uv run kb update-from-bib 'My Library.bib'\n"
    )


def load_custom_requirements(custom_file: str = None, default_file: str = None) -> str | None:
    """
    載入自訂需求

    優先順序：
    1. custom_file（明確指定的檔案）
    2. default_file（預設檔案，若存在）

    Args:
        custom_file: 使用者指定的檔案路徑
        default_file: 預設檔案路徑

    Returns:
        自訂需求內容，或 None
    """
    # 1. 使用者指定的檔案
    if custom_file:
        path = Path(custom_file)
        if path.exists():
            print(f"📋 載入自訂需求：{path}")
            return path.read_text(encoding='utf-8')
        else:
            print(f"⚠️  警告：找不到自訂需求檔案 {path}")
            return None

    # 2. 預設檔案
    if default_file:
        path = Path(default_file)
        if path.exists():
            print(f"📋 載入預設需求：{path}")
            return path.read_text(encoding='utf-8')

    return None


def main():
    parser = argparse.ArgumentParser(
        description='Zettelkasten 卡片生成工具 - 從論文生成原子化知識卡片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方式：
  # 等效指令格式
  uv run zettel [選項]
  python generate_zettel.py [選項]

範例用法：
  # 從 PDF 生成卡片（自動入庫）
  uv run zettel --pdf paper.pdf

  # 從知識庫論文生成卡片
  uv run zettel --from-kb 1

  # 指定詳細程度
  uv run zettel --pdf paper.pdf --detail comprehensive

  # 使用自訂需求檔案
  uv run zettel --pdf paper.pdf --custom-file my_style.md

  # 跳過預設需求
  uv run zettel --pdf paper.pdf --no-custom

  # 不入庫（僅生成檔案）
  uv run zettel --pdf paper.pdf --no-add-to-kb

  # 啟用跨論文連結
  uv run zettel --pdf paper.pdf --cross-link
        """
    )

    # 內容來源（互斥）
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--pdf', type=str, help='PDF 檔案路徑')
    source_group.add_argument('--from-kb', type=int, metavar='PAPER_ID',
                              help='從知識庫中的論文 ID 生成')

    # 生成參數
    parser.add_argument('--detail', type=str, default='standard',
                        choices=AVAILABLE_DETAILS.keys(),
                        help='詳細程度（預設：standard）')
    parser.add_argument('--language', type=str, default='chinese',
                        choices=AVAILABLE_LANGUAGES.keys(),
                        help='語言模式（預設：chinese）')
    parser.add_argument('--domain', type=str, default='Research',
                        help='領域代碼（如 NeuroPsy、AI，預設：Research）')

    # 自訂需求
    parser.add_argument('--custom-file', type=str,
                        help='自訂需求檔案路徑（.txt 或 .md）')
    parser.add_argument('--no-custom', action='store_true',
                        help='忽略預設自訂需求檔案')

    # 知識庫整合
    parser.add_argument('--no-add-to-kb', action='store_true',
                        help='不將卡片加入知識庫（僅生成檔案）')
    parser.add_argument('--cross-link', action='store_true',
                        help='啟用跨論文連結（查詢知識庫相關概念）')

    # 向量嵌入
    parser.add_argument('--no-embed', action='store_true',
                        help='跳過向量嵌入（稍後用 uv run embeddings 補上）')

    # LLM 參數
    parser.add_argument('--model', type=str, default=None,
                        help='LLM 模型名稱（預設：自動選擇）')
    parser.add_argument('--llm-provider', type=str, default='auto',
                        choices=['auto', 'ollama', 'google', 'openai', 'anthropic'],
                        help='LLM 提供者（預設：auto）')
    parser.add_argument('--selection-strategy', type=str, default='balanced',
                        choices=['balanced', 'quality_first', 'cost_first', 'speed_first'],
                        help='模型選擇策略（預設：balanced）')

    # 輸出
    parser.add_argument('--output', type=str, help='輸出路徑（可選）')

    # 除錯
    parser.add_argument('--list-options', action='store_true',
                        help='列出所有可用選項')

    args = parser.parse_args()

    # 列出選項
    if args.list_options:
        print("\n📊 可用的詳細程度：")
        for key, desc in AVAILABLE_DETAILS.items():
            print(f"   • {key:15s} - {desc}")
        print("\n🌐 可用的語言模式：")
        for key, desc in AVAILABLE_LANGUAGES.items():
            print(f"   • {key:15s} - {desc}")
        print()
        return 0

    print("=" * 70)
    print("🗂️  Zettelkasten 卡片生成工具")
    print("=" * 70)

    # 載入自訂需求
    custom_requirements = None
    if not args.no_custom:
        custom_requirements = load_custom_requirements(
            custom_file=args.custom_file,
            default_file='config/custom_zettel.md'
        )

    print(f"\n詳細程度：{args.detail} - {AVAILABLE_DETAILS[args.detail]}")
    print(f"語言：{args.language} - {AVAILABLE_LANGUAGES[args.language]}")
    print(f"領域：{args.domain}")
    print(f"LLM 提供者：{args.llm_provider}")
    print(f"入庫：{'否' if args.no_add_to_kb else '是'}")
    print(f"跨論文連結：{'是' if args.cross_link else '否'}")
    if custom_requirements:
        print(f"自訂需求：已載入（{len(custom_requirements)} 字元）")

    print("\n" + "=" * 70)

    try:
        # 初始化生成器
        maker = SlideMaker(
            llm_provider=args.llm_provider,
            selection_strategy=args.selection_strategy
        )
        zettel_maker = ZettelMaker()

        # 準備內容
        pdf_content = None
        paper_data = None
        effective_topic = None

        # 從知識庫讀取
        if args.from_kb:
            print(f"\n📚 從知識庫讀取論文 ID {args.from_kb}...")
            kb = KnowledgeBaseManager()
            paper = kb.get_paper_by_id(args.from_kb)

            if not paper:
                print(f"\n❌ 錯誤：找不到論文 ID {args.from_kb}")
                print("💡 提示：使用 'uv run kb list' 查看所有論文")
                return 1

            paper_data = paper
            effective_topic = paper['title']

            # 讀取 Markdown 筆記
            md_path = Path(paper['file_path'])
            if md_path.exists():
                pdf_content = md_path.read_text(encoding='utf-8')
                print(f"✅ 成功讀取論文：{effective_topic}")
                print(f"   作者：{', '.join(paper['authors']) if paper['authors'] else '未知'}")
                print(f"   年份：{paper['year'] or '未知'}")
            else:
                print(f"⚠️  警告：找不到 Markdown 筆記，使用資料庫內容")
                authors_str = ', '.join(paper['authors']) if paper['authors'] else '未知'
                abstract = paper['abstract'] or '無摘要'
                pdf_content = f"# {paper['title']}\n\n作者：{authors_str}\n年份：{paper['year'] or '未知'}\n\n## 摘要\n{abstract}"

        # 從 PDF 讀取
        elif args.pdf:
            pdf_path = Path(args.pdf)
            if not pdf_path.exists():
                print(f"\n❌ 錯誤：找不到 PDF 檔案：{args.pdf}")
                return 1

            print(f"\n📄 正在提取 PDF 內容：{pdf_path.name}...")
            extractor = PDFExtractor(max_chars=40000)
            pdf_result = extractor.extract(str(pdf_path))
            pdf_content = pdf_result['full_text']
            effective_topic = pdf_result.get('title') or pdf_path.stem

            if pdf_result['truncated']:
                print(f"⚠️  警告：PDF 內容已截斷（{pdf_result['char_count']} → 40000 字元）")
            else:
                print(f"✅ 成功提取 {pdf_result['char_count']} 字元")

        # 獲取 cite_key
        if args.from_kb and paper_data:
            cite_key = _get_cite_key_or_fallback(paper_data)
        else:
            cite_key = Path(args.pdf).stem

        # 載入 Zettelkasten prompt 模板
        zettel_template_path = Path(__file__).parent / "templates" / "prompts" / "zettelkasten_template.jinja2"
        with open(zettel_template_path, 'r', encoding='utf-8') as f:
            zettel_template = Template(f.read())

        # 決定卡片數量
        style_config = zettel_maker.styles_config['styles']['zettelkasten']
        card_count = style_config['default_card_count'].get(args.detail, 12)

        # 查詢相關卡片（跨論文連結）
        related_cards = []
        if args.cross_link:
            print("\n🔍 查詢知識庫相關概念...")
            related_cards = _query_related_cards(
                paper_content=pdf_content,
                cite_key=cite_key,
                limit=10
            )
            if related_cards:
                print(f"  找到 {len(related_cards)} 個相關概念（將用於建立跨論文連結）")
            else:
                print("  未找到相關概念（將只建立論文內連結）")

        # 生成 prompt
        date_str = datetime.now().strftime("%Y%m%d")
        zettel_prompt = zettel_template.render(
            topic=effective_topic,
            pdf_content=pdf_content,
            card_count=card_count,
            domain=args.domain,
            date=date_str,
            cite_key=cite_key,
            language=args.language,
            existing_related_cards=related_cards,
            custom_requirements=custom_requirements  # 新增：自訂需求
        )

        # 調用 LLM
        print(f"\n🤖 正在生成 {card_count} 張原子筆記卡片...")
        llm_output, used_provider = maker.call_llm(zettel_prompt, model=args.model)
        print(f"✅ 使用 {used_provider} 生成完成")

        # 決定輸出目錄
        if args.output:
            output_dir = Path(args.output)
        elif args.from_kb and paper_data:
            output_dir = Path(f"output/zettelkasten_notes/zettel_{cite_key}_{date_str}")
        else:
            pdf_stem = Path(args.pdf).stem
            output_dir = Path(f"output/zettelkasten_notes/zettel_{pdf_stem}_{date_str}")

        # 準備論文資訊
        if paper_data:
            paper_info = {
                'title': paper_data['title'],
                'authors': ', '.join(paper_data.get('authors', [])),
                'year': paper_data.get('year', datetime.now().year),
                'paper_id': args.from_kb if args.from_kb else '',
                'cite_key': paper_data.get('cite_key', ''),
                'citation': paper_data['title']
            }
        else:
            paper_info = {
                'title': effective_topic,
                'authors': '',
                'year': datetime.now().year,
                'paper_id': '',
                'cite_key': cite_key,
                'citation': effective_topic
            }

        # 生成卡片
        result = zettel_maker.generate_zettelkasten(
            llm_output=llm_output,
            output_dir=output_dir,
            paper_info=paper_info
        )

        # 顯示結果
        print("\n" + "=" * 70)
        print("✅ Zettelkasten 原子筆記生成完成！")
        print("=" * 70)
        print(f"\n📁 輸出目錄：{result['output_dir']}")
        print(f"📄 索引文件：{result['index_file']}")
        print(f"🗂️  卡片數量：{result['card_count']}")
        print(f"📝 詳細程度：{args.detail}")
        print(f"🌐 語言模式：{args.language}")
        print(f"🤖 使用 LLM：{used_provider}")

        print("\n📚 生成的卡片文件：")
        for i, card_file in enumerate(result['card_files'][:5], 1):
            print(f"   {i}. {Path(card_file).name}")
        if len(result['card_files']) > 5:
            print(f"   ... 以及其他 {len(result['card_files']) - 5} 張卡片")

        # 入庫功能
        if not args.no_add_to_kb:
            print("\n📥 正在將卡片加入知識庫...")
            kb = KnowledgeBaseManager()

            # 獲取 paper_id（如果從知識庫生成）
            paper_id = args.from_kb if args.from_kb else None

            added_count = 0
            skipped_count = 0

            for card_file in result['card_files']:
                # 解析卡片
                card_data = kb.parse_zettel_card(card_file)
                if card_data:
                    # 添加到知識庫
                    add_result = kb.add_zettel_card(card_data)
                    if add_result.status == 'inserted':
                        added_count += 1
                        # 建立論文-卡片關聯
                        if paper_id and add_result.card_id > 0:
                            kb.link_paper_to_zettel(paper_id, add_result.card_id, 1.0)
                    elif add_result.status == 'duplicate':
                        skipped_count += 1

            print(f"   ✅ 新增 {added_count} 張卡片")
            if skipped_count > 0:
                print(f"   ⏭️  跳過 {skipped_count} 張重複卡片")

        # 向量嵌入
        if not args.no_embed and not args.no_add_to_kb:
            try:
                from integrations.vector_db import VectorDatabase
                from integrations.embedder import get_embedder

                print("\n📊 正在生成向量嵌入...")
                vector_db = VectorDatabase()
                embedder = get_embedder(provider='google')

                embedded_count = 0
                for card_file in result['card_files']:
                    card_data = kb.parse_zettel_card(card_file)
                    if card_data and card_data.get('content'):
                        # 生成嵌入
                        embedding = embedder.embed(
                            card_data['content'][:2000],
                            task_type="retrieval_document"
                        )
                        # 存入向量庫
                        vector_db.upsert_zettel(
                            embeddings=[embedding],
                            documents=[card_data['content'][:2000]],
                            ids=[card_data['zettel_id']],
                            metadatas=[{
                                'title': card_data.get('title', ''),
                                'core_concept': card_data.get('core_concept', ''),
                                'card_type': card_data.get('card_type', 'concept'),
                                'cite_key': cite_key
                            }]
                        )
                        embedded_count += 1

                print(f"   ✅ 嵌入 {embedded_count} 張卡片")

            except Exception as e:
                print(f"   ⚠️  向量嵌入失敗：{e}")
                print("   💡 可稍後執行 uv run embeddings 補上")

        return 0

    except ImportError as e:
        print(f"\n❌ 缺少必要的套件：{e}")
        print("💡 提示：請運行 uv sync")
        return 1

    except FileNotFoundError as e:
        print(f"\n❌ 找不到文件：{e}")
        return 1

    except ValueError as e:
        print(f"\n❌ 參數錯誤：{e}")
        return 1

    except Exception as e:
        print(f"\n❌ 未預期的錯誤：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
