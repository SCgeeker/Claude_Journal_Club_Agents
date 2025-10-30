# Zettel Indexer Skill

## 概述

**Zettel Indexer** 是專門用於批次索引 Zettelkasten 卡片到知識庫的技能組件。

**核心功能**：
- 解析 Zettelkasten Markdown 卡片（YAML frontmatter + Markdown content）
- 提取卡片元數據、核心概念、連結網絡
- 批次插入 SQLite 數據庫
- 自動關聯卡片與論文
- 生成索引報告

**技術特性**：
- 支援非標準 YAML 格式（fallback parser）
- 自動 ID 正規化（`CogSci20251028001` → `CogSci-20251028-001`）
- FTS5 全文搜索索引
- Windows 路徑和編碼相容

---

## 使用場景

### 場景 1：索引單個 Zettelkasten 資料夾

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager()

# 索引單個資料夾
stats = kb.index_zettelkasten(
    zettel_folder="output/zettelkasten_notes/zettel_Linguistics_20251029",
    domain="Linguistics"
)

print(f"成功: {stats['success']}/{stats['total']}")
```

**輸出**：
```
[SUCCESS] Linguistics-20251029-001.md → card_id=1
[SUCCESS] Linguistics-20251029-002.md → card_id=2
...
成功: 12/12
```

### 場景 2：批次索引多個資料夾

```python
from pathlib import Path

zettel_root = Path("output/zettelkasten_notes")
folders = [f for f in zettel_root.iterdir() if f.is_dir()]

total_stats = {'success': 0, 'failed': 0}

for folder in folders:
    stats = kb.index_zettelkasten(str(folder))
    total_stats['success'] += stats['success']
    total_stats['failed'] += stats['failed']

print(f"總計: {total_stats['success']} 張卡片索引成功")
```

### 場景 3：索引後自動關聯論文

```python
# 1. 索引卡片
stats = kb.index_zettelkasten(
    "output/zettelkasten_notes/zettel_Linguistics_20251029"
)

# 2. 自動關聯論文（基於 source_info 匹配）
link_stats = kb.auto_link_zettel_papers(similarity_threshold=0.7)

print(f"關聯成功: {link_stats['linked']} 張卡片")
```

---

## API 規格

### 主要方法

#### 1. `index_zettelkasten()`

批次索引 Zettelkasten 卡片資料夾。

**簽名**：
```python
def index_zettelkasten(
    self,
    zettel_folder: str,
    domain: str = None
) -> Dict
```

**參數**：
| 參數 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `zettel_folder` | str | ✅ | Zettelkasten 資料夾路徑（包含 `zettel_cards/` 子目錄） |
| `domain` | str | ❌ | 領域代碼過濾（CogSci/Linguistics/AI），None 表示全部 |

**返回值**：
```python
{
    'total': int,        # 找到的卡片總數
    'success': int,      # 成功索引的數量
    'failed': int,       # 失敗的數量
    'skipped': int,      # 跳過的數量（domain 不匹配）
    'cards': List[int]   # 成功的 card_id 列表
}
```

**示例**：
```python
stats = kb.index_zettelkasten(
    "output/zettelkasten_notes/zettel_CogSci_20251028",
    domain="CogSci"
)

# 結果: {'total': 15, 'success': 15, 'failed': 0, 'skipped': 0, 'cards': [1,2,3,...]}
```

#### 2. `parse_zettel_card()`

解析單張 Zettelkasten 卡片文件。

**簽名**：
```python
def parse_zettel_card(
    self,
    file_path: str
) -> Optional[Dict]
```

**參數**：
| 參數 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `file_path` | str | ✅ | 卡片文件路徑（.md 文件） |

**返回值**：
```python
{
    'zettel_id': str,         # 如 "Linguistics-20251029-001"
    'title': str,
    'content': str,           # 完整 Markdown 內容
    'core_concept': str,      # 核心概念（引用原文）
    'description': str,       # 說明文字
    'card_type': str,         # concept/method/finding/question
    'domain': str,            # CogSci/Linguistics/AI
    'tags': List[str],
    'source_info': str,       # 如 "Title" (2025)
    'file_path': str,
    'ai_notes': str,          # AI 批判性思考
    'human_notes': str,       # 人類筆記
    'links': List[Dict],      # 連結網絡
    'created_at': str
}
```

**示例**：
```python
card = kb.parse_zettel_card(
    "output/zettelkasten_notes/.../Linguistics-20251029-001.md"
)

