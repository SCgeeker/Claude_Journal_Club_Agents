# 知識庫元數據質量報告

**生成時間**: D:\core\research\claude_lit_workflow
**資料庫**: knowledge_base/index.db

---

## 📊 總覽

| 指標 | 數量 | 百分比 |
|------|------|--------|
| **總論文數** | 31 | 100% |
| **完整論文** | 3 | 9.7% |
| **缺少年份** | 0 | 0.0% |
| **缺少關鍵詞** | 16 | 51.6% |
| **缺少摘要** | 19 | 61.3% |
| **無效標題** | 2 | 6.5% |
| **檔案不存在** | 0 | 0.0% |

**整體質量分數**: -4/100

---

## ⚠️ 問題論文列表

共 28 篇論文有問題：


### ID 1: Taxonomy of Numeral Classifiers:

- ❌ 缺少摘要

### ID 2: Chinese Classifiers and Count Nouns

- ❌ 缺少摘要

### ID 4: Concepts in the Brain

- ❌ 缺少關鍵詞
- ❌ 缺少摘要

### ID 6: A single origin of numeral classifiers

- ❌ 缺少摘要

### ID 9: Classifiers

- ❌ 缺少關鍵詞

### ID 10: HuangLinguaSinica (2015) 1:1

- ❌ 缺少關鍵詞

### ID 13: JournalofMemoryandLanguage127(2022)104355

- ❌ 關鍵詞過少 (1個)
- ❌ 缺少摘要

### ID 14: Journal of Cognitive Psychology

- ❌ 缺少關鍵詞
- ❌ 缺少摘要

### ID 15: PsychonomicBulletin&Review

- ❌ 缺少關鍵詞

### ID 16: JournalofMemoryandLanguage135(2024)104478

- ❌ 關鍵詞過少 (1個)
- ❌ 缺少摘要

### ID 18: Memory&Cognition(2020)48:390–399

- ❌ 缺少關鍵詞

### ID 19: Cognitive Processing

- ❌ 缺少關鍵詞

### ID 20: Cognition 182 (2019) 84–94

- ❌ 關鍵詞過少 (1個)

### ID 21: This article was downloaded by: [134.117.10.200]

- ❌ 缺少摘要
- ❌ 無效標題

### ID 22: JOURNAL OF VERBAL LEARNING AND VERBAL BEHAVIOR 18,

- ❌ 缺少關鍵詞
- ❌ 缺少摘要

### ID 23: Psychological Science

- ❌ 缺少關鍵詞
- ❌ 缺少摘要

### ID 25: Memory & Cognition

- ❌ 缺少關鍵詞

### ID 26: Educational Psychology

- ❌ 缺少關鍵詞
- ❌ 缺少摘要

### ID 27: Journal Pre-proof

- ❌ 無效標題

### ID 28: Revisiting Mental Simulation in Language

- ❌ 缺少關鍵詞

### ID 29: PsychonBullRev(2018)25:1968–1972

- ❌ 缺少關鍵詞
- ❌ 缺少摘要

### ID 37: Goal-Setting Behavior of Workers on Crowdsourcing 

- ❌ 缺少關鍵詞
- ❌ 缺少摘要

### ID 38: “Events as intersecting object histories: A new th

- ❌ 關鍵詞過少 (1個)
- ❌ 缺少摘要

### ID 39: What Does ‘Human-Centred AI’ Mean?

- ❌ 關鍵詞過少 (1個)
- ❌ 缺少摘要

### ID 40: Classifiers: The many ways to profile 'one', a cas

- ❌ 缺少關鍵詞
- ❌ 缺少摘要

### ID 41: Multimodal Language Models Show Evidence of Embodi

- ❌ 缺少摘要

### ID 42: Numerical congruency effect in the sentence-pictur

- ❌ 關鍵詞過少 (1個)
- ❌ 缺少摘要

### ID 43: Expansion by migration and diffusion by contact is

- ❌ 缺少關鍵詞
- ❌ 缺少摘要


---

## 💡 修復建議

### 立即行動

1. **修復缺少年份** (0 篇)
   ```bash
   python fix_metadata.py --batch --field year
   ```

2. **修復缺少關鍵詞** (16 篇)
   ```bash
   python llm_metadata_generator.py --batch --provider gemini
   ```

3. **修復缺少摘要** (19 篇)
   ```bash
   python llm_metadata_generator.py --batch --provider gemini
   ```

4. **清理檔案不存在的記錄** (0 篇)
   ```bash
   python cleanup_db.py --delete
   ```

### 預期改進

修復後預計質量分數可達到 **85+/100**

---

**報告生成工具**: generate_quality_report.py
