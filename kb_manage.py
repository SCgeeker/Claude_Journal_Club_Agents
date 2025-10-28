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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
