# Workflows.yaml 重新設計可行性評估

**評估日期**: 2025-10-30
**評估範圍**: KB Manager Agent 工作流程參數重新設計
**目標**: 明確區分流程A（PDF→Zettelkasten）和流程B（PDF→簡報）

---

## 📋 用戶需求澄清

### 原始需求

> 流程B只生成簡報，不生成Zettel卡片。重新設計workflows.yaml的參數，流程A,B各有指定參數及預設值。

### 需求解讀

**流程A：直接生成Zettelkasten**
- 路徑：`PDF → Zettelkasten`
- 用途：批次處理論文，生成原子筆記
- 預設行為：**生成Zettelkasten**（不需要用戶明確設定）

**流程B：只生成簡報**
- 路徑：`PDF → 簡報`
- 用途：製作教學或展示材料
- 預設行為：**只生成簡報**，不提示或生成Zettelkasten

---

## 🔍 當前設計問題分析

### 問題1：batch_import 定位模糊

**當前設計**（workflows.yaml 第 8-108 行）:
```yaml
batch_import:
  name: "批次導入PDF"
  description: "批次處理PDF文件並加入知識庫"
  parameters:
    optional:
      - generate_zettel:
          type: boolean
          default: false  # ❌ 問題：如果流程A要生成Zettel，default=false 不合理
```

**問題**:
- 工作流名稱暗示「導入知識庫」，但也可以生成Zettelkasten
- `generate_zettel` 默認為 `false`，用戶需要明確設定才能觸發流程A
- 職責不清：既是「知識庫管理」也是「Zettelkasten生成」

**影響**:
- 用戶想執行流程A時，需要記得設定 `generate_zettel=true`
- 對話中需要額外詢問「是否生成Zettelkasten？」，增加操作步驟

---

### 問題2：generate_notes 功能定位不明

**當前設計**（workflows.yaml 第 437-517 行）:
```yaml
generate_notes:
  name: "生成筆記"
  description: "生成Zettelkasten原子筆記"
  parameters:
    required:
      - source: paper_id/pdf_path  # ⚠️ 只支援單篇
    optional:
      - domain: default = "CogSci"  # ❌ 有默認值，但不應該有
```

**問題**:
1. **單篇處理限制**: `source` 只接受單個 paper_id 或 pdf_path，不支援批次
2. **與 batch_import 重疊**: 功能與 `batch_import` + `generate_zettel=true` 重疊
3. **默認值不合理**: `domain` 默認為 "CogSci"，應該強制用戶選擇

**影響**:
- 流程A（批次生成Zettelkasten）沒有明確的入口
- 用戶可能困惑：「該用 batch_import 還是 generate_notes？」

---

### 問題3：generate_slides 與 generate_notes 的關係

**當前對話流程**（基於 instructions.md）:

```
用戶: 我想為 paper.pdf 製作簡報和卡片
Agent: [執行 generate_slides] → 生成簡報
Agent: 是否繼續生成 Zettelkasten？[Y/n]  # ❌ 不應該有這個提示
用戶: Y
Agent: [執行 generate_notes] → 生成卡片
```

**問題**:
- 用戶要求的是**流程B**（只生成簡報），但 Agent 仍提示生成 Zettelkasten
- 違反用戶澄清：「流程B只生成簡報，不生成Zettel卡片」

---

## 🎯 重新設計方案

### 方案A：重新定位工作流（推薦 ⭐）

#### 核心思想
- **職責分離**: 每個工作流有明確的單一職責
- **預設值合理**: 流程A預設生成Zettel，流程B預設只生成簡報
- **命名清晰**: 工作流名稱明確反映功能

#### 設計詳情

**1. batch_import → 重新命名為 `batch_import_papers`**

```yaml
batch_import_papers:
  name: "批次導入論文到知識庫"
  description: "批次處理PDF並加入知識庫（不生成Zettelkasten）"
  priority: high

  parameters:
    required:
      - folder_path: 資料夾路徑

    optional:
      - domain: ["CogSci", "Linguistics", "AI", "Research"]
        # 移除默認值，強制詢問
      - max_workers: default = 3

  # 移除 generate_zettel 參數
```

**變更說明**:
- 專注於「知識庫管理」單一職責
- 移除 `generate_zettel` 參數（避免混淆）
- `domain` 移除默認值，強制用戶選擇

**適用場景**:
- 純粹導入PDF到知識庫
- 不需要生成Zettelkasten
- 快速建立論文索引

---

**2. generate_notes → 重新命名為 `batch_generate_zettel`**

