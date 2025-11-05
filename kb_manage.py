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

# 導入元數據修復工具
try:
    from fix_metadata import MetadataFixer
except ImportError:
    MetadataFixer = None

# 導入關係發現器 (Phase 2.1)
try:
    from src.analyzers import RelationFinder
except ImportError:
    RelationFinder = None

import sqlite3
import json
import yaml
import re
from typing import Dict


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


def cmd_metadata_fix(args):
    """修復缺失的元數據"""
    if MetadataFixer is None:
        print("❌ 錯誤: 找不到 fix_metadata.py")
        print("請確保 fix_metadata.py 在專案根目錄")
        sys.exit(1)

    fixer = MetadataFixer()

    field_name = {
        'year': '年份',
        'keywords': '關鍵詞',
        'abstract': '摘要',
        'all': '所有缺失字段'
    }.get(args.field, '未知')

    print(f"\n{'=' * 60}")
    print(f"🔧 修復元數據: {field_name}")
    print(f"{'=' * 60}\n")

    # 獲取需要修復的論文
    papers = fixer.get_papers_needing_repair(field=args.field if args.field != 'all' else None)

    if not papers:
        print("✅ 沒有論文需要修復！")
        print(f"{'=' * 60}\n")
        return

    print(f"找到 {len(papers)} 篇需要修復的論文\n")

    if args.dry_run:
        print("⚠️ 預覽模式（不會實際修復）\n")
        for paper in papers[:10]:  # 只顯示前10個
            print(f"[ID {paper['id']}] {paper['title'][:60]}")
        if len(papers) > 10:
            print(f"... 還有 {len(papers) - 10} 篇")
        print(f"\n{'=' * 60}\n")
        return

    if args.batch:
        # 批次修復
        success = 0
        failed = 0

        for i, paper in enumerate(papers, 1):
            print(f"[{i}/{len(papers)}] ID {paper['id']}: {paper['title'][:50]}")

            result = fixer.auto_fix_paper(
                paper['id'],
                fields=[args.field] if args.field != 'all' else ['year', 'keywords', 'abstract']
            )

            if result.get('updates'):
                fixer.update_paper_metadata(
                    paper['id'],
                    year=result['updates'].get('year'),
                    keywords=result['updates'].get('keywords'),
                    abstract=result['updates'].get('abstract')
                )
                print(f"  ✅ 已修復: {', '.join(result['updates'].keys())}")
                success += 1
            else:
                print(f"  ⚠️ 無法修復: {result.get('reason', '未知')}")
                failed += 1

        print(f"\n{'=' * 60}")
        print(f"修復完成:")
        print(f"  成功: {success}")
        print(f"  失敗: {failed}")
        print(f"{'=' * 60}\n")
    else:
        # 單篇修復（交互式）
        print("使用 --batch 選項進行批次修復")
        print(f"{'=' * 60}\n")


