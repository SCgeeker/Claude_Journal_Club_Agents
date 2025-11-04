# 領域名稱策略影響分析

**分析日期**: 2025-11-04 14:40
**問題**: 如果領域名稱只放在知識庫 + YAML，不放在資料夾和檔案名稱，對當前實作計畫有何影響？

---

## 📊 當前系統中領域的使用位置

### 1. 資料夾名稱（檔案系統）

**位置**: `make_slides.py` 第 391 行

```python
output_dir = Path(f"output/zettelkasten_notes/zettel_{args.from_kb}_{cite_key}_{args.domain}_{date_str}")
```

**格式**: `zettel_{paper_id}_{cite_key}_{domain}_{date}/`

**範例**:
- `zettel_1_Her2007_Research_20251104/`
- `zettel_2_Allassonniere-Tang-2021_Linguistics_20251104/`

---

### 2. 卡片檔案名稱

**位置**: `src/generators/zettel_maker.py` 第 73-87 行

```python
def generate_card_id(self, domain: str, sequence: int, date: Optional[str] = None) -> str:
    """生成語義化卡片ID"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    return f"{domain}-{date}-{sequence:03d}"
```

**格式**: `{domain}-{date}-{序號}.md`

**範例**:
- `Research-20251104-001.md`
- `Linguistics-20251104-001.md`

---

### 3. 卡片 ID（資料庫主鍵）

**位置**: `zettel_cards.zettel_id` 欄位

**格式**: 與檔案名稱相同（無 `.md` 副檔名）

**範例**:
- `Research-20251104-001`
- `Linguistics-20251029-001`

**用途**:
- 資料庫主鍵
- 卡片間連結 `[[Research-20251104-002]]`
- Mermaid 圖表節點 ID

---

### 4. 資料庫欄位

**位置**: `zettel_cards.domain` 欄位

**格式**: 純文字

**範例**: `Research`, `Linguistics`, `CogSci`

---

### 5. YAML Front Matter

**位置**: 每張卡片的 metadata

```yaml
---
id: Research-20251104-001
title: "卡片標題"
domain: Research
...
---
```

---

## 🔍 改為「只在知識庫+YAML」的影響分析

### 建議新格式

#### 資料夾名稱
```
舊: zettel_{paper_id}_{cite_key}_{domain}_{date}/
新: zettel_{paper_id}_{cite_key}_{date}/
```

**範例**:
- 舊: `zettel_1_Her2007_Research_20251104/`
- 新: `zettel_1_Her2007_20251104/`

#### 卡片檔案名稱
```
舊: {domain}-{date}-{序號}.md
新: {paper_id}-{date}-{序號}.md  或  {序號}.md
```

**範例**:
- 舊: `Research-20251104-001.md`
- 新A: `1-20251104-001.md`（包含 paper_id）
- 新B: `001.md`（純序號）

#### 卡片 ID（zettel_id）
```
舊: {domain}-{date}-{序號}
新: {paper_id}-{date}-{序號}  或  {cite_key}-{序號}
```

**範例**:
- 舊: `Research-20251104-001`
- 新A: `1-20251104-001`（基於 paper_id）
- 新B: `Her2007-001`（基於 cite_key）

---

## ✅ 優點

### 1. 簡化資料夾結構
- 資料夾名稱更短、更清晰
- 避免領域變更時需要重命名資料夾

### 2. 避免 ID 衝突
**當前問題**:
- 如果兩篇論文同一天生成，且領域相同，卡片 ID 會重複
- 例如：`Research-20251104-001` 可能出現在多篇論文中

**解決方案**:
- 使用 `paper_id` 確保唯一性
- 例如：`1-20251104-001` 絕對唯一

### 3. 更靈活的領域管理
- 可以在資料庫中輕鬆更改領域
- 不需要重命名檔案或更新連結

### 4. 語義更清晰
- 檔案名稱反映論文來源（paper_id 或 cite_key）
- 領域資訊保留在 metadata 中

---

## ⚠️ 缺點與風險