print(card['zettel_id'])      # "Linguistics-20251029-001"
print(card['title'])          # "Mass Noun (Mass Noun)"
print(len(card['links']))     # 1
```

#### 3. `add_zettel_card()`

新增卡片到數據庫。

**簽名**：
```python
def add_zettel_card(
    self,
    card_data: Dict
) -> int
```

**參數**：
| 參數 | 類型 | 必需 | 說明 |
|------|------|------|------|
| `card_data` | Dict | ✅ | `parse_zettel_card()` 的返回值 |

**返回值**：
- `int`: 插入成功返回 `card_id`
- `-1`: 插入失敗（唯一約束衝突）

**示例**：
```python
card_data = kb.parse_zettel_card("card.md")
card_id = kb.add_zettel_card(card_data)

if card_id > 0:
    print(f"插入成功: card_id={card_id}")
```

---

## 數據結構

### Zettelkasten 卡片格式

```markdown
---
id: Linguistics-20251029-001
title: "Mass Noun (Mass Noun)"
tags: [Mass Noun, Non-Count Noun, Common Noun]
source: "Chinese Classifiers and Count Nouns" (2025)
paper_id:
created: 2025-10-29
type: concept
---

# Mass Noun (Mass Noun)

> **核心**: "I use mass noun interchangeably with non-count noun..."

## 說明
Mass Noun（不可數名詞）與 Non-Count Noun...

## 連結網絡

**導向** → [[Linguistics-20251029-002]], [[Linguistics-20251029-003]]

## 來源脈絡
- 📄 **文獻**: Chinese Classifiers and Count Nouns

## 個人筆記
**[AI Agent]**: 這是一個重要的定義...
**[Human]**: (TODO) <!-- 請在此處添加... -->
```

### 數據庫 Schema

#### zettel_cards 表

```sql
CREATE TABLE zettel_cards (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    zettel_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    core_concept TEXT,
    description TEXT,
    card_type TEXT DEFAULT 'concept',
    domain TEXT NOT NULL,
    tags TEXT,                      -- JSON 陣列
    paper_id INTEGER,
    zettel_folder TEXT NOT NULL,
    source_info TEXT,
    file_path TEXT UNIQUE NOT NULL,
    ai_notes TEXT,
    human_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);
