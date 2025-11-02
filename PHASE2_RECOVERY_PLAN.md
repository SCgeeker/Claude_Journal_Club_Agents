# Phase 2 恢復計畫 - 2025-11-02

**狀態**: 待啟動（前序依賴Phase 1.5已完成）
**恢復時間**: 2025-11-02
**優先級**: P1

---

## 📊 當前系統狀態快照

### Phase 1.5 完成成果（2025-11-01）
- ✅ 向量嵌入系統完成（31論文 + 52卡片 = 83向量）
- ✅ ChromaDB向量數據庫整合
- ✅ kb_manage.py 6個新命令：semantic-search, similar, hybrid-search, auto-link等
- ✅ 自動連結功能（基於向量相似度）
- ✅ 測試和準確性評估完成

### 未提交的更改
```
M AGENT_SKILL_DESIGN.md      # 文檔更新
M kb_manage.py               # Phase 1.5新增命令
M analyze_paper.py           # 可能的改進
M chroma_db/                 # 向量數據庫數據
M knowledge_base/papers/     # 知識庫更新
```

### 立即待辦
1. **提交Phase 1.5成果**：提交所有未提交的更改
2. **規劃Phase 2階段**：設計模組化架構
3. **開始實作relation-finder**：P1優先級

---

## 🎯 Phase 2 分階段計畫

### Phase 2.1: relation-finder (關係發現器) - 3-4天 ⭐ 優先

**目標**: 從知識庫論文和Zettelkasten中自動發現關係網絡

**核心功能**:
1. **引用關係抽取**: 基於向量相似度推測論文引用關係
2. **共同作者網絡**: 構建作者協作網絡
3. **概念共現分析**: 發現常見概念組合
4. **時間序列分析**: 論文發表時間線

**交付物**:
- `src/analyzers/relation_finder.py` (~400行)
- `src/analyzers/__init__.py`
- 單元測試 (`tests/test_relation_finder.py`)
- Skill文檔 (`.claude/skills/relation-finder.md`)

**主要類設計**:
```python
class RelationFinder:
    def find_citations(self, threshold=0.7) -> List[Citation]
    def find_co_authors(self) -> Dict[str, List[str]]
    def find_co_occurrence(self, min_freq=2) -> Dict[str, List[str]]
    def build_timeline(self) -> Dict[int, List[Paper]]
    def export_to_json(self, output_path) -> str
```

**技術實現**:
- 利用Phase 1.5的向量嵌入
- 計算論文之間的相似度
- 使用閾值識別潛在引用關係
- 從元數據提取作者和年份信息

**成功指標**:
- 發現 >50 個引用關係
- 構建 >30 人共同作者網絡
- 識別 >20 個概念簇
- 測試覆蓋 >80%

---

### Phase 2.2: concept-mapper (概念映射器) - 2-3天

**目標**: 構建知識領域的概念網絡圖

**核心功能**:
1. **概念提取**: 從論文摘要和卡片提取主要概念
2. **聚類分析**: 使用K-means或DBSCAN聚類相似概念
3. **圖譜構建**: 構建概念之間的關係圖
4. **可視化**: 生成Mermaid/GraphViz格式的圖表

**交付物**:
- `src/analyzers/concept_mapper.py` (~350行)
- 可視化輸出工具
- 測試套件

**主要類設計**:
```python
class ConceptMapper:
    def extract_concepts(self, papers: List[Paper]) -> List[Concept]
    def cluster_concepts(self, n_clusters=None) -> Dict[int, List[Concept]]
    def build_network(self) -> NetworkX.Graph
    def export_to_mermaid(self, output_path) -> str
    def export_to_graphviz(self, output_path) -> str
```

**技術實現**:
- 利用LLM提取概念（從論文摘要）
- 基於embedding相似度的聚類
- 計算概念之間的連接強度
- 生成多種圖表格式

---

### Phase 2.3: 元數據增強 - 4.5小時

**目標**: 從BibTeX和Zotero增強論文元數據

**核心功能**:
1. 從BibTeX文件導入高品質元數據
2. 從Zotero庫同步注釋和標籤
3. 更新DOI和URL信息
4. 增強關鍵詞和分類

**實現**:
- 使用既有的 `bibtex_parser.py` 和 `zotero_scanner.py`
- 整合到 `kb_manager.py`

---

### Phase 2.4: 測試補充 - 5天

**目標**: 為所有新功能添加完整的單元測試和集成測試

**測試類型**:
- 單元測試（relation-finder, concept-mapper）
- 集成測試（與kb_manager.py的交互）
- 準確性測試（成功率>80%）
- 性能測試（處理時間<5秒）

---

## 📋 優先實作順序

### 第1週（優先）
1. **提交Phase 1.5** (30分鐘)
   - git add / commit / push

2. **relation-finder實作** (3-4天)
   - 引用關係抽取
   - 共同作者網絡
   - 概念共現分析
   - 單元測試

3. **concept-mapper設計** (1天)
   - 架構設計
   - 概念提取邏輯

### 第2週
1. **concept-mapper實作** (2-3天)
2. **兩個模組的集成測試** (1-2天)
3. **文檔和Skill撰寫** (1天)

---

## 🔧 快速啟動指令

### 1. 檢查當前狀態
```bash
cd /d/core/research/claude_lit_workflow
git status
git diff --stat
```

### 2. 提交Phase 1.5
```bash
# 檢查要提交的檔案
git add AGENT_SKILL_DESIGN.md kb_manage.py analyze_paper.py
git add src/embeddings/ src/knowledge_base/

# 提交（示例）
git commit -m "feat(phase1.5): Complete vector search & auto-linking implementation"
git tag v1.1-phase1.5-complete
```

### 3. 創建Phase 2開發分支（可選）
```bash
git checkout -b feature/phase2-knowledge-organization
```

### 4. 開始relation-finder開發
```bash
# 創建模組結構
mkdir -p src/analyzers
touch src/analyzers/__init__.py
touch src/analyzers/relation_finder.py
touch tests/test_relation_finder.py

# 開始開發
code src/analyzers/relation_finder.py
```

---

## 📚 技術參考

### 依賴Phase 1.5的功能
- **向量嵌入**: 用於計算論文相似度
- **自動連結**: 已有auto_link_v2()實現
- **向量數據庫**: ChromaDB中的embeddings

### 新增依賴（如需要）
```bash
# 圖論和聚類
pip install networkx scikit-learn

# 可視化
pip install graphviz

# 其他
pip install tqdm colorama
```

---

## 📁 檔案結構更新

完成Phase 2.1-2.4後，預期新增以下檔案：

```
src/
├── analyzers/                    ✨ NEW
│   ├── __init__.py
│   ├── relation_finder.py        (400行)
│   └── concept_mapper.py         (350行)

.claude/
├── skills/
│   ├── relation-finder.md        ✨ NEW
│   └── concept-mapper.md         ✨ NEW

tests/
├── test_relation_finder.py       ✨ NEW
├── test_concept_mapper.py        ✨ NEW
└── test_data/
    └── sample_relations.json     ✨ NEW
```

---

## 🚀 下一步行動

### 立即（今天）
1. ✅ 提交Phase 1.5成果
2. ✅ 本恢復計畫文檔已創建
3. ⏳ 開始relation-finder設計

### 明日及之後
1. relation-finder實作（3-4天）
2. concept-mapper實作（2-3天）
3. 完整測試和文檔（3-5天）

---

**準備就緒！** 可以開始Phase 2開發。建議先提交Phase 1.5的成果，然後開始relation-finder的實作。

