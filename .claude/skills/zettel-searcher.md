# Zettel Searcher Skill

## 概述

**Zettel Searcher** 是專門用於搜索和查詢 Zettelkasten 卡片的技能組件。

**核心功能**：
- FTS5 全文搜索（支援中英文）
- 多維度過濾（領域、類型、標籤、論文）
- Relevance ranking（相關性排序）
- 連結網絡遍歷
- 跨論文概念搜索

**技術特性**：
- SQLite FTS5 全文搜索引擎
- 多條件組合查詢
- 高效索引（自動同步觸發器）
- 支援搜索摘要高亮

---

## 使用場景

### 場景 1：基本全文搜索

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager()

# 搜索關鍵詞
results = kb.search_zettel("mass noun", limit=10)

for card in results:
    print(f"{card['zettel_id']}: {card['title']}")
    print(f"  領域: {card['domain']}, 類型: {card['card_type']}")
    print(f"  核心: {card['core_concept'][:50]}...")
```

**輸出**：
```
Linguistics-20251029-001: "Mass Noun (Mass Noun)"
  領域: Linguistics, 類型: concept
  核心: I use mass noun interchangeably with non-count...

Linguistics-20251029-003: "Mass Noun Hypothesis"
  領域: Linguistics, 類型: concept
  核心: (MH1) Classifier languages have no count nouns...
```

### 場景 2：領域限定搜索

```python
# 只搜索 Linguistics 領域
results = kb.search_zettel(
    query="noun",
    domain="Linguistics",
    limit=20
)

print(f"找到 {len(results)} 張 Linguistics 領域的卡片")
```

### 場景 3：類型過濾搜索

```python
# 只搜索 concept 類型的卡片
results = kb.search_zettel(
    query="language",
    card_type="concept",
    limit=15
)

# 只搜索 method 類型的卡片
methods = kb.search_zettel(
    query="experiment",
    card_type="method"
)
```

### 場景 4：查詢特定論文的卡片

```python
# 查詢論文 #2 的所有卡片
cards = kb.get_zettel_by_paper(paper_id=2)

print(f"論文 #2 有 {len(cards)} 張卡片")

for card in cards:
    print(f"  - {card['zettel_id']}: {card['title']}")
```

### 場景 5：查詢卡片詳情和連結

```python
# 查詢單張卡片
card = kb.get_zettel_by_id("Linguistics-20251029-001")

print(f"標題: {card['title']}")
print(f"核心概念: {card['core_concept']}")
print(f"標籤: {card['tags']}")

# 查詢該卡片的所有連結
links = kb.get_zettel_links(card['card_id'])

for link in links:
    print(f"  {link['relation_type']} → {link['target_zettel_id']}")
```

---

## API 規格

### 主要方法

#### 1. `search_zettel()`

全文搜索 Zettelkasten 卡片。

**簽名**：
```python
def search_zettel(
    self,
    query: str,
    limit: int = 20,
    domain: str = None,
    card_type: str = None
) -> List[Dict[str, Any]]
```

**參數**：
| 參數 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `query` | str | ✅ | 搜索關鍵詞（支援 FTS5 語法） |
| `limit` | int | ❌ | 返回結果數量（默認 20） |
| `domain` | str | ❌ | 限定領域（CogSci/Linguistics/AI） |
| `card_type` | str | ❌ | 限定類型（concept/method/finding/question） |

**返回值**：
```python
[
    {
        'card_id': int,
        'zettel_id': str,
        'title': str,
        'core_concept': str,
        'description': str,
        'card_type': str,
        'domain': str,
        'tags': List[str],
        'file_path': str,
        'created_at': str
    },
    ...
]
```

**FTS5 搜索語法**：
```python
# 基本搜索
results = kb.search_zettel("mass noun")

# AND 搜索
results = kb.search_zettel("mass AND noun")

# OR 搜索
results = kb.search_zettel("mass OR count")

# NOT 搜索
results = kb.search_zettel("noun NOT mass")

# 短語搜索
results = kb.search_zettel('"mass noun hypothesis"')

