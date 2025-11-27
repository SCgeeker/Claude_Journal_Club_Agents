#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成概念網絡分析（避免 Windows 編碼問題）
"""

import sys
import io
from pathlib import Path

# 強制 UTF-8 輸出（Windows 相容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

sys.path.insert(0, str(Path(__file__).parent))

from src.analyzers.concept_mapper import ConceptMapper

def main():
    print("=" * 70)
    print("Phase 2.2: 概念網絡全面分析與視覺化")
    print("=" * 70)

    # 初始化 ConceptMapper
    print("\n[1/5] 初始化 ConceptMapper...")
    mapper = ConceptMapper()

    # 配置選項
    output_dir = "output/concept_analysis_20251119"
    obsidian_options = {
        'suggested_links_top_n': 50,
        'suggested_links_min_confidence': 0.4,
        'moc_top_n': 20,
        'max_communities': 10,
        'path_top_n': 10
    }

    print(f"\n[2/5] 輸出目錄: {output_dir}")
    print(f"[3/5] Obsidian 選項:")
    for key, value in obsidian_options.items():
        print(f"  - {key}: {value}")

    # 執行完整分析
    print("\n[4/5] 執行分析（這可能需要 2-3 分鐘）...")
    try:
        results = mapper.analyze_all(
            output_dir=output_dir,
            visualize=True,
            obsidian_mode=True,
            obsidian_options=obsidian_options
        )

        print("\n[5/5] 分析完成！")
        print("=" * 70)
        print("輸出摘要")
        print("=" * 70)

        print(f"\n主輸出目錄: {output_dir}")
        print(f"Obsidian 目錄: {output_dir}/obsidian")

        print("\n生成的文件:")
        print("  - concept_network.html (D3.js 互動圖)")
        print("  - concept_network.dot (Graphviz 格式)")
        print("  - analysis_report.md (完整報告)")
        print("  - obsidian/README.md (索引)")
        print("  - obsidian/suggested_links.md (智能連結)")
        print("  - obsidian/key_concepts_moc.md (核心概念)")

        print("\n統計摘要:")
        print(f"  - 節點數: {results.get('node_count', 'N/A')}")
        print(f"  - 邊數: {results.get('edge_count', 'N/A')}")
        print(f"  - 社群數: {results.get('community_count', 'N/A')}")
        print(f"  - 路徑數: {results.get('path_count', 'N/A')}")

        print("\n下一步:")
        print("  1. 在瀏覽器打開 concept_network.html 查看互動圖")
        print("  2. 在 Obsidian 中打開 output/concept_analysis_20251119/obsidian/")
        print("  3. 從 README.md 開始瀏覽")

        print("\n" + "=" * 70)
        print("SUCCESS - 所有分析已完成")
        print("=" * 70 + "\n")

        return 0

    except Exception as e:
        print(f"\nERROR - 分析過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