```

#### zettel_links 表

```sql
CREATE TABLE zettel_links (
    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_card_id INTEGER NOT NULL,
    target_zettel_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,    -- 基於/導向/相關/對比/上位/下位
    context TEXT,
    is_cross_paper BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    FOREIGN KEY (source_card_id) REFERENCES zettel_cards(card_id)
);
```

#### zettel_cards_fts 全文搜索表

```sql
CREATE VIRTUAL TABLE zettel_cards_fts USING fts5(
    title, content, core_concept, description,
    tags, ai_notes, human_notes,
    content='zettel_cards',
    content_rowid='card_id'
);
```

---

## 處理流程

### 批次索引流程圖

```
1. 掃描資料夾
   └─> 查找 zettel_cards/*.md

2. 逐個解析
   ├─> parse_zettel_card()
   │   ├─> 提取 YAML frontmatter (標準 or fallback)
   │   ├─> 提取 Markdown 區塊（核心、說明、筆記）
   │   ├─> 提取連結網絡
   │   └─> 正規化 ID
   │
   ├─> 領域過濾（如指定 domain）
   │
   └─> add_zettel_card()
       ├─> INSERT INTO zettel_cards
       ├─> INSERT INTO zettel_links (多條)
       └─> FTS5 自動觸發器同步索引

3. 統計報告
   └─> 返回 {total, success, failed, skipped}
```

---

## 錯誤處理

### 常見錯誤與解決方案

#### 1. YAML 解析失敗

**錯誤**: `yaml.YAMLError: expected <block end>`

**原因**: 非標準 YAML 格式，如：
```yaml
source: "Title" (2025)  # 括號未加引號
```

**解決**: 使用 fallback parser 逐行解析
```python
try:
    metadata = yaml.safe_load(yaml_content)
except yaml.YAMLError:
    # 回退：逐行解析
    metadata = {}
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
```

#### 2. 連結網絡提取失敗

**錯誤**: `links` 欄位為空

**原因**: 正則表達式無法處理多行空白

**解決**: 更新正則表達式
```python
# 改進前: r'## 連結網絡\n(.+?)'
# 改進後:
network_match = re.search(r'## 連結網絡\s*\n(.+?)(?=\n##|\Z)', markdown, re.DOTALL)
```

#### 3. ID 格式錯誤

**錯誤**: ID 不符合標準格式

**解決**: 自動正規化
```python
def normalize_id(zettel_id: str) -> str:
    zettel_id = zettel_id.replace('_', '-').strip()
    match = re.match(r'^([A-Za-z]+)[-]?(\d{8})[-]?(\d{3})$', zettel_id)
    if match:
        domain, date, num = match.groups()
        return f"{domain}-{date}-{num}"
    return zettel_id
```

#### 4. 唯一約束衝突

**錯誤**: `sqlite3.IntegrityError: UNIQUE constraint failed`

**原因**: 卡片已存在

**解決**: 返回現有 card_id
```python
try:
    cursor.execute("INSERT INTO zettel_cards ...")
    return cursor.lastrowid
except sqlite3.IntegrityError:
    cursor.execute("SELECT card_id FROM zettel_cards WHERE zettel_id=?", ...)
    return cursor.fetchone()[0]
```

---

## 性能考量

### 批次索引性能

**測試環境**: Windows 11, Python 3.10, SQLite 3.x

| 卡片數量 | 處理時間 | 速度 |
|---------|---------|------|
| 12 張 | 0.5 秒 | 24 張/秒 |
| 100 張 | 4 秒 | 25 張/秒 |
| 660 張 | 26 秒 | 25 張/秒 |

**瓶頸分析**:
1. YAML 解析：~40% 時間
2. 正則表達式匹配：~30% 時間
3. 數據庫插入：~20% 時間
4. 文件 I/O：~10% 時間

**優化建議**:
- 使用批次事務（`BEGIN TRANSACTION`）
- 預編譯正則表達式
- 多線程處理（需注意 SQLite 寫入限制）

---

## 相關 Skills

- **kb-connector**: 知識庫連接和查詢
- **batch-processor**: 批次處理 PDF 並生成 Zettelkasten
- **quality-checker**: 檢查卡片和論文元數據質量

---

## 實作位置

**核心代碼**: `src/knowledge_base/kb_manager.py`

**相關方法**:
- `index_zettelkasten()` (L865-927)
- `parse_zettel_card()` (L679-792)
- `add_zettel_card()` (L794-863)
- `parse_zettel_links()` (L631-677)
- `normalize_id()` (L591-615)

---

## 測試

**測試腳本**: `test_zettel_indexing.py`

**測試覆蓋**:
- ✅ 單張卡片解析
- ✅ 資料庫插入驗證
- ✅ 批次索引（12 張卡片）
- ✅ 全文搜索

**測試結果**: 4/4 通過 ✅

---

## 使用範例

### 完整工作流

```python
from src.knowledge_base import KnowledgeBaseManager
from pathlib import Path

# 初始化
kb = KnowledgeBaseManager()

# 1. 掃描所有 Zettelkasten 資料夾
zettel_root = Path("output/zettelkasten_notes")
folders = [f for f in zettel_root.iterdir() if f.is_dir()]

print(f"發現 {len(folders)} 個資料夾")

# 2. 批次索引
total_success = 0
total_failed = 0

for folder in folders:
    print(f"\n處理: {folder.name}")

    stats = kb.index_zettelkasten(str(folder))

    total_success += stats['success']
    total_failed += stats['failed']

    print(f"  成功: {stats['success']}")
    print(f"  失敗: {stats['failed']}")

# 3. 自動關聯論文
print("\n自動關聯論文...")
link_stats = kb.auto_link_zettel_papers(similarity_threshold=0.7)

print(f"\n總結:")
print(f"  卡片索引: {total_success}/{total_success + total_failed}")
print(f"  論文關聯: {link_stats['linked']}")

# 4. 查看統計
stats = kb.get_stats()
print(f"\n知識庫統計:")
print(f"  Zettel 卡片: {stats['total_zettel_cards']}")
print(f"  Zettel 連結: {stats['total_zettel_links']}")
print(f"  Zettel 領域: {stats['total_zettel_domains']}")
```

---

## 更新歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0.0 | 2025-10-30 | 初版：核心索引功能 |
| 1.1.0 | 2025-10-30 | 新增：自動論文關聯、完整度評分 |

---

## 參考文檔

- **實施計畫**: `TASK_1.3_IMPLEMENTATION_PLAN.md`
- **進度報告**: `TASK_1.3_PROGRESS_REPORT.md`
- **設計文檔**: `AGENT_SKILL_DESIGN.md` - Task 1.3
