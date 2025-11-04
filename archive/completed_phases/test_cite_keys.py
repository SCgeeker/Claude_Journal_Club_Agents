#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 cite_key 管理功能
"""
import sys
from pathlib import Path

# 添加 src 到 Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from knowledge_base.kb_manager import KnowledgeBaseManager

def test_check_cite_keys():
    """測試檢查缺少 cite_key 的論文"""
    print("=" * 80)
    print("測試：檢查缺少 cite_key 的論文")
    print("=" * 80)

    kb = KnowledgeBaseManager()
    missing = kb.list_papers_without_cite_key()

    print(f"\n發現 {len(missing)} 篇論文缺少 cite_key：\n")

    for paper in missing:
        print(f"ID: {paper['id']:3d} | {paper['title'][:60]}")
        if paper.get('authors'):
            authors_str = ', '.join(paper['authors'][:2])
            if len(paper['authors']) > 2:
                authors_str += f" et al."
            print(f"         | 作者: {authors_str}")
        print()

    print("=" * 80)
    return len(missing)

def test_get_paper_with_cite_key():
    """測試 get_paper_by_id 是否返回 cite_key"""
    print("\n" + "=" * 80)
    print("測試：獲取論文資訊（包含 cite_key）")
    print("=" * 80)

    kb = KnowledgeBaseManager()

    # 測試論文 ID 1
    paper = kb.get_paper_by_id(1)
    if paper:
        print(f"\n論文 ID 1:")
        print(f"  標題: {paper.get('title', 'N/A')}")
        print(f"  cite_key: {paper.get('cite_key', 'N/A')}")
        print(f"  zotero_key: {paper.get('zotero_key', 'N/A')}")
        print()

        if paper.get('cite_key'):
            print("[OK] cite_key field returned correctly")
        else:
            print("[WARNING] cite_key field is empty")
    else:
        print("[ERROR] Paper not found")

    print("=" * 80)

if __name__ == "__main__":
    try:
        # Test 1: Check papers without cite_key
        missing_count = test_check_cite_keys()

        # Test 2: Verify get_paper_by_id returns cite_key
        test_get_paper_with_cite_key()

        print(f"\n測試完成！")
        print(f"需要更新 cite_key 的論文數量: {missing_count}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
