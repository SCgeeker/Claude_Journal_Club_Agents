# Task 1.3 實施進度報告

**日期**: 2025-10-30
**狀態**: Phase 1 核心功能已完成 ✅

---

## 📊 階段性成果總覽

### 已完成功能 (8/13)

| 功能模組 | 狀態 | 程式碼行數 | 測試結果 |
|---------|------|-----------|---------|
| ✅ 實施計畫文檔 | 完成 | 1,000+ | - |
| ✅ 舊版PDF路徑問題記錄 | 完成 | 138 | - |
| ✅ 單卡片解析測試 | 完成 | 377 | 100% 通過 |
| ✅ parse_zettel_card() | 完成 | 108 | 100% 通過 |
| ✅ parse_zettel_links() | 完成 | 46 | 100% 通過 |
| ✅ index_zettelkasten() | 完成 | 62 | 12/12 成功 |
| ✅ search_zettel() | 完成 | 58 | 100% 通過 |
| ✅ 功能測試驗證 | 完成 | 201 | 4/4 通過 |

**總代碼量**: 約 2,000 行（含文檔、實作、測試）

---

## 🎯 核心實作細節

### 1. 資料結構定義

#### Zettelkasten 卡片表 (zettel_cards)
```sql
CREATE TABLE zettel_cards (
    card_id INTEGER PRIMARY KEY,
    zettel_id TEXT UNIQUE NOT NULL,       -- 如 CogSci-20251028-001
    title TEXT NOT NULL,
    content TEXT NOT NULL,                 -- 完整 Markdown 內容
    core_concept TEXT,                     -- 核心概念（引用原文）
    description TEXT,                      -- 說明文字
    card_type TEXT DEFAULT 'concept',      -- concept/method/finding/question
    domain TEXT NOT NULL,                  -- CogSci/Linguistics/AI
    tags TEXT,                             -- JSON 陣列
    paper_id INTEGER,                      -- 關聯論文 ID
    zettel_folder TEXT NOT NULL,
    source_info TEXT,                      -- 來源論文資訊
    file_path TEXT UNIQUE NOT NULL,
    ai_notes TEXT,                         -- AI 批判性思考
    human_notes TEXT,                      -- 人類筆記（待補充）
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id)
)
```

#### Zettelkasten 連結表 (zettel_links)
```sql
CREATE TABLE zettel_links (
    link_id INTEGER PRIMARY KEY,
    source_card_id INTEGER NOT NULL,
    target_zettel_id TEXT NOT NULL,       -- 目標卡片 ID
    relation_type TEXT NOT NULL,          -- 基於/導向/相關/對比/上位/下位
    context TEXT,                          -- 連結脈絡
    is_cross_paper BOOLEAN DEFAULT FALSE, -- 是否跨論文連結
    created_at TIMESTAMP,
    FOREIGN KEY (source_card_id) REFERENCES zettel_cards(card_id)
)
```

#### FTS5 全文搜索索引
```sql
CREATE VIRTUAL TABLE zettel_cards_fts USING fts5(
    title, content, core_concept, description,
    tags, ai_notes, human_notes,
    content='zettel_cards',
    content_rowid='card_id'
)
```

### 2. 核心方法實作

#### 2.1 parse_zettel_card() - 卡片解析器

**功能**: 解析單張 Zettelkasten Markdown 卡片
**程式碼**: `src/knowledge_base/kb_manager.py:679-792`
**特性**:
- 雙階段 YAML 解析器（標準 + fallback）
- 處理不規範 YAML 格式（如 `source: "Title" (2025)`）
- 9 個區塊提取（YAML、核心概念、說明、AI筆記、人類筆記、連結網絡等）
- 自動 ID 正規化（`CogSci20251028001` → `CogSci-20251028-001`）

**輸入範例**:
```markdown
---
id: Linguistics-20251029-001
title: "Mass Noun (Mass Noun)"
tags: [Mass Noun, Non-Count Noun]
source: "Chinese Classifiers" (2025)
created: 2025-10-29
type: concept
---

# Mass Noun

> **核心**: "I use mass noun interchangeably with non-count noun..."

## 說明
Mass Noun（不可數名詞）...

## 連結網絡
**導向** → [[Linguistics-20251029-002]], [[Linguistics-20251029-003]]

## 個人筆記
**[AI Agent]**: 這是一個重要的定義...
**[Human]**: (TODO) <!-- 請在此處添加... -->
```

