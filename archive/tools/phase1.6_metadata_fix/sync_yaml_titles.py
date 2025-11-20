#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步 YAML front matter 與資料庫的標題
正確處理含冒號的標題
"""

import sqlite3
import sys
import io
import re
from pathlib import Path
import yaml

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fix_yaml_title(md_path: Path, correct_title: str) -> bool:
    """修復 Markdown YAML front matter 中的標題"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 找到 YAML front matter
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if not yaml_match:
            print(f"  ⚠️ 找不到 YAML front matter")
            return False

        yaml_content = yaml_match.group(1)
        markdown_body = yaml_match.group(2)

        # 解析 YAML
        try:
            metadata = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            print(f"  ⚠️ YAML 解析失敗: {e}")
            return False

        # 檢查是否需要更新
        current_title = metadata.get('title', '')
        if current_title == correct_title:
            print(f"  ✓ 標題已正確，無需更新")
            return True

        # 更新標題
        metadata['title'] = correct_title

        # 重新生成 YAML（使用 default_flow_style=False 保持可讀性）
        new_yaml = yaml.dump(
            metadata,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )

        # 組合新的檔案內容
        new_content = f"---\n{new_yaml}---\n{markdown_body}"

        # 寫回檔案
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"  ✅ 已更新: {current_title} → {correct_title}")
        return True

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return False

def sync_all_titles(db_path: str = "knowledge_base/index.db", dry_run: bool = False):
    """同步所有論文的標題"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 獲取所有論文
    cursor.execute("SELECT id, title, file_path FROM papers ORDER BY id")
    papers = cursor.fetchall()

    conn.close()

    print(f"檢查 {len(papers)} 篇論文的標題同步狀況\n")
    print("=" * 80)

    success = 0
    skipped = 0
    failed = 0

    for paper_id, db_title, file_path in papers:
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            print(f"\n[{paper_id}] ⚠️ 檔案不存在: {file_path}")
            skipped += 1
            continue

        print(f"\n[{paper_id}] {db_title[:60]}")

        if dry_run:
            print(f"  [DRY RUN] 將同步標題到: {file_path_obj.name}")
            success += 1
        else:
            if fix_yaml_title(file_path_obj, db_title):
                success += 1
            else:
                failed += 1

    print("\n" + "=" * 80)
    print(f"同步完成:")
    print(f"  成功: {success}")
    print(f"  跳過: {skipped}")
    print(f"  失敗: {failed}")
    print(f"  總計: {len(papers)}")

def check_colon_titles(db_path: str = "knowledge_base/index.db"):
    """檢查含冒號的標題處理狀況"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, file_path FROM papers WHERE title LIKE '%:%' ORDER BY id")
    papers = cursor.fetchall()

    conn.close()

    print(f"含冒號的標題: {len(papers)} 篇\n")
    print("=" * 80)

    for paper_id, db_title, file_path in papers:
        file_path_obj = Path(file_path)

        print(f"\nID {paper_id}: {db_title}")
        print(f"  檔案: {file_path_obj.name}")

        if not file_path_obj.exists():
            print(f"  ⚠️ 檔案不存在")
            continue

        # 讀取 YAML title
        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()

            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                metadata = yaml.safe_load(yaml_match.group(1))
                yaml_title = metadata.get('title', '')

                if yaml_title == db_title:
                    print(f"  ✅ YAML 標題一致")
                else:
                    print(f"  ❌ YAML 標題不一致:")
                    print(f"     DB:   {db_title}")
                    print(f"     YAML: {yaml_title}")
        except Exception as e:
            print(f"  ⚠️ 讀取失敗: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="同步 YAML 標題與資料庫")
    parser.add_argument('--check', action='store_true', help='檢查含冒號的標題')
    parser.add_argument('--sync', action='store_true', help='同步所有標題')
    parser.add_argument('--dry-run', action='store_true', help='預覽模式（不實際修改）')

    args = parser.parse_args()

    if args.check:
        check_colon_titles()
    elif args.sync:
        sync_all_titles(dry_run=args.dry_run)
    else:
        parser.print_help()
