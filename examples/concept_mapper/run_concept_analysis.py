#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
臨時腳本：執行概念網絡分析（繞過 kb_manage.py 的 stdout 問題）
"""

from pathlib import Path
from src.analyzers.concept_mapper import ConceptMapper

def main():
    print("\n" + "=" * 70)
    print("🔍 Phase 2.3: 概念網絡分析 - 驗證修復")
    print("=" * 70)

    # 初始化 ConceptMapper
    print("\n1️⃣ 初始化 ConceptMapper...")
    mapper = ConceptMapper()

    # 準備輸出目錄和選項
    output_dir = "output/concept_analysis_fixed"
    obsidian_options = {
        'suggested_links_top_n': 50,
        'suggested_links_min_confidence': 0.4,
        'moc_top_n': 20,
        'max_communities': 10,
        'path_top_n': 10
    }

    print(f"   輸出目錄: {output_dir}")
    print(f"   最小信度: {obsidian_options['suggested_links_min_confidence']}")
    print(f"   Top N 建議: {obsidian_options['suggested_links_top_n']}")

    # 執行完整分析
    print("\n2️⃣ 執行完整分析...")
    try:
        results = mapper.analyze_all(
            output_dir=output_dir,
            visualize=True,
            obsidian_mode=True,
            obsidian_options=obsidian_options
        )

        print("\n" + "=" * 70)
        print("✅ 分析完成！")
        print("=" * 70)

        # 顯示統計
        print("\n📊 統計摘要:")
        print(f"   - 節點數: {results.get('node_count', 'N/A')}")
        print(f"   - 邊數: {results.get('edge_count', 'N/A')}")
        print(f"   - 社群數: {results.get('community_count', 'N/A')}")
        print(f"   - 路徑數: {results.get('path_count', 'N/A')}")

        # Obsidian 輸出提示
        obsidian_dir = Path(output_dir) / "obsidian"
        print(f"\n📁 Obsidian 輸出: {obsidian_dir.absolute()}")
        print("\n建議:")
        print(f"   1. 在 Obsidian 中打開 {obsidian_dir.absolute()}")
        print(f"   2. 從 README.md 開始瀏覽")
        print(f"   3. 查看 suggested_links.md 確認建議數量")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