### 1. 程式碼修改範圍

需要修改 3 個核心文件：

| 文件 | 修改內容 | 工作量 |
|------|---------|--------|
| `make_slides.py` | 資料夾名稱生成邏輯（第 391 行） | 5 分鐘 |
| `src/generators/zettel_maker.py` | `generate_card_id()` 方法（第 73-87 行） | 10 分鐘 |
| `batch_generate_zettel.py` | 確認參數傳遞 | 5 分鐘 |

**總工作量**: **20 分鐘**

---

### 2. 向後相容性

**問題**: 已生成的 Zettel（Abbas-2022, 以及 36 個舊資料夾）

**影響**:
- 舊資料夾：`zettel_Abbas-2022_Linguistics_20251104/`
- 新資料夾：`zettel_Abbas-2022_20251104/`（如果採用新格式）

**解決方案**:
- **選項 A**: 保留舊格式，只改未來生成的
- **選項 B**: 統一格式，重命名舊資料夾（需 10-15 分鐘）
- **選項 C**: 接受混合格式（不推薦）

---

### 3. ID 唯一性保證

**當前**: `{domain}-{date}-{序號}` → 可能重複

**新格式 A**: `{paper_id}-{date}-{序號}` → **絕對唯一** ✅

**新格式 B**: `{cite_key}-{序號}` → **絕對唯一** ✅（更簡潔）

**推薦**: 新格式 B（`{cite_key}-{序號}`）

**理由**:
- 最簡潔
- 有語義（cite_key 可識別論文）
- 絕對唯一
- 與資料夾名稱一致

---

### 4. 連結與索引

**影響**:
- Markdown 連結：`[[Research-20251104-002]]` → `[[Her2007-002]]`
- Mermaid 圖表：節點 ID 需要更新
- 索引文件：需要更新 ID 格式

**工作量**: 模板修改 5-10 分鐘

---

## 📋 實作建議

### 方案 A：立即採用新格式（推薦⭐）

**步驟**:

1. **修改 `make_slides.py`**（第 391 行）
   ```python
   # 舊
   output_dir = Path(f"output/zettelkasten_notes/zettel_{args.from_kb}_{cite_key}_{args.domain}_{date_str}")

   # 新
   output_dir = Path(f"output/zettelkasten_notes/zettel_{cite_key}_{date_str}")
   ```

2. **修改 `zettel_maker.py`**（第 73-87 行）
   ```python
   def generate_card_id(self, cite_key: str, sequence: int) -> str:
       """
       生成卡片ID（基於 cite_key）

       Args:
           cite_key: 論文的 bibtex cite_key
           sequence: 序號

       Returns:
           格式化ID（如 Her2007-001）
       """
       return f"{cite_key}-{sequence:03d}"
   ```

3. **更新模板和 Prompt**
   - 修改 `zettelkasten_template.jinja2`
   - 更新 LLM prompt，要求生成 `{cite_key}-{序號}` 格式的 ID

4. **測試**
   ```bash
   python make_slides.py "Test" --from-kb 2 --style zettelkasten --domain Research --detail comprehensive
   ```

**優點**:
- ✅ 一勞永逸
- ✅ ID 絕對唯一
- ✅ 簡化結構
- ✅ 更靈活

**缺點**:
- ⚠️ 需要 20-30 分鐘修改和測試
- ⚠️ 與舊資料不一致（但可接受）

---

### 方案 B：保持現狀，批量生成後再改（折衷）

**步驟**:
1. 使用當前格式完成批量生成（46 篇論文）
2. 批量生成完成後，實作新格式
3. Phase 2.4 開始使用新格式

**優點**:
- ✅ 不延誤批量生成
- ✅ 有時間仔細測試新格式

**缺點**:
- ⚠️ 46 篇論文會使用舊格式
- ⚠️ 需要接受混合格式或重新生成

---

### 方案 C：保持現狀，不修改（最簡單）

**理由**:
- 當前格式已經可用
- ID 重複問題可透過日期區分（機率極低）
- 領域資訊在檔案名稱中有參考價值

