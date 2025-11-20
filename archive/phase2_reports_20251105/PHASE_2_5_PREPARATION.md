# Phase 2.5 準備文件

**日期**: 2025-11-04 18:30
**狀態**: 準備開始
**前置條件**: Phase 2.4 完成並清理

---

## 📋 Phase 2.4 完成摘要

### 主要成就 ⭐⭐⭐⭐⭐

**元數據完整性**:
- ✅ cite_key 覆蓋率：**100%** (63/63 papers)
- ✅ 從 Phase 2.3 的 72% 提升至 100%

**Zettelkasten 生成**:
- ✅ 論文覆蓋率：**96.8%** (61/63 papers)
- ✅ 從 Phase 2.3 的 61% 提升至 96.8%
- ✅ 總卡片數：**777 張**
- ✅ 活躍資料夾：**61 個**

**系統清理**:
- ✅ 移動 40 個 Phase 2.3/2.4 臨時檔案到 `archive/completed_phases/`
- ✅ 刪除 30 個重複/過時的 Zettel 資料夾
- ✅ 刪除兩個 archive 資料夾（備份已壓縮為 0.51 MB）
- ✅ Git commit 完成：1474 files changed

### 最終目錄結構

```
output/zettelkasten_notes/
├── zettel_*_20251104/              # 58 個 (11/04 新生成)
├── zettel_Research_20251103/       # 1 個 (11/03)
├── zettel_Altmann2019_20251029/    # 保留 (Paper 38)
├── zettel_Setic2017_20251029/      # 保留 (Paper 42)
└── zettel_Allassonniere2021_20251029/  # 保留 (Paper 43)

archive/
├── completed_phases/               # 40 個 Phase 2.3/2.4 檔案
│   ├── batch_b1_reports/
│   ├── cleanup_reports/
│   ├── execution_docs/
│   ├── feature_logs/
│   ├── phase2_summaries/
│   ├── temp_files/
│   └── zotero_import/
└── archive_old_zettel_folders_20251104_174010.zip  # 22 個舊資料夾
```

### 未解決問題

**3 篇論文無 Zettelkasten** (6.3%):
- Paper 39: Guest-2025b
- Paper 40: Her-2012
- Paper 41: Jones-2024

*註：Papers 38, 42, 43 保留 10/29 舊版本*

---

## 🎯 Phase 2.5 目標

### 優先級 1: Relation Finder（自動關聯系統）⭐⭐⭐⭐⭐

**目標**: 建立論文-Zettelkasten 自動連結系統

**核心功能**:
1. **基於 cite_key 的自動關聯**
   - 解析 Zettel 卡片 ID（如 `Her-2012b-001`）
   - 匹配資料庫中的 paper_id
   - 更新 `zettel_cards.paper_id` 欄位

2. **概念網絡建立**
   - 創建 `concepts` 表
   - 創建 `concept_papers` 關聯表
   - 從 Zettel 標籤提取概念

3. **關係視覺化**
   - 生成論文-Zettel 連結圖
   - 生成概念共現網絡
   - 更新 `output/relations/` 目錄

**預期成果**:
- 61 個 Zettel 資料夾自動關聯到論文
- 提取 200+ 個獨特概念
- 生成 3 個關係圖表

**預計時間**: 2-3 小時

---

### 優先級 2: 處理剩餘 3 篇無 Zettel 的論文 ⭐⭐⭐

**論文列表**:
- Paper 39: Guest-2025b - "What Does 'Human-Centred AI' Mean?"
- Paper 40: Her-2012 - "Classifiers: The many ways to profile 'one'"
- Paper 41: Jones-2024 - "Multimodal Language Models"

**策略**:
1. 檢查論文 Markdown 內容完整性
2. 嘗試不同 LLM 模型（Gemini 2.0 Flash vs 1.5 Pro）
3. 調整生成參數（detail level, card count）
4. 如持續失敗，接受 96.8% 覆蓋率

**預計時間**: 1 小時

---

### 優先級 3: 元數據完整性提升 ⭐⭐

**任務**:
1. 補充 33 篇論文的年份資訊（51.6% 缺失）
2. 使用 `check_quality.py` 進行全面檢查
3. 修復摘要和關鍵詞缺失問題

**方法**:
- 從 PDF metadata 提取
- 從 DOI 查詢（CrossRef API）
- 從標題查詢（Semantic Scholar API）

**預計時間**: 1-2 小時

---

## ⚠️ 重要注意事項

### 1. Mermaid 節點已修復

**狀態**: ✅ 已在 Phase 2.4 修復

