# Phase 2.4 執行計畫

**日期**: 2025-11-04
**狀態**: 🚀 **執行中**
**目標**: 元數據修復與失敗論文重新生成

---

## 🎯 目標

1. **元數據完整性**: 達到 100% cite_key 覆蓋率，>95% 年份覆蓋率
2. **Zettel 完整性**: 重新生成 18 篇失敗的論文，達到 64/64 (100%)
3. **卡片總數**: 從 1,169 張增加到約 1,500-1,600 張

---

## 📋 任務清單

### 優先級 1: 元數據修復 (必須完成)

#### Task 1.1: 補充 cite_key
- **目標**: 18 篇論文 → 0 篇缺失 (100% 覆蓋)
- **方法**: 從 Zotero bib 文件同步
- **命令**:
  ```bash
  python kb_manage.py update-from-bib "D:\core\Research\Program_verse\+\My Library.bib" --verbose
  ```
- **預期時間**: 2-5 分鐘
- **驗證**:
  ```sql
  SELECT COUNT(*) FROM papers WHERE cite_key IS NULL;
  -- 預期: 0
  ```

#### Task 1.2: 補充年份
- **目標**: 33 篇論文 → <3 篇缺失 (>95% 覆蓋)
- **方法**: 從 bib 文件同步
- **預期時間**: 2-3 分鐘
- **驗證**:
  ```sql
  SELECT COUNT(*) FROM papers WHERE year IS NULL OR year = 0;
  -- 預期: <3
  ```

#### Task 1.3: 驗證元數據更新
- **檢查項目**:
  - [ ] 所有論文都有 cite_key
  - [ ] >95% 論文有年份
  - [ ] cite_key 格式正確 (Author-YYYY)
  - [ ] 無重複 cite_key
- **預期時間**: 2 分鐘

### 優先級 2: 重新生成失敗的 Zettel

#### Task 2.1: 準備失敗論文清單
- **來源**: `batch_zettel_stats.json`
- **數量**: 18 篇論文
- **ID 清單**:
  ```
  1, 3, 4, 8, 10, 13, 14, 15, 16, 18, 19, 20, 22, 25, 26, 27, 28, 29
  ```

#### Task 2.2: 批次重新生成
- **方法**: 使用更新後的 cite_key 重新執行
- **選項**:
  - **Option A**: 使用 `batch_generate_zettel.py` 針對特定 ID
  - **Option B**: 使用 `make_slides.py` 逐個生成
- **預期時間**: 10-15 分鐘 (18 篇 × 30-40 秒/篇)
- **預期輸出**:
  - 18 個新資料夾: `zettel_{cite_key}_20251104/`
  - 約 360-400 張新卡片 (18 × 20-22 張/篇)

#### Task 2.3: 驗證生成結果
- **檢查項目**:
  - [ ] 18 個資料夾全部生成成功
  - [ ] 每個資料夾包含 `zettel_index.md` 和 `zettel_cards/`
  - [ ] Mermaid 圖表正確顯示（無雙引號問題）
  - [ ] 卡片 ID 格式正確 (`{cite_key}-{序號}`)
- **預期時間**: 3-5 分鐘

### 優先級 3: 統計與報告

#### Task 3.1: 生成統計報告
- **指標**:
  - 總論文數: 64
  - Zettel 生成成功率: 100% (64/64)
  - 卡片總數: ~1,500-1,600 張
  - 平均卡片數/論文: ~23-25 張
  - 元數據完整性: cite_key 100%, year >95%

#### Task 3.2: 創建 Phase 2.4 完成報告
- **內容**:
  - 元數據修復詳情
  - 重新生成統計
  - 與 Phase 2.3 對比
  - Phase 2.5 建議 (Relation Finder)

---

## 🔧 執行步驟

### Step 1: 元數據修復 (預計 10 分鐘)

```bash
# 1.1 補充 cite_key
python kb_manage.py update-from-bib "D:\core\Research\Program_verse\+\My Library.bib" --verbose

# 1.2 驗證 cite_key 更新
python -c "
import sqlite3
conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM papers WHERE cite_key IS NULL')
missing = cursor.fetchone()[0]
print(f'Missing cite_key: {missing}')
cursor.execute('SELECT id, title FROM papers WHERE cite_key IS NULL')
for row in cursor.fetchall():
    print(f'  Paper {row[0]}: {row[1][:50]}')
conn.close()
"

# 1.3 補充年份（如果 update-from-bib 未自動處理）
# (根據結果決定是否需要額外處理)

# 1.4 驗證年份更新
python -c "
import sqlite3
conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM papers WHERE year IS NULL OR year = 0')
missing = cursor.fetchone()[0]
print(f'Missing year: {missing}')
conn.close()
"
```

