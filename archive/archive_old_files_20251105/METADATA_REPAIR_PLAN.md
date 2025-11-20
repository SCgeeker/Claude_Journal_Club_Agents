# Metadata 修復計劃

**生成時間**: 2025-11-01
**論文總數**: 31 篇
**需要修復**: 29 篇（93.5%）
**工具**: `fix_metadata.py`

---

## 📊 問題統計

| 問題類型 | 數量 | 百分比 | 優先級 |
|---------|------|--------|--------|
| 缺少年份 | 8 篇 | 25.8% | ⭐⭐⭐ 高 |
| 缺少關鍵詞 | 21 篇 | 67.7% | ⭐⭐ 中 |
| 缺少摘要 | 15 篇 | 48.4% | ⭐ 低 |
| 多重問題（2-3個） | 14 篇 | 45.2% | - |

---

## 🎯 修復策略

### 階段 1: 批次自動修復（15 分鐘）

**優先修復年份**（成功率 65%）：

```bash
# 1. 預覽修復
python fix_metadata.py --batch --field year --dry-run

# 2. 如果滿意，執行修復
python fix_metadata.py --batch --field year

# 3. 檢查結果
python check_quality.py --field year
```

### 階段 2: 手動修復失敗案例（30-60 分鐘）

針對 8 篇缺少年份且自動修復失敗的論文，使用以下方法之一：
1. 查看原始 PDF
2. Google Scholar 查詢標題
3. CrossRef DOI 查詢（如果有 DOI）
4. 直接編輯 Markdown 或數據庫

### 階段 3: 關鍵詞和摘要（可選，1-2 小時）

使用 LLM 輔助生成高質量 metadata。

---

## 📋 論文清單與修復建議

### 🔴 高優先級：缺少年份（8 篇）

這些論文需要手動修復年份，因為自動提取可能失敗。

#### 論文 5: 華語分類詞的界定與教學上的分級 1

**問題**: year, keywords
**檔案**: `knowledge_base\papers\華語分類詞的界定與教學上的分級_1.md`

**自動提取狀態**: ❌ 失敗（中文內容，格式特殊）

**修復方法 1 - 從摘要推斷**:
摘要提到「賴宛君（2011）」和「范慧貞等（2008）」，推測發表年份在 2011-2020 之間。
建議查詢原始期刊或使用期刊名「華文世界 126期」查詢。

**修復方法 2 - 手動編輯 Markdown**:
```bash
# 編輯 YAML front matter
vim knowledge_base/papers/華語分類詞的界定與教學上的分級_1.md

# 修改:
---
year: 2020  # 根據查詢結果填入
keywords: ["量詞", "分類詞", "對外華語教學", "教學分級"]
---
```

**修復方法 3 - CLI 直接更新**:
```bash
# 假設查詢到年份為 2020
sqlite3 knowledge_base/index.db
UPDATE papers SET year = 2020, keywords = '["量詞", "分類詞", "華語教學"]' WHERE id = 5;
.exit
```

---

#### 論文 7: International Journal of Computer Processing of Oriental Languages

**問題**: year, keywords, abstract
**檔案**: `knowledge_base\papers\International_Journal_of_Computer_Processing_of_Or.md`

**自動提取狀態**: ❌ 失敗（標題不完整）

**建議**:
1. 查看 Markdown 文件開頭判斷是否為期刊論文或書籍章節
2. 搜尋「International Journal of Computer Processing of Oriental Languages + [作者名]」
3. 如果無法找到，考慮從知識庫移除（質量過低）

**CLI 修復**:
```bash
# 假設查詢到完整資訊
sqlite3 knowledge_base/index.db
UPDATE papers SET
  year = 2015,
  keywords = '["Chinese", "Natural Language Processing", "Computational Linguistics"]',
  abstract = '...'
WHERE id = 7;
```

---

#### 論文 11: https://doi.org/10.1057/s41599-021-01003-5

**問題**: year, abstract
**檔案**: `knowledge_base\papers\httpsdoiorg101057s41599_021_01003_5.md`

**自動提取狀態**: ❌ 失敗（標題為 URL）

**修復方法 - 使用 DOI 查詢**:
```bash
# 1. 訪問 DOI URL
https://doi.org/10.1057/s41599-021-01003-5

# 2. 或使用 CrossRef API
curl "https://api.crossref.org/works/10.1057/s41599-021-01003-5"

# 3. 更新數據庫（假設查詢到的資訊）
sqlite3 knowledge_base/index.db
UPDATE papers SET
  title = 'Proper title from DOI',  -- 從 DOI 獲取正確標題
  year = 2021,  -- 從 DOI 路徑推斷 (s41599-021-01003-5)
  abstract = '...'  -- 從 CrossRef API 獲取
WHERE id = 11;
```

