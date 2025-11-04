#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Temporary script to update cite_keys from BibTeX file
Avoids chromadb import issue
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from knowledge_base.kb_manager import KnowledgeBaseManager


def main():
    bib_file = r"D:\core\Research\Program_verse\+\My Library.bib"

    if not Path(bib_file).exists():
        print(f"❌ Error: File not found {bib_file}")
        return 1

    print(f"📖 Parsing {bib_file}...")
    print()

    try:
        kb = KnowledgeBaseManager()
        result = kb.update_cite_keys_from_bib(bib_file, dry_run=False)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    # Print results in Traditional Chinese
    print(f"\n✅ 更新結果:")
    print(f"   總條目數: {result['total_entries']}")
    print(f"   成功更新: {result['success_count']}")
    print(f"   已有 cite_key: {result['already_has_key_count']}")
    print(f"   未找到匹配: {result['not_found_count']}")

    if result['updated']:
        print(f"\n✅ 已更新的論文:")
        for item in result['updated'][:20]:
            print(f"   ID {item['id']:2d}: {item['cite_key']:20s} - {item['title'][:50]}")
        if len(result['updated']) > 20:
            print(f"   ... 以及其他 {len(result['updated']) - 20} 篇")

    if result['not_found']:
        print(f"\n⚠️  未找到匹配的論文 ({len(result['not_found'])}):")
        for item in result['not_found'][:10]:
            print(f"   ID {item['id']:2d}: {item['title'][:50]}")
        if len(result['not_found']) > 10:
            print(f"   ... 以及其他 {len(result['not_found']) - 10} 篇")

    # Summary
    print(f"\n{'='*70}")
    print(f"✅ cite_key 更新完成！")
    print(f"{'='*70}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
