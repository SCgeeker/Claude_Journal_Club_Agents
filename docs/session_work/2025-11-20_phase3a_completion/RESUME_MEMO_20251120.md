# Phase 3A Pilot - Session Resume Memo

**Date**: 2025-11-20
**Session End Time**: ~17:15
**Status**: Test 2 完成，等待執行完整 Pilot

---

## 📊 當前進度

### 已完成測試

#### Test 1 (Single Paper) ✅
- **論文**: Adams-2020
- **時間**: 1:04
- **結果**: 18 張卡片生成（17 張重複，1 張新增）
- **問題**: Path import bug（已修復）
- **成本**: ~$0.10
- **Paper ID**: 7

#### Test 2 (3-Paper Batch) ✅
- **論文**: Baruch-2016, Créquit-2018, Hosseini-2015
- **時間**: 2:12
- **結果**: 60 張卡片生成（全部新增）
- **Papers ID**: 8, 9, 10
- **成本**: ~$0.30
- **關鍵驗證**:
  - ✅ 特殊字符處理 (Créquit é→e)
  - ✅ 併發處理 (workers=2)
  - ✅ 資料完整性 (60/60 導入)

### 累積統計

- **已處理**: 4 篇論文
- **剩餘**: 8 篇論文
- **累積成本**: ~$0.40
- **知識庫**: 10 篇 Papers，~205 張 Zettel cards

---

## 🎯 下一步執行計畫

### 立即任務: 執行完整 Phase 3A Pilot

**目標**: 處理剩餘 8 篇論文

**論文清單**:
1. Khazanchi-2019
2. LeeYoung-2020
3. Li-2017
4. Peer-2014
5. Peer-2017
6. Saito-2021
7. Salehi-2015
8. Tran-2021

**執行命令**:
```bash
cd "D:\core\research\claude_lit_workflow"

# Step 1: 提取剩餘 8 篇的 cite keys
tail -8 pilot_cite_keys_psycho_crowdsourcing.txt > pilot_batch_remaining.txt

# Step 2: 提取 BibTeX 子集
python extract_bibtex_subset.py \
  --cite-keys pilot_batch_remaining.txt \
  --output pilot_batch_remaining.bib

# Step 3: 執行批次處理
python batch_process.py \
  --from-bibtex pilot_batch_remaining.bib \
  --pdf-index pdf_index.json \
  --domain "Psycho Studies on crowdsourcing" \
  --add-to-kb \
  --generate-zettel \
  --cards 20 \
  --detail detailed \
  --llm-provider google \
  --model gemini-2.0-flash-exp \
  --workers 3 \
  --error-handling skip \
  --report output/pilot_full_report.json
```

**預期**:
- 時間: 8-10 分鐘
- 成本: ~$0.80
- 輸出: 160 張 Zettelkasten 卡片
- Papers ID: 11-18

---

## 📋 Phase 3A 完成後的任務

### 1. 驗證輸出品質

```bash
# 檢查知識庫狀態
python check_db.py

# 應該顯示:
# - Total papers: 18 (10 現有 + 8 新增)
# - Total cards: ~365 (205 現有 + 160 新增)
```

### 2. 生成 Concept Network 和 MOC

```bash
cd "D:\core\research\claude_lit_workflow"

# 生成概念網絡分析（包含 Obsidian 格式）
python kb_manage.py visualize-network --obsidian \
  --output output/concept_analysis_pilot \
  --min-confidence 0.4 \
  --top-n 50 \
  --moc-top 20
```

**預期輸出**:
- `output/concept_analysis_pilot/`
  - `concept_network.html` (D3.js 互動圖)
  - `concept_network.dot` (Graphviz)
  - `analysis_report.md`
  - `obsidian/` (Obsidian 友好格式)
    - `suggested_links.md` (智能連結建議)
    - `key_concepts_moc.md` (核心概念地圖)
    - `community_summaries/` (社群摘要)

### 3. 比較生成 MOC 與原始 Connection Note

**原始 Connection Note**: `D:\core\research\Program_verse\ACT\1️⃣Conn\🔗Psycho Studies on crowdsourcing.md`

**比較重點**:
1. **覆蓋範圍**: MOC 是否涵蓋所有 12 篇論文的核心概念？
2. **連結品質**: 建議連結是否合理、有意義？
3. **概念組織**: 社群檢測的分組是否符合領域邏輯？
4. **實用性**: MOC 能否取代或輔助手動 Connection notes？

### 4. 決定下一步行動

**Option A**: 基於 Pilot 成功，擴展到更多 Connection notes
- 選擇下一個 Connection note (10-20 篇論文)
- 重複 Phase 3A 流程

**Option B**: 優化和改進
- 根據 MOC 比較結果調整參數
- 改進 RelationFinder (Phase 2.4 設計)
- 優化 Prompt 模板

**Option C**: 整合到 Obsidian
- 將生成的 Papers 和 Zettelkasten 移動到 `Program_verse/Atlas/Sources/`
- 設定 Obsidian vault 路徑
- 測試 Wiki Links 和 Graph View

---

## 🔧 已完成的工具和修復

### 核心工具 (Phase 3)

1. ✅ **build_pdf_index.py**
   - 掃描 PDF 目錄
   - 建立 cite_key → PDF path 映射
   - 支援特殊字符 normalization
   - 輸出: `pdf_index.json` (2,703 entries)

2. ✅ **extract_bibtex_subset.py**
   - 從大型 BibTeX 提取子集
   - 基於 cite_key 列表
   - 輸出: 小型 BibTeX 文件

3. ✅ **test_pdf_resolution.py**
   - 測試 PDF 路徑解析
   - Hybrid Path Strategy 驗證
   - 輸出: 解析報告 JSON