**輸出結構**:
```python
{
    'zettel_id': 'Linguistics-20251029-001',
    'title': '"Mass Noun (Mass Noun)"',
    'content': '<完整 Markdown>',
    'core_concept': 'I use mass noun interchangeably...',
    'description': 'Mass Noun（不可數名詞）...',
    'card_type': 'concept',
    'domain': 'Linguistics',
    'tags': ['Mass Noun', 'Non-Count Noun'],
    'source_info': '"Chinese Classifiers" (2025)',
    'file_path': 'D:\\...\\Linguistics-20251029-001.md',
    'ai_notes': '這是一個重要的定義...',
    'human_notes': '(TODO) <!-- 請在此處添加... -->',
    'links': [
        {
            'relation_type': '導向',
            'target_ids': ['Linguistics-20251029-002', 'Linguistics-20251029-003']
        }
    ],
    'created_at': '2025-10-29'
}
```

#### 2.2 parse_zettel_links() - 連結網絡解析器

**功能**: 從 Markdown 提取連結網絡區塊
**程式碼**: `src/knowledge_base/kb_manager.py:631-677`
**特性**:
- 支援 6 種語義關係類型
- 處理多行空白和不規範格式
- 批次提取多個目標 ID

**支援的關係類型**:
| 關係 | 說明 | 範例 |
|------|------|------|
| 基於 | 基礎概念 | A 基於 B |
| 導向 | 衍生概念 | A 導向 C, D |
| 相關 | 相關主題 | A 相關 E |
| 對比 | 對立觀點 | A 對比 F |
| 上位 | 上層概念 | A 上位 G |
| 下位 | 下層概念 | A 下位 H |

**正則表達式**:
```python
# 區塊匹配（寬容空白處理）
network_match = re.search(r'## 連結網絡\s*\n(.+?)(?=\n##|\Z)', markdown, re.DOTALL)

# 連結行匹配（支援多行）
link_pattern = r'\*\*(基於|導向|相關|對比|上位|下位)\*\*\s*→\s*(.+?)(?=\n\s*\n|\n\*\*|\n##|\Z)'

# ID 提取
target_ids = re.findall(r'\[\[([A-Za-z]+-\d{8}-\d{3})\]\]', target_text)
```

#### 2.3 add_zettel_card() - 資料庫插入

**功能**: 新增卡片到資料庫（含連結）
**程式碼**: `src/knowledge_base/kb_manager.py:794-863`
**特性**:
- 自動提取 zettel_folder（從 file_path）
- 批次插入連結（1 張卡片可有多條連結）
- IntegrityError 處理（返回現有 card_id）
- FTS5 自動觸發器同步索引

**事務流程**:
```python
1. INSERT INTO zettel_cards → card_id
2. For each link:
   INSERT INTO zettel_links (source_card_id, target_zettel_id, relation_type)
3. FTS5 觸發器自動同步到 zettel_cards_fts
```

#### 2.4 index_zettelkasten() - 批次索引

**功能**: 批次索引整個資料夾的卡片
**程式碼**: `src/knowledge_base/kb_manager.py:865-927`
**特性**:
- 自動掃描 `zettel_cards/` 子資料夾
- 可選領域過濾（`domain` 參數）
- 詳細進度顯示（`[SUCCESS] filename → card_id`）
- 統計報告（總數、成功、失敗、跳過）

**使用範例**:
```python
kb = KnowledgeBaseManager()
stats = kb.index_zettelkasten(
    "output/zettelkasten_notes/zettel_Linguistics_20251029",
    domain="Linguistics"
)

# 輸出:
# [SUCCESS] Linguistics-20251029-001.md → card_id=1
# [SUCCESS] Linguistics-20251029-002.md → card_id=2
# ...
# 結果: {'total': 12, 'success': 12, 'failed': 0, 'skipped': 0}
```

#### 2.5 search_zettel() - 全文搜索

**功能**: FTS5 全文搜索卡片
**程式碼**: `src/knowledge_base/kb_manager.py:929-989`
**特性**:
- FTS5 relevance ranking
- 可選領域過濾（`domain`）
- 可選類型過濾（`card_type`）
- 返回精簡資訊（不含完整 content）

**查詢範例**:
```python
# 1. 基本搜索
results = kb.search_zettel("mass noun", limit=10)

# 2. 領域限定
results = kb.search_zettel("語言學", domain="Linguistics")

# 3. 類型限定
results = kb.search_zettel("concept", card_type="concept")

# 4. 組合條件
results = kb.search_zettel("classifier", domain="Linguistics", card_type="method")
```

