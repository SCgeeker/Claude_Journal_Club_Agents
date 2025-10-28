#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識庫互動工具
提供互動式介面來操作知識庫
"""

import sys
from pathlib import Path

# 設置UTF-8編碼（Windows相容性）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

from src.knowledge_base import KnowledgeBaseManager


def main():
    kb = KnowledgeBaseManager()

    print("\n" + "=" * 60)
    print("📚 知識庫互動工具")
    print("=" * 60)

    while True:
        print("\n選擇操作:")
        print("  1. 查看統計")
        print("  2. 列出所有論文")
        print("  3. 搜索論文")
        print("  4. 查看論文詳情")
        print("  5. 創建主題")
        print("  6. 連結論文到主題")
        print("  7. 按主題查看論文")
        print("  0. 退出")

        choice = input("\n請輸入選項 (0-7): ").strip()

        if choice == '0':
            print("\n👋 再見！")
            break

        elif choice == '1':
            # 查看統計
            stats = kb.get_stats()
            print(f"\n📊 知識庫統計:")
            print(f"   論文總數: {stats['total_papers']}")
            print(f"   主題總數: {stats['total_topics']}")
            print(f"   引用總數: {stats['total_citations']}")

        elif choice == '2':
            # 列出所有論文
            papers = kb.list_papers(limit=50)
            if papers:
                print(f"\n📄 共 {len(papers)} 篇論文:")
                for paper in papers:
                    print(f"\n   ID: {paper['id']}")
                    print(f"   標題: {paper['title']}")
                    print(f"   作者: {', '.join(paper['authors'][:3])}")
                    if paper['keywords']:
                        print(f"   關鍵詞: {', '.join(paper['keywords'][:5])}")
            else:
                print("\n⚠️  知識庫中還沒有論文")

        elif choice == '3':
            # 搜索論文
            query = input("\n🔍 請輸入搜索關鍵詞: ").strip()
            if query:
                results = kb.search_papers(query, limit=10)
                if results:
                    print(f"\n找到 {len(results)} 個結果:")
                    for i, paper in enumerate(results, 1):
                        print(f"\n{i}. ID: {paper['id']}")
                        print(f"   標題: {paper['title']}")
                        print(f"   作者: {', '.join(paper['authors'][:3])}")
                else:
                    print(f"\n❌ 未找到包含 '{query}' 的論文")

        elif choice == '4':
            # 查看論文詳情
            paper_id = input("\n請輸入論文ID: ").strip()
            try:
                paper_id = int(paper_id)
                paper = kb.get_paper_by_id(paper_id)
                if paper:
                    print(f"\n📄 論文詳情:")
                    print(f"   ID: {paper['id']}")
                    print(f"   標題: {paper['title']}")
                    print(f"   作者: {', '.join(paper['authors'])}")
                    print(f"   年份: {paper['year'] or '未知'}")
                    print(f"   檔案: {paper['file_path']}")
                    print(f"   創建: {paper['created_at']}")
                    print(f"   更新: {paper['updated_at']}")

                    if paper['abstract']:
                        print(f"\n   摘要:")
                        print(f"   {paper['abstract'][:300]}...")

                    if paper['keywords']:
                        print(f"\n   關鍵詞: {', '.join(paper['keywords'])}")
                else:
                    print(f"\n❌ 找不到ID為 {paper_id} 的論文")
            except ValueError:
                print("\n❌ 請輸入有效的數字ID")

        elif choice == '5':
            # 創建主題
            name = input("\n🏷️  主題名稱: ").strip()
            desc = input("   主題描述: ").strip()

            if name:
                topic_id = kb.add_topic(name, desc)
                print(f"\n✅ 主題已創建 (ID: {topic_id})")
            else:
                print("\n❌ 主題名稱不能為空")

        elif choice == '6':
            # 連結論文到主題
            paper_id = input("\n請輸入論文ID: ").strip()
            topic_id = input("請輸入主題ID: ").strip()
            relevance = input("相關度 (0-1, 默認1.0): ").strip() or "1.0"

            try:
                paper_id = int(paper_id)
                topic_id = int(topic_id)
                relevance = float(relevance)

                kb.link_paper_to_topic(paper_id, topic_id, relevance)
                print(f"\n✅ 已連結論文 {paper_id} 到主題 {topic_id}")
            except ValueError:
                print("\n❌ 請輸入有效的數字")

        elif choice == '7':
            # 按主題查看論文
            topic_name = input("\n🏷️  請輸入主題名稱: ").strip()
            if topic_name:
                papers = kb.get_papers_by_topic(topic_name)
                if papers:
                    print(f"\n找到 {len(papers)} 篇論文:")
                    for paper in papers:
                        print(f"\n   ID: {paper['id']}")
                        print(f"   標題: {paper['title']}")
                        print(f"   相關度: {paper['relevance']}")
                else:
                    print(f"\n❌ 主題 '{topic_name}' 下沒有論文")

        else:
            print("\n❌ 無效的選項，請重新選擇")


if __name__ == "__main__":
    main()
