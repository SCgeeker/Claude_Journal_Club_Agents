# Metadata 快速修復指南

**工具位置**: `fix_metadata.py`
**詳細計劃**: `output/METADATA_REPAIR_PLAN.md`

---

## ⚡ 3 分鐘快速開始

### 方法 1: 自動修復（推薦新手）

```bash
# 1️⃣ 預覽年份修復
python fix_metadata.py --batch --field year --dry-run

# 2️⃣ 執行年份修復（成功率 65%）
python fix_metadata.py --batch --field year

# 3️⃣ 檢查結果
python check_quality.py
```

**預期結果**: 23 篇中成功修復 15 篇年份

---

### 方法 2: SQL 批次修復（推薦高級用戶）

```bash
# 1️⃣ 更新確定的年份（2 篇）
sqlite3 knowledge_base/index.db < output/batch_update_years.sql

# 2️⃣ 更新關鍵詞（16 篇）
sqlite3 knowledge_base/index.db < output/batch_update_keywords.sql

# 3️⃣ 檢查結果
python check_quality.py
```

**優點**: 快速、可預測、可回滾

---

## 📋 需要手動處理的 8 篇論文

這些論文的年份無法自動提取，需要查詢：

| ID | 標題 | 建議查詢方法 | 預估年份 |
|----|------|-------------|---------|
| 5 | 華語分類詞... | Google Scholar | 2020? |
| 7 | International Journal | 查看 Markdown | 2015? |
| 11 | https://doi.org/... | **訪問 DOI** | 2021 ✅ |
| 12 | Events as... | Google Scholar | 2012? |
| 17 | Multimodal... | Google Scholar | 2024? |
| 24 | Research Article | 摘要線索 | 2018? |
| 30 | HCOMP2022 | **標題確認** | 2022 ✅ |
| 36 | Human-Centred AI | Google Scholar | 2024? |

### 快速查詢指令

```bash
# 論文 11 (最簡單 - 有 DOI)
curl -L "https://doi.org/10.1057/s41599-021-01003-5" | grep -i "published\|year"

# 論文 30 (最簡單 - 標題包含年份)
# 確定是 2022 年 ✅

# 其他論文 - Google Scholar
# 複製標題到 https://scholar.google.com/ 查詢
```

---

## 🛠️ 修復單篇論文（範例）

### 範例 1: 論文 30 (HCOMP2022)

**問題**: 缺少年份、關鍵詞、摘要
**難度**: ⭐ 簡單（標題包含年份）

```bash
sqlite3 knowledge_base/index.db
UPDATE papers SET
  year = 2022,
  keywords = '["crowdsourcing", "human computation", "AAAI"]'
WHERE id = 30;
.exit
```

---

### 範例 2: 論文 11 (DOI 論文)

**問題**: 缺少年份、摘要
**難度**: ⭐ 簡單（有 DOI）

```bash
# 1. 訪問 DOI 獲取資訊
curl -L "https://doi.org/10.1057/s41599-021-01003-5"

# 2. 更新數據庫
sqlite3 knowledge_base/index.db
UPDATE papers SET year = 2021 WHERE id = 11;
.exit
```

---

### 範例 3: 論文 5 (華語分類詞)

**問題**: 缺少年份、關鍵詞
**難度**: ⭐⭐ 中等（需要查詢）

```bash
# 1. Google Scholar 查詢
# 搜尋: "華語分類詞的界定與教學上的分級 陳羿如 何萬順"

# 2. 假設查到年份為 2020
sqlite3 knowledge_base/index.db
UPDATE papers SET
  year = 2020,
  keywords = '["量詞", "分類詞", "對外華語教學", "教學分級"]'
WHERE id = 5;
.exit
```

---

## 📊 修復效果預估

| 階段 | 操作 | 時間 | 效果 |
|------|------|------|------|
| 1️⃣ | 自動修復年份 | 2 分鐘 | 15/23 篇 ✅ |
| 2️⃣ | 批次更新關鍵詞 | 1 分鐘 | 16/21 篇 ✅ |
| 3️⃣ | 手動查詢 8 篇 | 30-60 分鐘 | 8/8 篇 ✅ |
| **總計** | | **~1 小時** | **年份 100%, 關鍵詞 76%** |

---

## ✅ 修復後檢查

```bash
# 統計改善情況
python -c "
import sqlite3
db = sqlite3.connect('knowledge_base/index.db')
cursor = db.cursor()

cursor.execute('SELECT COUNT(*) FROM papers WHERE year IS NOT NULL')
year_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM papers')
total = cursor.fetchone()[0]

print(f'年份完整率: {year_count}/{total} = {year_count/total:.1%}')
db.close()
"

# 質量檢查
python check_quality.py --min-score 70
```

---

## 🚨 常見問題

### Q1: 自動修復失敗怎麼辦？

**A**: 使用 SQL 手動更新或編輯 Markdown 文件

```bash
# 方法 1: SQL
sqlite3 knowledge_base/index.db
UPDATE papers SET year = 2020 WHERE id = 5;

# 方法 2: 編輯 Markdown
vim knowledge_base/papers/華語分類詞的界定與教學上的分級_1.md
# 修改 YAML front matter 中的 year
```

---

### Q2: 如何回滾更改？

**A**: 使用數據庫備份

```bash
# 修復前先備份
cp knowledge_base/index.db knowledge_base/index.db.backup

# 如果需要回滾
cp knowledge_base/index.db.backup knowledge_base/index.db
```

---

### Q3: 關鍵詞從哪裡獲取？

**A**: 3 種方法

```bash
# 方法 1: 從摘要提取（如論文 3, 8）
# 摘要末尾通常有 "Keywords: ..."

# 方法 2: 使用 LLM 生成
ollama run gemma2 "從以下內容提取5個關鍵詞: $(cat paper.md | head -200)"

# 方法 3: 從標題推斷
# 如 "Taxonomy of Numeral Classifiers" → ["numeral classifiers", "taxonomy"]
```

---

## 🎯 推薦工作流

```bash
# ===== 10 分鐘快速修復 =====

# 1. 自動修復年份
python fix_metadata.py --batch --field year

# 2. 批次更新確定的內容
sqlite3 knowledge_base/index.db < output/batch_update_years.sql
sqlite3 knowledge_base/index.db < output/batch_update_keywords.sql

# 3. 檢查結果
python check_quality.py

# ===== 30-60 分鐘完整修復 =====

# 4. 手動查詢 8 篇論文的年份
# 使用 Google Scholar 或 DOI

# 5. 更新數據庫
sqlite3 knowledge_base/index.db
UPDATE papers SET year = XXXX WHERE id IN (5, 7, 12, 17, 24, 36);

# 6. 最終檢查
python check_quality.py --detail comprehensive
```

---

## 📁 相關文件

- **詳細計劃**: `output/METADATA_REPAIR_PLAN.md`（500+ 行，每篇論文的具體建議）
- **完整指南**: `METADATA_REPAIR_GUIDE.md`（使用說明、策略、故障排除）
- **SQL 腳本**:
  - `output/batch_update_years.sql`（年份批次更新）
  - `output/batch_update_keywords.sql`（關鍵詞批次更新）

---

**快速指南版本**: 1.0
**更新時間**: 2025-11-01
**下一步**: 執行自動修復或 SQL 批次更新
