#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次修復 Markdown YAML front matter 語法錯誤
"""

import re
import sys
import io
from pathlib import Path
from typing import List, Tuple

# Windows UTF-8 支援
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fix_yaml_syntax(md_path: Path) -> Tuple[bool, str]:
    """
    修復單個 Markdown 檔案的 YAML 語法錯誤

    Returns:
        (是否修改, 修改描述)
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 YAML front matter
    yaml_match = re.match(r'^(---\s*\n)(.*?)(\n---\s*\n)', content, re.DOTALL)
    if not yaml_match:
        return False, "無 YAML front matter"

    yaml_content = yaml_match.group(2)
    modified = False
    fixes = []

    # 修復 1: 移除標題結尾的冒號
    def fix_title_colon(match):
        nonlocal modified
        title = match.group(1)
        if title.endswith(':'):
            modified = True
            fixes.append("移除標題結尾冒號")
            return f"title: {title[:-1]}"
        return match.group(0)

    yaml_content = re.sub(r'^title:\s*(.+)$', fix_title_colon, yaml_content, flags=re.MULTILINE)

    # 修復 2: 標題包含冒號時加引號
    def fix_title_with_colon(match):
        nonlocal modified
        title = match.group(1).strip()
        if ':' in title and not (title.startswith('"') or title.startswith("'")):
            modified = True
            fixes.append("標題加引號")
            # 轉義內部的引號
            title_escaped = title.replace('"', '\\"')
            return f'title: "{title_escaped}"'
        return match.group(0)

    yaml_content = re.sub(r'^title:\s*(.+)$', fix_title_with_colon, yaml_content, flags=re.MULTILINE)

    # 修復 3: 處理方括號（可能被誤認為 YAML 列表）
    def fix_brackets(match):
        nonlocal modified
        title = match.group(1).strip()
        if '[' in title or ']' in title:
            if not (title.startswith('"') or title.startswith("'")):
                modified = True
                fixes.append("處理方括號")
                title_escaped = title.replace('"', '\\"')
                return f'title: "{title_escaped}"'
        return match.group(0)

    yaml_content = re.sub(r'^title:\s*(.+)$', fix_brackets, yaml_content, flags=re.MULTILINE)

    # 修復 4: year: N/A → year: null
    if re.search(r'^year:\s*N/A\s*$', yaml_content, re.MULTILINE):
        yaml_content = re.sub(r'^year:\s*N/A\s*$', 'year: null', yaml_content, flags=re.MULTILINE)
        modified = True
        fixes.append("year: N/A → null")

    # 修復 5: abstract: None → abstract: null
    if re.search(r'^abstract:\s*None\s*$', yaml_content, re.MULTILINE):
        yaml_content = re.sub(r'^abstract:\s*None\s*$', 'abstract: null', yaml_content, flags=re.MULTILINE)
        modified = True
        fixes.append("abstract: None → null")

    # 修復 6: keywords: 空行 → keywords: []
    if re.search(r'^keywords:\s*$', yaml_content, re.MULTILINE):
        yaml_content = re.sub(r'^keywords:\s*$', 'keywords: []', yaml_content, flags=re.MULTILINE)
        modified = True
        fixes.append("keywords: 空 → []")

    if modified:
        # 重新組合內容
        new_content = yaml_match.group(1) + yaml_content + yaml_match.group(3) + content[yaml_match.end():]

        # 寫回檔案
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, "; ".join(fixes)

    return False, "無需修復"

def batch_fix_yaml(papers_dir: str = "knowledge_base/papers"):
    """批次修復所有 Markdown 檔案"""

    papers_path = Path(papers_dir)
    md_files = list(papers_path.glob("*.md"))

    print(f"找到 {len(md_files)} 個 Markdown 檔案")
    print("=" * 80)

    fixed_count = 0
    skipped_count = 0

    for md_file in md_files:
        modified, description = fix_yaml_syntax(md_file)

        if modified:
            print(f"✅ {md_file.name}")
            print(f"   修復: {description}")
            fixed_count += 1
        else:
            skipped_count += 1

    print()
    print("=" * 80)
    print(f"修復完成:")
    print(f"  修復: {fixed_count}")
    print(f"  跳過: {skipped_count}")
    print(f"  總計: {len(md_files)}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="修復 YAML front matter 語法錯誤")
    parser.add_argument('--file', help='單個檔案路徑')
    parser.add_argument('--batch', action='store_true', help='批次處理所有檔案')

    args = parser.parse_args()

    if args.file:
        md_path = Path(args.file)
        modified, description = fix_yaml_syntax(md_path)
        print(f"檔案: {md_path.name}")
        print(f"修改: {modified}")
        print(f"描述: {description}")
    elif args.batch:
        batch_fix_yaml()
    else:
        parser.print_help()
