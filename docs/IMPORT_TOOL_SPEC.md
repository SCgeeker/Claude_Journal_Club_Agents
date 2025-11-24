# ProgramVerse 匯入工具規格（階段 1）

**版本**: 1.0
**日期**: 2025-11-24
**狀態**: 設計階段

---

## 概述

本文檔定義 `import_zettel.py` 的功能規格，用於將 Claude Lit Workflow 生成的 Zettelkasten 匯入 ProgramVerse Obsidian vault。

---

## 工具定位

```
Claude Lit Workflow                    ProgramVerse
┌─────────────────────┐               ┌─────────────────────┐
│ output/             │               │ ACT/0️⃣Annotation/   │
│   zettelkasten_     │  import_      │   {citekey}/        │
│   notes/            │  zettel.py    │     annotation.md   │
│     zettel_{cite}/  │ ──────────►   │     cards/          │
│       zettel_index  │               │       {cite}-001.md │
│       zettel_cards/ │               │       ...           │
└─────────────────────┘               └─────────────────────┘
```

---

## 功能需求

### 核心功能

1. **解析 Claude Lit 輸出**
   - 讀取 `zettel_index.md` frontmatter 和內容
   - 列舉 `zettel_cards/` 下所有卡片

2. **偵測現有 Annotation**
   - 檢查 ProgramVerse 是否已有該 citekey 的筆記
   - 區分「升級」vs「新建」模式

3. **轉換格式**
   - zettel_index → Annotation Note 格式
   - 保留 Mermaid 概念網絡圖
   - 適配 ProgramVerse frontmatter

4. **寫入 ProgramVerse**
   - 建立資料夾結構
   - 複製/轉換卡片
   - 處理衝突

---

## 兩種處理模式

### 模式 A：新建（Create）

**條件**：ProgramVerse 無該 citekey 的 Annotation

**動作**：
1. 建立 `ACT/0️⃣Annotation/{citekey}/` 資料夾
2. 生成 `{citekey}_annotation.md`（從 zettel_index 轉換）
3. 建立 `cards/` 子資料夾
4. 複製所有卡片（可選轉換格式）

### 模式 B：升級（Upgrade）

**條件**：ProgramVerse 已有該 citekey 的 Annotation Note

**動作**：
1. 讀取現有 Annotation Note
2. 保留人工編輯區塊（Connection Gear、手寫筆記）
3. 插入/更新「📚 卡片清單」區塊
4. 插入/更新「🗺️ 概念網絡圖」區塊
5. 移動原筆記到資料夾結構（如需要）
6. 複製卡片到 `cards/` 子資料夾

---

## 命令列介面

```bash
# 基本用法
python import_zettel.py --source <claude_lit_output_path>

# 指定 citekey
python import_zettel.py --source <path> --citekey Adams-2020

# 批次匯入（整個 output 資料夾）
python import_zettel.py --source <path> --batch

# 乾跑模式（只顯示將執行的動作）
python import_zettel.py --source <path> --dry-run

# 強制覆蓋
python import_zettel.py --source <path> --force
```

### 參數說明

| 參數 | 簡寫 | 必填 | 說明 |
|------|------|------|------|
| `--source` | `-s` | 是 | Claude Lit 輸出路徑 |
| `--citekey` | `-c` | 否 | 指定單一 citekey |
| `--batch` | `-b` | 否 | 批次處理所有資料夾 |
| `--dry-run` | `-n` | 否 | 乾跑模式，不實際寫入 |
| `--force` | `-f` | 否 | 強制覆蓋，不詢問確認 |
| `--vault` | `-v` | 否 | ProgramVerse vault 路徑（可設預設值） |

---

## 輸出格式轉換

### Annotation Note 模板

```markdown
---
title: "{{title}}"
authors: {{authors}}
year: {{year}}
doi: {{doi}}
tags: "concept/anno"
annotated: true
conn: to be created
geared: [ ]
imported_from: "claude_lit_workflow"
imported_date: "{{import_date}}"
card_count: {{card_count}}
---

[Source pdf]({{citekey}}.pdf)

# 📚 卡片清單

{{card_list}}

# 🗺️ 概念網絡圖

{{mermaid_graph}}

# Connection Gear⚙️

{{preserved_connection_gear}}
```

### 欄位映射

| Claude Lit 欄位 | ProgramVerse 欄位 | 說明 |
|----------------|------------------|------|
| `title` | `title` | 直接對應 |
| `authors` | `authors` | 直接對應 |
| `year` | `year` | 直接對應 |
| `doi` | `doi` | 直接對應（可選） |
| `card_count` | `card_count` | 直接對應 |
| - | `tags` | 固定為 `"concept/anno"` |
| - | `annotated` | 設為 `true` |
| - | `imported_from` | 標記來源 |
| - | `imported_date` | 匯入時間 |

