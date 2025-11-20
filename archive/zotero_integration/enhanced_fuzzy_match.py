#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版PDF模糊匹配工具
從Markdown完整內容中提取作者和年份信息進行匹配
"""

import sys
import io
import sqlite3
from pathlib import Path
import re

# Windows UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def extract_author_year_from_markdown(md_path):
    """
    從Markdown文件中提取作者和年份信息

    策略:
    1. 查找 "To cite this article: Author (YYYY):"
    2. 查找 "Published online: DD Mon YYYY"
    3. 查找作者列表
    4. 查找年份 (YYYY)
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取前2000字元（通常包含元數據）
        header = content[:2000]

        authors = []
        year = None

        # 策略1: 查找 "To cite this article: Author (YYYY):"
        cite_match = re.search(r'To cite this article:?\s*(.+?)\s*\((\d{4})\)', header, re.IGNORECASE)
        if cite_match:
            author_str = cite_match.group(1)
            year = int(cite_match.group(2))

            # 提取作者姓氏
            # 格式: "B. de Koning, S. Wassenburg" 或 "Koning, B. & Smith, J."
            author_parts = re.split(r'[,&]', author_str)
            for part in author_parts:
                # 移除首字母縮寫
                part = re.sub(r'\b[A-Z]\.\s*', '', part.strip())
                # 提取姓氏（最後一個單詞）
                words = part.split()
                if words:
                    # 處理 "de Koning" 這類複合姓氏
                    if len(words) >= 2 and words[-2].lower() in ['de', 'van', 'von', 'del', 'la']:
                        last_name = ' '.join(words[-2:])
                    else:
                        last_name = words[-1]

                    # 清理姓氏
                    last_name = re.sub(r'[^a-zA-Z]', '', last_name)
                    if last_name and len(last_name) > 2:
                        authors.append(last_name)

        # 策略2: 如果沒找到年份，查找 "Published online: DD Mon YYYY"
        if not year:
            pub_match = re.search(r'Published.*?(\d{4})', header, re.IGNORECASE)
            if pub_match:
                year = int(pub_match.group(1))

        # 策略3: 如果沒找到年份，查找期刊引用中的年份
        # 格式: "Journal Name YYYY 13: 168" 或 "Journal (YYYY)"
        if not year:
            journal_year = re.search(r'(?:Science|Psychology|Journal|Review)\s+(\d{4})\s+\d+:', header, re.IGNORECASE)
            if journal_year:
                year = int(journal_year.group(1))

        # 策略4: 如果還沒找到，查找獨立的四位數年份（但排除2025，那是創建時間）
        if not year:
            year_matches = re.findall(r'\b(19\d{2}|20[01]\d|202[0-4])\b', header)
            # 排除 created: 2025 這類的年份
            filtered_years = [y for y in year_matches if y != '2025']
            if filtered_years:
                year = int(filtered_years[0])

        # 策略4: 如果沒找到作者，查找作者列表格式
        if not authors:
            # 格式: "Author1, Author2 & Author3"
            author_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z]\.\s+)?[A-Z][a-z]+(?:\s*[,&]\s*[A-Z][a-z]+(?:\s+[A-Z]\.\s+)?[A-Z][a-z]+)*)', header)
            if author_match:
                author_str = author_match.group(1)
                author_parts = re.split(r'[,&]', author_str)
                for part in author_parts:
                    words = part.strip().split()
                    if words:
                        last_name = words[-1]
                        last_name = re.sub(r'[^a-zA-Z]', '', last_name)
                        if last_name and len(last_name) > 2:
                            authors.append(last_name)

        return authors[:3], year  # 只返回前3位作者

    except Exception as e:
        print(f"⚠️  讀取失敗 {md_path}: {e}")
        return [], None


