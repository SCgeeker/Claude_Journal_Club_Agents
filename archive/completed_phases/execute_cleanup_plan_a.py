#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理舊資料夾並重新生成 Paper 43 (Plan A)
"""

import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

output_dir = Path('output/zettelkasten_notes')
archive_dir = output_dir / '_archive_old_format_20251029'
archive_dir.mkdir(exist_ok=True)

print('=' * 80)
print('執行清理方案 A')
print('=' * 80)
print(f'開始時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# Step 1: Delete incorrectly named folder
print('步驟 1: 刪除錯誤命名資料夾')
print('-' * 80)
error_folder = output_dir / 'zettel_1_paper_1_Research_20251104'
if error_folder.exists():
    shutil.rmtree(error_folder)
    print(f'✓ 已刪除: {error_folder.name}')
else:
    print(f'  (已不存在: {error_folder.name})')
print()

# Step 2: Archive folders without corresponding papers
print('步驟 2: 歸檔無對應論文的資料夾')
print('-' * 80)
to_archive = [
    'zettel_Kemmerer2019_20251029',
    'zettel_Rommers2013_20251029',
    'zettel_Speed2025_20251029',
    'zettel_Wu2020_20251029',
    'zettel_Zeelenberg2024_20251029',
    'zettel_Linguistics_20251029'
]

archived_count = 0
for folder_name in to_archive:
    folder = output_dir / folder_name
    if folder.exists():
        dest = archive_dir / folder_name
        shutil.move(str(folder), str(dest))
        print(f'✓ 已歸檔: {folder_name}')
        archived_count += 1
    else:
        print(f'  (已不存在: {folder_name})')

print(f'\n已歸檔 {archived_count} 個資料夾')
print()

# Step 3: Regenerate Paper 43
print('步驟 3: 重新生成 Paper 43')
print('-' * 80)
cmd = [
    'python', 'make_slides.py',
    'Paper 43 Zettelkasten',
    '--from-kb', '43',
    '--style', 'zettelkasten',
    '--domain', 'Research',
    '--detail', 'comprehensive',
    '--llm-provider', 'google',
    '--model', 'gemini-2.0-flash-exp'
]

paper43_success = False
try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode == 0:
        print('✓ Paper 43 重新生成成功')
        paper43_success = True
    else:
        error_msg = result.stderr[:200] if result.stderr else "未知錯誤"
        print(f'✗ Paper 43 重新生成失敗: {error_msg}')
        print('  保留舊版本 zettel_Allassonniere2021_20251029')
except subprocess.TimeoutExpired:
    print('✗ Paper 43 重新生成超時 (300秒)')
    print('  保留舊版本 zettel_Allassonniere2021_20251029')
except Exception as e:
    print(f'✗ 錯誤: {e}')
    print('  保留舊版本 zettel_Allassonniere2021_20251029')

print()

# Step 4: Archive old Allassonniere2021 if regeneration succeeded
if paper43_success:
    print('步驟 4: 歸檔舊的 Allassonniere2021')
    print('-' * 80)
    old_folder = output_dir / 'zettel_Allassonniere2021_20251029'
    if old_folder.exists():
        dest = archive_dir / old_folder.name
        shutil.move(str(old_folder), str(dest))
        print(f'✓ 已歸檔: {old_folder.name}')
    else:
        print('  (資料夾不存在)')
    print()
else:
    print('步驟 4: 跳過（Paper 43 生成失敗，保留舊版本）')
    print()

# Summary
print('=' * 80)
print('清理完成')
print('=' * 80)
print(f'結束時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()
print('保留的舊資料夾:')
print('  - zettel_Altmann2019_20251029 (Paper 38)')
print('  - zettel_Setic2017_20251029 (Paper 42)')
if not paper43_success:
    print('  - zettel_Allassonniere2021_20251029 (Paper 43, 生成失敗)')
print()
print(f'歸檔資料夾數: {archived_count + (1 if paper43_success else 0)}')
print(f'歸檔位置: {archive_dir}')