**建議**: 這是最容易修復的，因為有 DOI。

---

#### 論文 12: Events as Intersecting Object Histories: A New Theory of

**問題**: year, abstract
**檔案**: `knowledge_base\papers\Events_as_Intersecting_Object_Histories_A_New_Theo.md`

**自動提取狀態**: ❌ 失敗（標題不完整）

**已有關鍵詞**: ["eventrepresentation", "objectrepresentation", "episodicmemory", "semanticmemory", "typesand"]

**建議**:
1. Google Scholar 搜尋 "Events as Intersecting Object Histories"
2. 應該能找到完整論文資訊

**CLI 修復**:
```bash
# 假設找到論文是 2012 年發表
sqlite3 knowledge_base/index.db
UPDATE papers SET
  year = 2012,
  title = 'Events as Intersecting Object Histories: A New Theory of Event Representation',
  abstract = '...'
WHERE id = 12;
```

---

#### 論文 17: Multimodal Language Models Show Evidence of Embodied

**問題**: year, keywords
**檔案**: `knowledge_base\papers\Multimodal_Language_Models_Show_Evidence_of_Embodi.md`

**自動提取狀態**: ❌ 失敗

**已有摘要**: 有完整摘要（200+ 字）

**建議**:
摘要提到「MLLMs」（Multimodal Large Language Models），這是 2023-2024 年的熱門主題。
作者包含「R. Jones」和「Sean Trott」。

**CLI 修復**:
```bash
# 推測年份 2023-2024
sqlite3 knowledge_base/index.db
UPDATE papers SET
  year = 2024,  -- 根據查詢確認
  keywords = '["multimodal language models", "embodiment", "grounding", "shape simulation", "psycholinguistics"]'
WHERE id = 17;
```

---

#### 論文 24: Research Article

**問題**: year
**檔案**: `knowledge_base\papers\Research_Article.md`

**自動提取狀態**: ❌ 失敗（標題過於通用）

**已有資訊**:
- 關鍵詞: ["number", "quantity", "sentencecomprehension", "symbolgrounding"]
- 摘要: 有完整摘要（400+ 字）

**建議**:
1. 閱讀摘要找線索（提到 "Dehaene, 2009"、"Lyons, Ansari, and Beilock (2012)"）
2. 推測年份在 2012-2020 之間
3. Google Scholar 搜尋摘要關鍵句

**CLI 修復**:
```bash
sqlite3 knowledge_base/index.db
UPDATE papers SET year = 2018 WHERE id = 24;  -- 根據查詢確認
```

---

#### 論文 30: ProceedingsoftheTenthAAAIConferenceonHumanComputationandCrowdsourcing(HCOMP2022)

**問題**: year, keywords, abstract
**檔案**: `knowledge_base\papers\ProceedingsoftheTenthAAAIConferenceonHumanComputat.md`

**自動提取狀態**: ❌ 失敗

**提示**: 標題包含「HCOMP2022」，年份應為 **2022**

**CLI 修復（最簡單）**:
```bash
sqlite3 knowledge_base/index.db
UPDATE papers SET
  year = 2022,
  keywords = '["crowdsourcing", "human computation", "AAAI", "exploratory study"]'
WHERE id = 30;
```

---

#### 論文 36: What Does 'Human-Centred AI' Mean?

**問題**: year
**檔案**: `knowledge_base\papers\What_Does_Human_Centred_AI_Mean.md`

**自動提取狀態**: ❌ 失敗

**已有資訊**:
- 作者: ["What Does", "Olivia Guest"]
- 關鍵詞: ["artificial intelligence", "cognitive science", "sociotechnical relationship"]
- 摘要: 有完整摘要（500+ 字）

**建議**:
1. Google Scholar 搜尋 "What Does Human-Centred AI Mean? Olivia Guest"
2. 可能是 2023-2024 年的論文（AI 熱門話題）

**CLI 修復**:
```bash
sqlite3 knowledge_base/index.db
UPDATE papers SET year = 2024 WHERE id = 36;  -- 根據查詢確認
```

---

### 🟡 中優先級：缺少關鍵詞（21 篇）

這些論文大多已有年份和摘要，只需補充關鍵詞。

#### 自動修復建議（先測試 5 篇）

```bash
# 1. 小範圍測試
python fix_metadata.py --batch --field keywords --limit 5 --dry-run

# 2. 如果效果好，批次修復
python fix_metadata.py --batch --field keywords
```

