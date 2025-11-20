#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 LLM 生成高質量元數據（摘要、關鍵詞）
支援 Ollama (本地) 和 Google Gemini (雲端)
"""

import sys
import io
import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# Windows UTF-8 支援
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

def generate_with_ollama(content: str, task: str = "abstract") -> Optional[str]:
    """使用 Ollama 生成元數據"""
    try:
        import requests

        prompts = {
            "abstract": f"""請為以下學術論文內容撰寫一段學術摘要（繁體中文），150-250字，
包含：研究目的、方法、主要發現、結論。只返回摘要內容，不要其他說明。

論文內容（前2000字元）：
{content[:2000]}
""",
            "keywords": f"""請從以下學術論文內容提取5-10個關鍵詞（英文），用逗號分隔。
只返回關鍵詞列表，不要其他內容。

論文內容（前1500字元）：
{content[:1500]}
"""
        }

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma2:latest",
                "prompt": prompts.get(task, prompts["abstract"]),
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()

    except Exception as e:
        print(f"⚠️ Ollama 生成失敗: {e}")

    return None

def generate_with_gemini(content: str, task: str = "abstract") -> Optional[str]:
    """使用 Google Gemini 生成元數據"""
    try:
        import google.generativeai as genai

        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print("⚠️ 未設置 GOOGLE_API_KEY 環境變數")
            return None

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        prompts = {
            "abstract": f"""請為以下學術論文內容撰寫一段學術摘要（繁體中文），150-250字，
包含：研究目的、方法、主要發現、結論。只返回摘要內容，不要其他說明。

論文內容（前2000字元）：
{content[:2000]}
""",
            "keywords": f"""請從以下學術論文內容提取5-10個關鍵詞（英文），用逗號分隔。
只返回關鍵詞列表，不要其他內容。

論文內容（前1500字元）：
{content[:1500]}
"""
        }

        response = model.generate_content(prompts.get(task, prompts["abstract"]))
        return response.text.strip()

    except Exception as e:
        print(f"⚠️ Gemini 生成失敗: {e}")

    return None

def generate_metadata_for_paper(
    paper_id: int,
    provider: str = "auto",
    db_path: str = "knowledge_base/index.db"
) -> Dict:
    """為單篇論文生成元數據"""

    # 獲取論文信息
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, file_path, abstract, keywords
        FROM papers
        WHERE id = ?
    """, (paper_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {'success': False, 'error': f'論文 ID {paper_id} 不存在'}

    pid, title, file_path, abstract, keywords = row

    # 讀取檔案內容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'success': False, 'error': f'讀取檔案失敗: {e}'}

    result = {
        'paper_id': pid,
        'title': title,
        'generated': {}
    }

    # 選擇提供者
    if provider == "auto":
        # 優先 Gemini（快速便宜），再 Ollama（本地免費）
        if os.environ.get('GOOGLE_API_KEY'):
            provider = "gemini"
        else:
            provider = "ollama"

    # 生成摘要（如果缺失）
    if not abstract or abstract == 'None' or len(abstract) < 50:
        print(f"  生成摘要... (使用 {provider})")

        if provider == "ollama":
            generated_abstract = generate_with_ollama(content, "abstract")
        else:
            generated_abstract = generate_with_gemini(content, "abstract")

        if generated_abstract:
            result['generated']['abstract'] = generated_abstract

    # 生成關鍵詞（如果缺失）
    if not keywords or keywords == '[]':
        print(f"  生成關鍵詞... (使用 {provider})")

        if provider == "ollama":
            generated_keywords_str = generate_with_ollama(content, "keywords")
        else:
            generated_keywords_str = generate_with_gemini(content, "keywords")

        if generated_keywords_str:
            # 解析關鍵詞列表
            keywords_list = [kw.strip() for kw in generated_keywords_str.split(',')]
            result['generated']['keywords'] = keywords_list[:10]  # 最多 10 個

    return result

def update_paper_with_generated_metadata(paper_id: int, generated: Dict, db_path: str = "knowledge_base/index.db"):
    """更新論文的生成元數據"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    updates = []
    params = []

    if 'abstract' in generated:
        updates.append("abstract = ?")
        params.append(generated['abstract'])

    if 'keywords' in generated:
        updates.append("keywords = ?")
        params.append(json.dumps(generated['keywords'], ensure_ascii=False))

    if not updates:
        conn.close()
        return False

    params.append(paper_id)
    sql = f"UPDATE papers SET {', '.join(updates)} WHERE id = ?"

    try:
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 更新失敗: {e}")
        conn.close()
        return False

def batch_generate(
    provider: str = "auto",
    limit: Optional[int] = None,
    db_path: str = "knowledge_base/index.db"
):
    """批次生成缺失的元數據"""

    # 找出需要生成的論文
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title
        FROM papers
        WHERE (abstract IS NULL OR abstract = 'None' OR LENGTH(abstract) < 50)
           OR (keywords IS NULL OR keywords = '[]')
        ORDER BY id
    """)

    papers = cursor.fetchall()
    conn.close()

    if limit:
        papers = papers[:limit]

    print(f"找到 {len(papers)} 篇需要生成元數據的論文")
    print(f"提供者: {provider.upper()}")
    print("=" * 80)

    success_count = 0
    failed_count = 0

    for i, (pid, title) in enumerate(papers, 1):
        print(f"\n[{i}/{len(papers)}] ID {pid}: {title[:50]}")

        result = generate_metadata_for_paper(pid, provider, db_path)

        if result.get('generated'):
            # 更新資料庫
            success = update_paper_with_generated_metadata(pid, result['generated'], db_path)

            if success:
                print(f"  ✅ 生成成功")
                if 'abstract' in result['generated']:
                    print(f"    - 摘要: {result['generated']['abstract'][:80]}...")
                if 'keywords' in result['generated']:
                    print(f"    - 關鍵詞: {result['generated']['keywords'][:3]}... ({len(result['generated']['keywords'])} 個)")
                success_count += 1
            else:
                print(f"  ❌ 更新失敗")
                failed_count += 1
        else:
            print(f"  ⚠️ 生成失敗")
            failed_count += 1

    print("\n" + "=" * 80)
    print(f"生成完成:")
    print(f"  成功: {success_count}")
    print(f"  失敗: {failed_count}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="使用 LLM 生成元數據")
    parser.add_argument('--paper-id', type=int, help='單篇論文 ID')
    parser.add_argument('--batch', action='store_true', help='批次處理')
    parser.add_argument('--provider', choices=['auto', 'ollama', 'gemini'], default='auto', help='LLM 提供者')
    parser.add_argument('--limit', type=int, help='限制處理數量')

    args = parser.parse_args()

    if args.paper_id:
        result = generate_metadata_for_paper(args.paper_id, args.provider)
        print(f"\n論文 ID {args.paper_id}")
        print(f"生成結果: {result.get('generated', {})}")

        if result.get('generated'):
            success = update_paper_with_generated_metadata(args.paper_id, result['generated'])
            print(f"更新: {'✅ 成功' if success else '❌ 失敗'}")

    elif args.batch:
        batch_generate(args.provider, args.limit)

    else:
        parser.print_help()