---

## 衝突處理策略

### 策略 1：保守合併（預設）

- 保留所有人工編輯內容
- 只更新機器生成區塊（卡片清單、網絡圖）
- 不刪除任何現有內容

### 策略 2：完整覆蓋（--force）

- 完全重新生成 Annotation Note
- 警告：會丟失人工編輯

### 策略 3：互動確認

- 顯示差異
- 逐項詢問用戶決定

---

## 檔案結構

```
ProgramVerse/
├── +/
│   └── tools/
│       ├── import_zettel.py      # 主程式
│       ├── config.yaml           # 配置文件
│       └── README.md             # 使用說明
│
└── ACT/
    └── 0️⃣Annotation/
        ├── Adams-2020/           # 匯入後的結構
        │   ├── Adams-2020_annotation.md
        │   └── cards/
        │       ├── Adams-2020-001.md
        │       └── ...
        └── existing_paper.md     # 舊格式（待升級）
```

---

## 配置文件 (config.yaml)

```yaml
# ProgramVerse 匯入工具配置

paths:
  # Claude Lit Workflow 輸出路徑
  claude_lit_output: "D:/core/research/claude_lit_workflow/output/zettelkasten_notes"

  # ProgramVerse vault 路徑
  vault: "D:/core/research/Program_verse"

  # Annotation 資料夾
  annotation_folder: "ACT/0️⃣Annotation"

  # PDF 資料夾（用於生成連結）
  pdf_folder: "+/pdf"

templates:
  # Annotation Note 模板路徑
  annotation_template: "Templates/Template, Annotation Note.md"

behavior:
  # 預設衝突處理策略
  conflict_strategy: "conservative"  # conservative | force | interactive

  # 是否轉換卡片格式
  convert_cards: false

  # 是否生成匯入報告
  generate_report: true
```

---

## 錯誤處理

| 錯誤類型 | 處理方式 |
|---------|---------|
| 來源路徑不存在 | 報錯並退出 |
| 無效的 zettel_index 格式 | 跳過並記錄 |
| 目標資料夾已存在（新建模式） | 詢問或跳過 |
| 寫入權限不足 | 報錯並退出 |
| 編碼問題 | 使用 UTF-8，fallback 到 latin-1 |

---

## 日誌和報告

### 執行日誌

```
[2025-11-24 15:30:00] INFO: 開始匯入 Adams-2020
[2025-11-24 15:30:01] INFO: 模式: 新建
[2025-11-24 15:30:02] INFO: 建立資料夾: ACT/0️⃣Annotation/Adams-2020/
[2025-11-24 15:30:03] INFO: 寫入: Adams-2020_annotation.md
[2025-11-24 15:30:04] INFO: 複製 20 張卡片
[2025-11-24 15:30:05] INFO: 完成 Adams-2020
```

### 匯入報告

```markdown
# 匯入報告 - 2025-11-24

## 摘要
- 處理: 5 篇論文
- 新建: 3 篇
- 升級: 2 篇
- 失敗: 0 篇

## 詳細

| citekey | 模式 | 卡片數 | 狀態 |
|---------|------|--------|------|
| Adams-2020 | 新建 | 20 | ✅ |
| Baruch-2016 | 升級 | 18 | ✅ |
| ...
```

---

## 測試計畫

### 單元測試

1. `test_parse_zettel_index()` - 解析 zettel_index
2. `test_detect_existing_annotation()` - 偵測現有筆記
3. `test_convert_to_annotation()` - 格式轉換
4. `test_merge_content()` - 內容合併

### 整合測試

1. 新建模式：匯入全新論文
2. 升級模式：升級現有 Annotation
3. 批次模式：處理多篇論文
4. 邊界情況：空卡片、特殊字元、長檔名

---

## 開發時程（預估）

| 階段 | 工作項目 | 時間 |
|------|---------|------|
| 1 | 基本框架 + 解析器 | 2-3 小時 |
| 2 | 新建模式實作 | 2-3 小時 |
| 3 | 升級模式實作 | 3-4 小時 |
| 4 | CLI + 配置 | 1-2 小時 |
| 5 | 測試 + 除錯 | 2-3 小時 |
| **總計** | | **10-15 小時** |

---

## 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2025-11-24 | 初版設計 |

---

*本文檔為 ProgramVerse 匯入工具的設計規格*
