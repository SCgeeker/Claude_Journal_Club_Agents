#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作階段清理工具
清理 Phase 2.5-2 期間產生的臨時檔案和資料夾
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.session_organizer import SessionOrganizer
from datetime import datetime

def main():
    """執行清理"""
    print("=" * 70)
    print("[清理工作階段] Phase 2.5-2 臨時檔案清理")
    print("=" * 70)

    organizer = SessionOrganizer(
        project_root=".",
        dry_run=False,
        auto_backup=True,
        git_commit=False
    )

    # 定義要清理的臨時檔案
    temp_files_to_delete = [
        # Phase 2.5-2 標準化腳本
        "standardize_zettel.py",
        "fix_internal_links.py",
        "standardize_zettel_index.py",
        "verify_links.py",

        # 掃描和完成報告
        "ZETTELKASTEN_STANDARDIZATION_SCAN.md",
        "phase2_5_test_output.txt",

        # 其他臨時檔案
        "nul",  # 空白檔案
    ]

    # 定義要清理的臨時資料夾
    temp_dirs_to_delete = [
        # 暫無特定臨時資料夾需要刪除
    ]

    # 執行清理
    deleted_files = []
    deleted_dirs = []
    total_size = 0

    print("\n[清理檔案]")
    for filename in temp_files_to_delete:
        file_path = Path(filename)
        if file_path.exists():
            try:
                size = file_path.stat().st_size
                total_size += size
                file_path.unlink()
                deleted_files.append(filename)
                print(f"  [DELETE] {filename} ({size} bytes)")
            except Exception as e:
                print(f"  [ERROR] {filename}: {str(e)}")

    print("\n[清理資料夾]")
    for dirname in temp_dirs_to_delete:
        dir_path = Path(dirname)
        if dir_path.exists():
            try:
                import shutil
                shutil.rmtree(dir_path)
                deleted_dirs.append(dirname)
                print(f"  [DELETE] {dirname}/")
            except Exception as e:
                print(f"  [ERROR] {dirname}: {str(e)}")

    # 備份知識庫
    print("\n[備份]")
    kb_path = Path("knowledge_base")
    backup_path = Path("archive")

    try:
        backup_path.mkdir(exist_ok=True)

        import zipfile
        import time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"kb_backup_{timestamp}.zip"

        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in kb_path.rglob('*'):
                if file.is_file():
                    zf.write(file, arcname=file.relative_to(kb_path.parent))

        backup_size = backup_file.stat().st_size
        print(f"  [OK] {backup_file.name} ({backup_size} bytes)")
    except Exception as e:
        print(f"  [ERROR] 備份失敗: {str(e)}")

    # 輸出統計
    print("\n" + "=" * 70)
    print("[清理統計]")
    print("=" * 70)
    print(f"刪除的檔案: {len(deleted_files)}")
    print(f"刪除的資料夾: {len(deleted_dirs)}")
    print(f"釋放空間: {total_size} bytes ({total_size / 1024:.2f} KB)")
    print("\n[完成] 工作階段清理完畢")
    print("=" * 70)


if __name__ == "__main__":
    main()