**SQL 查詢**:
```sql
SELECT c.card_id, c.zettel_id, c.title, c.core_concept, ...
FROM zettel_cards c
JOIN zettel_cards_fts fts ON c.card_id = fts.rowid
WHERE zettel_cards_fts MATCH ?
  AND c.domain = ?         -- 可選
  AND c.card_type = ?      -- 可選
ORDER BY rank
LIMIT ?
```

### 3. 輔助方法

#### normalize_id() - ID 正規化
```python
# 修復錯誤格式
"CogSci20251028001"     → "CogSci-20251028-001"
"AI_20251029_005"       → "AI-20251029-005"
"Linguistics-20251029-001" → "Linguistics-20251029-001" (不變)
```

#### extract_domain_from_id() - 領域提取
```python
"CogSci-20251028-001"     → "CogSci"
"Linguistics-20251029-002" → "Linguistics"
"AI-20251030-010"         → "AI"
```

#### get_zettel_by_id() - ID 查詢
```python
# 根據 zettel_id 查詢完整卡片資訊（含 content、paper_id 等）
card = kb.get_zettel_by_id("Linguistics-20251029-001")
```

#### get_zettel_links() - 連結查詢
```python
# 根據 card_id 查詢所有外向連結
links = kb.get_zettel_links(1)
# [{'link_id': 1, 'target_zettel_id': '...', 'relation_type': '導向', ...}]
```

---

## 🧪 測試結果

### 測試 1：單張卡片解析
- **測試檔案**: `test_parse_single_zettel.py` (377 行)
- **測試卡片**: 2 張 (Linguistics-20251029-001, 003)
- **結果**: ✅ 100% 通過
- **驗證項目**:
  - [x] YAML frontmatter 提取（7 個欄位）
  - [x] 核心概念提取
  - [x] 說明文字提取
  - [x] AI 筆記提取
  - [x] 人類筆記提取
  - [x] 連結網絡提取（1-2 組連結）
  - [x] 完整度統計（8/8 欄位，100%）

### 測試 2：功能整合測試
- **測試檔案**: `test_zettel_indexing.py` (201 行)
- **測試資料夾**: `zettel_Linguistics_20251029` (12 張卡片)
- **結果**: ✅ 4/4 通過

#### 測試 2.1：單張卡片解析
- 狀態: ✅ PASS
- 卡片: Linguistics-20251029-001
- 提取結果: 所有欄位完整

#### 測試 2.2：資料庫插入驗證
- 狀態: ✅ PASS
- 插入: card_id=1
- 驗證: 從資料庫成功讀取
- 連結: 2 條連結正確寫入

#### 測試 2.3：批次索引
- 狀態: ✅ PASS
- 資料夾: zettel_Linguistics_20251029
- 結果:
  - 總數: 12 張
  - 成功: 12 張 (100%)
  - 失敗: 0 張
  - 跳過: 0 張

#### 測試 2.4：全文搜索
- 狀態: ✅ PASS
- 測試查詢:
  - `"mass noun"` → 5 張卡片
  - `domain="Linguistics"` → 過濾成功
  - `card_type="concept"` → 過濾成功

---

## 📈 資料庫統計

### 當前知識庫狀態

| 項目 | 數量 |
|------|------|
| 論文總數 | 30 |
| 主題總數 | 0 |
| 引用總數 | 0 |
| **Zettel 卡片** | **12** ✅ |
| **Zettel 連結** | **20** ✅ |
| **Zettel 領域** | **1** (Linguistics) |
| **Zettel 資料夾** | **1** |

### 連結網絡分析

**12 張卡片的連結分佈**:
- 平均每張卡片: 1.67 條連結
- 連結類型分佈:
  - 導向: ~60% (主要衍生方向)
  - 基於: ~30% (基礎概念引用)
  - 其他: ~10% (相關、對比等)

---

## 🔧 技術挑戰與解決方案

### 挑戰 1：非標準 YAML 格式

**問題**: 現有卡片的 YAML frontmatter 不符合標準格式：
```yaml
source: "Chinese Classifiers and Count Nouns" (2025)  # 未加引號的括號
```

**錯誤**: `yaml.YAMLError: expected <block end>, but found '<scalar>'`

**解決方案**: 實作 fallback parser
```python
try:
    metadata = yaml.safe_load(yaml_content)
except yaml.YAMLError:
    # 逐行解析
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            # 特殊處理 tags、source 等欄位
```

### 挑戰 2：連結網絡提取失敗

**問題**: 正則表達式無法處理多行空白
```markdown
## 連結網絡
                     ← 多行空白
**導向** → [[ID1]]
```