**修復內容**:
- 模板 `zettelkasten_index.jinja2` 第 29 行已加入 `replace('"', "'")`
- 未來生成的卡片自動正確
- 3 個保留的舊資料夾（Papers 38, 42, 43）無雙引號問題

**結論**: Phase 2.5 不需處理 Mermaid 相關問題

---

### 2. 資料庫狀態

**數據表現狀**:
| 表名 | 記錄數 | 狀態 |
|------|--------|------|
| `papers` | 63 | ✅ 完整 |
| `zettel_cards` | 777 | ✅ 完整 |
| `concepts` | 0 | ⚠️ 待建立 |
| `concept_papers` | 0 | ⚠️ 待建立 |

**欄位完整性**:
- `papers.cite_key`: 100% (63/63)
- `papers.year`: 48.4% (約 30/63) ⚠️
- `zettel_cards.paper_id`: 0% (0/777) ⚠️ **Phase 2.5 優先處理**

---

### 3. 向量搜索系統 (Phase 1.5)

**狀態**: ✅ 已完成（2025-11-03）

**可用功能**:
- `kb_manage.py semantic-search`: 語義搜索論文和卡片
- `kb_manage.py similar`: 尋找相似內容
- `kb_manage.py hybrid-search`: 混合搜索（FTS + 向量）

**ChromaDB 狀態**:
- 論文向量：31 個
- Zettel 向量：52 個
- 總向量：83 個

**注意**: 新增論文或 Zettel 後需重新生成向量嵌入

---

### 4. 自動模型選擇系統 (Phase 2.4.1)

**狀態**: ✅ 已完成（2025-10-31）

**配置文件**: `config/model_selection.yaml`

**可用策略**:
- `balanced`: 平衡成本和質量（默認）
- `quality_first`: 優先品質（使用 Gemini 1.5 Pro）
- `cost_first`: 優先成本（使用 Gemini 2.0 Flash）
- `speed_first`: 優先速度（使用 Claude 3 Haiku）

**成本追蹤**: 已啟用，日誌存於 `logs/model_usage/`

---

## 🔧 技術考量

### Relation Finder 實作建議

**資料庫設計**:
```sql
-- 已存在的表
CREATE TABLE IF NOT EXISTS zettel_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id TEXT UNIQUE NOT NULL,  -- 如 "Her-2012b-001"
    paper_id INTEGER,               -- 外鍵，待填充
    title TEXT,
    content TEXT,
    tags TEXT,  -- JSON array
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

-- 需要新增的表
CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT,  -- 可選分類
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS concept_papers (
    concept_id INTEGER,
    paper_id INTEGER,
    frequency INTEGER DEFAULT 1,
    PRIMARY KEY (concept_id, paper_id),
    FOREIGN KEY (concept_id) REFERENCES concepts(id),
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

CREATE TABLE IF NOT EXISTS concept_zettel (
    concept_id INTEGER,
    zettel_card_id INTEGER,
    PRIMARY KEY (concept_id, zettel_card_id),
    FOREIGN KEY (concept_id) REFERENCES concepts(id),
    FOREIGN KEY (zettel_card_id) REFERENCES zettel_cards(id)
);
```

**關聯算法**:
```python
def link_zettel_to_paper(card_id: str, db_manager):
    """
    從 card_id 提取 cite_key 並關聯到論文

    示例:
    - "Her-2012b-001" → cite_key="Her-2012b"
    - "CogSci-20251104-005" → cite_key="Research" (舊格式，需特殊處理)
    """
    parts = card_id.split('-')

    if len(parts) >= 3:
        # 新格式: Author-Year-Number
        cite_key = '-'.join(parts[:-1])
    else:
        # 舊格式: Domain-Date-Number
        # 需要從資料夾名稱推斷
        folder_name = get_folder_name(card_id)
        cite_key = extract_cite_key_from_folder(folder_name)

    paper = db_manager.get_paper_by_cite_key(cite_key)
    if paper:
        db_manager.update_zettel_paper_id(card_id, paper['id'])
        return True
    return False
```

**概念提取**:
```python
def extract_concepts_from_zettel(zettel_cards):
    """
    從 Zettel 標籤提取概念

    策略:
    1. 解析 tags JSON 欄位
    2. 標準化概念名稱（小寫、去重）
    3. 建立 concept -> papers/zettel 映射
    """
    concepts = {}
    for card in zettel_cards:
        tags = json.loads(card['tags'])
        for tag in tags:
            normalized = normalize_concept(tag)
            if normalized not in concepts:
                concepts[normalized] = {'papers': set(), 'zettel': set()}
            concepts[normalized]['zettel'].add(card['id'])
            if card['paper_id']:
                concepts[normalized]['papers'].add(card['paper_id'])

    return concepts
```