```yaml
batch_generate_zettel:
  name: "批次生成Zettelkasten"  # 新名稱
  description: "從PDF批次生成原子筆記並加入知識庫"  # 明確說明批次+加入知識庫
  priority: high  # 提升優先級（這是流程A的主要入口）

  parameters:
    required:
      - source: folder_path 或 pdf_path（支援批次）

    optional:
      - domain: ["CogSci", "Linguistics", "AI"]
        # 移除默認值，強制詢問 ⭐
      - card_count: default = 20
      - detail_level: default = "detailed"
      - llm_provider: default = "google"
      - add_to_kb: default = true  # 新增：預設加入知識庫
      - auto_link: default = true  # 新增：預設自動關聯論文

  steps:
    # 新增批次處理邏輯
    - id: detect_source_type
      description: "檢測來源類型（單篇或批次）"
      action: |
        if is_folder(source):
          mode = "batch"
        else:
          mode = "single"

    - id: collect_parameters
      prompts:
        domain: "領域？(CogSci/Linguistics/AI)（必填）"  # 強制詢問
        card_count: "每篇論文生成多少張卡片？(默認：20)"
        detail_level: "詳細程度？(brief/standard/detailed，默認：detailed)"

    - id: execute
      action: |
        if mode == "batch":
          調用 batch-processor
          參數: generate_zettel=true
        else:
          調用 zettel-maker
```

**變更說明**:
- 重新命名為 `batch_generate_zettel`，明確反映批次處理能力
- `source` 支援 folder_path（批次）和 pdf_path（單篇）
- `domain` **移除默認值**，強制用戶選擇（避免錯誤分類）
- 新增 `add_to_kb` 和 `auto_link` 參數，預設為 true
- 提升優先級為 `high`（這是流程A的主要入口）

**適用場景**:
- **流程A**: 批次處理PDF，生成Zettelkasten
- 自動加入知識庫並關聯論文
- 生成後可用於知識網絡分析

---

**3. generate_slides → 保持不變（已符合需求）**

```yaml
generate_slides:
  name: "生成簡報"
  description: "生成學術簡報（PPTX/Markdown）"
  priority: medium

  parameters:
    # 保持現有參數
    # 不添加任何 Zettelkasten 相關參數
```

**確認**:
- ✅ 當前設計已符合流程B需求
- ✅ 沒有 Zettelkasten 相關參數
- ✅ 不應該在對話中提示「是否生成Zettelkasten」

**適用場景**:
- **流程B**: 生成簡報（PPTX/Markdown）
- 教學、展示、論文報告
- 不涉及Zettelkasten

---

### 方案B：簡化合併（備選）

#### 核心思想
- 保留 `batch_import` 作為統一入口
- 通過對話引導區分兩種用途

#### 設計詳情

```yaml
batch_import:
  name: "批次處理PDF"
  description: "批次導入論文到知識庫，可選生成Zettelkasten"

  parameters:
    required:
      - folder_path

    optional:
      - domain  # 移除默認值
      - generate_zettel  # 移除默認值，強制詢問

  steps:
    - id: collect_parameters
      prompts:
        domain: "領域？(CogSci/Linguistics/AI/Research)（必填）"
        generate_zettel: |
          選擇處理方式：
          1. 只加入知識庫（不生成Zettelkasten）
          2. 加入知識庫 + 生成Zettelkasten（流程A）
```

**優點**:
- 簡化工作流數量
- 統一批次處理入口

**缺點**:
- 每次都需要額外詢問用戶意圖
- 職責不單一（既管理知識庫又生成Zettelkasten）
- 不符合「流程A,B各有指定參數及預設值」的需求

---

## 📊 方案對比

| 項目 | 方案A（重新定位）⭐ | 方案B（簡化合併） |
|------|-------------------|------------------|
| **職責分離** | ✅ 清晰 | ❌ 模糊 |
| **預設值合理** | ✅ 各流程有合理預設 | ⚠️ 需要額外詢問 |
| **用戶體驗** | ✅ 明確的入口 | ❌ 每次都要選擇 |
| **符合需求** | ✅ 完全符合 | ⚠️ 部分符合 |
| **實作難度** | 中等 | 簡單 |
| **工作量** | 2-3 小時 | 1 小時 |

**推薦**: **方案A**，理由：
1. 完全符合「流程A,B各有指定參數及預設值」的需求
2. 職責分離，用戶不會困惑
3. 預設值合理，減少操作步驟

---

## 🔧 實施細節（方案A）

### 修改檔案

| 檔案 | 修改內容 | 行數估計 |
|------|---------|---------|
| `workflows.yaml` | 重新命名和調整參數 | ~50 行修改 |
| `instructions.md` | 更新工作流程說明 | ~80 行修改 |
| `batch_process.py` | 新增 source 類型檢測 | ~30 行新增 |
| `make_slides.py` | 移除 Zettelkasten 提示 | ~10 行刪除 |

