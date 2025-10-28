# Knowledge Base Connector Skill

## 功能描述

連接和管理知識庫，支援論文存儲、索引、查詢和關聯分析。

## 能力

- 💾 混合式存儲：Markdown文件 + SQLite索引
- 🔍 全文搜索：基於SQLite FTS5
- 🏷️ 主題管理：論文分類和主題關聯
- 🔗 引用追蹤：論文間的引用關係
- 📊 統計分析：知識庫概覽和趨勢

## 架構設計

```
知識庫根目錄 (knowledge_base/)
├── papers/              # Markdown格式的論文筆記
├── metadata/            # 額外元數據文件
└── index.db            # SQLite數據庫（索引+元數據）
```

## 使用方式

### 初始化知識庫

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager(kb_root="knowledge_base")
```

### 新增論文

```python
paper_id = kb.add_paper(
    file_path="papers/smith_2024_deep_learning.md",
    title="Deep Learning for Medical Diagnosis",
    authors=["John Smith", "Jane Doe"],
    year=2024,
    abstract="這是摘要...",
    keywords=["deep learning", "medical diagnosis"],
    content="完整論文內容..."  # 用於全文搜索
)
```

### 全文搜索

```python
# 搜索包含特定關鍵詞的論文
results = kb.search_papers("deep learning medical", limit=10)

for paper in results:
    print(f"{paper['title']} ({paper['year']})")
    print(f"作者: {', '.join(paper['authors'])}")
```

### 主題管理

```python
# 創建主題
topic_id = kb.add_topic("深度學習", "深度學習相關研究")

# 連結論文到主題
kb.link_paper_to_topic(paper_id, topic_id, relevance=0.95)

# 查詢特定主題的論文
papers = kb.get_papers_by_topic("深度學習")
```

### 引用關係

```python
# 添加引用關係：論文A引用論文B
kb.add_citation(source_paper_id=1, target_paper_id=2, citation_type="cites")
```

### 創建Markdown筆記

```python
# 自動生成Markdown格式的論文筆記
md_path = kb.create_markdown_note({
    "title": "研究標題",
    "authors": ["作者1", "作者2"],
    "year": 2024,
    "abstract": "摘要內容",
    "keywords": ["關鍵詞1", "關鍵詞2"]
})

print(f"筆記已保存至: {md_path}")
```

### 知識庫統計

```python
stats = kb.get_stats()
print(f"論文總數: {stats['total_papers']}")
print(f"主題總數: {stats['total_topics']}")
print(f"引用總數: {stats['total_citations']}")
```

## 數據庫結構

### papers 表
- id: 論文ID
- file_path: Markdown文件路徑
- title: 標題
- authors: 作者列表（JSON）
- year: 發表年份
- abstract: 摘要
- keywords: 關鍵詞（JSON）
- created_at / updated_at: 時間戳

### topics 表
- id: 主題ID
- name: 主題名稱
- description: 描述

### paper_topics 表（多對多關聯）
- paper_id: 論文ID
- topic_id: 主題ID
- relevance: 相關度（0-1）

### citations 表
- source_paper_id: 來源論文
- target_paper_id: 目標論文
- citation_type: 引用類型

### papers_fts 表（全文搜索）
- FTS5虛擬表，支援快速全文搜索

## Markdown筆記格式

```markdown
---
title: 論文標題
authors: 作者1, 作者2
year: 2024
keywords: 關鍵詞1, 關鍵詞2
created: 2024-10-27 20:00:00
---

# 論文標題

## 基本信息
- **作者**: 作者列表
- **年份**: 2024
- **關鍵詞**: 關鍵詞列表

## 摘要
摘要內容...

## 研究背景

## 研究方法

## 主要結果

## 討論與結論

## 個人評論

## 相關文獻

## 引用
```

## 最佳實踐

1. **一致的命名**: 使用標準化的文件命名（作者_年份_標題）
2. **完整元數據**: 確保填寫完整的作者、年份、關鍵詞
3. **定期備份**: 定期備份knowledge_base目錄
4. **主題分類**: 使用清晰的主題層次結構
5. **引用追蹤**: 記錄論文間的引用關係以建立知識網絡

## 整合點

- **與pdf-extractor整合**: 自動從PDF提取元數據並創建筆記
- **與note-writer整合**: 生成結構化筆記後自動索引
- **與slide-maker整合**: 從知識庫查找相關文獻並引用

## 未來擴展

- 🔮 向量搜索：使用本地embeddings進行語義搜索
- 📈 知識圖譜：視覺化論文關聯網絡
- 🤖 自動標籤：AI自動提取主題和關鍵詞
- 🔄 雙向連結：支援Obsidian風格的雙向連結