4. ✅ **batch_process.py** (Enhanced)
   - 新增 `--from-bibtex` 參數
   - 新增 `--pdf-index` 參數
   - 新增 `--pdf-base-dir` 參數
   - 修復 Path import bug

### 測試工具

5. ✅ **verify_pilot_papers.py**
   - 驗證 PDF 和 BibTeX 可用性
   - 特殊字符處理
   - 100% 驗證率

6. ✅ **check_db.py**
   - 快速查詢知識庫統計

### 文檔

7. ✅ **PHASE3A_EXECUTION_SUMMARY.md** (1000+ 行)
   - 完整執行計畫
   - 風險評估
   - 測試選項

8. ✅ **TEST1_SUMMARY_20251120.md** (1000+ 行)
   - Test 1 詳細報告
   - 問題分析和修復

9. ✅ **TEST2_SUMMARY_20251120.md** (400+ 行)
   - Test 2 詳細報告
   - 下一步建議

---

## 🐛 已修復的問題

### Issue 1: Path Import Error ✅
**問題**: `UnboundLocalError: cannot access local variable 'Path'`
**位置**: `batch_process.py:289`
**原因**: Path 在條件分支內導入，報告保存時不在作用域
**修復**: 在所有輸入分支後統一導入 Path

```python
# batch_process.py:249
from pathlib import Path  # 移到所有分支後
```

### Issue 2: 特殊字符 PDF 解析 ✅
**問題**: Créquit-2018 PDF 無法從 BibTeX cite key 解析
**原因**: BibTeX 規範化 (é→e) vs 文件系統保留原始字符
**修復**:
- `build_pdf_index.py`: 同時索引 normalized 和 original cite keys
- `verify_pilot_papers.py`: denormalize_for_filesystem() 函數
- Hybrid Path Strategy 支援多種命名變體

---

## 📁 關鍵文件位置

### 配置和索引
```
D:\core\research\claude_lit_workflow\
├── pdf_index.json              # PDF 索引 (2,703 entries)
├── pilot_batch.bib             # 完整 12 篇 BibTeX
├── pilot_cite_keys_psycho_crowdsourcing.txt  # Cite keys 列表
├── test_single.bib             # Test 1 BibTeX
├── test_batch_3.bib            # Test 2 BibTeX
└── pilot_batch_remaining.txt   # 待建立 (剩餘 8 篇)
```

### 輸出目錄
```
D:\core\research\claude_lit_workflow\
├── knowledge_base/
│   ├── index.db                # SQLite 資料庫
│   └── papers/
│       ├── Adams-2020.md
│       ├── Baruch-2016.md
│       ├── Créquit-2018.md
│       └── Hosseini-2015.md
├── output/
│   ├── zettelkasten_notes/
│   │   ├── zettel_Adams-2020_20251120/
│   │   ├── zettel_Baruch-2016_20251120/
│   │   ├── zettel_Créquit-2018_20251120/
│   │   └── zettel_Hosseini-2015_20251120/
│   ├── test_single_report.json
│   └── test_batch_3_report.json
```

### 源數據
```
D:\core\research\Program_verse\
├── +/
│   ├── pdf/                    # 3,013 PDFs
│   └── My Library.bib          # 6,843 entries
├── ACT/
│   ├── 1️⃣Conn/
│   │   └── 🔗Psycho Studies on crowdsourcing.md
│   └── 0️⃣Annotation/
│       └── @*.md               # Annotation notes
```

---

## ⚙️ 系統配置

### LLM 設定
```yaml
Provider: Google Gemini
Model: gemini-2.0-flash-exp
API Key: GOOGLE_API_KEY (環境變數)
Cost: ~$0.10/paper (20 cards)
```

### 批次處理參數
```yaml
cards: 20                # Zettelkasten 卡片數
detail: detailed         # 詳細程度
workers: 3               # 併發執行緒 (建議 2-4)
error-handling: skip     # 錯誤策略
domain: "Psycho Studies on crowdsourcing"
```

### 資料庫狀態
```
Papers: 10 (目標 18)
Zettel Cards: ~205 (目標 ~365)
```

---

## 🎯 Session Resume Checklist

當新 session 開始時，按以下步驟執行：

### 1. 確認環境
```bash
cd "D:\core\research\claude_lit_workflow"
ls -la pdf_index.json pilot_batch.bib
python check_db.py
```

### 2. 回顧進度
- [ ] 閱讀此文件 (RESUME_MEMO_20251120.md)
- [ ] 檢查 TEST2_SUMMARY_20251120.md
- [ ] 確認 Test 2 成功完成

### 3. 執行剩餘 Pilot
- [ ] 建立 pilot_batch_remaining.txt (tail -8)
- [ ] 提取 BibTeX (extract_bibtex_subset.py)
- [ ] 執行批次處理 (batch_process.py)
- [ ] 監控成本和進度

### 4. 後續分析
- [ ] 執行 Concept Network 分析
- [ ] 生成 Obsidian MOC
- [ ] 比較 MOC vs 原始 Connection note
- [ ] 決定下一步行動

---

## 💡 重要提醒

1. **成本監控**: 每次執行前確認 API quota，累積成本 ~$0.40
2. **資料備份**: 完整 Pilot 前可選擇備份 knowledge_base/index.db
3. **併發限制**: workers=3 適合，避免 API rate limiting
4. **特殊字符**: Créquit 等特殊字符已驗證可正常處理
5. **防重複機制**: 資料庫 UNIQUE 約束防止重複導入

---

**Last Updated**: 2025-11-20 17:15
**Next Action**: 執行剩餘 8 篇論文的完整 Pilot
**Estimated Time**: 8-10 分鐘
**Estimated Cost**: ~$0.80
**Status**: ⏸️ Ready to Resume