### 詳細修改清單

#### 1. workflows.yaml 修改

**第 8-108 行：batch_import → batch_import_papers**

```yaml
# BEFORE
batch_import:
  name: "批次導入PDF"
  description: "批次處理PDF文件並加入知識庫"
  parameters:
    optional:
      - domain: default: "Research"
      - generate_zettel: default: false

# AFTER
batch_import_papers:
  name: "批次導入論文到知識庫"
  description: "批次處理PDF並加入知識庫（不生成Zettelkasten）"
  parameters:
    optional:
      - domain:
          options: ["CogSci", "Linguistics", "AI", "Research"]
          # 移除 default，強制詢問
      # 移除 generate_zettel 參數
```

**第 437-517 行：generate_notes → batch_generate_zettel**

```yaml
# BEFORE
generate_notes:
  name: "生成筆記"
  description: "生成Zettelkasten原子筆記"
  parameters:
    required:
      - source: paper_id/pdf_path  # 單篇
    optional:
      - domain: default: "CogSci"

# AFTER
batch_generate_zettel:
  name: "批次生成Zettelkasten"
  description: "從PDF批次生成原子筆記並加入知識庫"
  priority: high  # 提升優先級
  parameters:
    required:
      - source: folder_path 或 pdf_path  # 支援批次
    optional:
      - domain:
          options: ["CogSci", "Linguistics", "AI"]
          # 移除 default，強制詢問
      - add_to_kb: default: true  # 新增
      - auto_link: default: true  # 新增
      - card_count: default: 20
      - detail_level: default: "detailed"
      - llm_provider: default: "google"
```

---

#### 2. instructions.md 修改

**第 58-145 行：批次導入PDF → 批次導入論文**

```markdown
# BEFORE
### 1. 批次導入PDF

workflow: batch_import
是否生成Zettelkasten筆記？(是/否，默認：否)

# AFTER
### 1. 批次導入論文到知識庫

workflow: batch_import_papers
（不詢問 Zettelkasten，因為這個工作流不生成卡片）

用戶可能的輸入：
- "批次導入PDF到知識庫"
- "索引這些論文"
- "建立論文索引"
```

**新增章節：批次生成Zettelkasten**

```markdown
### 2. 批次生成Zettelkasten（流程A）

**用戶可能的輸入**：
- "批次生成Zettelkasten"
- "從這些PDF生成卡片"
- "處理D:\pdfs\並生成原子筆記"

workflow: batch_generate_zettel
steps:
  1. 檢測來源類型（資料夾或單個PDF）
  2. 收集參數：
     - domain: 領域（必填，無默認值）
     - card_count: 卡片數量（默認：20）
  3. 執行批次處理
  4. 自動加入知識庫並關聯論文
```

**第 267-306 行：生成簡報（流程B）**

```markdown
# BEFORE
### 5. 生成簡報

（保持不變，但移除任何關於 Zettelkasten 的提示）

# AFTER
### 5. 生成簡報（流程B）

workflow: generate_slides

**重要**: 此工作流只生成簡報，不生成Zettelkasten
不應該在對話中詢問「是否生成Zettelkasten」
```

---

#### 3. batch_process.py 修改

**新增 source 類型檢測**（約 30 行）

```python
# src/processors/batch_processor.py

def detect_source_type(source: str) -> str:
    """檢測來源類型（單篇或批次）

    Args:
        source: 檔案路徑或資料夾路徑

    Returns:
        "single" 或 "batch"
    """
    from pathlib import Path

    source_path = Path(source)

    if source_path.is_dir():
        return "batch"
    elif source_path.is_file() and source_path.suffix == ".pdf":
        return "single"
    else:
        raise ValueError(f"Invalid source: {source}")

# 在 batch_generate_zettel 調用時使用
def batch_generate_zettel(source, domain, card_count=20, **kwargs):
    """批次生成Zettelkasten（支援單篇和批次）"""
    source_type = detect_source_type(source)

    if source_type == "batch":
        # 調用批次處理器
        processor = BatchProcessor()
        result = processor.process_batch(
            pdf_paths=source,
            domain=domain,
            add_to_kb=True,
            generate_zettel=True,
            zettel_config={
                'card_count': card_count,
                **kwargs
            }
        )
    else:
        # 調用單篇處理
        result = process_single_pdf(source, domain, card_count, **kwargs)

    return result
```

---

#### 4. Agent 對話邏輯調整

**instructions.md 新增意圖識別邏輯**

