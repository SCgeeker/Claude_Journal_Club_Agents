#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自動匹配 PDF 文件
根據內容相似度自動匹配缺失 cite_key 的論文與 PDF 文件
"""

import sqlite3
import sys
from pathlib import Path
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding='utf-8')

def similarity(a, b):
    """計算字串相似度"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_author_year_from_filename(filename):
    """從文件名提取作者和年份"""
    import re
    patterns = [
        r'^([A-Z][a-z]+(?:[A-Z][a-z]+)?)-(\d{4})[a-z]?$',  # Ahrens-2016, ChenYiRu-2020
        r'^([A-Z][a-z]+)_([A-Z][a-z]+)-(\d{4})$',  # Glenberg_Kaschak-2002
    ]

    for pattern in patterns:
        match = re.match(pattern, filename)
        if match:
            if len(match.groups()) == 2:
                return match.group(1), int(match.group(2))
            else:
                return match.group(1) + match.group(2), int(match.group(3))
    return None, None

def read_md_content(md_path):
    """讀取 Markdown 文件的內容預覽"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取完整內容前幾行
        lines = content.split('\n')
        preview = []
        in_full = False

        for line in lines:
            if '## 完整內容' in line:
                in_full = True
                continue
            if in_full and line.strip() and not line.startswith('#'):
                preview.append(line.strip())
                if len(preview) >= 10:
                    break

        return ' '.join(preview)
    except:
        return ""

def main():
    pdf_dir = Path(r"D:\core\Research\Program_verse\+\pdf")

    if not pdf_dir.exists():
        print(f"❌ 目錄不存在: {pdf_dir}")
        return

    # 獲取所有 PDF 文件
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"📁 掃描目錄: {pdf_dir}")
    print(f"   找到 {len(pdf_files)} 個 PDF 文件")
    print()

    # 獲取缺失 cite_key 的論文
    conn = sqlite3.connect('knowledge_base/index.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, file_path
        FROM papers
        WHERE cite_key IS NULL
        ORDER BY id
    ''')

    missing_papers = cursor.fetchall()
    print(f"📄 缺少 cite_key 的論文: {len(missing_papers)} 篇")
    print()

    # 自動匹配
    matches = []
    manual_needed = []

    for paper_id, title, md_path in missing_papers:
        md_content = read_md_content(md_path)
        best_match = None
        best_score = 0.0

        # 策略 1: 根據內容相似度匹配
        for pdf_file in pdf_files:
            pdf_name = pdf_file.stem

            # 計算文件名與標題的相似度
            score_title = similarity(pdf_name, title)

            # 計算文件名與內容的相似度
            score_content = similarity(pdf_name, md_content[:200])

            # 綜合評分
            score = max(score_title, score_content)

            if score > best_score:
                best_score = score
                best_match = pdf_file

        # 判斷匹配置信度
        if best_score > 0.6:  # 高置信度
            matches.append({
                'paper_id': paper_id,
                'title': title,
                'pdf_path': str(best_match),
                'pdf_name': best_match.name,
                'confidence': best_score,
                'auto': True
            })
        elif best_score > 0.3:  # 中等置信度，需要確認
            matches.append({
                'paper_id': paper_id,
                'title': title,
                'pdf_path': str(best_match),
                'pdf_name': best_match.name,
                'confidence': best_score,
                'auto': False
            })
        else:  # 低置信度，需要手動
            manual_needed.append({
                'paper_id': paper_id,
                'title': title,
                'best_match': best_match.name if best_match else 'N/A',
                'confidence': best_score
            })

    conn.close()

    # 顯示結果
    print("=" * 80)
    print("自動匹配結果")
    print("=" * 80)
    print()

    if matches:
        print(f"✅ 高置信度匹配 ({len([m for m in matches if m['auto']])} 篇):")
        print()
        for match in matches:
            if match['auto']:
                print(f"  Paper {match['paper_id']:2d} → {match['pdf_name']}")
                print(f"    標題: {match['title'][:55]}")
                print(f"    置信度: {match['confidence']:.1%}")
                print()

        print()
        print(f"⚠️  需要確認的匹配 ({len([m for m in matches if not m['auto']])} 篇):")
        print()
        for match in matches:
            if not match['auto']:
                print(f"  Paper {match['paper_id']:2d} → {match['pdf_name']}")
                print(f"    標題: {match['title'][:55]}")
                print(f"    置信度: {match['confidence']:.1%}")
                print()

    if manual_needed:
        print()
        print(f"❌ 需要手動匹配 ({len(manual_needed)} 篇):")
        print()
        for item in manual_needed:
            print(f"  Paper {item['paper_id']:2d}: {item['title'][:55]}")
            print(f"    最佳猜測: {item['best_match']} (置信度: {item['confidence']:.1%})")
            print()

    # 生成映射文件
    if matches:
        mapping_file = Path("pdf_path_mapping.txt")

        print()
        print("=" * 80)
        print("生成映射文件")
        print("=" * 80)

        with open(mapping_file, 'w', encoding='utf-8') as f:
            f.write("# PDF 路徑映射文件\n")
            f.write("# 格式: paper_id|pdf_path\n")
            f.write("# 自動生成時間: " + Path(__file__).stat().st_mtime.__str__() + "\n")
            f.write("\n")

            f.write("# 高置信度匹配 (自動處理)\n")
            for match in matches:
                if match['auto']:
                    f.write(f"{match['paper_id']}|{match['pdf_path']}\n")

            f.write("\n# 需要確認的匹配 (請檢查後取消註釋)\n")
            for match in matches:
                if not match['auto']:
                    f.write(f"# {match['paper_id']}|{match['pdf_path']}  # {match['title'][:40]}\n")

            if manual_needed:
                f.write("\n# 需要手動添加\n")
                for item in manual_needed:
                    f.write(f"# {item['paper_id']}|<PDF_PATH>  # {item['title'][:40]}\n")

        print(f"✅ 已生成: {mapping_file}")
        print()
        print("下一步:")
        print("  1. 檢查 pdf_path_mapping.txt")
        print("  2. 確認匹配正確，取消需要的註釋")
        print("  3. 執行: python batch_fix_cite_keys.py")
    else:
        print()
        print("❌ 沒有找到任何匹配")

if __name__ == '__main__':
    main()