### Step 2: 準備失敗論文清單 (預計 2 分鐘)

```python
import json
from pathlib import Path

# 讀取失敗論文清單
stats_file = Path("batch_zettel_stats.json")
with open(stats_file, 'r', encoding='utf-8') as f:
    stats = json.load(f)

failed_ids = [error['paper_id'] for error in stats['errors']]
print(f"Failed paper IDs ({len(failed_ids)}): {failed_ids}")

# 驗證這些論文現在有 cite_key
import sqlite3
conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()

ready_to_retry = []
still_missing = []

for pid in failed_ids:
    cursor.execute('SELECT id, title, cite_key FROM papers WHERE id = ?', (pid,))
    row = cursor.fetchone()
    if row and row[2]:  # 有 cite_key
        ready_to_retry.append(pid)
    else:
        still_missing.append(pid)

print(f"\nReady to retry: {len(ready_to_retry)} papers")
print(f"Still missing cite_key: {len(still_missing)} papers")

if still_missing:
    print(f"Papers still missing cite_key: {still_missing}")

conn.close()
```

### Step 3: 批次重新生成 (預計 15 分鐘)

**Option A: 修改批次腳本支援 ID 清單**
```python
# 修改 batch_generate_zettel.py 添加 --paper-ids 參數
python batch_generate_zettel.py --paper-ids 1,3,4,8,10,13,14,15,16,18,19,20,22,25,26,27,28,29
```

**Option B: 使用循環逐個生成**
```bash
# 使用 make_slides.py 逐個生成
for id in 1 3 4 8 10 13 14 15 16 18 19 20 22 25 26 27 28 29; do
    echo "Generating Zettel for paper $id..."
    python make_slides.py "Paper $id Zettel" --from-kb $id --style zettelkasten --domain Research --detail comprehensive --llm-provider google --model gemini-2.0-flash-exp
done
```

### Step 4: 驗證與報告 (預計 5 分鐘)

```bash
# 統計新生成的資料夾
ls -d output/zettelkasten_notes/zettel_*_20251104 | wc -l
# 預期: 40 (原有) + 18 (新) = 58 個

# 統計總卡片數
find output/zettelkasten_notes -name "*.md" -path "*/zettel_cards/*" | wc -l
# 預期: ~1,500-1,600 張

# 生成 Phase 2.4 完成報告
```

---

## 📊 預期結果

| 指標 | Phase 2.3 | Phase 2.4 目標 | 改進 |
|------|-----------|---------------|------|
| **論文處理** | 39/64 (61%) | 64/64 (100%) | **+39%** |
| **Zettel 卡片** | 1,169 張 | ~1,550 張 | **+380 張** |
| **cite_key 覆蓋** | 46/64 (72%) | 64/64 (100%) | **+28%** |
| **年份覆蓋** | 31/64 (48%) | >61/64 (>95%) | **+47%** |
| **資料夾數** | 40 個 | 58 個 | **+18 個** |

---

## ⚠️ 風險與應對

### 風險 1: bib 文件中也缺少 cite_key
- **可能性**: 中
- **影響**: 部分論文仍無法生成
- **應對**:
  1. 從 PDF 文件名提取（如 `Her-2007.pdf` → `Her-2007`）
  2. 手動為剩餘論文生成 cite_key

### 風險 2: 批次生成過程中 LLM timeout
- **可能性**: 低
- **影響**: 部分論文生成失敗
- **應對**:
  1. 使用錯誤處理和重試機制
  2. 記錄失敗論文，手動重試

### 風險 3: 年份資訊在 bib 中也缺失
- **可能性**: 高
- **影響**: 索引顯示不完整，但不影響功能
- **應對**:
  1. 接受 <5% 缺失率
  2. 後續從 PDF 元數據或手動補充

---

## 🚀 下一步 (Phase 2.5)

完成 Phase 2.4 後，將進入：

### Phase 2.5: Relation Finder (自動關聯系統)

**核心功能**:
1. **論文-Zettel 自動關聯**
   - 根據 cite_key 和 paper_id 自動建立連結
   - 更新 `zettel_cards` 表的 `paper_id` 欄位

2. **概念-論文映射**
   - 提取 Zettel 卡片的核心概念
   - 建立 `concepts` 表和 `concept_papers` 關聯表

3. **關係圖表生成**
   - 論文引用網絡圖
   - 概念共現網絡圖
   - 論文-Zettel 關聯圖

**預期時間**: 2-3 小時實作 + 測試

---

**計畫創建時間**: 2025-11-04 15:25
**預計完成時間**: 2025-11-04 16:00 (35 分鐘)
**實際開始時間**: _待記錄_

