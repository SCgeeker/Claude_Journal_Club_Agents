#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作階段清理工具
自動整理和清理工作過程產生的文件，並可選擇性提交到 Git

使用範例:
    # 乾跑模式（只顯示不執行）
    python cleanup_session.py

    # 實際執行清理
    python cleanup_session.py --execute

    # 執行清理並提交到 Git（推薦）
    python cleanup_session.py --execute --git-commit

    # 自動模式（自動執行 + Git 提交）
    python cleanup_session.py --auto --git-commit

    # 指定工作階段類型
    python cleanup_session.py --session batch --execute

    # 不自動備份
    python cleanup_session.py --execute --no-backup

    # 指定報告輸出路徑
    python cleanup_session.py --execute --report my_cleanup_report.md
"""

import sys
import argparse
from pathlib import Path

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.session_organizer import SessionOrganizer


def main():
    parser = argparse.ArgumentParser(
        description="工作階段清理工具 - 自動整理產生的文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 乾跑模式（預設）- 只顯示會做什麼
  python cleanup_session.py

  # 實際執行清理
  python cleanup_session.py --execute

  # 執行清理並提交到 Git
  python cleanup_session.py --execute --git-commit

  # 自動模式（推薦）
  python cleanup_session.py --auto --git-commit

  # 指定工作階段類型
  python cleanup_session.py --session batch --execute

  # 開發文件整理（測試、調試工具、報告歸檔）
  python cleanup_session.py --session development --execute

工作階段類型:
  auto        - 自動檢測（預設）
  batch       - 批次處理
  analysis    - 論文分析
  generation  - 簡報/筆記生成
  development - 開發文件整理（測試腳本、調試工具、報告歸檔）
  full        - 完整清理（包含所有類型）

注意事項:
  • 預設為乾跑模式，使用 --execute 或 --auto 實際執行
  • 建議先執行乾跑模式查看會做什麼
  • 清理前會自動備份資料庫（除非使用 --no-backup）
  • 清理報告會自動保存到根目錄
  • 使用 --git-commit 自動提交整理後的文件到版本控制

開發文件整理說明:
  development 模式會：
  • 移動 test_*.py 到 tests/ 目錄
  • 歸檔 check_*.py, verify_*.py 等調試工具到 archive/debug_tools/
  • 歸檔 *_REPORT_*.md 等開發報告到 archive/reports/
  • 歸檔 setup_*.bat/sh 等設置腳本到 archive/setup_scripts/

歸檔壓縮功能:
  • 自動檢查 archive/ 目錄中超過 7 天的文件
  • 將舊文件壓縮成 archived_YYYYMMDD.zip 格式
  • 壓縮後自動刪除原文件以節省空間
  • 保持原有目錄結構在壓縮檔內
  • 排除已經是壓縮格式的文件（.zip, .tar, .gz 等）
        """
    )

    parser.add_argument(
        '--execute',
        action='store_true',
        help='實際執行清理（預設為乾跑模式）'
    )

    parser.add_argument(
        '--auto',
        action='store_true',
        help='自動模式：實際執行 + 自動確認'
    )

    parser.add_argument(
        '--session',
        choices=['auto', 'batch', 'analysis', 'generation', 'development', 'full'],
        default='auto',
        help='工作階段類型（預設: auto）'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='不自動備份資料庫'
    )

    parser.add_argument(
        '--report',
        type=str,
        help='報告輸出路徑（預設自動生成）'
    )

    parser.add_argument(
        '--rules',
        type=str,
        help='清理規則文件路徑（預設使用內建規則）'
    )

    parser.add_argument(
        '--git-commit',
        action='store_true',
        help='自動提交變更到 Git'
    )

    parser.add_argument(
        '--no-git-auto-stage',
        action='store_true',
        help='不自動 stage 文件（需手動選擇）'
    )

    parser.add_argument(
        '--compress-after-days',
        type=int,
        default=7,
        help='歸檔文件超過指定天數後壓縮（預設: 7 天）'
    )

    parser.add_argument(
        '--no-compress',
        action='store_true',
        help='不執行歸檔壓縮'
    )

    args = parser.parse_args()

    # 確定是否實際執行
    execute = args.execute or args.auto
    dry_run = not execute

    # 自動備份（除非明確禁用）
    auto_backup = not args.no_backup

    # 顯示模式
    if dry_run:
        print("\n" + "="*60)
        print("⚠️  乾跑模式: 只顯示會執行的動作")
        print("   使用 --execute 或 --auto 實際執行")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("🚀 執行清理")
        print("="*60)

        if not args.auto:
            # 需要確認
            confirm = input("\n確認要執行清理？[y/N] ")
            if confirm.lower() != 'y':
                print("❌ 取消清理")
                return

    # 動態更新規則（如果需要）
    rules_overrides = {}
    if args.no_compress:
        rules_overrides['archive_compression'] = {'enabled': False}
    elif args.compress_after_days != 7:
        rules_overrides['archive_compression'] = {
            'enabled': True,
            'compress_after_days': args.compress_after_days
        }

    # 創建整理器
    organizer = SessionOrganizer(
        dry_run=dry_run,
        auto_backup=auto_backup and execute,  # 只在實際執行時備份
        rules_file=args.rules,
        git_commit=args.git_commit and execute,  # 只在實際執行時提交
        git_auto_stage=not args.no_git_auto_stage,
        rules_overrides=rules_overrides
    )

    # 執行清理
    try:
        report = organizer.organize_session(session_type=args.session)

        # 保存報告
        if execute or args.report:
            report_path = organizer.save_report(args.report)
            print(f"\n✅ 清理完成！報告: {report_path}")
        else:
            print("\n✅ 乾跑完成！")
            print("   使用 --execute 實際執行清理")

    except KeyboardInterrupt:
        print("\n\n⚠️  清理已中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 清理失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