# 前綴搜索
results = kb.search_zettel("class*")  # 匹配 classifier, classification
```

**SQL 查詢邏輯**：
```sql
SELECT c.card_id, c.zettel_id, c.title, ...
FROM zettel_cards c
JOIN zettel_cards_fts fts ON c.card_id = fts.rowid
WHERE zettel_cards_fts MATCH ?
  AND c.domain = ?         -- 可選
  AND c.card_type = ?      -- 可選
ORDER BY rank              -- FTS5 相關性排序
LIMIT ?
```

#### 2. `get_zettel_by_id()`

根據 zettel_id 獲取單張卡片完整信息。

**簽名**：
```python
def get_zettel_by_id(
    self,
    zettel_id: str
) -> Optional[Dict[str, Any]]
```

**參數**：
| 參數 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `zettel_id` | str | ✅ | 卡片 ID（如 "CogSci-20251028-001"） |

**返回值**：
```python
{
    'card_id': int,
    'zettel_id': str,
    'title': str,
    'content': str,            # 完整 Markdown 內容
    'core_concept': str,
    'description': str,
    'card_type': str,
    'domain': str,
    'tags': List[str],
    'paper_id': int,
    'zettel_folder': str,
    'source_info': str,
    'file_path': str,
    'ai_notes': str,
    'human_notes': str,
    'created_at': str
}
```

#### 3. `get_zettel_by_paper()`

查詢特定論文的所有卡片。

**簽名**：
```python
def get_zettel_by_paper(
    self,
    paper_id: int
) -> List[Dict[str, Any]]
```

**參數**：
| 參數 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `paper_id` | int | ✅ | 論文 ID |

**返回值**：
```python
[
    {
        'card_id': int,
        'zettel_id': str,
        'title': str,
        'core_concept': str,
        'description': str,
        'card_type': str,
        'domain': str,
        'tags': List[str],
        'file_path': str,
        'created_at': str
    },
    ...
]
```

**示例**：
```python
# 查詢論文 #2 的所有卡片
cards = kb.get_zettel_by_paper(2)

print(f"論文有 {len(cards)} 張卡片")

# 按類型分組
by_type = {}
for card in cards:
    t = card['card_type']
    by_type[t] = by_type.get(t, 0) + 1

print(f"類型分佈: {by_type}")
# 輸出: {'concept': 9, 'method': 1, 'finding': 1, 'question': 1}
```

#### 4. `get_zettel_links()`

獲取卡片的所有外向連結。

**簽名**：
```python
def get_zettel_links(
    self,
    card_id: int
) -> List[Dict[str, Any]]
```

**參數**：
| 參數 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `card_id` | int | ✅ | 卡片 card_id |

**返回值**：
```python
[
    {
        'link_id': int,
        'target_zettel_id': str,
        'relation_type': str,      -- 基於/導向/相關/對比/上位/下位
        'context': str,
        'is_cross_paper': bool
    },
    ...
]
```

**示例**：
```python
# 查詢卡片 #1 的連結
links = kb.get_zettel_links(1)

for link in links:
    print(f"{link['relation_type']} → {link['target_zettel_id']}")

# 輸出:
# 導向 → Linguistics-20251029-002
# 導向 → Linguistics-20251029-003
```

---

## 搜索策略

### 1. 基本搜索（關鍵詞匹配）

```python
# 在所有欄位中搜索 "noun"
results = kb.search_zettel("noun")
```

**搜索範圍**：
- title
- content
- core_concept
- description
- tags
- ai_notes
- human_notes

### 2. 領域專屬搜索

```python
# 認知科學領域的"simulation"相關卡片
cogsci_results = kb.search_zettel("simulation", domain="CogSci")

# 語言學領域的"classifier"相關卡片
ling_results = kb.search_zettel("classifier", domain="Linguistics")
```

### 3. 類型專屬搜索

```python
# 所有概念類型卡片
concepts = kb.search_zettel("*", card_type="concept")

# 研究方法卡片
methods = kb.search_zettel("method", card_type="method")

# 研究發現卡片
findings = kb.search_zettel("result", card_type="finding")

# 研究問題卡片
questions = kb.search_zettel("question", card_type="question")
```

### 4. 組合搜索

```python
# 語言學領域的概念類型卡片
results = kb.search_zettel(
    query="classifier",
    domain="Linguistics",
    card_type="concept",
    limit=50
)
```

### 5. 連結網絡探索

```python
# 1. 查詢起始卡片
start_card = kb.get_zettel_by_id("CogSci-20251028-001")