#### 使用 LLM 生成關鍵詞（推薦）

對於自動提取失敗的論文，使用 Ollama 或 Gemini 生成：

**範例腳本（論文 1）**:
```bash
# 使用 Ollama（本地免費）
ollama run gemma2 "請從以下論文摘要提取 5-8 個英文關鍵詞，用逗號分隔：

標題: Taxonomy of Numeral Classifiers
作者: Soon Her, Au Yeung, Shiung Wu
內容: $(cat knowledge_base/papers/Taxonomy_of_Numeral_Classifiers.md | head -200)

只返回關鍵詞列表，不要其他內容。"
```

#### 論文 1: Taxonomy of Numeral Classifiers

**問題**: keywords, abstract
**檔案**: `knowledge_base\papers\Taxonomy_of_Numeral_Classifiers.md`
**年份**: 2007 ✅

**建議關鍵詞**（從標題推斷）:
```bash
sqlite3 knowledge_base/index.db
UPDATE papers SET keywords = '["numeral classifiers", "taxonomy", "linguistic typology", "formal semantics"]' WHERE id = 1;
```

---

#### 論文 3: LanguageSciences25(2003)353–373

**問題**: keywords
**檔案**: `knowledge_base\papers\LanguageSciences252003353373.md`
**年份**: 2003 ✅
**摘要**: 有 ✅（提到 Chinese, Classifier, Coercion）

**摘要已提供關鍵詞**: Chinese; Classifier; Coercion

**CLI 修復（最簡單）**:
```bash
sqlite3 knowledge_base/index.db
UPDATE papers SET keywords = '["Chinese", "Classifier", "Coercion", "kinds", "individuals", "events"]' WHERE id = 3;
```

---

#### 論文 4: Concepts in the Brain

**問題**: keywords, abstract
**檔案**: `knowledge_base\papers\Concepts_in_the_Brain.md`
**年份**: 2019 ✅（已修復）

**建議**（從標題和作者推斷）:
```bash
sqlite3 knowledge_base/index.db
UPDATE papers SET keywords = '["concepts", "brain", "neuroscience", "cognitive science", "semantic typology", "cross-linguistic"]' WHERE id = 4;
```

---

#### 論文 8: LinguisticsVanguard2022;8(1):151–164

**問題**: keywords
**檔案**: `knowledge_base\papers\LinguisticsVanguard202281151164.md`
**年份**: 2022 ✅
**摘要**: 有 ✅（提到 classifiers, database, WACL）

**摘要已提供關鍵詞**: classifiers; database; nominal classification; numeral classifiers; sortal classifiers; wacl

**CLI 修復（最簡單）**:
```bash
sqlite3 knowledge_base/index.db
UPDATE papers SET keywords = '["classifiers", "database", "nominal classification", "numeral classifiers", "sortal classifiers", "WACL"]' WHERE id = 8;
```

---

#### 論文 9-10, 14-15, 18-19, 22-23, 25-26, 28-29

這些論文大多有摘要但缺關鍵詞，可以：
1. 從摘要內容推斷關鍵詞
2. 使用 LLM 生成
3. 批次執行 `python fix_metadata.py --batch --field keywords`

**批次更新範例**:
```bash
# 論文 9
sqlite3 knowledge_base/index.db
UPDATE papers SET keywords = '["classifiers", "Mandarin Chinese", "semantic", "measure words"]' WHERE id = 9;

# 論文 10
UPDATE papers SET keywords = '["measure words", "classifiers", "Chinese grammar", "ontology", "endurant", "perdurant"]' WHERE id = 10;

# 論文 14
UPDATE papers SET keywords = '["cognitive psychology", "language comprehension"]' WHERE id = 14;

# 論文 15
UPDATE papers SET keywords = '["embodied cognition", "language comprehension", "action", "grounding"]' WHERE id = 15;

# 論文 18
UPDATE papers SET keywords = '["object state", "mental representation", "language comprehension", "tense"]' WHERE id = 18;

# 論文 19
UPDATE papers SET keywords = '["cognitive processing", "mental simulation", "color", "language comprehension"]' WHERE id = 19;

# 論文 22
UPDATE papers SET keywords = '["verbal learning", "verbal behavior", "noun phrases"]' WHERE id = 22;

# 論文 23
UPDATE papers SET keywords = '["psychological science", "mental representation", "orientation", "shape"]' WHERE id = 23;

# 論文 25
UPDATE papers SET keywords = '["memory", "cognition", "mental simulation", "color match", "bilingualism"]' WHERE id = 25;

# 論文 26
UPDATE papers SET keywords = '["educational psychology", "experimental", "learning"]' WHERE id = 26;

# 論文 28
UPDATE papers SET keywords = '["mental simulation", "language comprehension", "replication", "orientation", "shape", "color"]' WHERE id = 28;

# 論文 29
UPDATE papers SET keywords = '["participant nonnaivete", "open science", "replication"]' WHERE id = 29;

.exit
```

