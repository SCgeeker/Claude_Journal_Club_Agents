#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
論文質量檢查命令行工具
檢查知識庫中論文的元數據質量並生成報告

使用範例:
    # 檢查所有論文
    python check_quality.py

    # 檢查特定論文
    python check_quality.py --paper-id 1

    # 檢查並生成詳細報告
    python check_quality.py --detail comprehensive --output quality_report.txt

    # 檢查並自動修復問題
    python check_quality.py --auto-fix

    # 檢測重複論文
    python check_quality.py --detect-duplicates --threshold 0.85

    # 僅顯示有嚴重問題的論文
    python check_quality.py --critical-only
"""

import sys
import argparse
import json
from pathlib import Path

# Windows 編碼修復
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.checkers import QualityChecker


def main():
    parser = argparse.ArgumentParser(
        description="論文質量檢查工具 - 檢查知識庫中論文的元數據質量",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 檢查所有論文（標準報告）
  python check_quality.py

  # 檢查特定論文
  python check_quality.py --paper-id 1

  # 生成詳細報告
  python check_quality.py --detail comprehensive

  # 僅顯示有嚴重問題的論文
  python check_quality.py --critical-only

  # 檢查並自動修復問題
  python check_quality.py --auto-fix

  # 檢測重複論文（相似度 >= 85%）
  python check_quality.py --detect-duplicates --threshold 0.85

  # 將報告保存到文件
  python check_quality.py --output quality_report.txt

  # JSON格式輸出
  python check_quality.py --format json --output quality_report.json

詳細程度:
  minimal        - 僅總結統計和嚴重問題
  standard       - 包含警告和質量評分（預設）
  comprehensive  - 包含所有詳細信息和建議
        """
    )

    # 檢查目標
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        '--paper-id',
        type=int,
        help='檢查特定論文ID'
    )
    target_group.add_argument(
        '--all',
        action='store_true',
        default=True,
        help='檢查所有論文（預設）'
    )

    # 輸出選項
    parser.add_argument(
        '--detail',
        choices=['minimal', 'standard', 'comprehensive'],
        default='standard',
        help='報告詳細程度（預設: standard）'
    )

    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='輸出格式（預設: text）'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='輸出文件路徑（可選，默認輸出到終端）'
    )

    # 過濾選項
    parser.add_argument(
        '--critical-only',
        action='store_true',
        help='僅顯示有嚴重問題的論文'
    )

    parser.add_argument(
        '--min-score',
        type=float,
        help='僅顯示評分低於此值的論文'
    )

    # 修復選項
    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='自動修復可修復的問題'
    )

    # 重複檢測
    parser.add_argument(
        '--detect-duplicates',
        action='store_true',
        help='檢測重複論文'
    )

    parser.add_argument(
        '--threshold',
        type=float,
        default=0.85,
        help='重複檢測相似度閾值（0-1，預設: 0.85）'
    )

    # API選項
    parser.add_argument(
        '--disable-api',
        action='store_true',
        help='禁用外部API（跳過元數據增強）'
    )

    args = parser.parse_args()

    # 創建檢查器
    print("初始化質量檢查器...")
    checker = QualityChecker(enable_api=not args.disable_api)

    # 檢測重複論文（如果啟用）
    if args.detect_duplicates:
        print(f"\n檢測重複論文（相似度閾值: {args.threshold}）...")
        duplicates = checker.detect_duplicates(threshold=args.threshold)

        if duplicates:
            print(f"\n🔍 發現 {len(duplicates)} 組可能重複的論文:")
            print("=" * 70)
            for i, (id1, id2, similarity) in enumerate(duplicates, 1):
                paper1 = checker.kb.get_paper_by_id(id1)
                paper2 = checker.kb.get_paper_by_id(id2)
                print(f"\n{i}. 相似度: {similarity:.2%}")
                print(f"   論文 {id1}: {paper1.get('title', 'Unknown')[:60]}...")
                print(f"   論文 {id2}: {paper2.get('title', 'Unknown')[:60]}...")
        else:
            print("✅ 未發現重複論文")

        if not args.paper_id and not args.all:
            return

    # 執行檢查
    if args.paper_id:
        # 檢查單篇論文
        print(f"\n檢查論文 ID {args.paper_id}...")
        try:
            report = checker.check_paper(args.paper_id, auto_fix=args.auto_fix)
            reports = [report]
        except ValueError as e:
            print(f"❌ 錯誤: {e}")
            sys.exit(1)
    else:
        # 檢查所有論文
        print("\n檢查知識庫中的所有論文...")
        reports = checker.check_all_papers(auto_fix=args.auto_fix)

    # 應用過濾
    if args.critical_only:
        reports = [r for r in reports if r.has_critical_issues()]
        print(f"過濾後: {len(reports)} 篇論文有嚴重問題")

    if args.min_score is not None:
        reports = [r for r in reports if r.overall_score < args.min_score]
        print(f"過濾後: {len(reports)} 篇論文評分低於 {args.min_score}")

    if not reports:
        print("✅ 沒有符合條件的論文")
        return

    # 生成輸出
    if args.format == 'json':
        # JSON格式
        output_data = {
            "summary": {
                "total_papers": len(reports),
                "average_score": sum(r.overall_score for r in reports) / len(reports),
                "critical_issues": sum(len(r.get_critical_issues()) for r in reports),
                "warnings": sum(len(r.get_warnings()) for r in reports)
            },
            "reports": [r.to_dict() for r in reports]
        }
        output_content = json.dumps(output_data, ensure_ascii=False, indent=2)
    else:
        # 文本格式
        if len(reports) == 1:
            # 單篇論文詳細報告
            output_content = reports[0].to_text(detail_level=args.detail)
        else:
            # 多篇論文總結報告
            output_content = checker.generate_summary_report(reports, detail_level=args.detail)

            # 添加個別論文詳情（如果是comprehensive模式）
            if args.detail == "comprehensive":
                output_content += "\n\n" + "=" * 80
                output_content += "\n個別論文詳細報告:\n"
                output_content += "=" * 80 + "\n"

                for i, report in enumerate(reports, 1):
                    if i > 20:  # 最多顯示20篇詳細報告
                        output_content += f"\n... 還有 {len(reports) - 20} 篇論文報告已省略\n"
                        break
                    output_content += "\n" + report.to_text(detail_level="standard") + "\n"

    # 輸出結果
    if args.output:
        # 保存到文件
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)

        print(f"\n✅ 報告已保存: {output_path}")
        print(f"   檢查論文數: {len(reports)}")
        print(f"   平均評分: {sum(r.overall_score for r in reports) / len(reports):.1f}/100")

        if args.auto_fix:
            print(f"   自動修復: 已啟用")
    else:
        # 輸出到終端
        print("\n" + output_content)

    # 退出碼
    # 如果有嚴重問題，返回1；否則返回0
    has_critical = any(r.has_critical_issues() for r in reports)
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  已中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
