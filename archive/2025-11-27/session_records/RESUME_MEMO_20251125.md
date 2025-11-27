# Resume Memo - 2025-11-25

## 本次工作摘要

### 完成項目

#### 1. Zettelkasten 卡片生成
- **Barsalou-1999**: 20 張卡片 ✅
  - 位置: `output/zettelkasten_notes/zettel_Barsalou-1999_20251125_gemini_2.0_flash_exp/`
  - 主題: Perceptual Symbol Systems（知覺符號系統）

- **Friedrich-2025**: 20 張卡片 ✅
  - 位置: `output/zettelkasten_notes/zettel_Friedrich-2025_20251125_gemini_2.0_flash_exp/`
  - 主題: Issues in Grounded Cognition - Minimalist Account

#### 2. 知識庫一致性修復
- 問題: 23 篇論文的 `cite_key` 全部為 NULL
- 修復: 建立所有 Zettel 資料夾與知識庫論文的對應關係
- 結果: 23/23 完全匹配 ✅

#### 3. Citekey 命名一致性修復
- 問題: `zettel_index.md` 的 `title` 使用論文標題而非 citekey
- 修復:
  - 更新模板 `templates/markdown/zettelkasten_index.jinja2`
  - 批次更新 Barsalou-1999 和 Friedrich-2025 的 zettel_index.md
- 新增 `paper_title` 欄位保留原始論文標題

---

## 待處理問題

### 🔴 高優先級

#### 1. Barsalou-1999 paper_title 錯誤
- **目前值**: `"BEHAVIORAL AND BRAIN SCIENCES(1999) 22,577–660"`（期刊資訊）
- **正確值**: `"Perceptual symbol systems"`
- **可能原因**:
  - PDF 提取時抓到期刊標頭而非論文標題
  - BibTeX 解析問題
- **待辦**: 檢查 BibTeX 整合流程，確保正確提取論文標題

### 🟡 中優先級

#### 2. 其他論文元數據品質
- 多數知識庫論文的標題是從 PDF 提取，品質參差不齊
- 建議: 優先使用 BibTeX 資料作為元數據來源

---

## 知識庫狀態

| 項目 | 數量 |
|------|------|
| 論文總數 | 23 |
| Zettel 資料夾 | 23 |
| cite_key 對應 | 23/23 ✅ |

---

## 修改的檔案

| 檔案 | 修改內容 |
|------|----------|
| `templates/markdown/zettelkasten_index.jinja2` | title 改用 cite_key，新增 paper_title 欄位 |
| `knowledge_base/index.db` | 更新 23 篇論文的 cite_key |
| `output/.../zettel_Barsalou-1999_.../zettel_index.md` | frontmatter 修正 |
| `output/.../zettel_Friedrich-2025_.../zettel_index.md` | frontmatter 修正 |

---

## 下次繼續

1. 檢查 BibTeX 整合流程（`src/integrations/bibtex_parser.py`）
2. 修正 Barsalou-1999 的 paper_title
3. 考慮建立元數據品質檢查的自動化流程

---

*Generated: 2025-11-25 16:30*
