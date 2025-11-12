# 📖 Obsidian 整合使用指南

**版本**: Phase 2.2
**更新日期**: 2025-11-05
**狀態**: ✅ 完整實作並測試

---

## 📋 目錄

1. [簡介](#簡介)
2. [功能概述](#功能概述)
3. [快速開始](#快速開始)
4. [詳細使用](#詳細使用)
5. [輸出文件說明](#輸出文件說明)
6. [在 Obsidian 中使用](#在-obsidian-中使用)
7. [參數調整](#參數調整)
8. [故障排除](#故障排除)
9. [實際範例](#實際範例)

---

## 簡介

Concept Mapper 的 Obsidian 整合功能（Phase 2.2）可以將 Zettelkasten 卡片之間的語義關係分析結果，自動轉換為 Obsidian 友好的 Markdown 格式，並生成互動式網絡視覺化。

### 主要優勢

- **無縫整合**: 生成的 Wiki Links 直接連接到 zettel_index.md 錨點，完美融入 Obsidian
- **智能推薦**: 基於向量相似度的概念連結建議（信度評分）
- **多層分析**: 社群檢測、中心性分析、路徑分析三位一體
- **視覺化**: D3.js 互動式網絡圖 + Graphviz DOT 格式
- **可調整**: 支援多種參數自定義（信度閾值、顯示數量等）

---

## 功能概述

### 生成的文件類型

| 文件名 | 類型 | 說明 |
|--------|------|------|
| `README.md` | 索引 | 快速導航所有生成文件 |
| `suggested_links.md` | 建議連結 | 基於語義相似度的智能連結推薦 |
| `key_concepts_moc.md` | 核心概念地圖 | Top 20 概念（PageRank）|
| `community_summaries/` | 社群摘要 | 概念社群檢測結果（Louvain 算法）|
| `path_analysis.md` | 路徑分析 | 概念演化和推導路徑 |
| `concept_network.html` | 互動視覺化 | D3.js 網絡圖（可縮放、點擊） |
| `concept_network.dot` | 圖檔來源 | Graphviz DOT 格式（可轉 PNG） |

### Wiki Links 格式

所有生成的連結使用錨點格式，指向 `zettel_index.md` 的特定條目：

```markdown
[[zettel_Abbas-2022_20251104/zettel_index#1. [目標設定理論](zettel_cards/Abbas-2022-001.md)|目標設定理論]]
```

---

## 快速開始

### 方法 1：使用 CLI（推薦）

```bash
# 基本使用（生成所有分析結果 + Obsidian 格式）
python kb_manage.py visualize-network --obsidian

# 自定義輸出目錄
python kb_manage.py visualize-network --obsidian --output my_analysis

# 調整參數
python kb_manage.py visualize-network --obsidian \
    --min-confidence 0.35 \
    --top-n 100 \
    --moc-top 30
```

### 方法 2：直接運行 Python 模組

```bash
# 運行測試（concept_mapper.py 已啟用 obsidian_mode）
python src/analyzers/concept_mapper.py
```

### 方法 3：Python API

```python
from src.analyzers.concept_mapper import ConceptMapper

mapper = ConceptMapper()

results = mapper.analyze_all(
    output_dir="output/my_analysis",
    visualize=True,
    obsidian_mode=True,
    obsidian_options={
        'suggested_links_min_confidence': 0.4,
        'suggested_links_top_n': 50,
        'moc_top_n': 20,
        'max_communities': 10,
        'path_top_n': 10
    }
)
```

---

## 詳細使用

### CLI 命令完整說明

```
python kb_manage.py visualize-network [選項]
```

**主要選項**:

| 參數 | 說明 | 默認值 |
|------|------|--------|
| `--output` | 輸出目錄 | `output/concept_analysis` |
| `--obsidian` | 啟用 Obsidian 格式輸出 | False |
| `--no-viz` | 跳過視覺化生成 | False |
| `--top-n` | 建議連結顯示數量 | 50 |
| `--min-confidence` | 建議連結最小信度 | 0.4 |
| `--moc-top` | 核心概念地圖顯示數量 | 20 |
| `--max-communities` | 最多顯示社群數 | 10 |
| `--max-paths` | 路徑分析顯示數量 | 10 |

**使用範例**:

```bash
# 1. 基本分析（不含 Obsidian）
python kb_manage.py visualize-network

# 2. 完整分析 + Obsidian 格式
python kb_manage.py visualize-network --obsidian

# 3. 只要 Obsidian 格式，不要視覺化
python kb_manage.py visualize-network --obsidian --no-viz

# 4. 降低信度閾值，獲取更多建議
python kb_manage.py visualize-network --obsidian --min-confidence 0.3

# 5. 增加顯示的核心概念數量
python kb_manage.py visualize-network --obsidian --moc-top 50 --top-n 100
```

---

## 輸出文件說明

### 1. README.md（索引文件）

快速導航所有生成的文件，包含統計摘要和使用指南。

**內容結構**:
- 文件列表（含 Wiki Links）
- 網絡統計（節點數、邊數、密度等）
- 關係類型分布
- 使用建議

### 2. suggested_links.md（建議連結）

基於向量相似度（Gemini embeddings）的智能連結推薦。

**特性**:
- 按關係類型分組（leads_to, related_to, contrasts_with 等）
- 信度評分（confidence）和相似度（similarity）
- 每個建議包含：
  - 來源和目標卡片的標題
  - Wiki Links（可直接複製到 Obsidian）
  - 核心概念預覽

**示例**:
```markdown
### 1. 目標設定理論 → 動機理論

- **信度**: 0.87 (相似度: 0.82)
- **關係類型**: `related_to`
- **建議操作**:
  ```markdown
  在 [[zettel_Abbas-2022_20251104/zettel_index#1. ...]] 中新增: [[zettel_Locke-1990_20251105/zettel_index#5. ...]]
  ```
```

**注意事項**:
- 如果文件為空（0 個建議），可能是信度閾值過高
- 建議調整 `--min-confidence` 參數（推薦範圍: 0.3-0.5）
- 所有關係基於 AI 分析，請根據實際情況判斷是否採納

### 3. key_concepts_moc.md（核心概念地圖）

基於 PageRank 算法識別的最具影響力概念。

**包含內容**:
- Top 20 概念表格（PageRank、度中心性、介數中心性）
- Hub 節點（高度連接的概念）
- Bridge 節點（橋接不同知識領域的概念）
- 指標說明

**使用建議**:
- 從 Top 5 概念開始學習和整理
- Hub 節點是知識網絡的核心，優先完善
- Bridge 節點連接不同領域，適合跨領域整合

### 4. community_summaries/（社群摘要）

使用 Louvain 算法檢測的概念社群。

**每個社群文件包含**:
- 社群統計（節點數、密度、中心節點）
- 核心概念列表（前 10 個）
- 所有概念（完整列表，按字母順序）

**特性**:
- 社群內的概念通常討論相同或相關主題
- 適合批次學習和整理相關知識
- 中心節點是該社群的核心概念

### 5. path_analysis.md（路徑分析）

識別有影響力的概念推導路徑。

**內容**:
- 推導路徑可視化（文字鏈）
- 節點詳情（含 Wiki Links）
- 路徑長度和信度

**注意**: 路徑數量可能較少或為 0（取決於網絡結構）

### 6. concept_network.html（互動視覺化）

基於 D3.js 的互動式網絡圖。

**功能**:
- 縮放和拖曳
- 點擊節點顯示詳細信息
- 顏色編碼（根據社群）
- 邊的粗細（根據關係強度）

**使用方法**:
- 直接在瀏覽器中打開
- 滾輪縮放、滑鼠拖曳移動
- 點擊節點查看連接

### 7. concept_network.dot（Graphviz 格式）

可轉換為高品質圖片的圖檔來源。

**轉換為圖片**:
```bash
# 需要安裝 Graphviz
dot -Tpng concept_network.dot -o network.png
dot -Tsvg concept_network.dot -o network.svg
```

---

## 在 Obsidian 中使用

### 步驟 1：設置 Obsidian Vault

有兩種方式將生成的文件整合到 Obsidian：

**方式 A：直接打開輸出目錄**（推薦）
```
File → Open folder as vault → 選擇 output/concept_analysis/obsidian/
```

**方式 B：複製到現有 Vault**
```bash
# 複製生成的文件到你的 Obsidian vault
cp -r output/concept_analysis/obsidian/* /path/to/your/vault/concept_analysis/
```

### 步驟 2：配置 Obsidian 設置

建議設置（可選）:
1. **啟用 Wiki Links**: Settings → Files & Links → Use [[Wikilinks]]
2. **啟用自動連結**: Settings → Files & Links → Automatically update internal links
3. **圖表視圖**: 啟用 Graph View 插件

### 步驟 3：瀏覽分析結果

1. **從 README.md 開始**
   - 了解整體統計和文件結構
   - 點擊連結導航到其他文件

2. **查看核心概念**
   - 打開 `key_concepts_moc.md`
   - 點擊 Top 概念的 Wiki Link
   - 跳轉到 zettel_index.md 的特定條目

3. **探索社群**
   - 瀏覽 `community_summaries/` 資料夾
   - 點擊中心節點了解社群主題
   - 按字母順序查看所有相關概念

4. **應用建議連結**
   - 打開 `suggested_links.md`
   - 評估每個建議的相關性
   - 複製 Wiki Link 到你的筆記中

5. **使用圖表視圖**
   - 開啟 Obsidian 的 Graph View
   - 查看概念之間的連接結構
   - 與 `concept_network.html` 對照

### 步驟 4：添加人類筆記

在自動生成的連結基礎上，添加你自己的理解：

```markdown
## 我的筆記

- [[相關概念A]] 與 [[相關概念B]] 的關係是...
- 這個概念在實際應用中的例子：...
- 與 [[其他文獻]] 的觀點對比：...
```

---

## 參數調整

### 信度閾值（min-confidence）

控制建議連結的質量與數量平衡。

**推薦值**:
- `0.3`: 寬鬆（更多建議，可能有雜訊）
- `0.4`: 平衡（默認，推薦）
- `0.5`: 嚴格（高品質，但數量少）

**調整依據**:
```bash
# 1. 查看平均信度
grep "平均信度" output/concept_analysis/analysis_report.md

# 2. 調整閾值（比平均值低 0.05-0.1）
python kb_manage.py visualize-network --obsidian --min-confidence 0.35
```

### 顯示數量調整

根據知識庫大小調整顯示數量：

| 知識庫規模 | 建議 top-n | 建議 moc-top |
|-----------|-----------|-------------|
| <200 張卡片 | 30-50 | 15-20 |
| 200-500 張 | 50-100 | 20-30 |
| 500-1000 張 | 100-200 | 30-50 |
| >1000 張 | 200+ | 50-100 |

**範例**:
```bash
# 大型知識庫
python kb_manage.py visualize-network --obsidian \
    --top-n 200 \
    --moc-top 50 \
    --max-communities 20
```

---

## 故障排除

### 問題 1: suggested_links.md 為空

**原因**: 信度閾值過高，沒有關係滿足條件

**解決方法**:
1. 檢查平均信度：
   ```bash
   grep "平均信度\|平均相似度" output/concept_analysis/analysis_report.md
   ```

2. 降低閾值：
   ```bash
   python kb_manage.py visualize-network --obsidian --min-confidence 0.3
   ```

### 問題 2: Wiki Links 無法跳轉

**原因**: 路徑格式或 Obsidian 設置問題

**解決方法**:
1. 確認 Obsidian 已啟用 Wiki Links
2. 檢查連結格式是否為：
   ```markdown
   [[zettel_xxx/zettel_index#條目|顯示標題]]
   ```
3. 確保 `output/zettelkasten_notes/` 在 Obsidian vault 範圍內

### 問題 3: 社群列表過長（>500 個概念）

**原因**: 所有概念被識別為單一社群（網絡密度高）

**解決方法**:
- 這是正常現象（高度相關的知識庫）
- 可以按字母順序分段瀏覽
- 關注 Top 概念和中心節點即可

### 問題 4: 視覺化無法打開

**原因**: 瀏覽器安全設置或文件路徑問題

**解決方法**:
1. 使用現代瀏覽器（Chrome, Firefox, Edge）
2. 確保 JavaScript 已啟用
3. 檢查文件路徑中是否有特殊字元

### 問題 5: 分析時間過長

**原因**: 知識庫過大或電腦效能不足

**解決方法**:
- 預期時間：每 100 張卡片約 30-60 秒
- 可先用小規模測試：創建子集 vault
- 跳過視覺化：`--no-viz`

---

## 實際範例

### 範例 1：初次使用

```bash
# 1. 執行分析
python kb_manage.py visualize-network --obsidian

# 2. 在 Obsidian 中打開
# File → Open folder as vault → output/concept_analysis/obsidian/

# 3. 從 README.md 開始瀏覽
# 4. 查看 key_concepts_moc.md 了解核心概念
# 5. 探索 suggested_links.md 應用建議
```

### 範例 2：進階調整

```bash
# 1. 降低閾值獲取更多建議
python kb_manage.py visualize-network --obsidian \
    --min-confidence 0.35 \
    --top-n 100

# 2. 增加核心概念顯示數量
python kb_manage.py visualize-network --obsidian \
    --moc-top 30

# 3. 只要 Obsidian 格式，節省時間
python kb_manage.py visualize-network --obsidian --no-viz
```

### 範例 3：整合現有工作流

```bash
# 1. 分析論文並生成 Zettelkasten
python analyze_paper.py paper.pdf --generate-zettel --add-to-kb

# 2. 執行網絡分析
python kb_manage.py visualize-network --obsidian

# 3. 在 Obsidian 中：
#    - 查看新增卡片在網絡中的位置
#    - 應用建議連結到現有筆記
#    - 使用圖表視圖查看整體結構
```

---

## 技術細節

### 向量嵌入

- **提供者**: Google Gemini Embedding-001
- **維度**: 768
- **成本**: ~$0.00015/1K tokens
- **相似度計算**: 餘弦相似度（Cosine Similarity）

### 網絡分析算法

- **社群檢測**: Louvain 算法（modularity optimization）
- **中心性分析**: PageRank、度中心性、介數中心性
- **路徑分析**: BFS/DFS + PageRank 加權

### 資料來源

- **Zettelkasten 卡片**: `output/zettelkasten_notes/`
- **向量數據**: `chroma_db/` (ChromaDB 持久化)
- **知識庫**: `knowledge_base/index.db` (SQLite)

---

## 參考資料

- **Concept Mapper 文檔**: `src/analyzers/concept_mapper.py` 頂部注釋
- **Obsidian 文檔**: https://help.obsidian.md/
- **Phase 2.2 設計文檔**: `AGENT_SKILL_DESIGN.md`
- **測試報告**: `OBSIDIAN_INTEGRATION_TEST_REPORT.md`

---

**版本歷史**:
- v1.0 (2025-11-05): 初版發布，包含完整功能和測試驗證
