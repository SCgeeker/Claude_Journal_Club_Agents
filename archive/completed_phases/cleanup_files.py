#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""文件清理脚本 - 移动已完成的文档到归档目录"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# 归档基础目录
ARCHIVE_BASE = Path("archive/completed_phases")

# 文件分类映射
FILE_CATEGORIES = {
    'phase2_summaries': [
        'PHASE2_DAY1_SUMMARY.md',
        'PHASE2_DAY3_SUMMARY.md',
        'PHASE2_RECOVERY_PLAN.md',
        'PHASE2_COMPLETION_REPORT.md',
    ],
    'cleanup_reports': [
        'CLEANUP_REPORT_20251101.md',
        'CLEANUP_UPDATE_20251101.md',
        'FILE_CLEANUP_REPORT_20251102_214305.md',
        'FILE_CLEANUP_REPORT_20251103_215517.md',
        'FILE_CLEANUP_REPORT_20251103_220152.md',
    ],
    'session_summaries': [
        'SESSION_SUMMARY_20251103.md',
        'END_OF_DAY_SUMMARY_20251103_FINAL.md',
    ],
    'feature_logs': [
        'ARCHIVE_COMPRESSION_FEATURE_20251101.md',
        'WORK_LOG_PHASE1.5.md',
        'VECTOR_SEARCH_TEST_REPORT.md',
        'ZETTELKASTEN_USAGE_GUIDE.md',
    ],
    'execution_docs': [
        'EXECUTION_QUICK_REFERENCE.md',
        'EXECUTION_STATUS_2025_11_03.md',
        'TOMORROW_QUICK_START.md',
        'BATCH_C_ZETTEL_EXPANDED_REPORT.md',
    ],
    'zotero_import': [
        'ZOTERO_IMPORT_ASSESSMENT.md',
        'ZOTERO_SYNC_ROADMAP.md',
        'SMART_IMPORT_READY_REPORT.md',
        'PHASE2_2_EXECUTION_PLAN.md',
        'PHASE2_2_PRIORITY_ANALYSIS.md',
    ],
    'temp_files': [
        'batch_test_limit1.log',
        'batch_zettel_generation.log',
        'citation_network.json',
        'kb_profile.json',
        'pdf_verification_result.json',
        'smart_import_list.json',
        'batch_b1_candidates.bib',
        'nul',
    ],
}

# 错误路径文件（需要删除）
ERROR_PATH_FILES = [
    'D:coreresearchclaude_lit_workflowsrcanalyzers',
    'D:coreresearchclaude_lit_workflowsrcanalyzers__init__.py',
    'D:coreresearchclaude_lit_workflowsrcanalyzersrelation_finder.py',
]

def move_files():
    """移动文件到归档目录"""
    stats = {
        'moved': 0,
        'missing': 0,
        'errors': 0,
    }

    moved_files = []
    missing_files = []

    for category, files in FILE_CATEGORIES.items():
        dest_dir = ARCHIVE_BASE / category
        dest_dir.mkdir(parents=True, exist_ok=True)

        for filename in files:
            src = Path(filename)
            if src.exists():
                try:
                    dest = dest_dir / filename
                    shutil.move(str(src), str(dest))
                    moved_files.append(f"{category}/{filename}")
                    stats['moved'] += 1
                    print(f"[OK] {filename} -> {category}/")
                except Exception as e:
                    print(f"[ERROR] Failed to move {filename}: {e}")
                    stats['errors'] += 1
            else:
                missing_files.append(filename)
                stats['missing'] += 1

    return stats, moved_files, missing_files

def delete_error_files():
    """删除错误路径文件"""
    deleted = []
    for path_str in ERROR_PATH_FILES:
        path = Path(path_str)
        try:
            if path.is_file():
                path.unlink()
                deleted.append(path_str)
                print(f"[DEL] File: {path_str}")
            elif path.is_dir():
                shutil.rmtree(path)
                deleted.append(path_str)
                print(f"[DEL] Directory: {path_str}")
            else:
                print(f"[WARN] Not found: {path_str}")
        except Exception as e:
            print(f"[ERROR] Failed to delete {path_str}: {e}")

    return deleted

def generate_report(stats, moved_files, missing_files, deleted_files):
    """生成清理报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"FILE_CLEANUP_REPORT_{timestamp}.md"

    content = f"""# 文件清理报告

**执行时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 统计摘要

- ✅ 成功移动: {stats['moved']} 个文件
- ⚠️  文件不存在: {stats['missing']} 个
- ❌ 移动失败: {stats['errors']} 个
- 🗑️  删除错误文件: {len(deleted_files)} 个

## 📦 移动的文件

"""

    # 按类别组织
    from collections import defaultdict
    by_category = defaultdict(list)
    for filepath in moved_files:
        category, filename = filepath.split('/', 1)
        by_category[category].append(filename)

    for category, files in sorted(by_category.items()):
        content += f"\n### {category.replace('_', ' ').title()}\n\n"
        for f in sorted(files):
            content += f"- {f}\n"

    if missing_files:
        content += "\n## ⚠️ 未找到的文件\n\n"
        for f in sorted(missing_files):
            content += f"- {f}\n"

    if deleted_files:
        content += "\n## 🗑️ 删除的错误路径文件\n\n"
        for f in deleted_files:
            content += f"- {f}\n"

    content += f"\n---\n\n**归档位置**: `archive/completed_phases/`\n"
    content += f"**下一步**: 压缩归档为 ZIP 文件\n"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n[REPORT] Generated: {report_file}")
    return report_file

def main():
    print("[*] Starting file cleanup...\n")

    # Step 1: 移动文件
    print("=" * 60)
    print("Step 1: Moving files to archive")
    print("=" * 60)
    stats, moved_files, missing_files = move_files()

    # Step 2: 删除错误文件
    print("\n" + "=" * 60)
    print("Step 2: Deleting error files")
    print("=" * 60)
    deleted_files = delete_error_files()

    # Step 3: 生成报告
    print("\n" + "=" * 60)
    print("Step 3: Generating cleanup report")
    print("=" * 60)
    report_file = generate_report(stats, moved_files, missing_files, deleted_files)

    # 摘要
    print("\n" + "=" * 60)
    print("[OK] Cleanup completed!")
    print("=" * 60)
    print(f"Moved: {stats['moved']} files")
    print(f"Deleted: {len(deleted_files)} error files")
    print(f"Report: {report_file}")
    print("\nNext step: Compress archive to ZIP file")

if __name__ == '__main__':
    main()
