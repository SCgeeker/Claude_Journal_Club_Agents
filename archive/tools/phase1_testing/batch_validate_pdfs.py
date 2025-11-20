#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次驗證PDF提取質量
對每個有PDF的論文使用 analyze_paper.py --validate 檢查
"""

import sys
import io
import subprocess
from pathlib import Path

# Windows UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 11篇有PDF的論文
papers = [
    {"id": 2, "bibkey": "Yi-2009", "title": "Chinese Classifiers and Count Nouns"},
    {"id": 5, "bibkey": "ChenYiRu-2020", "title": "華語分類詞的界定與教學上的分級"},
    {"id": 6, "bibkey": "Her-2023", "title": "A single origin of numeral classifiers"},
    {"id": 9, "bibkey": "Ahrens-2016", "title": "Classifiers"},
    {"id": 21, "bibkey": "Pecher-2009", "title": "Language comprehenders retain..."},
    {"id": 37, "bibkey": "Abbas-2022", "title": "Goal-Setting Behavior of Workers"},
    {"id": 38, "bibkey": "Altmann-2019", "title": "Events as intersecting object histories"},
    {"id": 39, "bibkey": "Guest-2025b", "title": "What Does 'Human-Centred AI' Mean?"},
    {"id": 40, "bibkey": "Her-2012", "title": "Classifiers: The many ways to profile 'one'"},
    {"id": 41, "bibkey": "Jones-2024", "title": "Multimodal Language Models..."},
    {"id": 42, "bibkey": "Setic-2017", "title": "Numerical congruency effect"},
]

pdf_folder = Path("D:/core/research/Program_verse/+/pdf")

print(f"\n{'='*80}")
print(f"📋 批次驗證PDF提取質量")
print(f"{'='*80}\n")

for i, paper in enumerate(papers, 1):
    pdf_path = pdf_folder / f"{paper['bibkey']}.pdf"

    if not pdf_path.exists():
        print(f"[{i}/11] ❌ ID {paper['id']}: {paper['title'][:50]}")
        print(f"        PDF不存在: {pdf_path.name}\n")
        continue

    print(f"[{i}/11] 🔍 ID {paper['id']}: {paper['title'][:50]}")
    print(f"        PDF: {pdf_path.name}")
    print(f"{'─'*80}")

    try:
        # 使用 analyze_paper.py --validate 檢查提取質量
        result = subprocess.run(
            ['python', 'analyze_paper.py', str(pdf_path), '--validate', '--min-score', '60'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120
        )

        # 顯示輸出（只顯示關鍵信息）
        output_lines = result.stdout.split('\n')

        # 提取關鍵信息
        show_next = False
        for line in output_lines:
            # 顯示基本信息區段
            if '📊 基本信息' in line:
                show_next = True
            elif '📑 論文結構' in line:
                show_next = False

            # 顯示質量檢查區段
            if '🔍 元數據質量檢查' in line:
                show_next = True
            elif '📚 加入知識庫' in line or '✅ 分析完成' in line:
                show_next = False

            if show_next or '質量分數' in line or '發現' in line or '問題' in line:
                # 過濾空行和分隔線
                if line.strip() and not line.strip().startswith('='):
                    print(f"        {line}")

        print()

    except subprocess.TimeoutExpired:
        print(f"        ❌ 處理超時\n")
    except Exception as e:
        print(f"        ❌ 處理失敗: {e}\n")

print(f"{'='*80}")
print(f"✅ 批次驗證完成")
print(f"{'='*80}\n")