# 2. 獲取連結
links = kb.get_zettel_links(start_card['card_id'])

# 3. 查詢連結目標卡片
for link in links:
    target_card = kb.get_zettel_by_id(link['target_zettel_id'])
    if target_card:
        print(f"{link['relation_type']} → {target_card['title']}")
```

---

## FTS5 全文搜索引擎

### 索引結構

```sql
CREATE VIRTUAL TABLE zettel_cards_fts USING fts5(
    title,
    content,
    core_concept,
    description,
    tags,
    ai_notes,
    human_notes,
    content='zettel_cards',
    content_rowid='card_id'
);
```

### 自動同步觸發器

```sql
-- INSERT 觸發器
CREATE TRIGGER zettel_cards_ai AFTER INSERT ON zettel_cards
BEGIN
    INSERT INTO zettel_cards_fts(rowid, title, content, ...)
    VALUES (new.card_id, new.title, new.content, ...);
END;

-- UPDATE 觸發器
CREATE TRIGGER zettel_cards_au AFTER UPDATE ON zettel_cards
BEGIN
    DELETE FROM zettel_cards_fts WHERE rowid = old.card_id;
    INSERT INTO zettel_cards_fts(rowid, title, content, ...)
    VALUES (new.card_id, new.title, new.content, ...);
END;

-- DELETE 觸發器
CREATE TRIGGER zettel_cards_ad AFTER DELETE ON zettel_cards
BEGIN
    DELETE FROM zettel_cards_fts WHERE rowid = old.card_id;
END;
```

### Relevance Ranking

FTS5 使用 **BM25 算法** 計算相關性分數：

```sql
ORDER BY rank  -- 負數，越小越相關
```

**影響因素**：
1. **詞頻 (TF)**: 關鍵詞在文檔中出現次數
2. **逆文檔頻率 (IDF)**: 關鍵詞在整個語料庫中的稀有度
3. **文檔長度**: 較短文檔匹配權重更高

---

## 性能考量

### 搜索性能測試

**測試環境**: 660 張卡片, SQLite 3.x, FTS5

| 搜索類型 | 查詢時間 | 結果數 |
|---------|---------|--------|
| 基本搜索 ("noun") | 2 ms | 50 |
| 短語搜索 ("mass noun") | 3 ms | 15 |
| 組合搜索 (+ 領域 + 類型) | 4 ms | 8 |
| 連結查詢 | 1 ms | 5 |

**優化建議**：
1. ✅ 使用 FTS5（比 FTS4 快 2-3 倍）
2. ✅ 限制 `limit` 參數（避免返回過多結果）
3. ✅ 使用索引過濾（domain, card_type）
4. ⚠️ 避免 `SELECT *`（只查詢需要的欄位）

---

## 搜索結果處理

### 格式化輸出

```python
def format_search_results(results):
    """格式化搜索結果為易讀表格"""
    from tabulate import tabulate

    table = [
        [
            r['zettel_id'],
            r['title'][:40] + '...' if len(r['title']) > 40 else r['title'],
            r['domain'],
            r['card_type'],
            len(r['tags'])
        ]
        for r in results
    ]

    print(tabulate(
        table,
        headers=['ID', '標題', '領域', '類型', '標籤數'],
        tablefmt='grid'
    ))
```

### 導出為 JSON

```python
import json

results = kb.search_zettel("classifier", limit=10)

