#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識庫功能演示
展示KnowledgeBaseManager的所有主要功能
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


def demo_all_features():
    """演示所有知識庫功能"""

    print("=" * 60)
    print("知識庫功能演示")
    print("=" * 60)

    # 初始化知識庫
    kb = KnowledgeBaseManager()
    print("\n✅ 知識庫已初始化")

    # ====================================
    # 1. 查看統計信息
    # ====================================
    print("\n" + "=" * 60)
    print("1️⃣  知識庫統計")
    print("=" * 60)

    stats = kb.get_stats()
    print(f"📊 論文總數: {stats['total_papers']}")
    print(f"🏷️  主題總數: {stats['total_topics']}")
    print(f"🔗 引用總數: {stats['total_citations']}")

    # ====================================
    # 2. 列出所有論文
    # ====================================
    print("\n" + "=" * 60)
    print("2️⃣  列出所有論文")
    print("=" * 60)

    papers = kb.list_papers(limit=10)
    if papers:
        for paper in papers:
            print(f"\n📄 ID: {paper['id']}")
            print(f"   標題: {paper['title']}")
            print(f"   作者: {', '.join(paper['authors'][:3])}")
            if len(paper['authors']) > 3:
                print(f"         (+{len(paper['authors'])-3} 位作者)")
            print(f"   年份: {paper['year'] or '未知'}")
            print(f"   關鍵詞: {', '.join(paper['keywords'][:5])}")
            print(f"   創建時間: {paper['created_at']}")
    else:
        print("⚠️  知識庫中還沒有論文")

    # ====================================
    # 3. 搜索功能演示
    # ====================================
    print("\n" + "=" * 60)
    print("3️⃣  全文搜索功能")
    print("=" * 60)

    search_terms = ["AI", "cognitive science", "generalizability", "LLM"]

    for term in search_terms:
        print(f"\n🔍 搜索: '{term}'")
        results = kb.search_papers(term, limit=5)

        if results:
            print(f"   找到 {len(results)} 個結果:")
            for i, paper in enumerate(results[:3], 1):
                print(f"   {i}. {paper['title'][:60]}...")
        else:
            print(f"   ❌ 未找到包含 '{term}' 的論文")

    # ====================================
    # 4. 主題管理演示
    # ====================================
    print("\n" + "=" * 60)
    print("4️⃣  主題管理")
    print("=" * 60)

    # 創建示例主題
    example_topics = [
        ("AI與認知科學", "人工智能在認知科學研究中的應用與批判"),
        ("研究方法論", "認知科學研究的方法論問題"),
        ("泛化性問題", "研究發現的外部效度與泛化性"),
    ]

    print("\n🏷️  可以創建的主題示例:")
    for name, desc in example_topics:
        print(f"   • {name}: {desc}")

    print("\n💡 創建主題的方法:")
    print("   topic_id = kb.add_topic('主題名稱', '主題描述')")
    print("   kb.link_paper_to_topic(paper_id, topic_id, relevance=0.95)")

    # ====================================
    # 5. 獲取特定論文詳情
    # ====================================
    print("\n" + "=" * 60)
    print("5️⃣  查看論文詳細信息")
    print("=" * 60)

    if stats['total_papers'] > 0:
        paper = kb.get_paper_by_id(1)
        if paper:
            print(f"\n📄 論文 ID: {paper['id']}")
            print(f"標題: {paper['title']}")
            print(f"作者: {', '.join(paper['authors'])}")
            print(f"年份: {paper['year'] or '未知'}")
            print(f"檔案位置: {paper['file_path']}")
            print(f"創建時間: {paper['created_at']}")
            print(f"更新時間: {paper['updated_at']}")

            if paper['abstract']:
                print(f"\n摘要:")
                abstract = paper['abstract'][:300]
                print(f"{abstract}..." if len(paper['abstract']) > 300 else abstract)

    # ====================================
    # 6. 引用關係管理
    # ====================================
    print("\n" + "=" * 60)
    print("6️⃣  引用關係管理")
    print("=" * 60)

    print("\n🔗 建立引用關係的方法:")
    print("   kb.add_citation(source_paper_id=1, target_paper_id=2)")
    print("   # 表示論文1引用了論文2")

    # ====================================
    # 7. 添加新論文
    # ====================================
    print("\n" + "=" * 60)
    print("7️⃣  添加新論文到知識庫")
    print("=" * 60)

    print("\n📝 方法1: 使用analyze_paper.py腳本")
    print("   python analyze_paper.py paper.pdf --add-to-kb")

    print("\n📝 方法2: 直接使用Python API")
    print("""
   paper_id = kb.add_paper(
       file_path="papers/smith_2024.md",
       title="Deep Learning for Medical Diagnosis",
       authors=["John Smith", "Jane Doe"],
       year=2024,
       abstract="研究摘要...",
       keywords=["deep learning", "medical"],
       content="完整內容..."
   )
    """)

    # ====================================
    # 8. 創建Markdown筆記
    # ====================================
    print("\n" + "=" * 60)
    print("8️⃣  創建結構化Markdown筆記")
    print("=" * 60)

    print("\n📄 自動生成筆記模板:")
    print("""
   md_path = kb.create_markdown_note({
       'title': '論文標題',
       'authors': ['作者1', '作者2'],
       'year': 2024,
       'abstract': '摘要內容',
       'keywords': ['關鍵詞1', '關鍵詞2']
   })
    """)

    # ====================================
    # 9. 實用查詢示例
    # ====================================
    print("\n" + "=" * 60)
    print("9️⃣  實用查詢示例")
    print("=" * 60)

    print("\n🔍 查詢示例:")

    queries = [
        ("最近添加的論文", "kb.list_papers(limit=5)"),
        ("搜索特定主題", "kb.search_papers('deep learning')"),
        ("按主題查找論文", "kb.get_papers_by_topic('AI與認知科學')"),
        ("獲取論文詳情", "kb.get_paper_by_id(1)"),
        ("知識庫統計", "kb.get_stats()"),
    ]

    for desc, code in queries:
        print(f"\n   • {desc}:")
        print(f"     {code}")

    # ====================================
    # 10. 數據庫直接查詢
    # ====================================
    print("\n" + "=" * 60)
    print("🔟 進階: 直接查詢SQLite數據庫")
    print("=" * 60)

    print("\n💻 使用SQLite命令行:")
    print(f"   sqlite3 {kb.db_path}")
    print("   SELECT * FROM papers;")
    print("   SELECT * FROM topics;")
    print("   SELECT * FROM paper_topics;")

    print("\n📊 數據庫表結構:")
    tables = [
        "papers - 論文元數據",
        "topics - 主題分類",
        "paper_topics - 論文-主題關聯",
        "citations - 引用關係",
        "papers_fts - 全文搜索索引（FTS5）"
    ]
    for table in tables:
        print(f"   • {table}")

    # ====================================
    # 總結
    # ====================================
    print("\n" + "=" * 60)
    print("✨ 功能總結")
    print("=" * 60)

    features = [
        "✅ 論文存儲與索引（Markdown + SQLite）",
        "✅ 全文搜索（基於SQLite FTS5）",
        "✅ 主題分類與標籤",
        "✅ 引用關係追蹤",
        "✅ 自動創建結構化筆記",
        "✅ 統計與分析",
        "✅ 批量導入與管理",
        "✅ Python API + 命令行工具"
    ]

    for feature in features:
        print(f"   {feature}")

    print("\n" + "=" * 60)
    print("📚 更多資訊請參考:")
    print("   • CLAUDE.md - 完整文檔")
    print("   • .claude/skills/kb-connector.md - Skill文檔")
    print("   • src/knowledge_base/kb_manager.py - 源碼")
    print("=" * 60)


if __name__ == "__main__":
    demo_all_features()