**優點**:
- ✅ 零延遲
- ✅ 零風險

**缺點**:
- ⚠️ 未來領域變更困難
- ⚠️ ID 可能重複（理論上）

---

## 🎯 推薦決策

### 情境 1：時間充裕（有 30 分鐘）

**推薦**: **方案 A**（立即採用新格式）

**理由**:
1. ✅ 20-30 分鐘可完成修改和測試
2. ✅ 一次性解決未來問題
3. ✅ 新格式更優雅、更靈活
4. ✅ 46 篇論文從一開始就使用新格式

**流程**:
```
修改代碼（20 分鐘）
  ↓
單篇測試（5 分鐘）
  ↓
啟動批量生成（25-90 分鐘）
```

---

### 情境 2：立即開始（無額外時間）

**推薦**: **方案 B**（保持現狀，批量生成後再改）

**理由**:
1. ✅ 立即開始批量生成
2. ✅ Phase 2.3 完成後再優化
3. ✅ 不影響當前進度

**流程**:
```
啟動批量生成（現在）
  ↓
Phase 2.3 完成
  ↓
實作新格式（Phase 2.4 前）
```

---

## 🔧 新格式詳細規格

如果採用方案 A，以下是完整的新格式規格：

### 資料夾結構
```
output/zettelkasten_notes/
└── zettel_{cite_key}_{date}/          ← 移除 domain
    ├── zettel_index.md
    └── zettel_cards/
        ├── {cite_key}-001.md          ← 使用 cite_key 而非 domain
        ├── {cite_key}-002.md
        └── ...
```

### 卡片 ID 格式
```
{cite_key}-{序號}

範例：
- Her2007-001
- Abbas-2022-001
- Allassonniere-Tang-2021-001
```

### YAML Front Matter
```yaml
---
id: Her2007-001                        # 卡片唯一 ID
title: "卡片標題"
domain: Research                       # 領域資訊保留在這裡
tags: [標籤1, 標籤2]
source: "論文標題" (年份)
paper_id: 1                            # 關聯論文
created: 2025-11-04
---
```

### 資料庫欄位
```sql
zettel_cards (
    zettel_id TEXT PRIMARY KEY,        -- Her2007-001
    domain TEXT,                        -- Research
    paper_id INTEGER,                   -- 1
    ...
)
```

---

## 📊 對比總結

| 特性 | 當前格式 | 新格式 |
|------|---------|--------|
| **資料夾** | `zettel_1_Her2007_Research_20251104/` | `zettel_Her2007_20251104/` |
| **卡片檔案** | `Research-20251104-001.md` | `Her2007-001.md` |
| **卡片 ID** | `Research-20251104-001` | `Her2007-001` |
| **唯一性** | 理論上可能重複 | 絕對唯一 ✅ |
| **語義性** | 中等（領域+日期） | 高（論文識別碼） ✅ |
| **簡潔性** | 較長 | 更簡潔 ✅ |
| **靈活性** | 低（領域變更困難） | 高 ✅ |
| **實作難度** | - | 20-30 分鐘 |

---

## ✅ 最終建議

### 如果您有 30 分鐘 ⭐

**採用方案 A**：
1. 立即修改代碼（20 分鐘）
2. 單篇測試驗證（5 分鐘）
3. 啟動批量生成（新格式）

**優點**: 一次性解決，未來無憂

---

### 如果要立即開始

**採用方案 B**：
1. 使用當前格式批量生成（現在）
2. Phase 2.3 完成後實作新格式
3. Phase 2.4 開始使用新格式

**優點**: 不延誤進度

---

## 💬 決策問題

**請問您想要**：

**A**: 花 30 分鐘改用新格式（`{cite_key}-{序號}`），然後批量生成 ⭐
**B**: 保持現狀立即批量生成，Phase 2.3 後再優化
**C**: 保持現狀，不修改

**我的建議**: **選擇 A**（如果有時間）或 **B**（如果趕時間）

您的選擇是？
