#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試更新後的清理工具
"""

import sys
from pathlib import Path

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.session_organizer import SessionOrganizer


def test_development_cleanup():
    """測試開發文件清理功能"""
    print("=" * 60)
    print("測試開發文件清理功能")
    print("=" * 60)

    # 創建整理器（乾跑模式）
    organizer = SessionOrganizer(
        dry_run=True,  # 只顯示不執行
        auto_backup=False,
        git_commit=False
    )

    # 執行開發文件清理
    report = organizer.organize_session(session_type='development')

    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)

    # 顯示報告摘要
    print(f"\n預計整理文件: {sum(len(files) for files in report.files_organized.values())} 個")
    print(f"預計刪除文件: {len(report.files_deleted)} 個")

    # 詳細顯示各類別
    if report.files_organized:
        print("\n各類別文件：")
        for category, files in report.files_organized.items():
            if files:
                print(f"  {category}: {len(files)} 個文件")


if __name__ == "__main__":
    try:
        test_development_cleanup()
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)