**原始正則**: `r'## 連結網絡\n(.+?)'` （無法匹配）

**修正後**: `r'## 連結網絡\s*\n(.+?)'` （允許任意空白）

### 挑戰 3：Windows 編碼問題

**問題**: `UnicodeEncodeError: 'cp950' codec can't encode character '\u2705'`

**解決方案**:
```python
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

### 挑戰 4：ID 格式不一致

**問題**: 現有卡片可能使用錯誤格式（如 `CogSci20251028001`）

**解決方案**: 自動正規化
```python
def normalize_id(zettel_id: str) -> str:
    zettel_id = zettel_id.replace('_', '-').strip()
    match = re.match(r'^([A-Za-z]+)[-]?(\d{8})[-]?(\d{3})$', zettel_id)
    if match:
        domain, date, num = match.groups()
        return f"{domain}-{date}-{num}"
```

---

## 📋 待完成功能 (5/13)

### P0 高優先級

1. **實作卡片與論文的關聯邏輯** (進行中)
   - `link_zettel_to_paper(card_id, paper_id)`
   - `get_zettel_by_paper(paper_id)`
   - 自動關聯（基於 source_info 匹配）

2. **實作論文元數據增強功能**
   - 從卡片反向填充論文 keywords
   - 統計每篇論文的卡片數量
   - 論文完整度評分

### P1 中優先級

3. **創建 CLI 命令**
   - `index-zettel`: 批次索引命令
   - `sync-zotero`: Zotero 同步命令
   - `search-zettel`: 交互式搜索

4. **撰寫單元測試**
   - 目標覆蓋率: >80%
   - pytest 框架
   - 測試資料生成器

### P2 低優先級

5. **執行全量測試並生成報告**
   - 測試 ~660 張卡片（33 個資料夾）
   - 效能基準測試
   - 錯誤案例收集

---

## 📊 進度追蹤

### 時間統計

- **計畫階段**: 2 小時（實施計畫文檔）
- **開發階段**: 4 小時（實作 + 除錯）
- **測試階段**: 1 小時（測試腳本 + 驗證）
- **總計**: ~7 小時

### 代碼統計

| 模組 | 檔案 | 行數 |
|------|------|------|
| 核心實作 | kb_manager.py | +478 |
| 測試腳本 1 | test_parse_single_zettel.py | 377 |
| 測試腳本 2 | test_zettel_indexing.py | 201 |
| 實施計畫 | TASK_1.3_IMPLEMENTATION_PLAN.md | 1,000+ |
| 設計文檔 | AGENT_SKILL_DESIGN.md | +138 |
| **總計** | | **~2,200 行** |

---

## 🎯 下一步計畫

### 短期 (本週)

1. **完成卡片-論文關聯邏輯**
   - 時間估計: 2 小時
   - 優先級: P0
   - 產出: 3 個新方法 + 測試

2. **實作論文元數據增強**
   - 時間估計: 2 小時
   - 優先級: P0
   - 產出: 2 個新方法 + 統計報告

### 中期 (下週)

3. **創建 CLI 工具**
   - 時間估計: 4 小時
   - 優先級: P1
   - 產出: 3 個命令 + 說明文檔

4. **單元測試套件**
   - 時間估計: 4 小時
   - 優先級: P1
   - 產出: 15+ 測試案例

### 長期 (兩週內)

5. **全量測試與報告**
   - 時間估計: 3 小時
   - 優先級: P2
   - 產出: 測試報告 + 效能基準

---

## 📝 技術文檔索引

### 核心文檔
- **實施計畫**: `TASK_1.3_IMPLEMENTATION_PLAN.md` (1,000+ 行)
- **設計文檔**: `AGENT_SKILL_DESIGN.md` (含 Task 1.3 規格)
- **進度報告**: `TASK_1.3_PROGRESS_REPORT.md` (本文檔)

### 代碼文件
- **核心實作**: `src/knowledge_base/kb_manager.py` (Zettelkasten 方法 L589-L1067)
- **測試腳本**: `test_parse_single_zettel.py`, `test_zettel_indexing.py`

### 資料庫
- **SQLite**: `knowledge_base/index.db`
- **表結構**: `zettel_cards`, `zettel_links`, `zettel_cards_fts`

---

## 🤝 貢獻者

- **實作**: Claude Code (Sonnet 4.5)
- **需求定義**: AGENT_SKILL_DESIGN.md
- **測試資料**: output/zettelkasten_notes/zettel_Linguistics_20251029/

---

**報告生成時間**: 2025-10-30
**下次更新**: 完成卡片-論文關聯邏輯後