```markdown
## 🎯 意圖識別邏輯（更新）

### 用戶想要「生成Zettelkasten」
關鍵詞: "生成卡片", "Zettelkasten", "原子筆記", "zettel"
→ 推薦 `batch_generate_zettel` 工作流（流程A）

### 用戶想要「生成簡報」
關鍵詞: "簡報", "投影片", "slides", "presentation"
→ 推薦 `generate_slides` 工作流（流程B）
→ **不**詢問是否生成 Zettelkasten

### 用戶想要「導入知識庫」
關鍵詞: "導入", "索引", "加入知識庫", "import"
→ 推薦 `batch_import_papers` 工作流
→ **不**詢問是否生成 Zettelkasten
```

---

## ✅ 驗收標準

### 功能驗收

- [ ] **流程A（batch_generate_zettel）**:
  - [ ] 支援批次處理（folder_path）
  - [ ] 支援單篇處理（pdf_path）
  - [ ] `domain` 無默認值，強制詢問
  - [ ] 預設加入知識庫（add_to_kb=true）
  - [ ] 預設自動關聯論文（auto_link=true）

- [ ] **流程B（generate_slides）**:
  - [ ] 只生成簡報，不涉及 Zettelkasten
  - [ ] 對話中不詢問「是否生成Zettelkasten」
  - [ ] 保持現有參數和預設值

- [ ] **batch_import_papers**:
  - [ ] 只導入知識庫，不生成 Zettelkasten
  - [ ] `domain` 無默認值，強制詢問
  - [ ] 移除 `generate_zettel` 參數

### 用戶體驗驗收

- [ ] 用戶說「批次生成Zettelkasten」→ 執行流程A
- [ ] 用戶說「生成簡報」→ 執行流程B，不詢問卡片
- [ ] 用戶說「導入知識庫」→ 執行 batch_import_papers
- [ ] 每個工作流的預設值合理，減少詢問次數

### 測試案例

**測試1：流程A（批次生成Zettelkasten）**
```
用戶: 批次處理 D:\pdfs\mental_simulation 並生成Zettelkasten
Agent: 好的！領域？(CogSci/Linguistics/AI)（必填）
用戶: CogSci
Agent: 卡片數量？(默認：20)
用戶: 默認
Agent: [執行批次處理...]
      ✅ 成功生成 15 篇論文的 Zettelkasten（共 300 張卡片）
      ✅ 已加入知識庫並自動關聯
```

**測試2：流程B（只生成簡報）**
```
用戶: 為 Crockett-2025.pdf 生成簡報
Agent: 主題？
用戶: AI 代理者與認知科學
Agent: 風格？(modern_academic/teaching/...)
用戶: teaching
Agent: [生成簡報...]
      ✅ 簡報已生成：output/AI代理者_teaching.pptx
      （不詢問「是否生成Zettelkasten」）
```

---

## 📅 實施時間估計

| 階段 | 任務 | 時間 |
|------|------|------|
| **Phase 1** | workflows.yaml 修改 | 1 小時 |
| **Phase 2** | instructions.md 更新 | 1 小時 |
| **Phase 3** | batch_process.py 調整 | 0.5 小時 |
| **Phase 4** | 測試和驗收 | 0.5 小時 |
| **總計** | | **3 小時** |

---

## 🎯 總結

### 可行性評估：✅ **高度可行**

**優點**:
1. ✅ 完全符合用戶需求（流程A,B各有指定參數及預設值）
2. ✅ 職責分離，用戶體驗清晰
3. ✅ 預設值合理，減少操作步驟
4. ✅ 向後兼容（保留原有工作流結構）

**風險**:
1. ⚠️ 需要更新文檔和測試
2. ⚠️ 用戶需要適應新的工作流名稱（可透過意圖識別緩解）

**建議**:
- **立即實施方案A**（重新定位工作流）
- 保留原有工作流名稱作為別名（transition period）
- 更新 Agent 意圖識別邏輯，自動引導到正確的工作流

---

## 📝 實施檢查清單

### 準備階段
- [ ] 備份當前 workflows.yaml 和 instructions.md
- [ ] 創建測試環境（避免影響現有系統）

### 實施階段
- [ ] 修改 workflows.yaml（3 個工作流）
- [ ] 更新 instructions.md（4 個章節）
- [ ] 調整 batch_process.py（source 類型檢測）
- [ ] 移除 make_slides.py 中的 Zettelkasten 提示

### 測試階段
- [ ] 測試流程A（batch_generate_zettel）
- [ ] 測試流程B（generate_slides）
- [ ] 測試 batch_import_papers
- [ ] 驗證意圖識別邏輯

### 部署階段
- [ ] 合併修改到主分支
- [ ] 更新 CLAUDE.md 文檔
- [ ] 通知用戶新的工作流名稱

---

**報告完成時間**: 2025-10-30 22:00
**評估結論**: ✅ **高度可行，建議立即實施方案A**
**預計工作量**: 3 小時
**優先級**: P1（應該改進）
