# 向量搜索系統 (Vector Search)

**狀態**: ✅ Phase 1.5 完成實作
**版本**: 1.0.0
**最後更新**: 2025-11-01

基於向量嵌入的語義搜索系統，支援論文和 Zettelkasten 卡片的智能檢索。

---

## 目錄

- [系統架構](#系統架構)
- [核心組件](#核心組件)
- [CLI 使用指南](#cli-使用指南)
- [使用工作流](#使用工作流)
- [性能與成本](#性能與成本)
- [搜索質量評估](#搜索質量評估)
- [故障排除](#故障排除)
- [下一步擴展](#下一步擴展)

---

## 系統架構

```
src/embeddings/
├── providers/
│   ├── gemini_embedder.py    # Google Gemini Embedding-001 (768維)
│   └── ollama_embedder.py    # 本地 Qwen3-Embedding-4B (2560維)
├── vector_db.py               # ChromaDB 封裝
└── __init__.py

generate_embeddings.py         # 批次生成腳本
kb_manage.py                   # CLI整合（semantic-search, similar, hybrid-search）
chroma_db/                     # ChromaDB 持久化目錄
```

---

## 核心組件

### 1. GeminiEmbedder

**檔案**: `src/embeddings/providers/gemini_embedder.py`

Google Gemini Embedding-001 API 封裝，提供雲端高品質向量生成。

#### 規格

| 項目 | 值 |
|------|-----|
| 模型 | models/embedding-001 |
| 維度 | 768 |
| 成本 | $0.00015/1K tokens |
| 速率限制 | 60 requests/min |

#### 特性

- ✅ 自動速率限制（60 req/min）
- ✅ 支援兩種任務類型
  - `retrieval_document`（文檔嵌入）
  - `retrieval_query`（查詢嵌入）
- ✅ 批次處理優化
- ✅ 精確的成本估算

#### 使用範例

```python
from src.embeddings.providers.gemini_embedder import GeminiEmbedder

embedder = GeminiEmbedder()

# 單個文本嵌入
embedding = embedder.embed("認知科學研究")

# 批次嵌入
texts = ["論文1", "論文2", "論文3"]
embeddings = embedder.embed_batch(texts)
```

**完整範例**: [examples/vector_search/embedder_usage.py](../../examples/vector_search/embedder_usage.py)

---

### 2. OllamaEmbedder

**檔案**: `src/embeddings/providers/ollama_embedder.py`

本地 Qwen3-Embedding-4B 模型封裝，完全免費的備用方案。

#### 規格

| 項目 | 值 |
|------|-----|
| 模型 | qwen3-embedding:4b |
| 維度 | 2560 |
| 成本 | $0 (本地免費) |
| 速度 | ~8.6 秒/文本 (CPU) |

#### 特性

- ✅ 完全本地運行，數據隱私保護
- ✅ 自動檢查 Ollama 服務和模型可用性
- ✅ 保守的速率限制（20 req/min，避免資源耗盡）
- ✅ 適合大規模離線處理

#### 使用範例

```python
from src.embeddings.providers.ollama_embedder import OllamaEmbedder

embedder = OllamaEmbedder()

# 單個文本嵌入
embedding = embedder.embed("認知科學研究")

# 批次嵌入
texts = ["論文1", "論文2", "論文3"]
embeddings = embedder.embed_batch(texts)
```

#### 安裝 Ollama

```bash
# 1. 下載並安裝 Ollama
# https://ollama.com/download

# 2. 啟動 Ollama 服務
ollama serve

# 3. 下載 Qwen3 Embedding 模型
ollama pull qwen3-embedding:4b
```

**完整範例**: [examples/vector_search/embedder_usage.py](../../examples/vector_search/embedder_usage.py)

---

### 3. VectorDatabase

**檔案**: `src/embeddings/vector_db.py`

ChromaDB 封裝類，提供向量存儲和語義搜索功能。

#### 資料集合

- `papers`: 論文向量集合
- `zettelkasten`: Zettelkasten 卡片向量集合

#### 支援的操作

| 方法 | 說明 |
|------|------|
| `upsert` | 插入/更新向量 |
| `semantic_search` | 語義搜索 |
| `get_by_id` | 根據 ID 獲取 |
| `find_similar` | 尋找相似內容 |
| `delete` | 刪除向量 |
| `reset` | 清空集合 |

#### 使用範例

```python
from src.embeddings.vector_db import VectorDatabase

db = VectorDatabase()

# 插入向量
db.upsert(
    collection_name="papers",
    ids=["paper_1"],
    embeddings=[[0.1, 0.2, ...]],
    metadatas=[{"title": "論文標題", "authors": "作者"}]
)

# 語義搜索
results = db.semantic_search(
    collection_name="papers",
    query_embedding=[0.1, 0.2, ...],
    n_results=5
)

# 尋找相似內容
similar = db.find_similar(
    collection_name="papers",
    item_id="paper_1",
    n_results=5
)
```

**完整範例**: [examples/vector_search/vector_db_usage.py](../../examples/vector_search/vector_db_usage.py)

---

### 4. 批次生成腳本

**檔案**: `generate_embeddings.py`

為知識庫中的所有論文和 Zettelkasten 卡片批次生成向量嵌入。

#### 文本組合策略

**論文** (from `papers` table):
```
標題: {title}
作者: {authors}
摘要: {abstract}
關鍵詞: {keywords}
內容: {markdown_content[:2000]}  # 如果元數據不足
```

**Zettelkasten** (from `zettel_cards` table):
```
標題: {title}
核心概念: {core_concept}
描述: {description}
內容: {content[:1500]}
```

#### 使用方式

```bash
# 為所有內容生成嵌入（使用 Gemini）
python generate_embeddings.py

# 使用 Ollama（本地免費）
python generate_embeddings.py --provider ollama

# 只為論文生成
python generate_embeddings.py --type papers

# 只為 Zettelkasten 生成
python generate_embeddings.py --type zettel
```

#### 成本估算

**實際測試數據**（31篇論文 + 52張卡片 = 83個向量）:
- 生成成本: ~$0.0173 (Gemini) / $0 (Ollama)
- 單次查詢: ~$0.00001 (Gemini) / $0 (Ollama)

**完整範例**: [examples/vector_search/semantic_search_cli.sh](../../examples/vector_search/semantic_search_cli.sh)

---

## CLI 使用指南

系統提供三個強大的語義搜索命令，整合到 `kb_manage.py` 中。

### 命令 1: semantic-search

根據自然語言查詢，搜索相關的論文或 Zettelkasten 卡片。

#### 語法

```bash
python kb_manage.py semantic-search "<查詢>" [選項]
```

#### 參數

| 參數 | 說明 | 可選值 | 默認值 |
|------|------|--------|--------|
| `query` | 搜索查詢（必需） | 任意文字 | - |
| `--type` | 搜索類型 | papers / zettel / all | all |
| `--limit` | 返回數量 | 整數 | 5 |
| `--provider` | 嵌入提供者 | gemini / ollama | gemini |
| `--verbose, -v` | 顯示詳細信息 | 標記 | False |

#### 範例

```bash
# 基本搜索
python kb_manage.py semantic-search "認知科學"

# 只搜索論文
python kb_manage.py semantic-search "machine learning" --type papers --limit 10

# 使用 Ollama（本地免費）
python kb_manage.py semantic-search "語言學" --provider ollama

# 詳細輸出
python kb_manage.py semantic-search "心理學" --verbose
```

#### 輸出範例

```
============================================================
🔍 語義搜索: '認知科學'
提供者: GEMINI
============================================================

生成查詢向量...

📄 搜索論文 (top 3):
------------------------------------------------------------

1. [38.6%] 華語分類詞的界定與教學上的分級
   ID: 5
   作者: ...
   年份: 未知

2. [34.2%] International Journal of Computer Processing
   ID: 7
   ...
```

---

### 命令 2: similar

根據論文或卡片 ID，尋找最相似的其他內容。

#### 語法

```bash
python kb_manage.py similar <ID> [選項]
```

#### 參數

| 參數 | 說明 | 示例 |
|------|------|------|
| `id` | 論文ID或卡片ID（必需） | 14, paper_14, zettel_xxx |
| `--limit` | 返回數量（默認: 5） | 3, 10, 20 |

#### 範例

```bash
# 尋找與論文 ID=14 相似的內容
python kb_manage.py similar 14

# 指定數量
python kb_manage.py similar paper_5 --limit 10

# Zettelkasten 卡片
python kb_manage.py similar zettel_CogSci-20251104-001 --limit 5
```

#### 輸出範例

```
============================================================
🔍 尋找與論文相似的內容
論文: Journal of Cognitive Psychology
============================================================

📄 相似論文 (top 3):
------------------------------------------------------------

1. [71.8%] PsychonBullRev(2018)25:1968–1972
   ID: 29
   作者: Participant Nonnaivet, Open Science, A.Zwaan

2. [68.1%] Educational Psychology
   ID: 26
   ...
```

#### 特性

- ✅ 自動排除自身（`exclude_self=True`）
- ✅ 高相似度結果（通常 60-80%）
- ✅ 適合發現相關研究和連結知識

---

### 命令 3: hybrid-search

結合全文搜索（FTS）和語義搜索，提供更全面的結果。

#### 語法

```bash
python kb_manage.py hybrid-search "<查詢>" [選項]
```

#### 參數

| 參數 | 說明 | 默認值 |
|------|------|--------|
| `query` | 搜索查詢（必需） | - |
| `--limit` | 返回數量 | 10 |
| `--provider` | 嵌入提供者 | gemini |

#### 範例

```bash
# 基本混合搜索
python kb_manage.py hybrid-search "machine learning"

# 更多結果
python kb_manage.py hybrid-search "神經網絡" --limit 20

# 使用 Ollama
python kb_manage.py hybrid-search "deep learning" --provider ollama
```

#### 輸出範例

```
============================================================
🔍 混合搜索: 'machine learning'
提供者: GEMINI
============================================================

📝 全文搜索結果:
------------------------------------------------------------
1. [FTS] LinguisticsVanguard2022
   ID: 8
2. [FTS] International Journal
   ID: 7

🔍 語義搜索結果:
------------------------------------------------------------
生成查詢向量...
1. [22.6%] HCOMP2022 Proceedings
   ID: 30
...

✨ 混合結果 (兩種方法的聯集):
------------------------------------------------------------

1. [SEM 22.6%] HCOMP2022 Proceedings
   ID: 30
   作者: ...

2. [FTS + SEM 19.3%] Psychological Science
   ID: 23
   ...

統計:
  全文搜索: 2 篇
  語義搜索: 5 篇
  共同結果: 0 篇
  總計: 7 篇
```

#### 特性

- ✅ 結合關鍵詞匹配（FTS）和語義理解（向量搜索）
- ✅ 按語義相似度排序
- ✅ 標註每個結果的來源（FTS / SEM / 兩者）
- ✅ 提供統計摘要

**完整範例**: [examples/vector_search/semantic_search_cli.sh](../../examples/vector_search/semantic_search_cli.sh)

---

## 使用工作流

### 典型場景

#### 1. 初次設置

```bash
# 步驟 1: 安裝依賴
pip install chromadb tqdm numpy google-generativeai

# 步驟 2: 設置 API Key（如使用 Gemini）
export GOOGLE_API_KEY="your-api-key-here"
# 或在 .env 文件中設置

# 步驟 3: 生成嵌入
python generate_embeddings.py

# 步驟 4: 測試搜索
python kb_manage.py semantic-search "認知科學"
```

#### 2. 新增論文後更新

```bash
# 步驟 1: 分析論文
python analyze_paper.py paper.pdf --add-to-kb

# 步驟 2: 重新生成嵌入
python generate_embeddings.py

# 步驟 3: 驗證
python kb_manage.py similar <新論文ID>
```

#### 3. 研究文獻相關性

```bash
# 步驟 1: 關鍵詞搜索
python kb_manage.py search "關鍵詞"

# 步驟 2: 尋找相似論文
python kb_manage.py similar <論文ID>

# 步驟 3: 語義搜索探索
python kb_manage.py semantic-search "相關概念"

# 步驟 4: 混合搜索
python kb_manage.py hybrid-search "主題"
```

---

## 性能與成本

### 數據規模

**實際測試** (31篇論文 + 52張卡片 = 83個向量):

| 指標 | 數值 |
|------|------|
| 數據規模 | 31篇論文 + 52張卡片 = 83個向量 |
| 生成成本 | ~$0.0173 (Gemini) / $0 (Ollama) |
| 查詢成本 | ~$0.00001/次 (Gemini) / $0 (Ollama) |
| 查詢時間 | 3-8秒 (含向量生成) |
| 相似度範圍 | 同領域: 60-80% / 跨領域: 30-50% |

### 成本優化建議

1. **大規模處理使用 Ollama**（免費但慢）
   - 初次生成所有嵌入
   - 批次更新

2. **互動式查詢使用 Gemini**（快速且便宜）
   - 實時搜索
   - 探索性查詢

3. **定期批次更新而非即時更新**
   - 每週或每月統一更新
   - 節省 API 調用次數

---

## 搜索質量評估

### 實測數據（31篇論文，52張卡片）

| 搜索類型 | 相似度範圍 | 準確性 | 評級 |
|----------|-----------|--------|------|
| 同領域論文查找 | 67-72% | 優秀 | ⭐⭐⭐⭐⭐ |
| Zettelkasten 語義搜索 | 40-45% | 良好 | ⭐⭐⭐⭐ |
| 跨領域概念搜索 | 33-44% | 良好 | ⭐⭐⭐⭐ |
| 混合搜索精準度 | 14-23% | 良好 | ⭐⭐⭐⭐ |

### 觀察結果

- ✅ Zettelkasten 卡片的相似度普遍較高（內容更聚焦）
- ✅ 論文搜索在同領域表現優異
- ✅ 混合搜索能發現 FTS 無法找到的語義相關內容
- ⚠️ 跨語言查詢（中英混合）相似度較低

---

## 故障排除

### 問題 1: ModuleNotFoundError

**錯誤**: `ModuleNotFoundError: No module named 'chromadb'`

**解決方案**:
```bash
pip install chromadb tqdm numpy
```

---

### 問題 2: Ollama 連接失敗

**錯誤**: `ConnectionError: Unable to connect to Ollama`

**解決方案**:
```bash
# 檢查服務
curl http://localhost:11434/api/tags

# 啟動服務
ollama serve

# 下載模型
ollama pull qwen3-embedding:4b
```

---

### 問題 3: Google API Key 未設置

**錯誤**: `ValueError: GOOGLE_API_KEY not found`

**解決方案**:
```bash
# 方法 1: 環境變數
export GOOGLE_API_KEY="your-api-key-here"

# 方法 2: .env 文件
echo "GOOGLE_API_KEY=your-api-key-here" >> .env
```

---

### 問題 4: 相似度偏低

**症狀**: 搜索結果相似度 < 20%

**可能原因和解決方案**:
1. **語言不一致**
   - 確保查詢和文檔語言一致（中文/英文）
   - 使用與文檔相同語言的查詢

2. **查詢詞不夠具體**
   - 使用更具體的查詢詞
   - 增加相關領域術語

3. **嵌入向量未更新**
   - 重新生成嵌入: `python generate_embeddings.py`

4. **考慮使用混合搜索**
   - 結合關鍵詞匹配: `python kb_manage.py hybrid-search "查詢"`

---

## 下一步擴展

### 計畫中功能

#### 1. auto_link_v2() - 自動連結

自動基於向量相似度建立論文-Zettelkasten 連結。

```python
# 使用範例（計畫中）
python kb_manage.py auto-link \
    --min-similarity 0.6 \
    --max-links 10
```

#### 2. 增量更新

僅為新內容生成嵌入，無需重新生成所有。

```python
# 使用範例（計畫中）
python generate_embeddings.py --incremental
```

#### 3. 多語言支援

改進中英文混合查詢的相似度標準。

#### 4. 加權混合搜索

允許調整 FTS 和語義搜索的權重。

```python
# 使用範例（計畫中）
python kb_manage.py hybrid-search "查詢" \
    --fts-weight 0.3 \
    --semantic-weight 0.7
```

#### 5. 過濾條件

支援年份、作者、領域過濾。

```python
# 使用範例（計畫中）
python kb_manage.py semantic-search "認知科學" \
    --year-range 2020-2025 \
    --domain CogSci \
    --author "Smith"
```

---

## 相關文檔

- **完整測試報告**: `VECTOR_SEARCH_TEST_REPORT.md`（如存在）
- **範例代碼**: [examples/vector_search/](../../examples/vector_search/)
- **主文檔**: [CLAUDE.md](../../CLAUDE.md)
- **故障排除**: [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)

---

**最後更新**: 2025-11-01
**版本**: 1.0.0
**狀態**: ✅ Phase 1.5 完成實作
