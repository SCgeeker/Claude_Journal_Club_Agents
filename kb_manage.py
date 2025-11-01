#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識庫管理命令行工具
使用方式: python kb_manage.py <command> [options]
"""

import sys
import argparse
from pathlib import Path

# 設置UTF-8編碼（Windows相容性）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

from src.knowledge_base import KnowledgeBaseManager
from src.embeddings.providers import GeminiEmbedder, OllamaEmbedder
from src.embeddings.vector_db import VectorDatabase


def cmd_stats(args):
    """顯示知識庫統計信息"""
    kb = KnowledgeBaseManager()
    stats = kb.get_stats()

    print("\n" + "=" * 60)
    print("📊 知識庫統計")
    print("=" * 60)
    print(f"論文總數: {stats['total_papers']}")
    print(f"主題總數: {stats['total_topics']}")
    print(f"引用總數: {stats['total_citations']}")
    print("=" * 60 + "\n")


def cmd_list(args):
    """列出所有論文"""
    kb = KnowledgeBaseManager()
    papers = kb.list_papers(limit=args.limit)

    print("\n" + "=" * 60)
    print(f"📄 論文列表 (最多 {args.limit} 篇)")
    print("=" * 60)

    if papers:
        for paper in papers:
            print(f"\n[ID: {paper['id']}] {paper['title']}")
            print(f"  作者: {', '.join(paper['authors'][:3])}")
            if len(paper['authors']) > 3:
                print(f"        (+{len(paper['authors'])-3} 位)")
            print(f"  年份: {paper['year'] or '未知'}")
            if paper['keywords']:
                print(f"  關鍵詞: {', '.join(paper['keywords'][:5])}")
            print(f"  時間: {paper['created_at']}")
    else:
        print("\n⚠️  知識庫中還沒有論文")

    print("\n" + "=" * 60 + "\n")


def cmd_search(args):
    """搜索論文"""
    kb = KnowledgeBaseManager()
    results = kb.search_papers(args.query, limit=args.limit)

    print("\n" + "=" * 60)
    print(f"🔍 搜索: '{args.query}'")
    print("=" * 60)

    if results:
        print(f"\n找到 {len(results)} 個結果:\n")
        for i, paper in enumerate(results, 1):
            print(f"{i}. [ID: {paper['id']}] {paper['title']}")
            print(f"   作者: {', '.join(paper['authors'][:3])}")
            print(f"   年份: {paper['year'] or '未知'}")
            if paper['abstract']:
                preview = paper['abstract'][:100].replace('\n', ' ')
                print(f"   摘要: {preview}...")
            print()
    else:
        print(f"\n❌ 未找到包含 '{args.query}' 的論文\n")

    print("=" * 60 + "\n")


def cmd_show(args):
    """顯示論文詳情"""
    kb = KnowledgeBaseManager()
    paper = kb.get_paper_by_id(args.id)

    print("\n" + "=" * 60)
    print(f"📄 論文詳情 (ID: {args.id})")
    print("=" * 60)

    if paper:
        print(f"\n標題: {paper['title']}")
        print(f"作者: {', '.join(paper['authors'])}")
        print(f"年份: {paper['year'] or '未知'}")
        print(f"檔案: {paper['file_path']}")
        print(f"創建: {paper['created_at']}")
        print(f"更新: {paper['updated_at']}")

        if paper['keywords']:
            print(f"關鍵詞: {', '.join(paper['keywords'])}")

        if paper['abstract']:
            print(f"\n摘要:")
            print(f"{paper['abstract'][:500]}")
            if len(paper['abstract']) > 500:
                print("...")
    else:
        print(f"\n❌ 找不到ID為 {args.id} 的論文")

    print("\n" + "=" * 60 + "\n")


def cmd_add_topic(args):
    """創建主題"""
    kb = KnowledgeBaseManager()
    topic_id = kb.add_topic(args.name, args.description)

    print("\n" + "=" * 60)
    print("🏷️  創建主題")
    print("=" * 60)
    print(f"名稱: {args.name}")
    print(f"描述: {args.description}")
    print(f"ID: {topic_id}")
    print("=" * 60 + "\n")


def cmd_link(args):
    """連結論文到主題"""
    kb = KnowledgeBaseManager()
    kb.link_paper_to_topic(args.paper_id, args.topic_id, args.relevance)

    print("\n" + "=" * 60)
    print("🔗 連結論文與主題")
    print("=" * 60)
    print(f"論文ID: {args.paper_id}")
    print(f"主題ID: {args.topic_id}")
    print(f"相關度: {args.relevance}")
    print("✅ 連結成功")
    print("=" * 60 + "\n")


def cmd_topic_papers(args):
    """按主題查看論文"""
    kb = KnowledgeBaseManager()
    papers = kb.get_papers_by_topic(args.name)

    print("\n" + "=" * 60)
    print(f"🏷️  主題: {args.name}")
    print("=" * 60)

    if papers:
        print(f"\n找到 {len(papers)} 篇論文:\n")
        for paper in papers:
            print(f"[ID: {paper['id']}] {paper['title']}")
            print(f"  作者: {', '.join(paper['authors'][:3])}")
            print(f"  相關度: {paper['relevance']:.2f}")
            print()
    else:
        print(f"\n⚠️  主題 '{args.name}' 下沒有論文\n")

    print("=" * 60 + "\n")


def cmd_cite(args):
    """添加引用關係"""
    kb = KnowledgeBaseManager()
    kb.add_citation(args.source, args.target, args.type)

    print("\n" + "=" * 60)
    print("📚 添加引用關係")
    print("=" * 60)
    print(f"來源論文ID: {args.source}")
    print(f"目標論文ID: {args.target}")
    print(f"引用類型: {args.type}")
    print("✅ 引用關係已添加")
    print("=" * 60 + "\n")


def cmd_semantic_search(args):
    """語義搜索論文或Zettelkasten卡片"""
    # 初始化
    if args.provider == "gemini":
        embedder = GeminiEmbedder()
    else:
        embedder = OllamaEmbedder()

    vector_db = VectorDatabase()
    kb = KnowledgeBaseManager()

    print("\n" + "=" * 60)
    print(f"🔍 語義搜索: '{args.query}'")
    print(f"提供者: {args.provider.upper()}")
    print("=" * 60)

    # 生成查詢向量
    print("\n生成查詢向量...")
    query_embedding = embedder.embed(args.query, task_type="retrieval_query")

    # 搜索論文
    if args.type in ['papers', 'all']:
        print(f"\n📄 搜索論文 (top {args.limit}):")
        print("-" * 60)

        results = vector_db.semantic_search_papers(
            query_embedding=query_embedding,
            n_results=args.limit
        )

        if results['ids'] and len(results['ids'][0]) > 0:
            for i, (paper_id, distance) in enumerate(zip(results['ids'][0], results['distances'][0])):
                metadata = results['metadatas'][0][i]
                similarity = (1 - distance) * 100  # 轉換為百分比

                # 從知識庫獲取完整信息
                pid = int(paper_id.replace('paper_', ''))
                paper = kb.get_paper_by_id(pid)

                if paper:
                    print(f"\n{i+1}. [{similarity:.1f}%] {paper['title']}")
                    print(f"   ID: {pid}")
                    print(f"   作者: {', '.join(paper['authors'][:3])}")
                    if len(paper['authors']) > 3:
                        print(f"         (+{len(paper['authors'])-3} 位)")
                    print(f"   年份: {paper['year'] or '未知'}")

                    if args.verbose and paper['abstract']:
                        preview = paper['abstract'][:150].replace('\n', ' ')
                        print(f"   摘要: {preview}...")
        else:
            print("\n未找到相關論文")

    # 搜索Zettelkasten
    if args.type in ['zettel', 'all']:
        print(f"\n🗂️  搜索 Zettelkasten 卡片 (top {args.limit}):")
        print("-" * 60)

        results = vector_db.semantic_search_zettel(
            query_embedding=query_embedding,
            n_results=args.limit
        )

        if results['ids'] and len(results['ids'][0]) > 0:
            for i, (zettel_id, distance) in enumerate(zip(results['ids'][0], results['distances'][0])):
                metadata = results['metadatas'][0][i]
                similarity = (1 - distance) * 100
                title = metadata.get('title', 'Unknown')

                print(f"\n{i+1}. [{similarity:.1f}%] {title}")
                print(f"   ID: {zettel_id}")

                if args.verbose:
                    doc = results['documents'][0][i]
                    preview = doc[:150].replace('\n', ' ')
                    print(f"   內容: {preview}...")
        else:
            print("\n未找到相關卡片")

    print("\n" + "=" * 60 + "\n")


def cmd_similar(args):
    """尋找相似的論文或Zettelkasten卡片"""
    vector_db = VectorDatabase()
    kb = KnowledgeBaseManager()

    print("\n" + "=" * 60)

    # 判斷是論文還是Zettelkasten
    if args.id.startswith('paper_') or args.id.isdigit():
        # 論文
        paper_id = f"paper_{args.id}" if args.id.isdigit() else args.id
        pid = int(paper_id.replace('paper_', ''))

        paper = kb.get_paper_by_id(pid)
        if not paper:
            print(f"❌ 找不到論文 ID: {args.id}")
            print("=" * 60 + "\n")
            return

        print(f"🔍 尋找與論文相似的內容")
        print(f"論文: {paper['title']}")
        print("=" * 60)

        # 尋找相似論文
        results = vector_db.find_similar_papers(
            paper_id=paper_id,
            n_results=args.limit,
            exclude_self=True
        )

        if results['ids'] and len(results['ids'][0]) > 0:
            print(f"\n📄 相似論文 (top {args.limit}):")
            print("-" * 60)

            for i, (sim_id, distance) in enumerate(zip(results['ids'][0], results['distances'][0])):
                similarity = (1 - distance) * 100
                sim_pid = int(sim_id.replace('paper_', ''))
                sim_paper = kb.get_paper_by_id(sim_pid)

                if sim_paper:
                    print(f"\n{i+1}. [{similarity:.1f}%] {sim_paper['title']}")
                    print(f"   ID: {sim_pid}")
                    print(f"   作者: {', '.join(sim_paper['authors'][:3])}")
        else:
            print("\n未找到相似論文")

    else:
        # Zettelkasten
        zettel_id = args.id

        print(f"🔍 尋找與卡片相似的內容")
        print(f"卡片 ID: {zettel_id}")
        print("=" * 60)

        # 尋找相似卡片
        results = vector_db.find_similar_zettel(
            zettel_id=zettel_id,
            n_results=args.limit,
            exclude_self=True
        )

        if results['ids'] and len(results['ids'][0]) > 0:
            print(f"\n🗂️  相似卡片 (top {args.limit}):")
            print("-" * 60)

            for i, (sim_id, distance) in enumerate(zip(results['ids'][0], results['distances'][0])):
                similarity = (1 - distance) * 100
                metadata = results['metadatas'][0][i]
                title = metadata.get('title', 'Unknown')

                print(f"\n{i+1}. [{similarity:.1f}%] {title}")
                print(f"   ID: {sim_id}")
        else:
            print("\n未找到相似卡片")

    print("\n" + "=" * 60 + "\n")


def cmd_hybrid_search(args):
    """混合搜索：結合全文搜索和語義搜索"""
    # 初始化
    if args.provider == "gemini":
        embedder = GeminiEmbedder()
    else:
        embedder = OllamaEmbedder()

    vector_db = VectorDatabase()
    kb = KnowledgeBaseManager()

    print("\n" + "=" * 60)
    print(f"🔍 混合搜索: '{args.query}'")
    print(f"提供者: {args.provider.upper()}")
    print("=" * 60)

    # 1. 全文搜索
    print("\n📝 全文搜索結果:")
    print("-" * 60)
    fts_results = kb.search_papers(args.query, limit=args.limit)
    fts_ids = set()

    if fts_results:
        for i, paper in enumerate(fts_results, 1):
            fts_ids.add(paper['id'])
            print(f"{i}. [FTS] {paper['title']}")
            print(f"   ID: {paper['id']}")
    else:
        print("未找到結果")

    # 2. 語義搜索
    print(f"\n🔍 語義搜索結果:")
    print("-" * 60)
    print("生成查詢向量...")
    query_embedding = embedder.embed(args.query, task_type="retrieval_query")

    sem_results = vector_db.semantic_search_papers(
        query_embedding=query_embedding,
        n_results=args.limit
    )

    sem_ids = set()
    sem_scores = {}

    if sem_results['ids'] and len(sem_results['ids'][0]) > 0:
        for i, (paper_id, distance) in enumerate(zip(sem_results['ids'][0], sem_results['distances'][0])):
            pid = int(paper_id.replace('paper_', ''))
            similarity = (1 - distance) * 100
            sem_ids.add(pid)
            sem_scores[pid] = similarity

            paper = kb.get_paper_by_id(pid)
            if paper:
                print(f"{i+1}. [{similarity:.1f}%] {paper['title']}")
                print(f"   ID: {pid}")
    else:
        print("未找到結果")

    # 3. 混合結果
    print(f"\n✨ 混合結果 (兩種方法的聯集):")
    print("-" * 60)

    all_ids = fts_ids | sem_ids
    both_ids = fts_ids & sem_ids

    if all_ids:
        # 按語義相似度排序
        sorted_ids = sorted(all_ids,
                          key=lambda x: sem_scores.get(x, 0),
                          reverse=True)[:args.limit]

        for i, pid in enumerate(sorted_ids, 1):
            paper = kb.get_paper_by_id(pid)
            if paper:
                tags = []
                if pid in fts_ids:
                    tags.append("FTS")
                if pid in sem_ids:
                    tags.append(f"SEM {sem_scores[pid]:.1f}%")

                tag_str = " + ".join(tags)

                print(f"\n{i}. [{tag_str}] {paper['title']}")
                print(f"   ID: {pid}")
                print(f"   作者: {', '.join(paper['authors'][:3])}")
    else:
        print("未找到結果")

    print(f"\n統計:")
    print(f"  全文搜索: {len(fts_ids)} 篇")
    print(f"  語義搜索: {len(sem_ids)} 篇")
    print(f"  共同結果: {len(both_ids)} 篇")
    print(f"  總計: {len(all_ids)} 篇")

    print("\n" + "=" * 60 + "\n")


def cmd_auto_link(args):
    """為論文自動建立與Zettelkasten的連結（基於向量相似度）"""
    from src.knowledge_base.auto_link import auto_link_v2

    print("\n" + "=" * 60)
    print(f"🔗 自動連結論文 {args.paper_id}")
    print("=" * 60)
    print(f"相似度閾值: {args.threshold}")
    print(f"最多連結: {args.max_links}")

    try:
        result = auto_link_v2(
            paper_id=args.paper_id,
            threshold=args.threshold,
            max_links=args.max_links
        )

        print(f"\n✅ 完成！")
        print(f"論文: {result['paper_title']}")
        print(f"建立連結: {result['links_created']} 個")
        print(f"候選總數: {result['candidates_found']} 個 (>= {args.threshold} 相似度)")

        if result['links']:
            print("\n連結詳情:")
            print("-" * 60)
            for i, link in enumerate(result['links'], 1):
                print(f"\n{i}. [{link['similarity']:.1%}] {link['title']}")
                print(f"   ID: {link['zettel_id']} (card_id: {link['card_id']})")
                if link['core_concept']:
                    print(f"   核心概念: {link['core_concept'][:80]}...")
        else:
            print(f"\n⚠️  未找到相似度 >= {args.threshold} 的卡片")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        if args.verbose:
            traceback.print_exc()

    print("\n" + "=" * 60 + "\n")


def cmd_auto_link_all(args):
    """為所有論文批次建立連結"""
    from src.knowledge_base.auto_link import auto_link_all_papers

    print("\n" + "=" * 60)
    print("🔗 批次自動連結所有論文")
    print("=" * 60)
    print(f"相似度閾值: {args.threshold}")
    print(f"每篇最多連結: {args.max_links}")

    result = auto_link_all_papers(
        threshold=args.threshold,
        max_links=args.max_links,
        verbose=args.verbose
    )

    print("\n" + "=" * 60)
    print("✅ 批次處理完成")
    print("=" * 60)
    print(f"總論文數: {result['total_papers']}")
    print(f"成功處理: {result['processed']}")
    print(f"失敗數量: {result['failed']}")
    print(f"總連結數: {result['total_links_created']}")
    print(f"平均每篇: {result['average_links_per_paper']:.2f} 個連結")
    print("\n" + "=" * 60 + "\n")


def cmd_show_links(args):
    """查看論文的Zettelkasten連結"""
    kb = KnowledgeBaseManager()

    paper = kb.get_paper_by_id(args.paper_id)
    if not paper:
        print(f"\n❌ 論文 ID {args.paper_id} 不存在\n")
        return

    links = kb.get_paper_zettel_links(args.paper_id, min_similarity=args.min_similarity)

    print("\n" + "=" * 60)
    print(f"🔗 論文的 Zettelkasten 連結")
    print("=" * 60)
    print(f"論文: {paper['title']}")
    print(f"ID: {args.paper_id}")
    print(f"連結數: {len(links)}")
    print("=" * 60)

    if links:
        for i, link in enumerate(links, 1):
            print(f"\n{i}. [{link['similarity']:.1%}] {link['title']}")
            print(f"   Zettel ID: {link['zettel_id']}")
            print(f"   Card ID: {link['card_id']}")
            print(f"   類型: {link['card_type']} | 領域: {link['domain']}")
            if link['core_concept']:
                print(f"   核心概念: {link['core_concept'][:100]}...")
            print(f"   連結方法: {link['method']}")
            print(f"   創建時間: {link['created_at']}")
    else:
        threshold_msg = f" (相似度 >= {args.min_similarity})" if args.min_similarity > 0 else ""
        print(f"\n⚠️  此論文沒有連結{threshold_msg}")
        print("提示: 執行 'python kb_manage.py auto-link <paper_id>' 來建立連結")

    print("\n" + "=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="知識庫管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看統計
  python kb_manage.py stats

  # 列出論文
  python kb_manage.py list
  python kb_manage.py list --limit 5

  # 搜索論文
  python kb_manage.py search "deep learning"
  python kb_manage.py search "AI" --limit 10

  # 查看論文詳情
  python kb_manage.py show 1

  # 創建主題
  python kb_manage.py add-topic "AI與認知科學" -d "AI技術在認知科學中的應用"

  # 連結論文到主題
  python kb_manage.py link 1 1 --relevance 0.95

  # 按主題查看論文
  python kb_manage.py topic-papers "AI與認知科學"

  # 添加引用關係
  python kb_manage.py cite 1 2

  # 語義搜索
  python kb_manage.py semantic-search "深度學習" --type papers --limit 5
  python kb_manage.py semantic-search "認知科學" --type all --verbose

  # 尋找相似內容
  python kb_manage.py similar 1 --limit 5
  python kb_manage.py similar zettel_CogSci-20251029-001 --limit 3

  # 混合搜索
  python kb_manage.py hybrid-search "machine learning" --limit 10

  # 自動連結論文到Zettelkasten（基於向量相似度）
  python kb_manage.py auto-link 14 --threshold 0.6 --max-links 5

  # 批次為所有論文建立連結
  python kb_manage.py auto-link-all --threshold 0.6 --max-links 5

  # 查看論文的Zettelkasten連結
  python kb_manage.py show-links 14
  python kb_manage.py show-links 14 --min-similarity 0.7
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # stats 命令
    parser_stats = subparsers.add_parser('stats', help='顯示知識庫統計')
    parser_stats.set_defaults(func=cmd_stats)

    # list 命令
    parser_list = subparsers.add_parser('list', help='列出所有論文')
    parser_list.add_argument('--limit', type=int, default=50, help='最多顯示數量')
    parser_list.set_defaults(func=cmd_list)

    # search 命令
    parser_search = subparsers.add_parser('search', help='搜索論文')
    parser_search.add_argument('query', help='搜索關鍵詞')
    parser_search.add_argument('--limit', type=int, default=10, help='最多顯示數量')
    parser_search.set_defaults(func=cmd_search)

    # show 命令
    parser_show = subparsers.add_parser('show', help='顯示論文詳情')
    parser_show.add_argument('id', type=int, help='論文ID')
    parser_show.set_defaults(func=cmd_show)

    # add-topic 命令
    parser_topic = subparsers.add_parser('add-topic', help='創建主題')
    parser_topic.add_argument('name', help='主題名稱')
    parser_topic.add_argument('-d', '--description', default='', help='主題描述')
    parser_topic.set_defaults(func=cmd_add_topic)

    # link 命令
    parser_link = subparsers.add_parser('link', help='連結論文到主題')
    parser_link.add_argument('paper_id', type=int, help='論文ID')
    parser_link.add_argument('topic_id', type=int, help='主題ID')
    parser_link.add_argument('--relevance', type=float, default=1.0, help='相關度 (0-1)')
    parser_link.set_defaults(func=cmd_link)

    # topic-papers 命令
    parser_tp = subparsers.add_parser('topic-papers', help='按主題查看論文')
    parser_tp.add_argument('name', help='主題名稱')
    parser_tp.set_defaults(func=cmd_topic_papers)

    # cite 命令
    parser_cite = subparsers.add_parser('cite', help='添加引用關係')
    parser_cite.add_argument('source', type=int, help='來源論文ID')
    parser_cite.add_argument('target', type=int, help='目標論文ID')
    parser_cite.add_argument('--type', default='cites', help='引用類型')
    parser_cite.set_defaults(func=cmd_cite)

    # semantic-search 命令
    parser_semantic = subparsers.add_parser('semantic-search', help='語義搜索論文或Zettelkasten')
    parser_semantic.add_argument('query', help='搜索查詢')
    parser_semantic.add_argument('--type', choices=['papers', 'zettel', 'all'],
                                default='all', help='搜索類型 (默認: all)')
    parser_semantic.add_argument('--limit', type=int, default=5, help='最多顯示數量 (默認: 5)')
    parser_semantic.add_argument('--provider', choices=['gemini', 'ollama'],
                                default='gemini', help='嵌入提供者 (默認: gemini)')
    parser_semantic.add_argument('--verbose', '-v', action='store_true',
                                help='顯示詳細信息（摘要/內容預覽）')
    parser_semantic.set_defaults(func=cmd_semantic_search)

    # similar 命令
    parser_similar = subparsers.add_parser('similar', help='尋找相似的論文或Zettelkasten卡片')
    parser_similar.add_argument('id', help='論文ID (數字) 或 Zettelkasten ID (如: zettel_xxx)')
    parser_similar.add_argument('--limit', type=int, default=5, help='最多顯示數量 (默認: 5)')
    parser_similar.set_defaults(func=cmd_similar)

    # hybrid-search 命令
    parser_hybrid = subparsers.add_parser('hybrid-search', help='混合搜索（全文+語義）')
    parser_hybrid.add_argument('query', help='搜索查詢')
    parser_hybrid.add_argument('--limit', type=int, default=10, help='最多顯示數量 (默認: 10)')
    parser_hybrid.add_argument('--provider', choices=['gemini', 'ollama'],
                              default='gemini', help='嵌入提供者 (默認: gemini)')
    parser_hybrid.set_defaults(func=cmd_hybrid_search)

    # auto-link 命令
    parser_auto_link = subparsers.add_parser('auto-link', help='自動建立論文與Zettelkasten的連結（向量相似度）')
    parser_auto_link.add_argument('paper_id', type=int, help='論文ID')
    parser_auto_link.add_argument('--threshold', type=float, default=0.6,
                                 help='相似度閾值 (0-1，默認: 0.6)')
    parser_auto_link.add_argument('--max-links', type=int, default=5,
                                 help='最多建立幾個連結 (默認: 5)')
    parser_auto_link.add_argument('--verbose', action='store_true', help='顯示詳細錯誤信息')
    parser_auto_link.set_defaults(func=cmd_auto_link)

    # auto-link-all 命令
    parser_auto_link_all = subparsers.add_parser('auto-link-all', help='為所有論文批次建立連結')
    parser_auto_link_all.add_argument('--threshold', type=float, default=0.6,
                                     help='相似度閾值 (0-1，默認: 0.6)')
    parser_auto_link_all.add_argument('--max-links', type=int, default=5,
                                     help='每篇論文最多建立幾個連結 (默認: 5)')
    parser_auto_link_all.add_argument('--verbose', action='store_true', help='顯示詳細進度')
    parser_auto_link_all.set_defaults(func=cmd_auto_link_all)

    # show-links 命令
    parser_show_links = subparsers.add_parser('show-links', help='查看論文的Zettelkasten連結')
    parser_show_links.add_argument('paper_id', type=int, help='論文ID')
    parser_show_links.add_argument('--min-similarity', type=float, default=0.0,
                                  help='最小相似度過濾 (0-1，默認: 0.0)')
    parser_show_links.set_defaults(func=cmd_show_links)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