---

## 📊 成功指標

Phase 2.5 完成時應達到：

**必達指標** (P0):
- ✅ 777 張 Zettel 卡片關聯到對應論文（paper_id 填充率 100%）
- ✅ 創建 concepts 表並提取 200+ 概念
- ✅ 生成關係圖表（論文-Zettel 網絡、概念共現）

**期望指標** (P1):
- 🎯 3 篇失敗論文重新生成成功（覆蓋率 → 100%）
- 🎯 補充年份資訊（缺失率 51.6% → <20%）

**額外指標** (P2):
- 📈 整合向量搜索到 Relation Finder
- 📈 創建互動式視覺化網頁

---

## 📁 參考文件

**Phase 2.4 相關** (已歸檔):
- `archive/completed_phases/PHASE2_4_COMPLETION_REPORT.md`
- `archive/completed_phases/PHASE2_4_FINAL_ASSESSMENT.md`
- `archive/completed_phases/CLEANUP_COMPLETE_SUMMARY.md`

**Phase 2.5 規劃**:
- `PHASE2_REVISED_ROADMAP.md` - Phase 2 整體路線圖
- `src/analyzers/relation_finder.py` - 關聯查找器（待完成）
- `src/knowledge_base/kb_manager.py` - 知識庫管理器（需擴展）

**技術文檔**:
- `CLAUDE.md` - 系統完整文檔
- `templates/markdown/zettelkasten_index.jinja2` - Zettel 索引模板

---

## ✅ 開始前檢查清單

在開始 Phase 2.5 之前，請確認：

- [x] Phase 2.4 Git commit 完成
- [x] 清理工作完成（archive 已整理）
- [x] 知識庫備份存在（`knowledge_base/backups/`）
- [x] 61 個 Zettel 資料夾結構完整
- [x] 資料庫可正常訪問（`knowledge_base/index.db`）
- [x] 向量搜索系統正常運作（ChromaDB）

---

## 🚀 啟動 Phase 2.5

**命令**:
```bash
# 檢查資料庫狀態
python kb_manage.py stats

# 啟動 Relation Finder 開發
# (待實作)

# 測試概念提取
# (待實作)
```

**預計總時間**: 4-6 小時

**建議分段執行**:
1. **Session 1** (2-3 小時): Relation Finder 核心功能
2. **Session 2** (1 小時): 失敗論文處理
3. **Session 3** (1-2 小時): 元數據完整性與質量檢查

---

**文件生成時間**: 2025-11-04 18:30
**Phase 2.4 狀態**: ✅ **完成並清理**
**Phase 2.5 狀態**: 🟡 **準備就緒，待開始**

---

## 💡 開發者提示

1. **優先處理 paper_id 關聯**
   - 這是 Relation Finder 的基礎
   - 影響所有後續關係分析

2. **漸進式測試**
   - 先處理 10 個 Zettel 驗證算法
   - 再批次處理全部 777 張

3. **錯誤處理**
   - 記錄無法關聯的 card_id
   - 提供人工修正介面

4. **向量搜索整合**
   - Relation Finder 可利用語義相似度
   - 發現跨論文的概念連結

5. **文檔更新**
   - 完成後更新 `CLAUDE.md`
   - 記錄 Phase 2.5 成果到新報告

---

**準備完成！Phase 2.5 可以開始了** 🎉


# 用戶建議

- 在zettel_index模板增加YAML欄位 `aliases` 預設置入bibtext key/cite_key ，此項目可增加Obsidian Vault檔案內連結效率，方便人類用戶在卡片筆記撰寫自已洞察的文獻內連結。此更新會如何影響由Phase 2.5開始的開發事項？
- (回覆方案A) 1- zettel模板檔案只要 "zettelkasten_index.jinja2" 增加aliases欄位，"zettelkasten_card.jinja2"不需變動，實作可用Obsidian內部語法串連; 2- alieases 欄位只要放置純文字cite_key，不需要放置 [] 或其他引號。 
- (再覆方案A)見以下YAML模板 for "templates/markdown/zettelkasten_index.jinja2"
```
{% for card in cards %}
  ### {{ loop.index }}. [{{ card.title }}](zettel_cards/{{ card.id }}.md)
  - **ID**: `{{ card.id }}`
  - aliases: {{ cite_key }}  ## Obsidian 相容格式
  - **類型**: {{ card.type }}
  - **核心**: {{ card.core_summary }}
  - **標籤**: {% for tag in card.tags %}`{{ tag }}`{% if not loop.last %}, {% endif %}{% endfor %}
```