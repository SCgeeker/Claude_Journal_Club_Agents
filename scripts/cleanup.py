#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專案清理腳本
清理臨時文件、快取和舊輸出
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# 設置UTF-8編碼（Windows相容性）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 專案根目錄
ROOT = Path(__file__).parent.parent


def clean_cache():
    """清理快取目錄"""
    cache_dir = ROOT / ".cache"
    if cache_dir.exists():
        file_count = len(list(cache_dir.glob("*")))
        if file_count > 0:
            for item in cache_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            print(f"✅ 清理快取: 刪除 {file_count} 個文件")
        else:
            print("✅ 快取目錄已經是空的")
    else:
        print("⚠️  快取目錄不存在")


def clean_old_outputs(days=30):
    """清理舊的輸出文件"""
    output_dir = ROOT / "output"
    if not output_dir.exists():
        print("⚠️  輸出目錄不存在")
        return

    cutoff_date = datetime.now() - timedelta(days=days)
    deleted = 0

    for file in output_dir.glob("*.json"):
        if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_date:
            file.unlink()
            deleted += 1

    if deleted > 0:
        print(f"✅ 清理輸出: 刪除 {deleted} 個超過 {days} 天的文件")
    else:
        print(f"✅ 沒有超過 {days} 天的輸出文件")


def clean_logs(days=7):
    """清理舊日誌"""
    logs_dir = ROOT / "logs"
    if not logs_dir.exists():
        print("⚠️  日誌目錄不存在")
        return

    cutoff_date = datetime.now() - timedelta(days=days)
    deleted = 0

    for file in logs_dir.glob("*.log"):
        if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_date:
            file.unlink()
            deleted += 1

    if deleted > 0:
        print(f"✅ 清理日誌: 刪除 {deleted} 個超過 {days} 天的日誌")
    else:
        print(f"✅ 沒有超過 {days} 天的日誌文件")


def clean_pycache():
    """清理Python快取"""
    deleted = 0
    for pycache in ROOT.rglob("__pycache__"):
        shutil.rmtree(pycache)
        deleted += 1

    for pyc in ROOT.rglob("*.pyc"):
        pyc.unlink()
        deleted += 1

    if deleted > 0:
        print(f"✅ 清理Python快取: 刪除 {deleted} 個項目")
    else:
        print("✅ 沒有Python快取需要清理")


def show_disk_usage():
    """顯示磁碟使用情況"""
    print("\n📊 磁碟使用情況:")

    dirs_to_check = [
        ("知識庫", ROOT / "knowledge_base"),
        ("輸出", ROOT / "output"),
        ("快取", ROOT / ".cache"),
        ("日誌", ROOT / "logs"),
    ]

    for name, dir_path in dirs_to_check:
        if dir_path.exists():
            total_size = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())
            size_mb = total_size / (1024 * 1024)
            file_count = len(list(dir_path.rglob("*")))
            print(f"   {name}: {size_mb:.2f} MB ({file_count} 個文件)")
        else:
            print(f"   {name}: 不存在")


def main():
    print("=" * 60)
    print("🧹 專案清理工具")
    print("=" * 60)

    print("\n開始清理...\n")

    clean_cache()
    clean_old_outputs(days=30)
    clean_logs(days=7)
    clean_pycache()

    show_disk_usage()

    print("\n" + "=" * 60)
    print("✅ 清理完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
