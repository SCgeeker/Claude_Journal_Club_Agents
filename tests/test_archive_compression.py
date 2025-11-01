#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試歸檔壓縮功能
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 設置UTF-8編碼（Windows相容性）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

def test_archive_compression():
    """測試歸檔壓縮功能"""
    print("=" * 60)
    print("測試歸檔壓縮功能")
    print("=" * 60)

    # 檢查 archive 目錄是否存在
    archive_dir = Path("archive")
    if not archive_dir.exists():
        print("\n⚠️ archive 目錄不存在")
        return

    print(f"\n📂 檢查 archive 目錄...")

    # 列出所有文件及其修改時間
    all_files = []
    for file_path in archive_dir.rglob('*'):
        if file_path.is_file():
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age_days = (datetime.now() - mtime).days
            size = file_path.stat().st_size
            all_files.append((file_path, mtime, age_days, size))

    if not all_files:
        print("   沒有找到任何文件")
        return

    # 按年齡分類
    old_files = [f for f in all_files if f[2] > 7]
    recent_files = [f for f in all_files if f[2] <= 7]

    print(f"\n📊 文件統計:")
    print(f"   總文件數: {len(all_files)}")
    print(f"   超過 7 天: {len(old_files)} 個文件")
    print(f"   7 天內: {len(recent_files)} 個文件")

    if old_files:
        print(f"\n🗓️ 超過 7 天的文件:")
        total_size = 0
        for file_path, mtime, age, size in old_files[:10]:  # 只顯示前10個
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                # 如果不在當前目錄下，使用絕對路徑
                rel_path = file_path
            total_size += size
            print(f"   • {rel_path} ({age} 天前, {size/1024:.1f}KB)")
        if len(old_files) > 10:
            print(f"   ... 還有 {len(old_files) - 10} 個文件")

        print(f"\n   總大小: {total_size/1024/1024:.2f}MB")
        print(f"   這些文件將被壓縮成 archived_{datetime.now().strftime('%Y%m%d')}.zip")

    # 測試壓縮功能（乾跑模式）
    print("\n" + "=" * 60)
    print("執行乾跑測試...")
    print("=" * 60)

    os.system("python cleanup_session.py --session full")

    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)
    print("\n💡 提示:")
    print("   • 使用 --execute 參數實際執行壓縮")
    print("   • 使用 --compress-after-days N 自訂天數閾值")
    print("   • 使用 --no-compress 跳過壓縮")


if __name__ == "__main__":
    test_archive_compression()