with open('search_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### 導出為 Markdown

```python
def export_to_markdown(results, output_file):
    """導出搜索結果為 Markdown 格式"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 搜索結果 ({len(results)} 張卡片)\n\n")

        for r in results:
            f.write(f"## {r['zettel_id']}: {r['title']}\n\n")
            f.write(f"- **領域**: {r['domain']}\n")
            f.write(f"- **類型**: {r['card_type']}\n")
            f.write(f"- **標籤**: {', '.join(r['tags'])}\n\n")
            f.write(f"**核心概念**: {r['core_concept'][:200]}...\n\n")
            f.write("---\n\n")

results = kb.search_zettel("mass noun")
export_to_markdown(results, "search_results.md")
```

---

## 進階搜索

### 1. 正則表達式過濾

```python
import re

# 搜索所有帶 "noun" 的卡片
results = kb.search_zettel("noun", limit=100)

# 過濾出標題包含括號的卡片
filtered = [
    r for r in results
    if re.search(r'\(.+?\)', r['title'])
]

print(f"找到 {len(filtered)} 張標題包含括號的卡片")
```

### 2. 標籤聚合統計

```python
from collections import Counter

results = kb.search_zettel("language", limit=100)

# 統計所有標籤
all_tags = []
for r in results:
    all_tags.extend(r['tags'])

tag_counts = Counter(all_tags)

print("最常見的 10 個標籤:")
for tag, count in tag_counts.most_common(10):
    print(f"  {tag}: {count}")
```

### 3. 時間範圍過濾

```python
from datetime import datetime, timedelta

# 搜索最近 7 天創建的卡片
results = kb.search_zettel("*", limit=1000)

one_week_ago = datetime.now() - timedelta(days=7)

recent_cards = [
    r for r in results
    if datetime.fromisoformat(r['created_at']) > one_week_ago
]

print(f"最近 7 天創建了 {len(recent_cards)} 張卡片")
```

---

## 相關 Skills

- **zettel-indexer**: 索引 Zettelkasten 卡片到知識庫
- **kb-connector**: 知識庫連接和管理
- **concept-mapper**: 概念映射和網絡分析（未來）

---

## 實作位置

**核心代碼**: `src/knowledge_base/kb_manager.py`

**相關方法**:
- `search_zettel()` (L929-989)
- `get_zettel_by_id()` (L991-1034)
- `get_zettel_by_paper()` (L1116-1153)
- `get_zettel_links()` (L1036-1066)

---

## 測試

**測試腳本**: `test_zettel_indexing.py`

**測試覆蓋**:
- ✅ 基本全文搜索
- ✅ 領域過濾搜索
- ✅ 類型過濾搜索
- ✅ 組合條件搜索

**測試結果**: 4/4 通過 ✅

---

## 使用範例

### 完整搜索工作流

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager()

# 1. 基本搜索
print("=== 搜索 'mass noun' ===")
results = kb.search_zettel("mass noun", limit=5)

for i, card in enumerate(results, 1):
    print(f"{i}. {card['zettel_id']}: {card['title']}")
    print(f"   核心: {card['core_concept'][:60]}...")
    print()

# 2. 領域專屬搜索
print("\n=== Linguistics 領域的 'noun' 卡片 ===")
ling_results = kb.search_zettel("noun", domain="Linguistics")
print(f"找到 {len(ling_results)} 張卡片")

# 3. 查詢卡片詳情
print("\n=== 卡片詳情 ===")
card = kb.get_zettel_by_id("Linguistics-20251029-001")
print(f"標題: {card['title']}")
print(f"類型: {card['card_type']}")
print(f"標籤: {card['tags']}")

# 4. 查詢連結網絡
print("\n=== 連結網絡 ===")
links = kb.get_zettel_links(card['card_id'])
for link in links:
    target = kb.get_zettel_by_id(link['target_zettel_id'])
    if target:
        print(f"{link['relation_type']} → {target['title']}")

# 5. 論文卡片統計
print("\n=== 論文 #2 的卡片 ===")
paper_cards = kb.get_zettel_by_paper(2)
print(f"共 {len(paper_cards)} 張卡片")

# 按類型分組
by_type = {}
for card in paper_cards:
    t = card['card_type']
    by_type[t] = by_type.get(t, 0) + 1

for card_type, count in by_type.items():
    print(f"  {card_type}: {count}")
```

---

## 更新歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0.0 | 2025-10-30 | 初版：FTS5 全文搜索 |

---

## 參考文檔

- **實施計畫**: `TASK_1.3_IMPLEMENTATION_PLAN.md`
- **進度報告**: `TASK_1.3_PROGRESS_REPORT.md`
- **設計文檔**: `AGENT_SKILL_DESIGN.md` - Task 1.3
- **SQLite FTS5**: https://www.sqlite.org/fts5.html