def generate_possible_bibkeys(authors, year):
    """
    根據作者和年份生成可能的bibkey組合

    Args:
        authors: ['Koning', 'Wassenburg', 'Bos']
        year: 2017

    Returns:
        ['Koning-2017', 'deKoning-2017', 'Wassenburg-2017', ...]
    """
    if not year:
        return []

    bibkeys = []

    for author in authors:
        # 基本格式: Author-YYYY
        bibkeys.append(f"{author}-{year}")

        # 首字母小寫: author-YYYY
        bibkeys.append(f"{author.lower()}-{year}")

        # 處理複合姓氏
        if ' ' in author:
            parts = author.split()
            # de Koning -> deKoning-2017
            bibkeys.append(f"{''.join(parts)}-{year}")
            # de Koning -> Koning-2017 (只用最後部分)
            bibkeys.append(f"{parts[-1]}-{year}")

    return list(set(bibkeys))  # 去重


def main():
    db_path = "knowledge_base/index.db"
    pdf_folder = Path("D:/core/research/Program_verse/+/pdf")

    print(f"\n{'='*80}")
    print(f"🔍 增強版PDF模糊匹配工具")
    print(f"{'='*80}\n")

    # 掃描PDF資料夾
    print(f"📁 掃描PDF資料夾: {pdf_folder}")
    pdf_files = {f.stem: str(f) for f in pdf_folder.glob('*.pdf')}
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
    print(f"🔍 從Markdown內容提取作者和年份")
    print(f"{'='*80}\n")

    # 用於儲存匹配結果
    matched_papers = []

    for i, (pid, title, cite_key, file_path) in enumerate(no_pdf_papers, 1):
        print(f"[{i}/{len(no_pdf_papers)}] ID {pid}: {title[:55]}")

        # 從Markdown提取作者和年份
        authors, year = extract_author_year_from_markdown(file_path)

        if authors:
            print(f"  📝 提取作者: {', '.join(authors)}")
        if year:
            print(f"  📅 提取年份: {year}")

        # 生成可能的bibkey
        possible_bibkeys = generate_possible_bibkeys(authors, year)

        if possible_bibkeys:
            print(f"  🔑 可能的bibkey: {', '.join(possible_bibkeys[:5])}")

            # 檢查是否有匹配的PDF
            found_pdfs = []
            for bibkey in possible_bibkeys:
                if bibkey in pdf_files:
                    found_pdfs.append((bibkey, pdf_files[bibkey]))

            if found_pdfs:
                print(f"  ✅ 找到 {len(found_pdfs)} 個匹配的PDF:")
                for bibkey, pdf_path in found_pdfs:
                    print(f"     → {bibkey}.pdf")

                matched_papers.append({
                    'paper_id': pid,
                    'paper_title': title,
                    'authors': authors,
                    'year': year,
                    'matches': found_pdfs
                })
            else:
                print(f"  ❌ 未找到匹配的PDF")
        else:
            print(f"  ⚠️  無法提取作者/年份信息")

        print()

    # 顯示總結
    print(f"{'='*80}")
    print(f"📊 匹配總結")
    print(f"{'='*80}\n")

    print(f"找到匹配的論文: {len(matched_papers)}/{len(no_pdf_papers)}")
    print(f"未找到匹配: {len(no_pdf_papers) - len(matched_papers)}")

    if matched_papers:
        print(f"\n📋 匹配詳情:\n")
        for item in matched_papers:
            print(f"ID {item['paper_id']:2d}: {item['paper_title'][:50]}")
            print(f"      作者: {', '.join(item['authors'])}")
            print(f"      年份: {item['year']}")
            print(f"      PDF: {', '.join([Path(m[1]).name for m in item['matches']])}")
            print()

        # 保存結果
        import json
        with open('enhanced_match_results.json', 'w', encoding='utf-8') as f:
            # 轉換Path為字串以便JSON序列化
            results_for_json = []
            for item in matched_papers:
                item_copy = item.copy()
                item_copy['matches'] = [(bibkey, str(path)) for bibkey, path in item['matches']]
                results_for_json.append(item_copy)

            json.dump(results_for_json, f, ensure_ascii=False, indent=2)

        print(f"💾 匹配結果已保存到: enhanced_match_results.json")
        print(f"\n💡 下一步:")
        print(f"   使用 interactive_repair.py 處理這些論文")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