def cmd_metadata_sync_yaml(args):
    """同步資料庫標題到 YAML front matter"""
    kb = KnowledgeBaseManager()

    print(f"\n{'=' * 60}")
    print("🔄 同步標題到 YAML")
    print(f"{'=' * 60}\n")

    # 獲取所有論文
    conn = sqlite3.connect(kb.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, file_path FROM papers ORDER BY id")
    papers = cursor.fetchall()
    conn.close()

    success = 0
    skipped = 0
    failed = 0

    for paper_id, db_title, file_path in papers:
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            print(f"[{paper_id}] ⚠️ 檔案不存在: {file_path}")
            skipped += 1
            continue

        # 讀取並更新 YAML
        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()

            yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
            if not yaml_match:
                print(f"[{paper_id}] ⚠️ 找不到 YAML front matter")
                skipped += 1
                continue

            metadata = yaml.safe_load(yaml_match.group(1))
            yaml_title = metadata.get('title', '')

            if yaml_title == db_title:
                skipped += 1
                continue

            # 更新標題
            metadata['title'] = db_title
            new_yaml = yaml.dump(metadata, allow_unicode=True, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{new_yaml}---\n{yaml_match.group(2)}"

            if not args.dry_run:
                with open(file_path_obj, 'w', encoding='utf-8') as f:
                    f.write(new_content)

            print(f"[{paper_id}] ✅ 已更新: {db_title[:60]}")
            success += 1

        except Exception as e:
            print(f"[{paper_id}] ❌ 錯誤: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"同步完成:")
    print(f"  成功: {success}")
    print(f"  跳過: {skipped}")
    print(f"  失敗: {failed}")
    print(f"{'=' * 60}\n")


def cmd_cleanup(args):
    """清理孤立的資料庫記錄"""
    kb = KnowledgeBaseManager()

    print(f"\n{'=' * 60}")
    print("🗑️ 清理孤立記錄")
    print(f"{'=' * 60}\n")

    conn = sqlite3.connect(kb.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, file_path FROM papers")
    papers = cursor.fetchall()

    orphans = []
    for pid, title, file_path in papers:
        if not Path(file_path).exists():
            orphans.append((pid, title, file_path))

    if not orphans:
        print("✅ 沒有發現孤立記錄！")
        conn.close()
        print(f"{'=' * 60}\n")
        return

    print(f"找到 {len(orphans)} 筆孤立記錄:\n")

    for pid, title, file_path in orphans:
        print(f"ID {pid}: {title[:60]}")
        print(f"  檔案: {file_path}\n")

    if args.dry_run:
        print("⚠️ 預覽模式（不會實際刪除）")
    else:
        # 刪除孤立記錄
        for pid, _, _ in orphans:
            cursor.execute("DELETE FROM papers WHERE id = ?", (pid,))
            cursor.execute("DELETE FROM paper_topics WHERE paper_id = ?", (pid,))
        conn.commit()
        print(f"✅ 已刪除 {len(orphans)} 筆記錄")

    conn.close()
    print(f"{'=' * 60}\n")


def cmd_import_papers(args):
    """導入未記錄的 Markdown 檔案"""
    kb = KnowledgeBaseManager()
    papers_dir = Path("knowledge_base/papers")

    print(f"\n{'=' * 60}")
    print("📥 導入未記錄的 Markdown 檔案")
    print(f"{'=' * 60}\n")

    # 獲取所有 Markdown 檔案
    actual_files = set(f.name for f in papers_dir.glob("*.md"))

    # 獲取已記錄的檔案
    conn = sqlite3.connect(kb.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT file_path FROM papers')
    db_files = set(Path(row[0]).name for row in cursor.fetchall())
    conn.close()

    # 找出未記錄的檔案
    unrecorded = actual_files - db_files

    if not unrecorded:
        print("✅ 沒有未記錄的檔案！")
        print(f"{'=' * 60}\n")
        return

    print(f"找到 {len(unrecorded)} 個未記錄的檔案\n")

    success = 0
    failed = 0

    for filename in sorted(unrecorded):
        file_path = papers_dir / filename
        print(f"[{success + failed + 1}/{len(unrecorded)}] {filename}")

        try:
            # 讀取 YAML front matter
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                print(f"  ⚠️ 找不到 YAML front matter\n")
                failed += 1
                continue

            metadata = yaml.safe_load(yaml_match.group(1))

            title = metadata.get('title', filename.replace('.md', ''))
            authors = metadata.get('authors', '')
            year = metadata.get('year')
            keywords = metadata.get('keywords', [])

            # 解析 authors
            if isinstance(authors, str):
                authors_list = [a.strip() for a in authors.split(',') if a.strip()]
            elif isinstance(authors, list):
                authors_list = authors
            else:
                authors_list = []

            # 解析 keywords
            if isinstance(keywords, str):
                keywords_list = [k.strip() for k in keywords.split(',') if k.strip()]
            elif isinstance(keywords, list):
                keywords_list = keywords
            else:
                keywords_list = []

            if not args.dry_run:
                # 導入到資料庫
                paper_id = kb.add_paper(
                    file_path=str(file_path),
                    title=title,
                    authors=authors_list,
                    year=year,
                    keywords=keywords_list,
                    source='imported'
                )
                print(f"  ✅ 已導入 (ID: {paper_id})")
            else:
                print(f"  [DRY RUN] 標題: {title[:60]}")

            success += 1

        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            failed += 1

        print()

    print(f"{'=' * 60}")
    print(f"導入完成:")
    print(f"  成功: {success}")
    print(f"  失敗: {failed}")
    print(f"{'=' * 60}\n")


def cmd_find_relations(args):
    """發現論文關係 (Phase 2.1)"""
    if RelationFinder is None:
        print("❌ RelationFinder 未安裝，請確認 src/analyzers/ 已建立")
        return

    finder = RelationFinder()

    print(f"\n{'=' * 80}")
    print(f"🔍 論文關係分析 (ID: {args.paper_id})")
    print(f"{'=' * 80}\n")

    # 獲取論文信息
    kb = KnowledgeBaseManager()
    try:
        paper = kb.get_paper(args.paper_id)
        print(f"📄 論文: {paper['title'][:60]}")
        print(f"   作者: {', '.join(paper.get('authors', [])[:3])}")
        print(f"   年份: {paper.get('year', '未知')}\n")
    except:
        print(f"❌ 論文 ID {args.paper_id} 不存在\n")
        return

    # 發現所有關係
    all_relations = finder.find_all_relations(args.paper_id)

    total_relations = sum(len(rels) for rels in all_relations.values())

    if total_relations == 0:
        print("未發現任何關係")
        print(f"{'=' * 80}\n")
        return

    # 顯示各類關係
    for rel_type, relations in all_relations.items():
        if not relations:
            continue

        type_names = {
            'citation': '引用關係',
            'shared_topic': '主題關聯',
            'author_collaboration': '作者合作',
            'similarity': '相似論文'
        }

        print(f"🔗 {type_names.get(rel_type, rel_type)} ({len(relations)}個)\n")

        for i, rel in enumerate(relations[:args.limit], 1):
            try:
                target = kb.get_paper(rel.target_id)
                print(f"   {i}. [{rel.target_id}] {target['title'][:60]}")
                print(f"      強度: {rel.strength:.2%}")

                if 'shared_keywords' in rel.metadata:
                    kw_display = ', '.join(rel.metadata['shared_keywords'][:5])
                    if len(rel.metadata['shared_keywords']) > 5:
                        kw_display += f" (+{len(rel.metadata['shared_keywords'])-5}個)"
                    print(f"      共享關鍵詞: {kw_display}")

                if 'shared_authors' in rel.metadata:
                    print(f"      共同作者: {', '.join(rel.metadata['shared_authors'])}")

                print()
            except:
                print(f"   {i}. [ERROR] Paper {rel.target_id} 無法載入\n")

    print(f"{'=' * 80}")
    print(f"總計: {total_relations} 個關係")
    print(f"{'=' * 80}\n")


def cmd_build_network(args):
    """構建引用網絡 (Phase 2.1)"""
    if RelationFinder is None:
        print("❌ RelationFinder 未安裝，請確認 src/analyzers/ 已建立")
        return

    finder = RelationFinder()

    print(f"\n{'=' * 80}")
    print(f"📊 構建引用網絡")
    print(f"{'=' * 80}\n")

    # 解析論文ID列表
    if args.paper_ids:
        paper_ids = [int(pid.strip()) for pid in args.paper_ids.split(',')]
        print(f"目標論文: {len(paper_ids)} 篇 (ID: {', '.join(map(str, paper_ids))})\n")
    else:
        print(f"目標論文: 所有論文\n")
        paper_ids = None

    # 構建網絡
    print("正在構建網絡...")
    network = finder.build_citation_network(paper_ids)

    print(f"\n✅ 網絡構建完成:")
    print(f"   節點數: {network['metadata']['total_nodes']}")
    print(f"   邊數: {network['metadata']['total_edges']}")

    # 導出JSON
    if args.output:
        finder.export_to_json(network, args.output)
        print(f"\n💾 已導出JSON: {args.output}")

    # 導出GraphML (if networkx available)
    if args.graphml:
        try:
            G = finder.export_to_networkx(network)
            finder.export_to_graphml(G, args.graphml)
            print(f"💾 已導出GraphML: {args.graphml}")
        except ImportError:
            print(f"\n⚠️  NetworkX未安裝，無法導出GraphML")
            print(f"    安裝: pip install networkx")

    print(f"\n{'=' * 80}\n")


def cmd_analyze_relations(args):
    """分析 Zettelkasten 概念關係 (Phase 2.1)"""
    if RelationFinder is None:
        print("❌ RelationFinder 未安裝，請確認 src/analyzers/ 已建立")
        return

    print("\n" + "=" * 70)
    print("🔍 Zettelkasten 概念關係分析 (Phase 2.1)")
    print("=" * 70)

    finder = RelationFinder()

    # 根據參數選擇操作模式
    if args.mode == 'find':
        # 模式 1: 僅識別關係
        print(f"\n模式: 識別概念關係")
        print(f"最小相似度: {args.min_similarity}")
        print(f"最小信度: {args.min_confidence}")
        if args.relation_types:
            print(f"關係類型: {args.relation_types}")

        relations = finder.find_concept_relations(
            min_similarity=args.min_similarity,
            relation_types=args.relation_types.split(',') if args.relation_types else None,
            limit=args.limit
        )

        # 過濾信度
        relations = [r for r in relations if r.confidence_score >= args.min_confidence]

        if relations:
            print(f"\n📋 關係列表 (top {min(len(relations), 20)}):")
            print("-" * 70)
            for i, rel in enumerate(relations[:20], 1):
                print(f"\n{i}. {rel.card_id_1} --{rel.relation_type}--> {rel.card_id_2}")
                print(f"   {rel.card_title_1[:35]} → {rel.card_title_2[:35]}")
                print(f"   信度: {rel.confidence_score:.3f} | 相似度: {rel.semantic_similarity:.3f}")
                if rel.link_explicit:
                    print(f"   ✓ 明確連結存在")
                if rel.shared_concepts:
                    print(f"   共同概念: {', '.join(rel.shared_concepts[:5])}")
        else:
            print("\n未找到符合條件的關係")

    elif args.mode == 'network':
        # 模式 2: 建構完整網絡
        print(f"\n模式: 建構概念網絡")
        print(f"最小相似度: {args.min_similarity}")
        print(f"最小信度: {args.min_confidence}")

        network = finder.build_concept_network(
            min_similarity=args.min_similarity,
            relation_types=args.relation_types.split(',') if args.relation_types else None,
            min_confidence=args.min_confidence
        )

        # 顯示網絡摘要（已在 build_concept_network 中顯示）

        # 導出為 JSON
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(network, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n💾 網絡數據已導出: {args.output}")

        # 生成報告
        if args.report:
            report_path = Path(args.report)
            report_path.parent.mkdir(parents=True, exist_ok=True)

            report = _generate_relation_report(network, finder)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"💾 報告已生成: {args.report}")

        # 生成 Mermaid 圖表
        if args.mermaid:
            mermaid_path = Path(args.mermaid)
            mermaid_path.parent.mkdir(parents=True, exist_ok=True)

            mermaid_diagram = _generate_mermaid_diagram(network, max_nodes=args.max_nodes)
            with open(mermaid_path, 'w', encoding='utf-8') as f:
                f.write(f"# Zettelkasten 概念網絡\n\n{mermaid_diagram}")
            print(f"💾 Mermaid 圖表已生成: {args.mermaid}")

    print("\n" + "=" * 70 + "\n")


def _generate_relation_report(network: Dict, finder: 'RelationFinder') -> str:
    """生成 Zettelkasten 概念關係分析報告（Markdown格式）"""
    stats = network['statistics']
    hub_nodes = network['hub_nodes']
    relations = network['relations']

    report_lines = [
        "# Zettelkasten 概念關係分析報告",
        "",
        f"**生成時間**: {Path('.').absolute()}",
        "",
        "---",
        "",
        "## 📊 網絡統計",
        "",
        "| 指標 | 數值 |",
        "|------|------|",
        f"| **節點數** | {stats['node_count']} |",
        f"| **邊數** | {stats['edge_count']} |",
        f"| **平均度** | {stats['avg_degree']} |",
        f"| **最大度** | {stats['max_degree']} |",
        f"| **最小度** | {stats['min_degree']} |",
        f"| **網絡密度** | {stats['density']} |",
        f"| **平均信度** | {stats['avg_confidence']} |",
        f"| **平均相似度** | {stats['avg_similarity']} |",
        "",
        "## 🎯 關係類型分布",
        "",
        "| 關係類型 | 數量 | 佔比 |",
        "|---------|------|------|",
    ]

    total_relations = sum(stats['relation_type_counts'].values())
    for rel_type, count in sorted(stats['relation_type_counts'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_relations * 100) if total_relations > 0 else 0
        report_lines.append(f"| {rel_type} | {count} | {percentage:.1f}% |")

    report_lines.extend([
        "",
        "## 🌟 核心節點 (Hub Nodes)",
        "",
        "高度中心性節點（連接數最多的卡片）：",
        "",
        "| 排名 | 卡片 ID | 標題 | 度 | 入度 | 出度 |",
        "|------|---------|------|-----|------|------|",
    ])

    for i, node in enumerate(hub_nodes[:10], 1):
        title = node['title'][:40] + "..." if len(node['title']) > 40 else node['title']
        report_lines.append(
            f"| {i} | {node['card_id']} | {title} | {node['degree']} | "
            f"{node['in_degree']} | {node['out_degree']} |"
        )

    report_lines.extend([
        "",
        "## 🔗 高信度關係 (Top 20)",
        "",
        "信度最高的概念關係：",
        "",
    ])

    sorted_relations = sorted(relations, key=lambda r: r['confidence_score'], reverse=True)
    for i, rel in enumerate(sorted_relations[:20], 1):
        report_lines.extend([
            f"### {i}. {rel['card_id_1']} → {rel['card_id_2']}",
            f"- **關係類型**: {rel['relation_type']}",
            f"- **信度**: {rel['confidence_score']:.3f}",
            f"- **相似度**: {rel['semantic_similarity']:.3f}",
            f"- **明確連結**: {'是' if rel['link_explicit'] else '否'}",
        ])
        if rel['shared_concepts']:
            report_lines.append(f"- **共同概念**: {', '.join(rel['shared_concepts'][:8])}")
        report_lines.append("")

    report_lines.extend([
        "---",
        "",
        "*報告由 Knowledge Production System (Phase 2.1) 自動生成*"
    ])

    return "\n".join(report_lines)


def _generate_mermaid_diagram(network: Dict, max_nodes: int = 50) -> str:
    """生成 Mermaid 概念網絡圖表"""
    nodes = network['nodes']
    relations = network['relations']

    # 選擇最重要的節點（高度節點）
    sorted_nodes = sorted(nodes, key=lambda n: n['degree'], reverse=True)[:max_nodes]
    node_ids = {n['card_id'] for n in sorted_nodes}

    lines = [
        "```mermaid",
        "graph TD",
        ""
    ]

    # 添加節點
    for node in sorted_nodes:
        node_id = node['card_id'].replace('-', '_')  # Mermaid ID 不能有連字號
        title = node['title'][:25] + "..." if len(node['title']) > 25 else node['title']
        lines.append(f"    {node_id}[\"{title}\"]")

    lines.append("")

    # 添加邊（只顯示高信度關係）
    sorted_relations = sorted(relations, key=lambda r: r['confidence_score'], reverse=True)
    edge_count = 0
    for rel in sorted_relations:
        if rel['card_id_1'] not in node_ids or rel['card_id_2'] not in node_ids:
            continue

        node1_id = rel['card_id_1'].replace('-', '_')
        node2_id = rel['card_id_2'].replace('-', '_')

        # 根據關係類型選擇箭頭樣式
        if rel['relation_type'] == 'leads_to':
            arrow = '-->'
        elif rel['relation_type'] == 'based_on':
            arrow = '<--'
        elif rel['relation_type'] == 'contrasts_with':
            arrow = '-..->'
        elif rel['confidence_score'] >= 0.7:
            arrow = '==>'  # 高信度
        else:
            arrow = '-->'

        lines.append(f"    {node1_id} {arrow} {node2_id}")
        edge_count += 1

        if edge_count >= 100:  # 限制邊數避免圖表過於複雜
            break

    lines.append("```")
    return "\n".join(lines)


def cmd_check_cite_keys(args):
    """檢查缺少 cite_key 的論文"""
    kb = KnowledgeBaseManager()
    papers = kb.list_papers_without_cite_key()

    if not papers:
        print("✅ 所有論文都有 cite_key！")
        return

    print(f"⚠️  發現 {len(papers)} 篇論文缺少 cite_key：\n")
    for p in papers:
        authors_str = ', '.join(p['authors'][:2]) if p['authors'] else '未知'
        if len(p['authors']) > 2:
            authors_str += f" 等 {len(p['authors'])} 位作者"

        print(f"  ID {p['id']:2d}: {p['title'][:50]}")
        print(f"         作者: {authors_str}")
        print(f"         年份: {p['year'] or '未知'}")
        print()

    print(f"\n💡 解決方法:")
    print(f"   1. 從 Zotero 導出 'My Library.bib' 文件")
    print(f"      （Zotero: File → Export Library → BibTeX）")
    print(f"   2. 執行預覽：python kb_manage.py update-from-bib 'My Library.bib' --dry-run")
    print(f"   3. 確認無誤後執行：python kb_manage.py update-from-bib 'My Library.bib'")
    print()


def cmd_update_from_bib(args):
    """從 BibTeX 文件更新 cite_key"""
    from pathlib import Path

    kb = KnowledgeBaseManager()

    if not Path(args.bib_file).exists():
        print(f"❌ 錯誤：找不到文件 {args.bib_file}")
        return

    print(f"📖 正在解析 {args.bib_file}...")
    try:
        result = kb.update_cite_keys_from_bib(args.bib_file, dry_run=args.dry_run)
    except Exception as e:
        print(f"❌ 錯誤：{str(e)}")
        return

    print(f"\n{'🔍 模擬結果' if args.dry_run else '✅ 更新結果'}:")
    print(f"   總條目數: {result['total_entries']}")
    print(f"   成功更新: {result['success_count']}")
    print(f"   已有 cite_key: {result['already_has_key_count']}")
    print(f"   未找到匹配: {result['not_found_count']}")

    if result['updated']:
        print(f"\n✅ 已更新的論文:")
        for item in result['updated'][:10]:
            print(f"   ID {item['id']:2d}: {item['cite_key']:20s} - {item['title'][:40]}")
        if len(result['updated']) > 10:
            print(f"   ... 以及其他 {len(result['updated']) - 10} 篇")

    if result['not_found']:
        print(f"\n⚠️  .bib 中有但知識庫中未找到的論文:")
        for item in result['not_found'][:5]:
            reason = item.get('reason', '')
            print(f"   {item['cite_key']:20s} - {item['title'][:40]} {reason}")
        if len(result['not_found']) > 5:
            print(f"   ... 以及其他 {len(result['not_found']) - 5} 篇")

    if args.dry_run:
        print(f"\n💡 提示：移除 --dry-run 參數以實際更新")


def cmd_set_cite_key(args):
    """手動設置論文的 cite_key"""
    kb = KnowledgeBaseManager()

    paper = kb.get_paper_by_id(args.paper_id)
    if not paper:
        print(f"❌ 錯誤：找不到論文 ID {args.paper_id}")
        return

    print(f"論文信息:")
    print(f"  ID: {paper['id']}")
    print(f"  標題: {paper['title']}")
    print(f"  當前 cite_key: {paper.get('cite_key', '(無)')}")
    print(f"  新 cite_key: {args.cite_key}")
    print()

    confirm = input("確認更新？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    success = kb.update_cite_key(args.paper_id, args.cite_key)
    if success:
        print(f"✅ 成功更新 cite_key 為: {args.cite_key}")
    else:
        print(f"❌ 更新失敗")


def cmd_check_llm(args):
    """檢查 LLM 提供者訪問狀態"""
    print("\n" + "=" * 60)
    print("LLM Access Status Check")
    print("=" * 60)
    print()

    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("[OK] .env file exists")
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("[WARN] python-dotenv not installed, using environment variables")
    else:
        print("[WARN] .env file not found, using environment variables")
    print()

    results = {}
    providers_tested = []

    # Test Ollama
    print("Testing Ollama (local)...", end=" ", flush=True)
    try:
        import requests
        url = "http://localhost:11434"
        response = requests.get(f"{url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            results['Ollama'] = True
            providers_tested.append(f"Ollama: {len(models)} models available")
            print(f"[OK] {len(models)} models available")
        else:
            results['Ollama'] = False
            print(f"[FAIL] HTTP {response.status_code}")
    except Exception as e:
        results['Ollama'] = False
        print(f"[FAIL] {str(e)}")

    # Test Google Gemini
    print("Testing Google Gemini...", end=" ", flush=True)
    try:
        import os
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key.startswith("your-"):
            results['Gemini'] = False
            print("[FAIL] API key not configured")
        else:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content("Say 'Hi'", request_options={"timeout": 10})
            results['Gemini'] = True
            providers_tested.append("Gemini: API key valid")
            print(f"[OK] API key valid")
    except Exception as e:
        results['Gemini'] = False
        print(f"[FAIL] {str(e)}")

    # Test OpenAI
    print("Testing OpenAI...", end=" ", flush=True)
    try:
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("your-"):
            results['OpenAI'] = False
            print("[FAIL] API key not configured")
        else:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, timeout=10)
            models = client.models.list()
            results['OpenAI'] = True
            providers_tested.append(f"OpenAI: {len(models.data)} models available")
            print(f"[OK] {len(models.data)} models available")
    except Exception as e:
        results['OpenAI'] = False
        error_msg = str(e)
        if "401" in error_msg:
            print("[FAIL] Invalid API key")
        else:
            print(f"[FAIL] {error_msg[:50]}")

    # Test Anthropic Claude
    print("Testing Anthropic Claude...", end=" ", flush=True)
    try:
        import os
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key.startswith("your-"):
            results['Claude'] = False
            print("[FAIL] API key not configured")
        else:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key, timeout=10)
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            results['Claude'] = True
            providers_tested.append("Claude: API key valid")
            print("[OK] API key valid")
    except Exception as e:
        results['Claude'] = False
        error_msg = str(e)
        if "401" in error_msg:
            print("[FAIL] Invalid API key")
        else:
            print(f"[FAIL] {error_msg[:50]}")

    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    available = sum(results.values())
    total = len(results)
    print(f"Available providers: {available}/{total}")

    if available == 0:
        print("\n[WARN] No LLM providers available!")
        print("Suggestions:")
        print("  1. Check API keys in .env file")
        print("  2. Ensure Ollama service is running (ollama serve)")
        print("  3. Run 'python test_llm_access.py' for detailed diagnostics")
    elif available < total:
        print("\n[WARN] Some providers unavailable")
        unavailable = [name for name, success in results.items() if not success]
        print(f"Unavailable: {', '.join(unavailable)}")
        print("\nTo configure missing providers:")
        print("  - Edit .env file with valid API keys")
        print("  - See LLM_ACCESS_REPORT.md for setup instructions")
    else:
        print("\n[OK] All providers available!")

    # Show recommendations
    if args.verbose and available > 0:
        print("\n" + "-" * 60)
        print("RECOMMENDATIONS")
        print("-" * 60)
        available_providers = [name for name, success in results.items() if success]

        if 'Gemini' in available_providers:
            print("Primary: Google Gemini (free quota, fast, high quality)")
        if 'Ollama' in available_providers:
            print("Backup: Ollama (free, local, offline)")
        if 'Claude' in available_providers:
            print("Batch: Claude Haiku (cheap ~$0.02/use, fast)")
        if 'OpenAI' in available_providers:
            print("Premium: OpenAI GPT-4 (highest quality)")

    print()


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

  # 元數據管理
  python kb_manage.py metadata-fix --field year --batch
  python kb_manage.py metadata-fix --field all --batch --dry-run
  python kb_manage.py metadata-sync-yaml
  python kb_manage.py metadata-sync-yaml --dry-run

  # 資料庫維護
  python kb_manage.py cleanup
  python kb_manage.py cleanup --dry-run
  python kb_manage.py import-papers
  python kb_manage.py import-papers --dry-run

  # LLM 訪問檢查
  python kb_manage.py check-llm
  python kb_manage.py check-llm --verbose
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

    # metadata fix 命令
    parser_metadata_fix = subparsers.add_parser('metadata-fix', help='修復缺失的元數據')
    parser_metadata_fix.add_argument('--field', choices=['year', 'keywords', 'abstract', 'all'],
                                    default='all', help='要修復的字段 (默認: all)')
    parser_metadata_fix.add_argument('--batch', action='store_true', help='批次修復')
    parser_metadata_fix.add_argument('--dry-run', action='store_true', help='預覽模式（不實際修復）')
    parser_metadata_fix.set_defaults(func=cmd_metadata_fix)

    # metadata sync-yaml 命令
    parser_metadata_sync = subparsers.add_parser('metadata-sync-yaml',
                                                help='同步資料庫標題到 YAML front matter')
    parser_metadata_sync.add_argument('--dry-run', action='store_true', help='預覽模式（不實際修改）')
    parser_metadata_sync.set_defaults(func=cmd_metadata_sync_yaml)

    # cleanup 命令
    parser_cleanup = subparsers.add_parser('cleanup', help='清理孤立的資料庫記錄')
    parser_cleanup.add_argument('--dry-run', action='store_true', help='預覽模式（不實際刪除）')
    parser_cleanup.set_defaults(func=cmd_cleanup)

    # import-papers 命令
    parser_import = subparsers.add_parser('import-papers', help='導入未記錄的 Markdown 檔案')
    parser_import.add_argument('--dry-run', action='store_true', help='預覽模式（不實際導入）')
    parser_import.set_defaults(func=cmd_import_papers)

    # find-relations 命令 (Phase 2.1)
    parser_find_relations = subparsers.add_parser('find-relations',
                                                  help='發現論文關係（引用、主題、作者合作）')
    parser_find_relations.add_argument('paper_id', type=int, help='論文ID')
    parser_find_relations.add_argument('--limit', type=int, default=10,
                                      help='每種關係最多顯示數量 (默認: 10)')
    parser_find_relations.set_defaults(func=cmd_find_relations)

    # build-network 命令 (Phase 2.1)
    parser_build_network = subparsers.add_parser('build-network',
                                                 help='構建論文引用網絡')
    parser_build_network.add_argument('--paper-ids', type=str,
                                     help='論文ID列表（逗號分隔，如 "1,2,5,6"，不指定則為所有論文）')
    parser_build_network.add_argument('--output', type=str,
                                     help='JSON輸出路徑 (例如: network.json)')
    parser_build_network.add_argument('--graphml', type=str,
                                     help='GraphML輸出路徑 (例如: network.graphml，需安裝networkx)')
    parser_build_network.set_defaults(func=cmd_build_network)

    # analyze-relations 命令 (Phase 2.1 - Zettelkasten)
    parser_analyze_relations = subparsers.add_parser('analyze-relations',
                                                     help='分析 Zettelkasten 概念關係 (Phase 2.1)')
    parser_analyze_relations.add_argument('--mode', choices=['find', 'network'],
                                         default='network',
                                         help='操作模式: find (僅識別關係) 或 network (建構網絡)')
    parser_analyze_relations.add_argument('--min-similarity', type=float, default=0.4,
                                         help='最小語義相似度閾值 (0-1，默認: 0.4)')
    parser_analyze_relations.add_argument('--min-confidence', type=float, default=0.3,
                                         help='最小信度閾值 (0-1，默認: 0.3)')
    parser_analyze_relations.add_argument('--relation-types', type=str,
                                         help='關係類型過濾（逗號分隔，如 "leads_to,based_on"）')
    parser_analyze_relations.add_argument('--limit', type=int, default=100,
                                         help='每張卡片檢查的最大相似卡片數 (默認: 100)')
    parser_analyze_relations.add_argument('--output', type=str,
                                         help='網絡數據 JSON 輸出路徑')
    parser_analyze_relations.add_argument('--report', type=str,
                                         help='Markdown 報告輸出路徑')
    parser_analyze_relations.add_argument('--mermaid', type=str,
                                         help='Mermaid 圖表輸出路徑')
    parser_analyze_relations.add_argument('--max-nodes', type=int, default=50,
                                         help='Mermaid 圖表最大節點數 (默認: 50)')
    parser_analyze_relations.set_defaults(func=cmd_analyze_relations)

    # check-cite-keys 命令 (Phase 2)
    parser_check_keys = subparsers.add_parser('check-cite-keys',
                                             help='檢查缺少 cite_key 的論文')
    parser_check_keys.set_defaults(func=cmd_check_cite_keys)

    # update-from-bib 命令 (Phase 2)
    parser_update_bib = subparsers.add_parser('update-from-bib',
                                             help='從 BibTeX 文件更新 cite_key')
    parser_update_bib.add_argument('bib_file', help='.bib 文件路徑')
    parser_update_bib.add_argument('--dry-run', action='store_true',
                                  help='只模擬，不實際更新')
    parser_update_bib.set_defaults(func=cmd_update_from_bib)

    # set-cite-key 命令 (Phase 2)
    parser_set_key = subparsers.add_parser('set-cite-key',
                                          help='手動設置論文的 cite_key')
    parser_set_key.add_argument('paper_id', type=int, help='論文ID')
    parser_set_key.add_argument('cite_key', help='BibTeX cite_key')
    parser_set_key.set_defaults(func=cmd_set_cite_key)

    # check-llm 命令
    parser_check_llm = subparsers.add_parser('check-llm',
                                            help='檢查 LLM 提供者訪問狀態')
    parser_check_llm.add_argument('--verbose', '-v', action='store_true',
                                 help='顯示詳細建議')
    parser_check_llm.set_defaults(func=cmd_check_llm)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