---

### 🟢 低優先級：缺少摘要（15 篇）

摘要修復較困難，建議：
1. 閱讀 Markdown 文件首段提取
2. 使用 LLM 生成（推薦）
3. 如果論文質量低，可以暫時跳過

**LLM 生成摘要範例**:
```bash
# 使用 Gemini（快速便宜）
python -c "
import google.generativeai as genai
import os

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('gemini-2.0-flash-exp')

with open('knowledge_base/papers/Taxonomy_of_Numeral_Classifiers.md', 'r', encoding='utf-8') as f:
    content = f.read()[:5000]

prompt = f'''
請為以下論文內容撰寫一段學術摘要（繁體中文），150-200字，
包含：研究目的、方法、主要發現、結論。

論文標題: Taxonomy of Numeral Classifiers
論文內容：
{content}
'''

response = model.generate_content(prompt)
print(response.text)
"
```

---

## 🔧 批次修復指令集

### 完整修復流程（推薦）

```bash
# ===== 階段 1: 年份修復 =====

# 1.1 預覽年份修復
python fix_metadata.py --batch --field year --dry-run

# 1.2 執行年份修復
python fix_metadata.py --batch --field year

# 1.3 檢查結果
python check_quality.py --field year

# ===== 階段 2: 手動修復 8 篇年份失敗的論文 =====

# 打開 SQLite 數據庫
sqlite3 knowledge_base/index.db

# 逐一修復（根據上方建議）
UPDATE papers SET year = 2020 WHERE id = 5;   -- 華語分類詞（需查詢）
UPDATE papers SET year = 2015 WHERE id = 7;   -- International Journal（需查詢）
UPDATE papers SET year = 2021 WHERE id = 11;  -- DOI 論文（從 URL 推斷）
UPDATE papers SET year = 2012 WHERE id = 12;  -- Events（需查詢）
UPDATE papers SET year = 2024 WHERE id = 17;  -- Multimodal（需查詢）
UPDATE papers SET year = 2018 WHERE id = 24;  -- Research Article（需查詢）
UPDATE papers SET year = 2022 WHERE id = 30;  -- HCOMP2022（從標題確認）
UPDATE papers SET year = 2024 WHERE id = 36;  -- Human-Centred AI（需查詢）

.exit

# ===== 階段 3: 關鍵詞修復 =====

# 3.1 測試自動修復（前 5 篇）
python fix_metadata.py --batch --field keywords --limit 5 --dry-run

# 3.2 如果效果好，批次修復
python fix_metadata.py --batch --field keywords

# 3.3 或使用 SQL 批次更新（從摘要提取）
sqlite3 knowledge_base/index.db < update_keywords.sql

# ===== 階段 4: 質量檢查 =====

# 4.1 檢查所有論文質量
python check_quality.py --min-score 60

# 4.2 生成詳細報告
python check_quality.py --detail comprehensive --output quality_report_fixed.txt

# 4.3 檢查重複論文
python check_quality.py --detect-duplicates --threshold 0.85
```

---

## 📝 手動編輯指引

### 方法 1: 編輯 Markdown YAML Front Matter

```bash
# 1. 找到論文文件
cd knowledge_base/papers

# 2. 編輯 Markdown 文件（以論文 5 為例）
vim 華語分類詞的界定與教學上的分級_1.md

# 3. 修改 YAML front matter
---
title: 華語分類詞的界定與教學上的分級
authors: ["陳羿如", "何萬順"]
year: 2020  # 修改這裡
keywords: ["量詞", "分類詞", "對外華語教學", "教學分級"]  # 修改這裡
created: 2025-10-29 15:49:05
---

# 4. 保存後，重新導入知識庫（可選）
# analyze_paper.py 會自動更新數據庫
```

### 方法 2: 直接更新 SQLite 數據庫

