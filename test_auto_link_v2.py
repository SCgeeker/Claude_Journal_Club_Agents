#!/usr/bin/env python3
"""
測試 auto_link_v2 改進算法

測試目標：
- cite_key 匹配成功率
- fallback 機制有效性
- 總體成功率 >80%

Author: Claude Code
Date: 2025-10-30
"""

import sys
from pathlib import Path

# 添加項目根目錄到 path
sys.path.insert(0, str(Path(__file__).parent))

from src.knowledge_base import KnowledgeBaseManager


def test_auto_link_v2():
    """測試 auto_link_v2 功能"""
    print("=" * 70)
    print("測試 auto_link_zettel_papers_v2")
    print("=" * 70)

    kb = KnowledgeBaseManager()

    # 執行 v2 算法
    result = kb.auto_link_zettel_papers_v2(
        bib_file=r"D:\core\research\Program_verse\+\My Library.bib",
        similarity_threshold=0.7
    )

    # 評估結果
    print("\n" + "=" * 70)
    print("評估結果")
    print("=" * 70)

    total = result['linked'] + result['unmatched'] + result['skipped']
    success_rate = result['linked'] / total * 100 if total > 0 else 0

    print(f"\n總成功率: {success_rate:.1f}%")

    if success_rate >= 80:
        print("[PASS] 達成目標 (>80%)")
    elif success_rate >= 50:
        print("[PARTIAL] 部分達成 (50-80%)")
    else:
        print("[FAIL] 未達標 (<50%)")

    print(f"\ncite_key 匹配: {result['method_breakdown']['cite_key']} 張")
    print(f"標題模糊匹配: {result['method_breakdown']['fuzzy_match']} 張")

    return result


if __name__ == '__main__':
    try:
        result = test_auto_link_v2()
        print("\n[OK] 測試完成")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
