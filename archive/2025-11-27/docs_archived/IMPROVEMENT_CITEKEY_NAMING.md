# 改善建議：Citekey 命名一致性

**建立日期**: 2025-11-25
**優先級**: 高
**狀態**: 待修復
**相關文件**: EXPORT_FORMAT_SPEC.md, IMPORT_TOOL_SPEC.md

---

## 問題描述

### 現象

生成的 `zettel_index.md` 的 `title` 欄位使用論文標題而非 citekey，導致 ProgramVerse 匯入時建立錯誤的資料夾名稱。

### 範例

**@Barsalou-1999**:
- **資料夾名**: `zettel_Barsalou-1999_20251125` ✅ 正確
- **zettel_index.md title**: `"BEHAVIORAL AND BRAIN SCIENCES(1999) 22,577–660"` ❌ 錯誤
- **預期 title**: `"Barsalou-1999"` ✅

**@Friedrich-2025**:
- **資料夾名**: `zettel_Friedrich-2025_20251125` ✅ 正確
- **zettel_index.md title**: `"Issues in Grounded Cognition and How to Solve Them..."` ❌ 錯誤
- **預期 title**: `"Friedrich-2025"` ✅

### 影響

1. **ProgramVerse 匯入工具** (`import_zettel.py`) 使用 `title` 欄位建立目標資料夾
2. 導致建立如 `BEHAVIORAL AND BRAIN SCIENCES(1999) 22,577–660/` 的錯誤資料夾名
3. 需要手動重新命名，增加維護成本

---

## 規格與實際的差異

### EXPORT_FORMAT_SPEC.md 規定 (第 38-40 行)

```yaml
---
title: "{citekey}"    # 應為 citekey，如 "Barsalou-1999"
aliases:
  - "{citekey}"
```

### 實際生成內容

```yaml
---
title: "BEHAVIORAL AND BRAIN SCIENCES(1999) 22,577–660"  # 論文標題
aliases:
  - "BEHAVIORAL AND BRAIN SCIENCES(1999) 22,577–660"
```

---

## 建議修復方案

### 方案 A：修改 zettel 生成腳本（推薦）

**位置**：`src/batch_process.py` 或相關 zettel 生成模組

**修改內容**：
```python
# 從資料夾名稱提取 citekey
# 例如：zettel_Barsalou-1999_20251125 → Barsalou-1999

import re

def extract_citekey_from_folder(folder_name: str) -> str:
    """從資料夾名稱提取 citekey"""
    match = re.match(r'zettel_(.+?)_\d{8}', folder_name)
    if match:
        return match.group(1)
    return folder_name  # fallback

# 在生成 zettel_index.md 時使用 citekey
frontmatter = {
    'title': citekey,  # 使用 citekey 而非論文標題
    'aliases': [citekey],
    # ...
}
```

### 方案 B：新增 citekey 欄位（備選）

保留現有 title 行為，另外新增明確的 `citekey` 欄位：

```yaml
---
title: "Issues in Grounded Cognition..."  # 保留論文標題
citekey: "Friedrich-2025"                  # 新增明確 citekey
aliases:
  - "Friedrich-2025"
```

**優點**：保留標題資訊，不破壞現有流程
**缺點**：需要同時更新 import_zettel.py 解析邏輯

---

## 臨時解決方案

在修復完成前，ProgramVerse 端採用以下臨時方案：

1. **手動重新命名**：匯入後手動修正資料夾和檔案名稱
2. **修改 import_zettel.py**：改為從來源路徑提取 citekey

```python
# import_zettel.py 臨時修正
def get_citekey_from_source(source_path: Path) -> str:
    """從來源路徑提取 citekey"""
    # zettel_Barsalou-1999_20251125 → Barsalou-1999
    folder_name = source_path.name
    match = re.match(r'zettel_(.+?)_\d{8}', folder_name)
    return match.group(1) if match else None
```

---

## 測試案例

修復後應確保以下測試通過：

| 來源資料夾 | 預期 title | 預期匯入目標 |
|-----------|-----------|-------------|
| `zettel_Barsalou-1999_20251125` | `Barsalou-1999` | `Barsalou-1999/` |
| `zettel_Friedrich-2025_20251125` | `Friedrich-2025` | `Friedrich-2025/` |
| `zettel_vanRooij-2025_20251123` | `vanRooij-2025` | `vanRooij-2025/` |

---

## 相關文件

- [[EXPORT_FORMAT_SPEC|輸出格式規範]] - 定義 zettel_index.md 格式
- [[IMPORT_TOOL_SPEC|匯入工具規格]] - ProgramVerse 端匯入邏輯
- [[../Atlas/Sources/claude_lit_integration/PARALLEL_DEV_TRACKER|平行開發追蹤]] - 問題 #4

---

## 更新紀錄

| 日期 | 更新內容 |
|------|---------|
| 2025-11-25 | 初版建立，記錄問題與建議方案 |

---

*本文件用於追蹤 Claude Lit Workflow 與 ProgramVerse 整合問題*
