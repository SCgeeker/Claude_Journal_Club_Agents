# Claude Lit Workflow 輸出格式規範

**版本**: 1.0
**日期**: 2025-11-24
**用途**: 供 ProgramVerse 匯入工具參考

---

## 概述

本文檔定義 Claude Lit Workflow 的 Zettelkasten 輸出格式，作為與 ProgramVerse 平行開發的橋接介面規範。

---

## 輸出目錄結構

```
output/zettelkasten_notes/
└── zettel_{citekey}_{YYYYMMDD}/
    ├── zettel_index.md          # 索引文件（主要入口）
    └── zettel_cards/
        ├── {citekey}-001.md     # 原子卡片
        ├── {citekey}-002.md
        └── ...
```

**命名規則**：
- `{citekey}`: 論文引用鍵，格式為 `Author-Year` 或 `Author-Yeara`（如有重複）
- `{YYYYMMDD}`: 生成日期

---

## zettel_index.md 格式

### YAML Frontmatter

```yaml
---
title: "{citekey}"
aliases:
  - "{citekey}"
authors: "First Author, Second Author"    # 可能為空字串
year: "2024"                              # 字串格式
doi: "10.1234/example.2024.001"           # 新增欄位（可選）
generated_date: "2025-11-24 14:30"
card_count: 20
---
```

**欄位說明**：

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `title` | string | 是 | 等同於 citekey |
| `aliases` | array | 是 | 別名列表 |
| `authors` | string | 是 | 作者列表（可能為空） |
| `year` | string | 是 | 出版年份 |
| `doi` | string | 否 | DOI（未來新增） |
| `generated_date` | string | 是 | 生成時間 |
| `card_count` | integer | 是 | 卡片數量 |

### 內容區塊

#### 1. 卡片清單 (`## 📚 卡片清單`)

```markdown
## 📚 卡片清單

### 1. [卡片標題](zettel_cards/{citekey}-001.md)
- **ID**: `{citekey}-001`
- **核心**: "原文摘錄或核心概念描述"

### 2. [卡片標題](zettel_cards/{citekey}-002.md)
- **ID**: `{citekey}-002`
- **核心**: "..."
```

**解析提示**：
- 使用正則 `### (\d+)\. \[(.+?)\]\((.+?)\)` 提取序號、標題、路徑
- ID 行格式：`- **ID**: \`(.+?)\``
- 核心行格式：`- **核心**: "(.+?)"`

#### 2. 概念網絡圖 (`## 🗺️ 概念網絡圖`)

```markdown
## 🗺️ 概念網絡圖

\`\`\`mermaid
graph TD
    {citekey}-001["卡片標題1"]
    {citekey}-002["卡片標題2"]

    {citekey}-001 --> {citekey}-002
    {citekey}-001 -.-> {citekey}-003
\`\`\`
```

**Mermaid 語法說明**：
- `-->`: 實線箭頭（強關係：導向、基於）
- `-.->`: 虛線箭頭（弱關係：對比、參考）
- 節點 ID 即卡片 ID

#### 3. 標籤索引 (`## 🏷️ 標籤索引`)

```markdown
## 🏷️ 標籤索引

### 標籤名稱
- [[{citekey}-001]] 卡片標題
- [[{citekey}-002]] 卡片標題
```

#### 4. 閱讀建議順序 (`## 📖 閱讀建議順序`)

```markdown
## 📖 閱讀建議順序

1. [[{citekey}-004]] 卡片標題
2. [[{citekey}-001]] 卡片標題
...
```

---

## zettel_card 格式

### YAML Frontmatter

```yaml
---
title: "卡片標題"
summary: |-
  "原文摘錄或核心概念的簡要描述"
---
```

**欄位說明**：

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `title` | string | 是 | 卡片標題（中文） |
| `summary` | string | 是 | 核心概念摘要 |

### 內容區塊

```markdown
## 說明
[概念的詳細說明，1-3 段]

## 連結網絡

**導向** → [[{citekey}-002]], [[{citekey}-003]]
**基於** ← [[{citekey}-001]]
**對比** ↔ [[{citekey}-005]]

## 來源脈絡
- 📄 **文獻**: {citekey}
- 📍 **位置**: Introduction / Methods / Results / Discussion
- 🎯 **情境**: [在什麼情境下引出此概念]

## 個人筆記

🤖 **AI**: [AI 生成的延伸思考或問題]

✍️ **Human**: [預留給人類編輯]

## 待解問題
[與此概念相關的待解問題]
```

---

## 解析範例（Python）

```python
import re
import yaml
from pathlib import Path

def parse_zettel_index(index_path: Path) -> dict:
    """解析 zettel_index.md"""
    content = index_path.read_text(encoding='utf-8')

    # 分離 frontmatter 和內容
    parts = content.split('---', 2)
    frontmatter = yaml.safe_load(parts[1])
    body = parts[2]

    # 提取卡片清單
    cards = []
    card_pattern = r'### (\d+)\. \[(.+?)\]\((.+?)\)\n- \*\*ID\*\*: `(.+?)`\n- \*\*核心\*\*: "(.+?)"'
    for match in re.finditer(card_pattern, body):
        cards.append({
            'order': int(match.group(1)),
            'title': match.group(2),
            'path': match.group(3),
            'id': match.group(4),
            'core': match.group(5)
        })

    # 提取 Mermaid 圖
    mermaid_match = re.search(r'```mermaid\n(.*?)```', body, re.DOTALL)
    mermaid = mermaid_match.group(1) if mermaid_match else None

    return {
        'frontmatter': frontmatter,
        'cards': cards,
        'mermaid': mermaid
    }
```

---

## 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2025-11-24 | 初版，定義基本格式 |

---

## 未來規劃

1. **doi 欄位**：待 Claude Lit 端實作 BibTeX 整合後新增
2. **共享知識庫**：考慮加入 `uuid` 或 `hash` 欄位供同步使用
3. **版本標記**：考慮在 frontmatter 加入 `format_version` 欄位

---

*本文檔由 Claude Lit Workflow 專案維護*
