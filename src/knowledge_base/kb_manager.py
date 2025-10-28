"""
知識庫管理模組
混合式架構：Markdown文件 + SQLite索引
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import re


class KnowledgeBaseManager:
    """知識庫管理器"""

    def __init__(self, kb_root: str = "knowledge_base", db_path: Optional[str] = None):
        """
        初始化知識庫管理器

        Args:
            kb_root: 知識庫根目錄
            db_path: 數據庫路徑（可選）
        """
        self.kb_root = Path(kb_root)
        self.kb_root.mkdir(parents=True, exist_ok=True)

        self.papers_dir = self.kb_root / "papers"
        self.papers_dir.mkdir(exist_ok=True)

        self.metadata_dir = self.kb_root / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)

        self.db_path = db_path or str(self.kb_root / "index.db")
        self._init_database()

    def _init_database(self):
        """初始化SQLite數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 論文表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                title TEXT,
                authors TEXT,
                year INTEGER,
                abstract TEXT,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 主題表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 論文-主題關聯表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paper_topics (
                paper_id INTEGER,
                topic_id INTEGER,
                relevance REAL DEFAULT 1.0,
                FOREIGN KEY (paper_id) REFERENCES papers(id),
                FOREIGN KEY (topic_id) REFERENCES topics(id),
                PRIMARY KEY (paper_id, topic_id)
            )
        """)

        # 引用關係表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citations (
                source_paper_id INTEGER,
                target_paper_id INTEGER,
                citation_type TEXT,
                FOREIGN KEY (source_paper_id) REFERENCES papers(id),
                FOREIGN KEY (target_paper_id) REFERENCES papers(id),
                PRIMARY KEY (source_paper_id, target_paper_id)
            )
        """)

        # 全文搜索表（FTS5）
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS papers_fts USING fts5(
                title,
                authors,
                abstract,
                content,
                keywords,
                content='papers',
                content_rowid='id'
            )
        """)

        conn.commit()
        conn.close()

    def add_paper(self,
                  file_path: str,
                  title: str,
                  authors: List[str],
                  year: Optional[int] = None,
                  abstract: Optional[str] = None,
                  keywords: Optional[List[str]] = None,
                  content: Optional[str] = None) -> int:
        """
        新增論文到知識庫

        Args:
            file_path: Markdown文件路徑
            title: 論文標題
            authors: 作者列表
            year: 發表年份
            abstract: 摘要
            keywords: 關鍵詞列表
            content: 完整內容（用於全文搜索）

        Returns:
            論文ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        authors_str = json.dumps(authors, ensure_ascii=False)
        keywords_str = json.dumps(keywords or [], ensure_ascii=False)

        try:
            cursor.execute("""
                INSERT INTO papers (file_path, title, authors, year, abstract, keywords)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (file_path, title, authors_str, year, abstract, keywords_str))

            paper_id = cursor.lastrowid

            # 添加到全文搜索索引
            if content:
                cursor.execute("""
                    INSERT INTO papers_fts (rowid, title, authors, abstract, content, keywords)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (paper_id, title, ', '.join(authors), abstract or '', content, ', '.join(keywords or [])))

            conn.commit()
            return paper_id

        except sqlite3.IntegrityError:
            # 文件已存在，更新
            cursor.execute("""
                UPDATE papers
                SET title=?, authors=?, year=?, abstract=?, keywords=?, updated_at=CURRENT_TIMESTAMP
                WHERE file_path=?
            """, (title, authors_str, year, abstract, keywords_str, file_path))

            cursor.execute("SELECT id FROM papers WHERE file_path=?", (file_path,))
            paper_id = cursor.fetchone()[0]
            conn.commit()
            return paper_id

        finally:
            conn.close()

    def search_papers(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        全文搜索論文

        Args:
            query: 搜索查詢
            limit: 返回結果數量限制

        Returns:
            匹配的論文列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.file_path, p.title, p.authors, p.year, p.abstract, p.keywords
            FROM papers p
            JOIN papers_fts fts ON p.id = fts.rowid
            WHERE papers_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "file_path": row[1],
                "title": row[2],
                "authors": json.loads(row[3]) if row[3] else [],
                "year": row[4],
                "abstract": row[5],
                "keywords": json.loads(row[6]) if row[6] else []
            })

        conn.close()
        return results

    def get_paper_by_id(self, paper_id: int) -> Optional[Dict[str, Any]]:
        """根據ID獲取論文信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, file_path, title, authors, year, abstract, keywords, created_at, updated_at
            FROM papers
            WHERE id = ?
        """, (paper_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "file_path": row[1],
                "title": row[2],
                "authors": json.loads(row[3]) if row[3] else [],
                "year": row[4],
                "abstract": row[5],
                "keywords": json.loads(row[6]) if row[6] else [],
                "created_at": row[7],
                "updated_at": row[8]
            }
        return None

    def list_papers(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """列出所有論文"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, file_path, title, authors, year, keywords, created_at
            FROM papers
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "file_path": row[1],
                "title": row[2],
                "authors": json.loads(row[3]) if row[3] else [],
                "year": row[4],
                "keywords": json.loads(row[5]) if row[5] else [],
                "created_at": row[6]
            })

        conn.close()
        return results

    def add_topic(self, name: str, description: Optional[str] = None) -> int:
        """新增主題"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO topics (name, description)
                VALUES (?, ?)
            """, (name, description))
            topic_id = cursor.lastrowid
            conn.commit()
            return topic_id

        except sqlite3.IntegrityError:
            cursor.execute("SELECT id FROM topics WHERE name=?", (name,))
            topic_id = cursor.fetchone()[0]
            return topic_id

        finally:
            conn.close()

    def link_paper_to_topic(self, paper_id: int, topic_id: int, relevance: float = 1.0):
        """連結論文與主題"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO paper_topics (paper_id, topic_id, relevance)
                VALUES (?, ?, ?)
            """, (paper_id, topic_id, relevance))
            conn.commit()
        finally:
            conn.close()

    def get_papers_by_topic(self, topic_name: str) -> List[Dict[str, Any]]:
        """根據主題獲取論文"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.title, p.authors, p.year, pt.relevance
            FROM papers p
            JOIN paper_topics pt ON p.id = pt.paper_id
            JOIN topics t ON pt.topic_id = t.id
            WHERE t.name = ?
            ORDER BY pt.relevance DESC
        """, (topic_name,))

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "authors": json.loads(row[2]) if row[2] else [],
                "year": row[3],
                "relevance": row[4]
            })

        conn.close()
        return results

    def add_citation(self, source_paper_id: int, target_paper_id: int, citation_type: str = "cites"):
        """添加引用關係"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO citations (source_paper_id, target_paper_id, citation_type)
                VALUES (?, ?, ?)
            """, (source_paper_id, target_paper_id, citation_type))
            conn.commit()
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, int]:
        """獲取知識庫統計信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) FROM papers")
        stats['total_papers'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM topics")
        stats['total_topics'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM citations")
        stats['total_citations'] = cursor.fetchone()[0]

        conn.close()
        return stats

    def create_markdown_note(self,
                            paper_data: Dict[str, Any],
                            output_path: Optional[str] = None) -> str:
        """
        創建Markdown格式的論文筆記

        Args:
            paper_data: 論文數據
            output_path: 輸出路徑（可選，自動生成）

        Returns:
            Markdown文件路徑
        """
        if output_path is None:
            # 自動生成文件名
            title_slug = re.sub(r'[^\w\s-]', '', paper_data.get('title', 'untitled')).strip()
            title_slug = re.sub(r'[-\s]+', '_', title_slug)[:50]
            output_path = self.papers_dir / f"{title_slug}.md"

        # 生成Markdown內容
        md_content = f"""---
title: {paper_data.get('title', 'Untitled')}
authors: {', '.join(paper_data.get('authors', []))}
year: {paper_data.get('year', 'N/A')}
keywords: {', '.join(paper_data.get('keywords', []))}
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# {paper_data.get('title', 'Untitled')}

## 基本信息

- **作者**: {', '.join(paper_data.get('authors', []))}
- **年份**: {paper_data.get('year', 'N/A')}
- **關鍵詞**: {', '.join(paper_data.get('keywords', []))}

## 摘要

{paper_data.get('abstract', '尚未提供摘要')}

## 研究背景

## 研究方法

## 主要結果

## 討論與結論

## 個人評論

## 相關文獻

## 完整內容

{paper_data.get('content', '尚未提供內容')}

## 引用

```
{paper_data.get('citation', '')}
```
"""

        # 寫入文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return str(output_path)


if __name__ == "__main__":
    # 測試代碼
    kb = KnowledgeBaseManager()
    stats = kb.get_stats()
    print("知識庫統計:")
    print(f"  論文總數: {stats['total_papers']}")
    print(f"  主題總數: {stats['total_topics']}")
    print(f"  引用總數: {stats['total_citations']}")
