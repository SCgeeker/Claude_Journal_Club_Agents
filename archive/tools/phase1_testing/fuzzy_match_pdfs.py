#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF標題模糊匹配工具
對沒有對應PDF的論文，使用標題在PDF資料夾中模糊搜索
"""

import sys
import io
import sqlite3
from pathlib import Path
from difflib import SequenceMatcher
import re

# Windows UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def normalize_title(title):
    """
    標準化標題用於匹配
    - 轉小寫
    - 移除標點符號
    - 移除多餘空格
    """
    # 轉小寫
    title = title.lower()

    # 移除特殊字元
    title = re.sub(r'[:\-–—()[\]{},.;!?\'\"&]', ' ', title)

    # 移除多餘空格
    title = ' '.join(title.split())

    return title


def extract_title_from_bibkey(bibkey):
    """
    從bibkey提取可能的標題關鍵詞
    例如: "Altmann-2019" -> "Altmann"
    """
    parts = bibkey.split('-')
    if len(parts) >= 2:
        # 移除年份部分
        return parts[0]
    return bibkey


def similarity_score(str1, str2):
    """計算兩個字串的相似度（0-1）"""
    return SequenceMatcher(None, str1, str2).ratio()


def find_matching_pdfs(paper_title, pdf_files, threshold=0.5, max_results=5):
    """
    在PDF檔案中尋找與論文標題相似的檔案

    Args:
        paper_title: 論文標題
        pdf_files: PDF檔案列表 {bibkey: Path}
        threshold: 最低相似度閾值
        max_results: 最多返回結果數

    Returns:
        [(bibkey, pdf_path, similarity), ...]
    """
    normalized_title = normalize_title(paper_title)

    matches = []

    for bibkey, pdf_path in pdf_files.items():
        # 從bibkey提取作者名
        author_name = extract_title_from_bibkey(bibkey)
        normalized_bibkey = normalize_title(bibkey)
        normalized_author = normalize_title(author_name)

        # 計算相似度（多種策略）

        # 策略1: 標題與bibkey整體相似度
        score1 = similarity_score(normalized_title, normalized_bibkey)

        # 策略2: 標題包含作者名
        score2 = 0
        if normalized_author in normalized_title or normalized_title in normalized_bibkey:
            score2 = 0.7

        # 策略3: 提取標題關鍵詞與bibkey匹配
        title_words = set(normalized_title.split())
        bibkey_words = set(normalized_bibkey.split())

        # Jaccard相似度
        if title_words and bibkey_words:
            intersection = title_words & bibkey_words
            union = title_words | bibkey_words
            score3 = len(intersection) / len(union) if union else 0
        else:
            score3 = 0

        # 綜合評分（加權平均）
        final_score = max(score1 * 0.4, score2 * 0.3, score3 * 0.3)

        if final_score >= threshold:
            matches.append((bibkey, pdf_path, final_score))

    # 按相似度排序
    matches.sort(key=lambda x: x[2], reverse=True)

    return matches[:max_results]


def main():
    db_path = "knowledge_base/index.db"
    pdf_folder = Path("D:/core/research/Program_verse/+/pdf")

    print(f"\n{'='*80}")
    print(f"🔍 PDF標題模糊匹配工具")
    print(f"{'='*80}\n")

    # 掃描PDF資料夾
    print(f"📁 掃描PDF資料夾: {pdf_folder}")
    pdf_files = {f.stem: f for f in pdf_folder.glob('*.pdf')}
    print(f"📄 找到 {len(pdf_files)} 個PDF文件\n")

    # 查詢沒有對應PDF的論文
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, cite_key, file_path
        FROM papers
        ORDER BY id
    ''')

    all_papers = cursor.fetchall()
    conn.close()

    # 篩選出沒有對應PDF的論文
    no_pdf_papers = []

    for pid, title, cite_key, file_path in all_papers:
        md_stem = Path(file_path).stem if file_path else None
        has_pdf = False

        # 檢查是否有PDF
        if md_stem and md_stem in pdf_files:
            has_pdf = True
        elif cite_key and cite_key in pdf_files:
            has_pdf = True

        if not has_pdf:
            no_pdf_papers.append((pid, title, cite_key, file_path))

    print(f"📊 統計:")
    print(f"  總論文數: {len(all_papers)}")
    print(f"  有PDF: {len(all_papers) - len(no_pdf_papers)}")
    print(f"  無PDF: {len(no_pdf_papers)}")

    if not no_pdf_papers:
        print("\n✅ 所有論文都有對應的PDF！")
        return

    print(f"\n{'='*80}")
    print(f"🔍 開始模糊匹配 {len(no_pdf_papers)} 篇論文")
    print(f"{'='*80}\n")

    # 用於儲存匹配結果
    matched_papers = []

    for i, (pid, title, cite_key, file_path) in enumerate(no_pdf_papers, 1):
        print(f"[{i}/{len(no_pdf_papers)}] ID {pid}: {title[:60]}")

        # 尋找匹配的PDF
        matches = find_matching_pdfs(title, pdf_files, threshold=0.3, max_results=5)

        if matches:
            print(f"  📌 找到 {len(matches)} 個可能的匹配:")
            for j, (bibkey, pdf_path, score) in enumerate(matches, 1):
                confidence = "高" if score >= 0.7 else "中" if score >= 0.5 else "低"
                print(f"     {j}. [{score*100:.1f}% 相似度 - {confidence}] {bibkey}.pdf")

            matched_papers.append({
                'paper_id': pid,
                'paper_title': title,
                'matches': matches
            })
        else:
            print(f"  ❌ 未找到匹配的PDF")

        print()

    # 顯示總結
    print(f"{'='*80}")
    print(f"📊 匹配總結")
    print(f"{'='*80}\n")

    high_confidence = sum(1 for p in matched_papers if p['matches'][0][2] >= 0.7)
    medium_confidence = sum(1 for p in matched_papers if 0.5 <= p['matches'][0][2] < 0.7)
    low_confidence = sum(1 for p in matched_papers if p['matches'][0][2] < 0.5)

    print(f"找到匹配的論文: {len(matched_papers)}/{len(no_pdf_papers)}")
    print(f"  高信度 (≥70%): {high_confidence}")
    print(f"  中信度 (50-69%): {medium_confidence}")
    print(f"  低信度 (<50%): {low_confidence}")
    print(f"\n未找到匹配: {len(no_pdf_papers) - len(matched_papers)}")

    # 保存結果到文件供後續處理
    if matched_papers:
        import json
        with open('fuzzy_match_results.json', 'w', encoding='utf-8') as f:
            json.dump(matched_papers, f, ensure_ascii=False, indent=2)

        print(f"\n💾 匹配結果已保存到: fuzzy_match_results.json")
        print(f"\n💡 下一步:")
        print(f"   1. 查看 fuzzy_match_results.json 確認匹配")
        print(f"   2. 使用 confirm_fuzzy_matches.py 確認並修復")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