```bash
# 1. 打開數據庫
sqlite3 knowledge_base/index.db

# 2. 查看論文資訊
SELECT id, title, year, keywords FROM papers WHERE id = 5;

# 3. 更新單個字段
UPDATE papers SET year = 2020 WHERE id = 5;

# 4. 更新多個字段
UPDATE papers SET
  year = 2020,
  keywords = '["量詞", "分類詞", "華語教學", "教學分級"]',
  abstract = '分類詞對於華語學習者是極具挑戰的...'
WHERE id = 5;

# 5. 批次更新多篇論文
UPDATE papers SET year = 2022 WHERE id IN (8, 13, 26, 30);

# 6. 檢查更新結果
SELECT id, title, year FROM papers WHERE year IS NOT NULL ORDER BY id;

# 7. 退出
.exit
```

### 方法 3: 使用 Python 腳本批次更新

創建 `batch_update_metadata.py`:

```python
#!/usr/bin/env python3
import sqlite3

# 批次更新字典
updates = {
    5: {'year': 2020, 'keywords': '["量詞", "分類詞", "華語教學"]'},
    7: {'year': 2015, 'keywords': '["NLP", "Chinese", "computational linguistics"]'},
    11: {'year': 2021},
    12: {'year': 2012},
    17: {'year': 2024, 'keywords': '["multimodal LLM", "embodiment", "grounding"]'},
    24: {'year': 2018},
    30: {'year': 2022, 'keywords': '["crowdsourcing", "human computation"]'},
    36: {'year': 2024},
}

db = sqlite3.connect('knowledge_base/index.db')
cursor = db.cursor()

for paper_id, data in updates.items():
    sets = []
    params = []

    if 'year' in data:
        sets.append('year = ?')
        params.append(data['year'])
    if 'keywords' in data:
        sets.append('keywords = ?')
        params.append(data['keywords'])
    if 'abstract' in data:
        sets.append('abstract = ?')
        params.append(data['abstract'])

    if sets:
        sql = f"UPDATE papers SET {', '.join(sets)} WHERE id = ?"
        params.append(paper_id)
        cursor.execute(sql, params)
        print(f"✅ 更新論文 {paper_id}")

db.commit()
db.close()
print("\n🎉 批次更新完成！")
```

執行:
```bash
python batch_update_metadata.py
```

---

## 📊 修復後檢查清單

完成修復後，執行以下檢查：

```bash
# ☐ 1. 質量檢查
python check_quality.py --min-score 60

# ☐ 2. 統計改善情況
python -c "
import sqlite3
db = sqlite3.connect('knowledge_base/index.db')
cursor = db.cursor()

cursor.execute('SELECT COUNT(*) FROM papers WHERE year IS NOT NULL')
year_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM papers WHERE keywords IS NOT NULL AND keywords != \"[]\"')
keywords_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM papers WHERE abstract IS NOT NULL AND LENGTH(abstract) > 50')
abstract_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM papers')
total = cursor.fetchone()[0]

print(f'年份完整率: {year_count}/{total} = {year_count/total:.1%}')
print(f'關鍵詞完整率: {keywords_count}/{total} = {keywords_count/total:.1%}')
print(f'摘要完整率: {abstract_count}/{total} = {abstract_count/total:.1%}')

db.close()
"

# ☐ 3. 重新執行向量生成（如果修復了大量論文）
python generate_embeddings.py --provider gemini --papers-only --yes

# ☐ 4. 重新建立自動連結
python kb_manage.py auto-link-all --threshold 0.5 --max-links 10

# ☐ 5. 測試語義搜索
python kb_manage.py semantic-search "認知科學" --limit 5
```

---

## 🎯 預期成果

完成所有修復後，知識庫質量應達到：

| 指標 | 修復前 | 目標 | 說明 |
|------|--------|------|------|
| 年份完整率 | 3.2% | **100%** | 所有論文都應有年份 |
| 關鍵詞完整率 | 35.5% | **>= 80%** | 大部分論文應有關鍵詞 |
| 摘要完整率 | 51.6% | **>= 70%** | 多數論文應有摘要 |
| 平均質量分 | 68.2 | **>= 75** | 從「可接受」提升至「良好」 |

---

## 📚 參考資源

### 查詢工具
- **Google Scholar**: https://scholar.google.com/
- **CrossRef API**: https://api.crossref.org/works/{DOI}
- **Semantic Scholar**: https://www.semanticscholar.org/

### 相關文檔
- `fix_metadata.py`: 自動修復工具
- `METADATA_REPAIR_GUIDE.md`: 完整使用指南
- `check_quality.py`: 質量檢查工具
- `OPTIMIZATION_REPORT_20251101.md`: 優化報告

---

**修復計劃版本**: 1.0
**生成時間**: 2025-11-01
**下一步**: 執行階段 1 批次自動修復
