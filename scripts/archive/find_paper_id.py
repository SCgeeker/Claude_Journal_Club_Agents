#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查找论文的 paper_id
"""

import sqlite3
from pathlib import Path

def find_paper_id(cite_key):
    """根据 cite_key 查找 paper_id"""
    db_path = Path("knowledge_base/index.db")

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return None

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查询论文
    cursor.execute("""
        SELECT id, title, authors, year, cite_key
        FROM papers
        WHERE cite_key LIKE ?
    """, (f"%{cite_key}%",))

    results = cursor.fetchall()
    conn.close()

    return results

def main():
    """主函数"""
    cite_key = "Abbas-2022"

    print(f"Searching for papers with cite_key containing: {cite_key}")
    print("=" * 70)

    results = find_paper_id(cite_key)

    if not results:
        print(f"No papers found for: {cite_key}")
        return

    for row in results:
        paper_id, title, authors, year, full_cite_key = row
        print(f"\nPaper ID: {paper_id}")
        print(f"Cite Key: {full_cite_key}")
        print(f"Title: {title}")
        print(f"Authors: {authors}")
        print(f"Year: {year}")

    if len(results) == 1:
        paper_id = results[0][0]
        print("\n" + "=" * 70)
        print(f"Found unique paper_id: {paper_id}")
        print("\nNext step:")
        print(f"  python generate_zettelkasten.py {paper_id}")

if __name__ == '__main__':
    main()
