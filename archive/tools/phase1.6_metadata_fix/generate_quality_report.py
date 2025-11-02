#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成知識庫元數據質量報告
"""

import sqlite3
import sys
import io
from pathlib import Path
from typing import Dict, List
import json

# Windows UTF-8 支援
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_quality(db_path: str = "knowledge_base/index.db") -> Dict:
    """分析元數據質量"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 獲取所有論文
    cursor.execute("""
        SELECT id, title, authors, year, keywords, abstract, file_path
        FROM papers
    """)

    papers = cursor.fetchall()

    stats = {
        'total': len(papers),
        'missing_year': 0,
        'missing_keywords': 0,
        'missing_abstract': 0,
        'invalid_title': 0,
        'file_not_found': 0,
        'complete': 0,
        'quality_score': 0
    }

    issues = []

    for pid, title, authors, year, keywords, abstract, file_path in papers:
        paper_issues = []

        # 檢查年份
        if not year:
            stats['missing_year'] += 1
            paper_issues.append('缺少年份')

        # 檢查關鍵詞
        if not keywords or keywords == '[]':
            stats['missing_keywords'] += 1
            paper_issues.append('缺少關鍵詞')
        else:
            try:
                kw_list = json.loads(keywords)
                if len(kw_list) < 3:
                    paper_issues.append(f'關鍵詞過少 ({len(kw_list)}個)')
            except:
                pass

        # 檢查摘要
        if not abstract or abstract == 'None' or len(abstract) < 50:
            stats['missing_abstract'] += 1
            paper_issues.append('缺少摘要')

        # 檢查標題
        invalid_title_patterns = ['Journal Pre-proof', 'https://', 'http://', 'downloaded by']
        if any(pattern in title for pattern in invalid_title_patterns):
            stats['invalid_title'] += 1
            paper_issues.append('無效標題')

        # 檢查檔案
        if not Path(file_path).exists():
            stats['file_not_found'] += 1
            paper_issues.append('檔案不存在')

        # 完整度
        if not paper_issues:
            stats['complete'] += 1

        if paper_issues:
            issues.append({
                'id': pid,
                'title': title[:50],
                'issues': paper_issues
            })

    # 計算質量分數
    total = stats['total']
    if total > 0:
        completeness = (total - stats['missing_year'] - stats['missing_keywords'] - stats['missing_abstract']) / (total * 3)
        stats['quality_score'] = int(completeness * 100)

    conn.close()

    return stats, issues

def generate_report(stats: Dict, issues: List[Dict], output_path: str = "QUALITY_REPORT.md"):
    """生成 Markdown 報告"""

    report = f"""# 知識庫元數據質量報告

**生成時間**: {Path().resolve()}
**資料庫**: knowledge_base/index.db

---

## 📊 總覽

| 指標 | 數量 | 百分比 |
|------|------|--------|
| **總論文數** | {stats['total']} | 100% |
| **完整論文** | {stats['complete']} | {stats['complete']/stats['total']*100:.1f}% |
| **缺少年份** | {stats['missing_year']} | {stats['missing_year']/stats['total']*100:.1f}% |
| **缺少關鍵詞** | {stats['missing_keywords']} | {stats['missing_keywords']/stats['total']*100:.1f}% |
| **缺少摘要** | {stats['missing_abstract']} | {stats['missing_abstract']/stats['total']*100:.1f}% |
| **無效標題** | {stats['invalid_title']} | {stats['invalid_title']/stats['total']*100:.1f}% |
| **檔案不存在** | {stats['file_not_found']} | {stats['file_not_found']/stats['total']*100:.1f}% |

**整體質量分數**: {stats['quality_score']}/100

---

## ⚠️ 問題論文列表

共 {len(issues)} 篇論文有問題：

"""

    for issue in issues:
        report += f"\n### ID {issue['id']}: {issue['title']}\n\n"
        for problem in issue['issues']:
            report += f"- ❌ {problem}\n"

    report += f"""

---

## 💡 修復建議

### 立即行動

1. **修復缺少年份** ({stats['missing_year']} 篇)
   ```bash
   python fix_metadata.py --batch --field year
   ```

2. **修復缺少關鍵詞** ({stats['missing_keywords']} 篇)
   ```bash
   python llm_metadata_generator.py --batch --provider gemini
   ```

3. **修復缺少摘要** ({stats['missing_abstract']} 篇)
   ```bash
   python llm_metadata_generator.py --batch --provider gemini
   ```

4. **清理檔案不存在的記錄** ({stats['file_not_found']} 篇)
   ```bash
   python cleanup_db.py --delete
   ```

### 預期改進

修復後預計質量分數可達到 **85+/100**

---

**報告生成工具**: generate_quality_report.py
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 報告已生成: {output_path}")

if __name__ == "__main__":
    print("分析知識庫元數據質量...")
    stats, issues = analyze_quality()

    print(f"\n總論文數: {stats['total']}")
    print(f"完整論文: {stats['complete']} ({stats['complete']/stats['total']*100:.1f}%)")
    print(f"質量分數: {stats['quality_score']}/100\n")

    generate_report(stats, issues)
