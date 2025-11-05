# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

**知識生產器 (Knowledge Production System)** 是一個以Claude Code為核心、Agents與Skills驅動的學術文獻處理系統。整合了SciMaker的Journal Club能力，支援多格式輸入輸出與混合式知識庫管理。

### 核心特性

- 🤖 **Agent驅動**: 智能代理自動化文獻分析和知識整合
- 🛠️ **Skills模組化**: 可重用的技能組件（PDF提取、簡報生成、筆記撰寫）
- 📚 **混合式知識庫**: Markdown文件 + SQLite索引 + 全文搜索
- 🎨 **多風格輸出**: 8種學術風格 × 5種詳細程度 × 3種語言
- 🤖 **多LLM支持**: Ollama、Google Gemini、OpenAI、Anthropic Claude
- 🔗 **可擴展架構**: 預留與其他專案串接的介面

## 專案架構

```
claude_lit_workflow/
├── .claude/
│   ├── skills/              # 核心Skills
│   │   ├── pdf-extractor.md     ✅
│   │   ├── slide-maker.md       ✅
│   │   ├── batch-processor.md   ✅ NEW
│   │   ├── note-writer.md       (待實作)
│   │   ├── viz-generator.md     (待實作)
│   │   └── kb-connector.md      ✅
│   ├── agents/              # 3個智能Agents (待實作)
│   │   ├── literature-analyzer/
│   │   ├── knowledge-integrator/
│   │   └── research-assistant/
│   └── commands/            # Slash Commands
│       └── analyze-paper.md
├── src/
│   ├── extractors/          # 提取器模組
│   │   └── pdf_extractor.py
│   ├── generators/          # 生成器模組
│   │   └── slide_maker.py   ✅ 多LLM支持的投影片生成器
│   ├── processors/          # 批次處理模組 ✅ NEW
│   │   ├── batch_processor.py
│   │   └── __init__.py
│   ├── checkers/            # 質量檢查模組 ✅ NEW
│   │   ├── quality_checker.py
│   │   ├── quality_rules.yaml
│   │   └── __init__.py
│   ├── knowledge_base/      # 知識庫管理
│   │   └── kb_manager.py
│   └── utils/               # 工具函數
│       ├── session_organizer.py  ✅ 檔案整理工具
│       ├── cleanup_rules.yaml
│       └── __init__.py
├── knowledge_base/          # 知識儲存區
│   ├── papers/              # Markdown論文筆記
│   ├── metadata/            # 元數據
│   └── index.db             # SQLite數據庫
├── templates/               # 模板庫
│   ├── prompts/             # Prompt模板（基於Journal Club）
│   │   ├── raw_templates.txt
│   │   └── journal_club_template.jinja2
│   └── styles/              # 學術風格定義
│       └── academic_styles.yaml
├── config/
│   └── settings.yaml        # 系統配置
├── batch_process.py         # 批次處理CLI ✅ NEW
├── check_quality.py         # 質量檢查CLI ✅ NEW
├── cleanup_session.py       # 檔案整理CLI ✅ NEW
├── requirements.txt
└── README.md
```

## 技術棧

- **Python 3.10+**: 主要開發語言
- **Claude Code**: AI驅動的開發環境
- **Ollama**: 本地LLM推理（整合自SciMaker）
- **SQLite**: 輕量級數據庫（知識庫索引）
- **Jinja2**: Prompt模板引擎
- **PyPDF2/pdfplumber**: PDF處理
- **python-pptx**: PowerPoint生成

## 快速開始

### 1. 環境設置

```bash
# 安裝依賴
pip install -r requirements.txt

# 初始化知識庫（首次使用）
python -c "from src.knowledge_base import KnowledgeBaseManager; KnowledgeBaseManager()"
```

### 2. 基本使用

```bash
# 分析單篇論文
/analyze-paper paper.pdf

# 分析並加入知識庫
/analyze-paper paper.pdf --add-to-kb

# 生成多種格式
/analyze-paper paper.pdf --format all --style modern_academic
```

### 3. 知識庫查詢

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager()

# 搜索論文
results = kb.search_papers("deep learning medical")

# 查看統計
stats = kb.get_stats()
print(f"論文總數: {stats['total_papers']}")
```

## 核心模組說明

### PDF提取器 (src/extractors/pdf_extractor.py)

**功能**: 從PDF提取文本、結構和元數據

```python
from src.extractors import PDFExtractor

extractor = PDFExtractor(max_chars=50000)
result = extractor.extract("paper.pdf")

# 訪問提取結果
title = result['structure']['title']
authors = result['structure']['authors']
abstract = result['structure']['abstract']
```

**特性**:
- 支援兩種提取方法：pdfplumber（推薦）和PyPDF2
- 字元限制：50,000（Journal Club的5倍）
- 自動識別：標題、作者、摘要、章節、關鍵詞
- 輸出JSON格式的結構化數據

**配置**: `config/settings.yaml` → `pdf` section

### 知識庫管理器 (src/knowledge_base/kb_manager.py)

**功能**: 混合式知識庫管理（Markdown + SQLite）

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager()

# 新增論文
paper_id = kb.add_paper(
    file_path="papers/smith_2024.md",
    title="Deep Learning for Medical Diagnosis",
    authors=["John Smith", "Jane Doe"],
    year=2024,
    keywords=["deep learning", "medical"],
    content="完整內容..."
)

# 全文搜索
results = kb.search_papers("deep learning", limit=10)

# 主題管理
topic_id = kb.add_topic("深度學習")
kb.link_paper_to_topic(paper_id, topic_id)

# 創建Markdown筆記
md_path = kb.create_markdown_note(paper_data)
```

**數據庫結構**:
- `papers`: 論文元數據
- `topics`: 主題分類
- `paper_topics`: 論文-主題關聯
- `citations`: 引用關係
- `papers_fts`: 全文搜索索引（FTS5）

**配置**: `config/settings.yaml` → `knowledge_base` section

### 批次處理器 (src/processors/batch_processor.py) ✅ NEW

**功能**: 穩定地批次處理大量PDF文件，支援知識庫和Zettelkasten生成

```bash
# 批次處理資料夾中的所有PDF
python batch_process.py --folder "D:\pdfs\mental_simulation"

# 批次處理並加入知識庫
python batch_process.py --folder "D:\pdfs" --domain CogSci --add-to-kb

# 批次處理並生成 Zettelkasten
python batch_process.py --folder "D:\pdfs" --domain CogSci --generate-zettel

# 完整處理（知識庫 + Zettelkasten）
python batch_process.py --folder "D:\pdfs" --domain CogSci --add-to-kb --generate-zettel --workers 4

# 指定特定文件
python batch_process.py --files paper1.pdf paper2.pdf --add-to-kb
```

**Python API**:
```python
from src.processors import BatchProcessor

processor = BatchProcessor(max_workers=3, error_handling='skip')

result = processor.process_batch(
    pdf_paths="D:\\pdfs",
    domain="CogSci",
    add_to_kb=True,
    generate_zettel=True,
    zettel_config={
        'detail_level': 'detailed',
        'card_count': 20,
        'llm_provider': 'google'
    }
)

# 查看結果
print(f"成功: {result.success}/{result.total}")
print(result.to_report())
```

**核心特性**:
- **平行處理**: ThreadPoolExecutor支援多工處理（預設3個worker）
- **穩定性保證**: 完整的錯誤處理和timeout機制（300秒/PDF）
- **Windows路徑支援**: pathlib.Path正確處理中文和特殊字元
- **進度追蹤**: 實時顯示處理進度 `[1/15] ✅ Paper1.pdf`
- **錯誤策略**: skip（跳過）、retry（重試）、stop（停止）三種模式
- **整合清理**: 處理完成後可自動執行檔案整理

**數據結構**:
- `ProcessResult`: 單個文件處理結果（成功/失敗、paper_id、錯誤信息）
- `BatchResult`: 批次處理總結（總數、成功數、失敗數、處理時間、報告）

**配置參數**:
| 參數 | 說明 | 默認值 |
|------|------|--------|
| `--workers` | 平行處理的執行緒數 | 3 |
| `--error-handling` | 錯誤處理策略 | skip |
| `--domain` | 領域代碼（CogSci/Linguistics/AI） | Research |
| `--add-to-kb` | 加入知識庫 | False |
| `--generate-zettel` | 生成Zettelkasten | False |
| `--report` | 報告輸出路徑 | - |

**效能指標**:
- 單個PDF處理時間：30-120秒（取決於大小和LLM速度）
- 建議worker數：2-4個（避免API rate limiting）
- 記憶體使用：約100MB + 50MB/worker

**詳細說明**: `.claude/skills/batch-processor.md`

### 質量檢查器 (src/checkers/quality_checker.py) ✅ NEW

**功能**: 檢查知識庫中論文的元數據質量，檢測問題並提供修復建議

```bash
# 檢查所有論文
python check_quality.py

# 檢查特定論文
python check_quality.py --paper-id 27

# 生成詳細報告
python check_quality.py --detail comprehensive --output quality_report.txt

# 僅顯示有嚴重問題的論文
python check_quality.py --critical-only

# 檢測重複論文（相似度 >= 85%）
python check_quality.py --detect-duplicates --threshold 0.85

# JSON格式輸出
python check_quality.py --format json --output quality_report.json
```

**Python API**:
```python
from src.checkers import QualityChecker

checker = QualityChecker()

# 檢查單篇論文
report = checker.check_paper(paper_id=27, auto_fix=False)
print(f"評分: {report.overall_score}/100")
print(f"質量等級: {report.quality_level}")

# 檢查所有論文
reports = checker.check_all_papers()
summary = checker.generate_summary_report(reports, detail_level="comprehensive")
print(summary)

# 檢測重複
duplicates = checker.detect_duplicates(threshold=0.85)
for id1, id2, similarity in duplicates:
    print(f"論文 {id1} 與 {id2} 相似度: {similarity:.2%}")
```

**檢查項目**:

**1. 標題檢查**:
- ❌ 無效模式：`Journal Pre-proof`、`Untitled`、URL、空白
- ⚠️ 可疑模式：包含`.pdf`、版本標記、過短/過長
- ✅ 品質指標：10-300字元，建議20-200字元

**2. 作者檢查**:
- ❌ 無效模式：`Unknown`、`N/A`、`Author 1`、空白
- ⚠️ 格式問題：缺少姓名、特殊字元、大小寫錯誤
- ✅ 品質指標：1-50位作者

**3. 年份檢查**:
- ❌ 嚴重問題：缺少年份、超出範圍（1900-2030）
- ⚠️ 可疑：過於古老（<1950）、過於未來（>當前年+2）

**4. 摘要檢查**:
- ❌ 嚴重問題：空白、佔位符（`尚未提供摘要`）、過短（<50字元）
- ⚠️ 警告：偏短（<100字元）、過長（>5000字元）、內容不足（<20字）
- ✅ 建議長度：100-2000字元

**5. 關鍵詞檢查**:
- ❌ 警告：數量不足（<1個）、過多（>20個）
- ⚠️ 格式問題：空字串、重複、長度不合理
- ✅ 建議數量：3-10個

**質量評分系統**:
```
評分權重:
  - 標題: 25%
  - 作者: 20%
  - 年份: 15%
  - 摘要: 25%
  - 關鍵詞: 15%

質量等級:
  - 優秀 ⭐⭐⭐⭐⭐: 90-100分
  - 良好 ⭐⭐⭐⭐: 75-89分
  - 可接受 ⭐⭐⭐: 60-74分
  - 較差 ⭐⭐: 40-59分
  - 嚴重問題 ⭐: 0-39分
```

**重複檢測演算法**:
```
相似度計算:
  - 標題相似度: 60% (SequenceMatcher)
  - 作者重疊度: 30% (集合交集/聯集)
  - 年份相似度: 10% (年份差異容忍度)

閾值建議:
  - 0.95-1.0: 極可能重複（建議合併）
  - 0.85-0.94: 高度相似（需人工檢查）
  - 0.70-0.84: 中度相似（可能相關論文）
```

**自動修復功能** (開發中):
- 從PDF內容提取標題、作者、年份
- 使用DOI查詢元數據（CrossRef API）
- 使用標題查詢元數據（Semantic Scholar API）
- 移除重複關鍵詞
- 修正年份範圍錯誤

**配置文件**: `src/checkers/quality_rules.yaml`
- 290行YAML規則定義
- 可自訂無效模式、可疑模式、質量指標
- 支援正則表達式匹配

**實際測試結果**（30篇論文知識庫）:
```
平均評分: 68.2/100
總問題數: 79
  - 嚴重問題: 50 (year missing: 30, abstract missing: 16)
  - 警告: 20 (keywords insufficient: 20)

質量分布:
  - 良好: 12篇 (40%)
  - 可接受: 6篇 (20%)
  - 較差: 12篇 (40%)

常見問題:
  1. 所有論文缺少年份 (100%)
  2. 關鍵詞不足 (67%)
  3. 摘要缺失 (53%)
  4. 無效標題格式 (7%)
```

**使用建議**:
1. **定期檢查**: 每週或每月執行一次完整檢查
2. **入庫前檢查**: 使用`analyze_paper.py`時先檢查提取質量
3. **批次修復**: 先用`--critical-only`找出嚴重問題，再逐一修復
4. **重複偵測**: 新增大量論文後執行，避免知識庫膨脹

---

## 向量搜索系統 (Vector Search) ✅ NEW

**Phase 1.5** 完成實作！基於向量嵌入的語義搜索系統，支援論文和 Zettelkasten 卡片的智能檢索。

### 系統架構

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

### 核心組件

#### 1. GeminiEmbedder (src/embeddings/providers/gemini_embedder.py)

Google Gemini Embedding-001 API 封裝，提供雲端高品質向量生成。

```python
from src.embeddings.providers import GeminiEmbedder

embedder = GeminiEmbedder()
# 模型: models/embedding-001
# 維度: 768
# 成本: $0.00015/1K tokens
# 速率: 60 requests/min

# 單個文本嵌入
embedding = embedder.embed("深度學習應用", task_type="retrieval_document")

# 批次嵌入（最多100個/批次）
texts = ["文本1", "文本2", "文本3"]
embeddings = embedder.embed_batch(texts, batch_size=100)

# 成本估算
cost = embedder.estimate_cost(texts)
print(f"預估成本: ${cost:.4f}")
```

**特性**:
- 自動速率限制（60 req/min）
- 支援兩種任務類型：`retrieval_document`（文檔）和 `retrieval_query`（查詢）
- 批次處理優化
- 精確的成本估算

#### 2. OllamaEmbedder (src/embeddings/providers/ollama_embedder.py)

本地 Qwen3-Embedding-4B 模型封裝，完全免費的備用方案。

```python
from src.embeddings.providers import OllamaEmbedder

embedder = OllamaEmbedder()
# 模型: qwen3-embedding:4b
# 維度: 2560
# 成本: $0 (本地免費)
# 速度: ~8.6 秒/文本 (CPU)

# 檢查服務狀態
info = embedder.get_info()
print(f"服務可用: {info['service_available']}")

# 嵌入文本
embedding = embedder.embed("測試文本")
```

**特性**:
- 完全本地運行，數據隱私
- 自動檢查 Ollama 服務和模型可用性
- 保守的速率限制（20 req/min，避免資源耗盡）
- 適合大規模離線處理

**安裝 Ollama 模型**:
```bash
# 啟動 Ollama
ollama serve

# 下載模型
ollama pull qwen3-embedding:4b
```

#### 3. VectorDatabase (src/embeddings/vector_db.py)

ChromaDB 封裝類，提供向量存儲和語義搜索功能。

```python
from src.embeddings.vector_db import VectorDatabase

db = VectorDatabase(persist_directory="chroma_db")

# 插入/更新論文向量
db.upsert_papers(
    embeddings=embeddings,      # numpy array or list
    documents=texts,             # 文本內容
    ids=["paper_1", "paper_2"], # 唯一ID
    metadatas=[{...}, {...}]    # 元數據字典
)

# 語義搜索論文
results = db.semantic_search_papers(
    query_embedding=query_vec,
    n_results=10,
    where={"year": {"$gte": 2020}}  # 可選過濾條件
)

# 尋找相似論文
similar = db.find_similar_papers(
    paper_id="paper_14",
    n_results=5,
    exclude_self=True
)

# 統計信息
stats = db.get_stats()
print(f"論文向量數: {stats['papers_count']}")
print(f"Zettelkasten 向量數: {stats['zettel_count']}")
```

**資料集合**:
- `papers`: 論文向量集合
- `zettelkasten`: Zettelkasten 卡片向量集合

**支援的操作**:
- `upsert`: 插入/更新向量
- `semantic_search`: 語義搜索
- `get_by_id`: 根據 ID 獲取
- `find_similar`: 尋找相似內容
- `delete`: 刪除向量
- `reset`: 清空集合

#### 4. 批次生成腳本 (generate_embeddings.py)

為知識庫中的所有論文和 Zettelkasten 卡片批次生成向量嵌入。

```bash
# 為所有內容生成嵌入（需確認成本）
python generate_embeddings.py --provider gemini

# 自動確認（用於自動化）
python generate_embeddings.py --provider gemini --yes

# 只處理論文
python generate_embeddings.py --papers-only --limit 10

# 只處理 Zettelkasten
python generate_embeddings.py --zettel-only

# 使用 Ollama（免費但較慢）
python generate_embeddings.py --provider ollama

# 查看統計
python generate_embeddings.py --stats
```

**文本組合策略**:

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

**成本估算**:
- 31篇論文 + 52張卡片 = 83個向量
- 實際成本: ~$0.0173
- 單次查詢: ~$0.00001

### kb_manage.py CLI 整合

系統提供三個強大的語義搜索命令，整合到知識庫管理工具中。

#### 命令 1: semantic-search - 語義搜索

根據自然語言查詢，搜索相關的論文或 Zettelkasten 卡片。

```bash
# 搜索論文
python kb_manage.py semantic-search "深度學習應用" --type papers --limit 5

# 搜索 Zettelkasten 卡片
python kb_manage.py semantic-search "認知科學" --type zettel --limit 3

# 搜索所有類型（默認）
python kb_manage.py semantic-search "機器學習" --type all

# 使用 Ollama（免費但較慢）
python kb_manage.py semantic-search "AI研究" --provider ollama

# 顯示詳細信息（摘要/內容預覽）
python kb_manage.py semantic-search "語言學" --verbose
```

**輸出範例**:
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

**參數說明**:
| 參數 | 說明 | 可選值 | 默認值 |
|------|------|--------|--------|
| `query` | 搜索查詢（必需） | 任意文字 | - |
| `--type` | 搜索類型 | papers / zettel / all | all |
| `--limit` | 返回數量 | 整數 | 5 |
| `--provider` | 嵌入提供者 | gemini / ollama | gemini |
| `--verbose, -v` | 顯示詳細信息 | 標記 | False |

#### 命令 2: similar - 尋找相似內容

根據論文或卡片 ID，尋找最相似的其他內容。

```bash
# 尋找與論文 14 相似的論文
python kb_manage.py similar 14 --limit 5

# 尋找與卡片相似的卡片
python kb_manage.py similar zettel_CogSci-20251029-001 --limit 3

# 也可以用 paper_ 前綴
python kb_manage.py similar paper_14 --limit 5
```

**輸出範例**:
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

**特性**:
- 自動排除自身（`exclude_self=True`）
- 高相似度結果（通常 60-80%）
- 適合發現相關研究和連結知識

**參數說明**:
| 參數 | 說明 | 示例 |
|------|------|------|
| `id` | 論文ID或卡片ID（必需） | 14, paper_14, zettel_xxx |
| `--limit` | 返回數量（默認: 5） | 3, 10, 20 |

#### 命令 3: hybrid-search - 混合搜索

結合全文搜索（FTS）和語義搜索，提供更全面的結果。

```bash
# 混合搜索
python kb_manage.py hybrid-search "machine learning" --limit 10

# 使用 Ollama
python kb_manage.py hybrid-search "深度學習" --provider ollama
```

**輸出範例**:
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

**特性**:
- 結合關鍵詞匹配（FTS）和語義理解（向量搜索）
- 按語義相似度排序
- 標註每個結果的來源（FTS / SEM / 兩者）
- 提供統計摘要

**參數說明**:
| 參數 | 說明 | 默認值 |
|------|------|--------|
| `query` | 搜索查詢（必需） | - |
| `--limit` | 返回數量 | 10 |
| `--provider` | 嵌入提供者 | gemini |

### 使用工作流

**典型場景 1: 初次設置**

```bash
# 1. 安裝依賴
pip install chromadb tqdm google-generativeai numpy

# 2. 設置 API Key（~/.bashrc 或 .env）
export GOOGLE_API_KEY="your-api-key-here"

# 3. 生成所有向量嵌入
python generate_embeddings.py --provider gemini --yes

# 4. 測試搜索
python kb_manage.py semantic-search "認知科學" --limit 3
```

**場景 2: 新增論文後更新**

```bash
# 分析並加入知識庫
python analyze_paper.py new_paper.pdf --add-to-kb

# 只為新論文生成嵌入（假設是 ID 32）
# 目前需要重新生成所有，未來可優化為增量更新
python generate_embeddings.py --papers-only --yes

# 驗證
python kb_manage.py similar 32 --limit 5
```

**場景 3: 研究文獻相關性**

```bash
# 找到感興趣的論文
python kb_manage.py search "深度學習"

# 假設找到 ID 25，尋找相似論文
python kb_manage.py similar 25 --limit 10

# 使用語義搜索探索相關概念
python kb_manage.py semantic-search "神經網絡架構" --type papers
```

### 性能與成本

| 指標 | 數值 |
|------|------|
| **數據規模** | 31篇論文 + 52張卡片 = 83個向量 |
| **生成成本** | ~$0.0173 (Gemini) / $0 (Ollama) |
| **查詢成本** | ~$0.00001/次 (Gemini) / $0 (Ollama) |
| **查詢時間** | 3-8秒 (含向量生成) |
| **相似度範圍** | 同領域: 60-80% / 跨領域: 30-50% |

**成本優化建議**:
1. 大規模處理使用 Ollama（免費但慢）
2. 互動式查詢使用 Gemini（快速且便宜）
3. 定期批次更新而非即時更新

### 搜索質量評估

根據實測數據（31篇論文，52張卡片）：

| 搜索類型 | 相似度範圍 | 準確性 | 評級 |
|----------|-----------|--------|------|
| 同領域論文查找 | 67-72% | 優秀 | ⭐⭐⭐⭐⭐ |
| Zettelkasten 語義搜索 | 40-45% | 良好 | ⭐⭐⭐⭐ |
| 跨領域概念搜索 | 33-44% | 良好 | ⭐⭐⭐⭐ |
| 混合搜索精準度 | 14-23% | 良好 | ⭐⭐⭐⭐ |

**觀察結果**:
- Zettelkasten 卡片的相似度普遍較高（內容更聚焦）
- 論文搜索在同領域表現優異
- 混合搜索能發現 FTS 無法找到的語義相關內容

### 故障排除

**問題 1: `ModuleNotFoundError: No module named 'chromadb'`**
```bash
pip install chromadb tqdm numpy
```

**問題 2: Ollama 連接失敗**
```bash
# 檢查服務
curl http://localhost:11434/api/tags

# 啟動服務
ollama serve

# 下載模型
ollama pull qwen3-embedding:4b
```

**問題 3: Google API Key 未設置**
```bash
export GOOGLE_API_KEY="your-api-key-here"

# 或在 .env 文件中設置
echo "GOOGLE_API_KEY=your-api-key-here" >> .env
```

**問題 4: 相似度偏低**
- 確保查詢和文檔語言一致（中文/英文）
- 使用更具體的查詢詞
- 考慮使用混合搜索結合關鍵詞匹配

### 下一步擴展

**計畫中功能**:
1. **auto_link_v2()**: 自動基於向量相似度建立論文-Zettelkasten 連結
2. **增量更新**: 僅為新內容生成嵌入，無需重新生成所有
3. **多語言支援**: 改進中英文混合查詢的相似度標準
4. **加權混合搜索**: 允許調整 FTS 和語義搜索的權重
5. **過濾條件**: 支援年份、作者、領域過濾

**完整測試報告**: 參見 `VECTOR_SEARCH_TEST_REPORT.md`

---

## Concept Mapper - 概念網絡分析器 (Phase 2.2) ✅ NEW

**Phase 2.2** 完成實作！基於圖論和網絡分析的 Zettelkasten 概念關係視覺化系統，支援 Obsidian 友好格式輸出。

### 系統架構

```
src/analyzers/
├── concept_mapper.py         # 概念網絡分析核心 (1,230行)
├── obsidian_exporter.py      # Obsidian 格式導出器 (700行)
└── relation_finder.py        # 關係識別器 (Phase 2.1)

output/concept_analysis/
├── concept_network.html      # D3.js 互動式網絡圖
├── concept_network.dot       # Graphviz DOT 格式
├── analysis_report.md        # 完整分析報告
├── analysis_data.json        # 原始數據
└── obsidian/                 # Obsidian 友好格式
    ├── README.md
    ├── suggested_links.md
    ├── key_concepts_moc.md
    ├── path_analysis.md
    └── community_summaries/
```

### 核心功能

#### 1. 概念網絡建構

基於 Phase 2.1 的關係識別結果，建構完整的概念網絡：

```python
from src.analyzers.concept_mapper import ConceptMapper

mapper = ConceptMapper()

# 執行完整分析
results = mapper.analyze_all(
    output_dir="output/concept_analysis",
    visualize=True,           # 生成 D3.js + Graphviz
    obsidian_mode=True,       # 生成 Obsidian 格式
    obsidian_options={
        'suggested_links_min_confidence': 0.4,
        'suggested_links_top_n': 50,
        'moc_top_n': 20,
        'max_communities': 10,
        'path_top_n': 10
    }
)
```

**網絡統計**:
- 節點數: 704
- 邊數: 56,423
- 平均度: 160.29
- 網絡密度: 0.228

#### 2. 社群檢測 (Louvain 算法)

自動識別概念社群，將相關概念分組：

```python
communities = mapper.detect_communities()

# 每個社群包含:
# - community_id: 社群編號
# - size: 節點數
# - density: 社群密度
# - hub_node: 中心節點
# - top_concepts: 核心概念列表
```

**實際測試結果**:
- 檢測到 1 個大型社群（高度相關的知識庫）
- 社群密度: 0.228
- 中心節點: Liu-2012-003 (視覺字符處理)

#### 3. 中心性分析 (PageRank + Centrality)

識別網絡中最具影響力的概念：

```python
centralities = mapper.analyze_centrality()

# 每個節點包含:
# - pagerank: PageRank 分數（整體影響力）
# - degree_centrality: 度中心性（連接數）
# - betweenness_centrality: 介數中心性（橋接能力）
# - closeness_centrality: 接近中心性（平均距離）
```

**Top 5 核心概念**:
1. Liu-2012-003 (PageRank: 0.0047, Degree: 0.836)
2. Liu-2012-002 (PageRank: 0.0047, Degree: 0.832)
3. Gao-2009a-001 (PageRank: 0.0046, Degree: 0.815)
4. Liu-2012-005 (PageRank: 0.0046, Degree: 0.815)
5. Gao-2009a-006 (PageRank: 0.0046, Degree: 0.812)

#### 4. 路徑分析 (Concept Evolution)

識別概念之間的推導和演化路徑：

```python
paths = mapper.find_influential_paths(min_length=2)

# 每條路徑包含:
# - start_node: 起始概念
# - end_node: 結束概念
# - path: 路徑節點列表
# - length: 路徑長度
# - confidence: 路徑信度
```

**注意**: 路徑數量取決於網絡結構，可能為 0（高度連接的網絡）

#### 5. Obsidian 整合 ✨

自動生成 Obsidian 友好的 Markdown 文件，包含完美的 Wiki Links：

**Wiki Links 格式**:
```markdown
[[zettel_Abbas-2022_20251104/zettel_index#1. [目標設定理論](zettel_cards/Abbas-2022-001.md)|目標設定理論]]
```

**生成的文件**:

1. **suggested_links.md** - 智能連結建議
   - 基於向量相似度 (Gemini embeddings)
   - 信度評分和關係類型
   - 可直接複製到 Obsidian 使用

2. **key_concepts_moc.md** - 核心概念地圖
   - Top 20 概念（PageRank 排序）
   - Hub 節點（高度連接）
   - Bridge 節點（橋接概念）

3. **community_summaries/** - 社群摘要
   - 每個社群一個文件
   - 包含所有概念的 Wiki Links
   - 中心節點和核心概念標註

4. **path_analysis.md** - 路徑分析
   - 概念推導路徑
   - 演化關係可視化

5. **README.md** - 索引和統計
   - 快速導航
   - 網絡統計摘要
   - 使用建議

#### 6. 視覺化

**D3.js 互動式網絡圖** (`concept_network.html`):
- 縮放和拖曳
- 點擊節點顯示詳細信息
- 顏色編碼（根據社群）
- 邊的粗細（根據關係強度）

**Graphviz DOT 格式** (`concept_network.dot`):
```bash
# 轉換為高品質圖片
dot -Tpng concept_network.dot -o network.png
dot -Tsvg concept_network.dot -o network.svg
```

### CLI 使用

```bash
# 基本使用（完整分析 + Obsidian 格式）
python kb_manage.py visualize-network --obsidian

# 自定義參數
python kb_manage.py visualize-network --obsidian \
    --min-confidence 0.35 \
    --top-n 100 \
    --moc-top 30

# 只要 Obsidian 格式，跳過視覺化
python kb_manage.py visualize-network --obsidian --no-viz

# 自定義輸出目錄
python kb_manage.py visualize-network --obsidian \
    --output my_analysis
```

**CLI 參數**:
| 參數 | 說明 | 默認值 |
|------|------|--------|
| `--output` | 輸出目錄 | `output/concept_analysis` |
| `--obsidian` | 生成 Obsidian 格式 | False |
| `--no-viz` | 跳過視覺化 | False |
| `--top-n` | 建議連結數量 | 50 |
| `--min-confidence` | 最小信度 | 0.4 |
| `--moc-top` | MOC 顯示數量 | 20 |
| `--max-communities` | 最多社群數 | 10 |
| `--max-paths` | 路徑數量 | 10 |

### 在 Obsidian 中使用

**步驟 1: 打開輸出目錄**
```
File → Open folder as vault → output/concept_analysis/obsidian/
```

**步驟 2: 瀏覽分析結果**
1. 從 `README.md` 開始了解整體結構
2. 查看 `key_concepts_moc.md` 識別核心概念
3. 探索 `community_summaries/` 了解概念分組
4. 應用 `suggested_links.md` 中的建議到你的筆記

**步驟 3: 使用 Graph View**
- 啟用 Obsidian 的 Graph View 插件
- 查看概念之間的連接結構
- 與 `concept_network.html` 對照

### 技術細節

**依賴庫**:
- `networkx`: 圖論和網絡分析
- `python-louvain`: 社群檢測
- `numpy`: 數值計算
- ChromaDB + Gemini: 向量相似度計算（Phase 1.5）

**演算法**:
- **社群檢測**: Louvain (modularity optimization)
- **中心性**: PageRank, Degree, Betweenness, Closeness
- **路徑搜索**: BFS/DFS with PageRank weighting
- **相似度**: Cosine similarity (768-dim Gemini embeddings)

**性能指標** (704 張卡片):
| 指標 | 數值 |
|------|------|
| 分析時間 | ~2-3 分鐘 |
| 記憶體使用 | ~500 MB |
| 輸出大小 | ~5 MB (含視覺化) |
| 網絡密度 | 0.228 (高度相關) |

### 配置選項

**調整信度閾值**:
- `0.3`: 寬鬆（更多建議，可能有雜訊）
- `0.4`: 平衡（默認，推薦）✅
- `0.5`: 嚴格（高品質，但數量少）

**依知識庫規模調整**:
| 規模 | top-n | moc-top |
|------|-------|---------|
| <200 張 | 30-50 | 15-20 |
| 200-500 張 | 50-100 | 20-30 |
| 500-1000 張 | 100-200 | 30-50 |
| >1000 張 | 200+ | 50-100 |

### 故障排除

**問題 1: suggested_links.md 為空**
- 原因: 信度閾值過高
- 解決: 降低 `--min-confidence` 至 0.3-0.35

**問題 2: Wiki Links 無法跳轉**
- 確認 Obsidian 已啟用 Wiki Links
- 檢查路徑格式: `zettel_xxx/zettel_index#條目`

**問題 3: 社群列表過長 (>500)**
- 這是正常現象（高度相關的知識庫）
- 關注 Top 概念和中心節點即可

### 使用場景

**場景 1: 知識結構探索**
```bash
# 1. 執行分析
python kb_manage.py visualize-network --obsidian

# 2. 在 Obsidian 中查看核心概念
# 3. 使用 Graph View 了解知識結構
# 4. 應用建議連結擴展筆記網絡
```

**場景 2: 文獻相關性研究**
```bash
# 1. 找到感興趣的概念在 key_concepts_moc.md
# 2. 查看該概念所在的社群
# 3. 探索相關概念和路徑
# 4. 整合到文獻回顧中
```

**場景 3: 定期維護**
```bash
# 每週執行一次，更新概念網絡
python kb_manage.py visualize-network --obsidian

# 檢查新增卡片的位置
# 應用新的連結建議
# 更新核心概念筆記
```

### 文檔資源

- **完整使用指南**: `OBSIDIAN_INTEGRATION_GUIDE.md` (3000+ 行)
- **測試報告**: `OBSIDIAN_INTEGRATION_TEST_REPORT.md`
- **代碼文檔**: `src/analyzers/concept_mapper.py` 頂部注釋
- **Skill 文檔**: `.claude/skills/concept-mapper.md`

---

## 學術風格系統

基於Journal Club逆向工程，支援8種學術風格：

1. **經典學術** (classic_academic): 傳統學術語言，強調理論和方法
2. **現代學術** (modern_academic): 結合視覺化和數據，清晰易懂
3. **臨床導向** (clinical): 強調臨床應用和病例分析
4. **研究方法** (research_methods): 著重研究設計和統計分析
5. **文獻回顧** (literature_review): 系統性文獻整理和比較
6. **案例分析** (case_analysis): 以具體案例為主的深入分析
7. **教學導向** (teaching): 循序漸進易懂，適合學習者
8. **Zettelkasten卡片盒** (zettelkasten): 原子化筆記，每張投影片為獨立知識單元 ✨ NEW

### 5種詳細程度

- **極簡** (minimal): 2-3點/張，1句話/點
- **簡要** (brief): 3-4點/張，1-2句話/點
- **標準** (standard): 4-5點/張，2-3句話/點 ⭐ 默認
- **詳細** (detailed): 5-6點/張，3-4句話/點
- **完整** (comprehensive): 6-8點/張，4-5句話/點

### 3種語言模式

- **中文** (chinese): 繁體中文
- **英文** (english): English
- **中英雙語** (bilingual): 中文為主，關鍵術語附英文

**配置**: `templates/styles/academic_styles.yaml`

## Slash Commands

### /analyze-paper

分析論文並提取關鍵信息

```bash
/analyze-paper <pdf_path> [--add-to-kb] [--style <style>] [--format <format>]
```

**參數**:
- `pdf_path`: PDF文件路徑（必需）
- `--add-to-kb`: 加入知識庫
- `--style`: 學術風格（默認：modern_academic）
- `--format`: 輸出格式（markdown/json/pptx/all）

**示例**:
```bash
/analyze-paper paper.pdf --add-to-kb --format all
```

**完整說明**: `.claude/commands/analyze-paper.md`

## Slide Maker 投影片生成器

### 核心功能

基於Journal Club架構的多風格學術投影片生成系統，支援多種LLM後端和三種工作流模式。

**主要文件**: `src/generators/slide_maker.py`, `make_slides.py`

### 使用方式

```bash
# 基本用法：從主題生成投影片
python make_slides.py "深度學習應用" --style modern_academic --slides 15

# 從PDF直接生成（快速模式）
python make_slides.py "論文摘要" --pdf paper.pdf --style research_methods

# 從PDF分析後生成（知識驅動模式，推薦）
python make_slides.py "論文摘要" --pdf paper.pdf --analyze-first --style literature_review

# 從知識庫已有論文生成（重用模式）
python make_slides.py "論文簡報" --from-kb 1 --style modern_academic

# 使用Google Gemini生成（更快）
python make_slides.py "AI研究" --pdf paper.pdf --llm-provider google --model gemini-2.5-flash

# 生成雙語投影片
python make_slides.py "機器學習入門" --style teaching --language bilingual --slides 20
```

### 參數說明

| 參數 | 說明 | 可選值 | 默認值 |
|------|------|--------|--------|
| `topic` | 簡報主題 | 任意文字 | 必需 |
| `--pdf` | PDF文件路徑 | 文件路徑 | - |
| `--analyze-first` | 先分析PDF並加入知識庫 | 標記 | False |
| `--from-kb` | 從知識庫論文ID生成 | 整數 | - |
| `--style` | 學術風格 | 8種風格 | modern_academic |
| `--detail` | 詳細程度 | 5種程度 | standard |
| `--language` | 語言模式 | chinese/english/bilingual | chinese |
| `--slides` | 投影片數量 | 整數 | 15 |
| `--llm-provider` | LLM提供者 | auto/ollama/google/openai/anthropic | auto |
| `--model` | 模型名稱 | 依提供者 | gemma2:latest |
| `--output` | 輸出路徑 | 文件路徑 | 自動生成 |

### 多LLM支持

系統支援4種LLM後端，並具備自動偵測和故障轉移：

1. **Ollama** (本地)
   - 模型：gemma2:latest, llama3, mistral等
   - URL：http://localhost:11434
   - 優點：完全離線、數據隱私

2. **Google Gemini**
   - 模型：gemini-2.0-flash-exp, gemini-pro
   - 需要：GOOGLE_API_KEY環境變數
   - 優點：速度快、品質高、有免費額度

3. **OpenAI**
   - 模型：gpt-4, gpt-3.5-turbo
   - 需要：OPENAI_API_KEY環境變數
   - 優點：品質最高、功能完整

4. **Anthropic Claude**
   - 模型：claude-3-haiku（成本最低）, claude-3-opus, claude-3-sonnet
   - 需要：ANTHROPIC_API_KEY環境變數
   - 優點：推理能力強、長文處理佳、haiku版本速度快且便宜

**自動選擇邏輯**：
```python
# --llm-provider auto 時的優先順序
1. Google Gemini (如果API key可用)
2. OpenAI (如果API key可用)
3. Anthropic Claude (如果API key可用)
4. Ollama (如果服務運行中)
5. 失敗並提示用戶
```

### 三種工作流模式

**1. 快速模式**（直接從PDF）
```bash
python make_slides.py "主題" --pdf paper.pdf
```
- 直接提取PDF文字生成投影片
- 速度最快
- 適合快速預覽

**2. 知識驅動模式**（推薦）
```bash
python make_slides.py "主題" --pdf paper.pdf --analyze-first
```
- 先用 `analyze_paper.py` 分析PDF
- 提取結構化信息（標題、作者、章節）
- 保存到知識庫
- 從結構化內容生成投影片
- **品質最高、內容最準確**

**3. 重用模式**（從知識庫）
```bash
python make_slides.py "主題" --from-kb <paper_id>
```
- 從已有知識庫論文生成
- 無需重新分析
- 可用不同風格重複生成

### 格式改進功能

系統包含智能排版功能，自動防止內容溢出：

**智能字體調整**：
- 內容 >1000字 或 >8項：11pt字體 + 0.9行距
- 內容 800-1000字 或 6-8項：12pt字體 + 1.0行距
- 內容 600-800字 或 5-6項：14pt字體 + 1.1行距
- 內容 400-600字：16pt字體 + 1.2行距
- 內容 <400字：18pt字體 + 1.3行距

**標題提取**：自動從LLM輸出提取真實標題而非「投影片1」

### 輸出格式

生成的PPTX文件包含：
- 標題頁：主標題和副標題
- 內容頁：自動格式化的項目符號列表
- 16:9寬螢幕格式
- 自動文字換行和縮放

### API密鑰配置

在專案根目錄創建 `.env` 文件：
```bash
# Google Gemini
GOOGLE_API_KEY=your-google-api-key-here

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Ollama（本地，無需API key）
OLLAMA_URL=http://localhost:11434
```

### 故障排除

**問題1：Ollama timeout**
```bash
# 使用雲端LLM代替
python make_slides.py "主題" --llm-provider google --model gemini-2.0-flash-exp
```

**問題2：內容不符合PDF**
- 確保使用 `--analyze-first` 或 `--from-kb`
- 檢查知識庫Markdown文件是否包含完整內容

**問題3：LLM連接失敗**
```bash
# 檢查API key
echo $GOOGLE_API_KEY

# 測試Ollama
curl http://localhost:11434/api/tags
```

## Skills參考

### pdf-extractor

PDF文本和結構提取

**說明**: `.claude/skills/pdf-extractor.md`

### slide-maker ✅

基於Journal Club的多風格學術投影片生成

**說明**: `.claude/skills/slide-maker.md`
**實作**: `src/generators/slide_maker.py`, `make_slides.py`

**特性**:
- 8種學術風格 × 5種詳細程度 × 3種語言
- 多LLM後端支持（Ollama、Gemini、OpenAI、Claude）
- 三種工作流模式（快速/知識驅動/重用）
- 智能排版和格式優化

### kb-connector ✅

知識庫連接和管理

**說明**: `.claude/skills/kb-connector.md`

### 待實作Skills

- **note-writer**: 結構化Markdown筆記生成
- **viz-generator**: 科學視覺化產品生成

## 配置管理

主配置文件: `config/settings.yaml`

### 重要配置項

```yaml
# LLM後端（自動選擇最佳模型）
llm:
  default_backend: "auto"  # 自動選擇最佳模型
  auto_select: true
  ollama:
    base_url: "http://localhost:11434"
    default_model: "gemma2:latest"

# PDF處理
pdf:
  max_characters: 50000
  extraction_method: "pdfplumber"

# 簡報生成
slides:
  default_style: "modern_academic"
  default_detail: "standard"
  default_language: "chinese"

# 知識庫
knowledge_base:
  root_directory: "knowledge_base"
  database_path: "knowledge_base/index.db"
  indexing:
    auto_index: true
    full_text_search: true
```

## 與SciMaker的整合

本專案複用了SciMaker (D:\Apps\LLM\SciMaker) 的以下資源：

### Prompt Templates

來源: `journal_club_analysis/prompt_templates.txt`
位置: `templates/prompts/raw_templates.txt`

包含22個完整的prompt模板，涵蓋：
- 7種學術風格變體
- 3種語言模式
- 投影片格式規範

### 學術風格定義

基於Journal Club的風格系統，提取並結構化為YAML配置。

### Ollama整合模式

參考SciMaker的本地LLM推理架構：
- Modelfile配置
- API調用邏輯
- 繁體中文優化

### Persona系統（可選）

SciMaker的persona記憶文件可選擇性整合：
- feynman_memory.md: 物理教育
- elon_musk_memory.md: 工程創新
- eren_jaeger_memory.md: 動機韌性
- frieren_memory.md: 長期智慧

## 開發指南

### 新增Skill

1. 在 `src/` 中實作功能模組
2. 在 `.claude/skills/` 中創建Skill文檔
3. 更新本文檔的Skills參考區

### 新增Agent

1. 在 `.claude/agents/` 中創建Agent定義
2. 描述Agent的任務、能力和調用的Skills
3. 提供使用示例

### 新增Slash Command

1. 在 `.claude/commands/` 中創建命令文檔
2. 說明參數、功能流程和示例
3. 實作對應的Python腳本（如需要）

### 修改Prompt模板

1. 編輯 `templates/prompts/journal_club_template.jinja2`
2. 或在 `templates/styles/academic_styles.yaml` 中調整風格定義
3. 測試不同參數組合的輸出

### 擴展知識庫

1. 修改 `src/knowledge_base/kb_manager.py` 添加新功能
2. 更新數據庫結構（如需要）
3. 更新 `.claude/skills/kb-connector.md` 文檔

## 常用命令

```bash
# 測試PDF提取
python src/extractors/pdf_extractor.py paper.pdf

# 測試知識庫
python src/knowledge_base/kb_manager.py

# 安裝新依賴後更新
pip freeze > requirements.txt

# 查看知識庫統計
python -c "from src.knowledge_base import KnowledgeBaseManager; kb = KnowledgeBaseManager(); print(kb.get_stats())"
```

## 故障排除

### PDF提取失敗

```python
# 嘗試切換提取方法
extractor = PDFExtractor(method="pypdf2")  # 或 "pdfplumber"
```

### 知識庫索引錯誤

```bash
# 重新初始化數據庫
rm knowledge_base/index.db
python -c "from src.knowledge_base import KnowledgeBaseManager; KnowledgeBaseManager()"
```

### Ollama連接失敗

```bash
# 檢查Ollama是否運行
curl http://localhost:11434/api/tags

# 啟動Ollama
ollama serve
```

## 未來擴展方向

### 短期 (1-2個月)
- ✅ 完成pdf-extractor和kb-connector Skills
- ✅ 實作slide-maker Skill（基於Journal Club）
  - ✅ 多LLM支持（Ollama/Gemini/OpenAI/Claude）
  - ✅ 8種學術風格 + Zettelkasten
  - ✅ 智能排版和格式優化
  - ✅ 三種工作流模式
- 🔄 實作note-writer Skill
- 🔄 創建literature-analyzer Agent

### 中期 (3-6個月)
- 📅 實作viz-generator Skill
- 📅 批量處理功能 (/batch-analyze)
- 📅 知識圖譜視覺化
- 📅 向量搜索整合（本地embeddings）

### 長期 (6-12個月)
- 📅 Web介面開發
- 📅 多用戶協作
- 📅 插件系統
- 📅 與其他研究工具整合

## 參考資源

### 內部文檔
- Journal Club分析: `D:\Apps\LLM\SciMaker\journal_club_analysis\`
- SciMaker文檔: `D:\Apps\LLM\SciMaker\CLAUDE.md`
- 實施計畫: `D:\Apps\LLM\SciMaker\create_plan.py`

### 外部資源
- Claude Code文檔: https://docs.claude.com/claude-code
- python-pptx文檔: https://python-pptx.readthedocs.io/
- SQLite FTS5: https://www.sqlite.org/fts5.html
- Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md

## 授權與致謝

本專案基於SciMaker的Journal Club模組逆向工程成果，感謝原始系統的設計理念和實作參考。

---

**最後更新**: 2025-11-01
**版本**: 0.6.0-alpha
**狀態**: 自動模型選擇系統完成 - 智能LLM選擇與成本控制實作完成

### 本次更新 (2025-11-01) ⭐ 文檔一致性檢查與修正

**📝 文檔一致性更新**

本次更新檢查並修正了 CLAUDE.md 和 README.md 之間的不一致之處。

#### **修正內容**:

1. **版本號統一**：
   - README.md 版本從 0.2.0-alpha 更新為 0.6.0-alpha
   - 與 CLAUDE.md 保持一致

2. **LLM 模型名稱更新**：
   - Google Gemini: gemini-2.5-flash → gemini-2.0-flash-exp
   - Anthropic Claude: 新增 claude-3-haiku 描述（成本最低版本）
   - 與實際配置檔 model_selection.yaml 保持一致

3. **配置範例更新**：
   - default_backend: "ollama" → "auto"
   - 新增 auto_select: true
   - 反映最新的自動模型選擇功能

4. **日期更新**：
   - 更新為 2025-11-01

#### **驗證結果**:
- ✅ 所有主要檔案均存在（analyze_paper.py, kb_manage.py, make_slides.py 等）
- ✅ 新增模組檔案均存在（model_monitor.py, usage_reporter.py, batch_processor.py 等）
- ✅ 配置檔與文檔描述一致

---

### 前次更新 (2025-10-29) ⭐ Phase 1 完成

**🚀 重大更新：批次處理器 + 質量檢查器 + 檔案整理系統**

本次更新完成了 AGENT_SKILL_DESIGN.md 中的 Phase 1 所有P0優先級任務，建立了穩定的批次處理和質量控制基礎設施。

#### **新增模組**:

**1. 批次處理器 (Batch Processor)** ✅
- **檔案**: `src/processors/batch_processor.py` (570行)、`batch_process.py` (237行)
- **功能**: 穩定地批次處理大量PDF文件
  - ThreadPoolExecutor平行處理（預設3個worker）
  - 完整錯誤處理：skip/retry/stop三種策略
  - Windows路徑支援：pathlib.Path處理中文和特殊字元
  - Timeout機制：300秒/PDF
  - 進度追蹤：實時顯示 `[1/15] ✅ Paper1.pdf`
  - 整合知識庫和Zettelkasten生成
  - 背景執行相容性：修復`sys.stdin.isatty()`檢測問題
- **數據結構**:
  - `ProcessResult`: 單文件處理結果
  - `BatchResult`: 批次處理總結（含JSON/文本報告）
- **測試**: 2篇PDF測試通過（1成功，1 timeout）
- **文檔**: `.claude/skills/batch-processor.md` 完整Skill文檔

**2. 質量檢查器 (Quality Checker)** ✅
- **檔案**: `src/checkers/quality_checker.py` (801行)、`check_quality.py` (312行)
- **功能**: 檢查知識庫論文元數據質量
  - **5大檢查項目**: 標題、作者、年份、摘要、關鍵詞
  - **290行YAML規則**: `quality_rules.yaml` 可自訂檢查規則
  - **質量評分系統**: 0-100分，5個等級（優秀/良好/可接受/較差/嚴重）
  - **重複檢測**: 相似度演算法（標題60% + 作者30% + 年份10%）
  - **自動修復**: 架構完成（API整合待實作）
  - **Windows編碼修復**: UTF-8輸出支援emoji
- **實測結果**（30篇論文）:
  - 平均評分: 68.2/100
  - 發現79個問題（50個嚴重、20個警告）
  - 最常見問題: 缺少年份(100%)、關鍵詞不足(67%)、摘要缺失(53%)
  - 檢測到2篇無效標題格式（"Journal Pre-proof"、URL）
  - 無重複論文（0.85閾值）
- **CLI特性**:
  - 多種詳細程度（minimal/standard/comprehensive）
  - 過濾選項（--critical-only、--min-score）
  - 重複檢測（--detect-duplicates --threshold 0.85）
  - 多格式輸出（text/json）

**3. 檔案整理系統 (Session Organizer)** ✅
- **檔案**: `src/utils/session_organizer.py` (397行)、`cleanup_session.py`
- **功能**: 自動整理工作階段產生的檔案
  - 整理PDF分析結果、簡報、Zettelkasten到專屬資料夾
  - 清理臨時檔案（.log、.tmp、cache）
  - 安全保護：不刪除.git、src、知識庫等重要目錄
  - 自動備份知識庫（index.db）
  - Dry-run模式預覽變更
  - 詳細清理報告（Markdown格式）
- **配置**: `src/utils/cleanup_rules.yaml` YAML規則定義
- **整合**: 批次處理完成後自動詢問是否執行整理

#### **架構改進**:

**新增目錄結構**:
```
src/
├── processors/           # 批次處理模組
│   ├── batch_processor.py
│   └── __init__.py
├── checkers/            # 質量檢查模組
│   ├── quality_checker.py
│   ├── quality_rules.yaml
│   └── __init__.py
└── utils/               # 工具模組
    ├── session_organizer.py
    ├── cleanup_rules.yaml
    └── __init__.py
```

**新增CLI工具**:
- `batch_process.py`: 批次處理命令列工具
- `check_quality.py`: 質量檢查命令列工具
- `cleanup_session.py`: 檔案整理命令列工具

#### **技術細節**:

**Windows相容性增強**:
1. UTF-8編碼強制：`io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`
2. 路徑正規化：`pathlib.Path` 處理中文路徑和特殊字元
3. 終端檢測：`sys.stdin.isatty()` 避免背景執行EOFError

**錯誤處理改進**:
1. Timeout機制：subprocess.run(timeout=300)
2. 重試邏輯：可配置重試次數和策略
3. 錯誤報告：詳細記錄失敗原因和堆疊追蹤

**測試覆蓋**:
- ✅ 批次處理器：2個PDF文件測試（1成功、1 timeout）
- ✅ 質量檢查器：30篇論文完整檢查
- ✅ 檔案整理：test文件創建和清理
- ✅ 重複檢測：30篇論文相似度計算
- ✅ 報告生成：text/json格式輸出

#### **已知問題與限制**:

1. **批次處理**:
   - 大型PDF可能超時（300秒限制）
   - 多個worker可能觸發API rate limiting
   - 建議worker數: 2-4個

2. **質量檢查**:
   - 自動修復功能架構完成但未實作（需外部API整合）
   - CrossRef/Semantic Scholar API整合為下階段任務
   - 某些規則需根據實際使用調整閾值

3. **知識庫元數據問題**:
   - 所有論文缺少年份（analyze_paper.py未提取）
   - 67%論文關鍵詞不足
   - 53%論文摘要缺失
   - 需改進PDF提取器的元數據提取能力

#### **文檔更新**:
- ✅ CLAUDE.md 新增批次處理器和質量檢查器完整說明
- ✅ 架構圖更新（新增processors/、checkers/、utils/）
- ✅ 核心模組說明（共250行詳細文檔）
- ✅ 實測結果和使用建議

#### **下一步計畫** (Phase 1 後續):
1. **外部API整合** (P1優先級):
   - CrossRef API: DOI查詢和元數據增強
   - Semantic Scholar API: 標題查詢和引用資訊
   - 實作自動修復功能
2. **PDF提取改進**:
   - 增強年份提取（從PDF metadata和內容）
   - 改進關鍵詞提取（使用TF-IDF或LLM）
3. **知識庫元數據修復**:
   - 批次執行質量檢查
   - 修復30篇現有論文的缺失元數據

---

### 前次更新 (2025-10-28 晚間)

**🎓 學術標準化改進 + 完整系統測試**

**Zettelkasten核心改進**:
- ✅ **核心概念直接擷取原文**
  - 不翻譯、不改寫，保持學術嚴謹性
  - 支援英文/中文原文保留
  - 明確要求LLM逐字引用（附範例指導）
- ✅ **AI/人類筆記明確標記**
  - `**[AI Agent]**:` AI生成的批判性思考
  - `**[Human]**: (TODO)` 人類待補充區域
  - HTML註釋提示使用者添加內容
- ✅ **AI筆記品質提升**
  - 要求批判性思考、質疑、反思
  - 指出概念局限性與爭議點
  - 連結相關理論與研究
- ✅ **ID格式自動修復**
  - 正則表達式自動轉換錯誤格式
  - `CogSci20251028001` → `CogSci-20251028-001`

**完整系統測試**（2篇論文）:

**測試1: Crockett-2025.pdf** (AI Surrogates)
- ✅ 教學導向Markdown簡報（25張，comprehensive）
  - 535行，19KB
  - 循序漸進、概念詳解
  - Marp相容格式
- ✅ Zettelkasten原子筆記（12張卡片，CogSci領域）
  - 語義化ID測試成功
  - 概念連結網絡完整
  - Mermaid視覺化

**測試2: Allassonnière-Tang-2021.pdf** (Noun Categorization)
- ✅ 加入知識庫（ID: 2）
- ✅ 現代學術風格雙格式簡報（21張，detailed）
  - PPTX: 53KB，智能排版
  - Markdown: 11KB，389行
  - 涵蓋語言演化完整內容
- ✅ 改進版Zettelkasten（12張卡片，Linguistics領域）
  - **核心概念全部為英文原文**（驗證成功）
  - AI筆記包含深度批判性思考
  - 人類TODO提示清晰

**發現的問題**:
- ⚠️ 簡報有繁簡中文混合（待修復Prompt）
- ⚠️ 知識庫標題為URL時導致路徑錯誤（已workaround）

**測試成果統計**:
- 論文分析：2篇（已入庫）
- 簡報生成：4個（教學MD、現代學術PPTX+MD）
- Zettelkasten：2套（舊版+改進版，共24張卡片）
- 格式穩定性：100%
- 內容準確性：高（正確反映原文）
- 學術嚴謹性：提升（原文保留）

---

### 早間更新 (2025-10-28)

**🎉 重大更新：Markdown輸出與Zettelkasten原子筆記**

**新增功能**:
- ✅ **Markdown簡報格式支援**（相容Marp/reveal.js）
  - 通用學術風格Markdown模板
  - 支援 `--format markdown/pptx/both` 參數
  - 自動格式化為投影片結構
- ✅ **Zettelkasten原子筆記系統**
  - 專用生成器 `zettel_maker.py`
  - 語義化ID格式（`領域-日期-序號`，如 `AI-20251028-001`）
  - 雙檔案輸出（索引 + 獨立卡片文件）
  - 概念連結網絡（基於/導向/相關/對比/上位/下位）
  - 支援4種卡片類型（concept/method/finding/question）
  - Mermaid圖表視覺化概念網絡
- ✅ **增強的配置系統**
  - Zettelkasten專屬配置（連結語義、ID格式、卡片數量）
  - 專用Prompt模板 `zettelkasten_template.jinja2`
  - 可調整領域代碼（`--domain` 參數）

**架構改進**:
- `src/generators/zettel_maker.py`: 原子筆記生成核心
- `templates/markdown/`: 新增3個Jinja2模板
  - `zettelkasten_card.jinja2`: 單張卡片模板
  - `zettelkasten_index.jinja2`: 索引與網絡圖
  - `academic_slides.jinja2`: 通用Markdown簡報
- `templates/prompts/zettelkasten_template.jinja2`: Zettelkasten專用Prompt
- `make_slides.py`: 整合Zettelkasten模式與格式選擇

**使用範例**:
```bash
# Zettelkasten原子筆記（自動Markdown）
python make_slides.py "深度學習" --pdf paper.pdf --style zettelkasten --domain AI

# Markdown簡報格式
python make_slides.py "研究方法" --pdf paper.pdf --format markdown --style modern_academic

# 同時生成PPTX和Markdown
python make_slides.py "文獻回顧" --pdf paper.pdf --format both --style literature_review
```

**輸出範例**（Zettelkasten）:
```
output/zettel_AI_20251028/
├── zettel_index.md          # 索引+概念網絡圖+標籤分類
└── zettel_cards/
    ├── AI-20251028-001.md   # 獨立原子卡片
    ├── AI-20251028-002.md
    └── ...
```

---

### 前次更新 (2025-10-27)

**完成功能**:
- ✅ Slide-maker Skill完整實作
- ✅ 多LLM後端支持（4種：Ollama/Gemini/OpenAI/Claude）
- ✅ 8種學術風格（新增Zettelkasten）
- ✅ 智能排版系統（自動字體調整、防溢出）
- ✅ 三種工作流模式（快速/知識驅動/重用）
- ✅ 知識庫內容儲存修復（Markdown包含完整PDF文字）
- ✅ 投影片格式優化（標題提取、動態行距）

**修復問題**:
1. 知識庫Markdown空白內容問題
2. 投影片標題顯示「投影片1」而非實際標題
3. 文字內容溢出投影片邊界
4. Google Gemini API整合和模型名稱

**測試結果**:
- 成功分析 Crockett-2025.pdf ("AI Surrogates and illusions of generalizability")
- 生成21張高品質文獻回顧風格投影片
- 內容準確度大幅提升（從幻覺內容→正確反映原文）
- 格式問題完全解決

---

### 本次更新 (2025-10-31) ⭐ 自動模型選擇系統完成

**🚀 重大更新：智能LLM模型選擇與成本控制系統**

本次更新完成了智能的LLM模型選擇系統，實現了自動根據任務需求、成本限制和效能指標選擇最佳模型的功能。

#### **核心功能**:

**1. 智能模型選擇**
- **自動檢測可用模型**: 檢查API keys和服務狀態
- **任務導向選擇**: 根據任務類型（zettelkasten、academic_slides等）選擇最佳模型
- **風格導向選擇**: 根據學術風格（research_methods、teaching等）優化模型選擇
- **策略模式**: 支援balanced、quality_first、cost_first、speed_first四種策略

**2. 成本控制與監控**
- **實時成本追蹤**: 記錄每次API調用的token使用和成本
- **多層級限制**: 支援會話、每日、每月成本限制
- **自動切換機制**: 接近成本限制時自動切換到免費模型
- **配額管理**: 追蹤Gemini等免費配額使用情況

**3. 使用報告生成**
- **每日報告**: 包含總覽、模型使用詳情、任務分布、錯誤記錄
- **週報告**: 週總覽、每日趨勢、模型排行、成本分析、優化建議
- **Markdown格式**: 易讀的表格和統計圖表

**4. CLI增強**
```bash
# 新增的CLI參數
--selection-strategy balanced  # 選擇策略
--max-cost 0.5                # 成本限制
--usage-report                 # 生成使用報告
--monitor                      # 啟用詳細監控
```

#### **實作文件**:

| 文件 | 功能 | 行數 |
|------|------|------|
| `config/model_selection.yaml` | 模型定義與映射配置 | 309行 |
| `src/utils/model_monitor.py` | 使用監控與成本追蹤 | 441行 |
| `src/utils/usage_reporter.py` | 報告生成器 | 321行 |
| `src/generators/slide_maker.py` | 整合智能選擇邏輯 | 新增約200行 |
| `make_slides.py` | CLI參數支援 | 新增約100行 |

#### **測試結果**:
- ✅ Claude 3 Haiku成功整合並測試
- ✅ Google Gemini免費配額追蹤正常
- ✅ 自動模型選擇邏輯運作正常
- ⚠️ MiniMax-M2僅CLI支援，JSON格式仍有問題

---

### 前次更新 (2025-10-30) ⭐ Workflows重新設計

**🎯 重大更新：KB Manager Agent工作流程重新設計**

本次更新重新設計了KB Manager Agent的工作流結構，明確區分兩種獨立的工作流程，提升用戶體驗和系統清晰度。

#### **核心變更**:

**1. 工作流重新命名和職責分離**
- `batch_import` → **`batch_import_papers`**（批次導入論文到知識庫）
  - 專注於「知識庫管理」單一職責
  - 移除 `generate_zettel` 參數（避免混淆）
  - `domain` 移除默認值，強制用戶選擇（支援自定義領域）

- `generate_notes` → **`batch_generate_zettel`**（批次生成Zettelkasten）
  - 重新命名反映批次處理能力（流程A）
  - `source` 支援 folder_path（批次）、pdf_path（單篇）和 paper_id
  - `domain` 移除默認值，強制用戶選擇（支援自定義領域）
  - 新增 `add_to_kb` 和 `auto_link` 參數（默認為 true）
  - 提升優先級為 `high`

- `generate_slides` → 保持不變（流程B）
  - 明確標註：**只生成簡報**，不生成Zettelkasten
  - 不在對話中詢問「是否生成Zettelkasten」

**2. 參數設計改進**
- **domain 支援自定義**: 保留 ["CogSci", "Linguistics", "AI", "Research", "Other"] 預設選項，同時允許輸入自定義領域名稱
- **batch_generate_zettel 新增參數**:
  - `add_to_kb`: default = true（自動加入知識庫）
  - `auto_link`: default = true（自動關聯論文）
  - `source`: 支援資料夾/PDF/paper_id（統一入口）

**3. 技術實施**:

**修改檔案**:
| 檔案 | 修改內容 | 行數 |
|------|---------|------|
| `workflows.yaml` | 重新命名、調整參數、移除generate_zettel | ~50行 |
| `instructions.md` | 新增流程A章節、更新流程B說明、範例對話 | ~100行 |
| `batch_processor.py` | 支援單個PDF文件路徑 | ~30行 |

**batch_processor.py 增強**:
```python
def _find_pdfs(self, path: str) -> List[str]:
    """
    支援:
    - 資料夾路徑: 返回所有PDF文件
    - 單個PDF路徑: 返回包含該文件的列表
    """
    path_obj = Path(path)

    if path_obj.is_file() and path_obj.suffix.lower() == '.pdf':
        return [str(path_obj)]  # 支援單個PDF ✅

    if path_obj.is_dir():
        return [str(f) for f in path_obj.glob("*.pdf")]

    return []
```

#### **工作流程對比**:

| 項目 | 流程A（batch_generate_zettel） | 流程B（generate_slides） |
|------|-------------------------------|-------------------------|
| **用途** | 批次生成Zettelkasten原子筆記 | 生成學術簡報（PPTX/Markdown） |
| **輸入** | 資料夾/PDF/paper_id | PDF/paper_id/topic |
| **批次支援** | ✅ 是 | ❌ 否（單篇） |
| **生成Zettelkasten** | ✅ 是（主要功能） | ❌ 否 |
| **生成簡報** | ❌ 否 | ✅ 是（主要功能） |
| **知識庫整合** | ✅ 自動（add_to_kb=true） | ✅ 自動 |
| **自動關聯論文** | ✅ 是（auto_link=true） | N/A |

#### **範例對話**:

**流程A（批次生成Zettelkasten）**:
```
用戶: 批次處理 D:\pdfs\mental_simulation 並生成Zettelkasten
Agent: 好的！請問這些論文屬於哪個領域？（必填）
      1. CogSci（認知科學）
      2. Linguistics（語言學）
      3. AI（人工智慧）
      4. Research（通用研究）
      5. Other（或輸入自定義領域）

用戶: CogSci

Agent: 每篇論文生成多少張卡片？(默認：20)

用戶: 默認

Agent: ✅ 開始處理...
      [1/15] 處理中: paper1.pdf → 生成20張卡片
      ...
      完成！卡片總數: 300張
      已加入知識庫並自動關聯（成功率: 95%）
```

**流程B（只生成簡報）**:
```
用戶: 為 Crockett-2025.pdf 生成簡報
Agent: 好的！請告訴我簡報主題？

用戶: AI 代理者與認知科學研究

Agent: 選擇簡報風格：
      1. modern_academic（現代學術）
      2. teaching（教學導向）
      ...

用戶: teaching

Agent: ✅ 簡報生成完成！
      文件路徑: output/AI代理者_teaching.pptx
      （不詢問「是否生成Zettelkasten」）⚠️
```

#### **文檔更新**:
- ✅ `workflows.yaml`: 工作流重新命名和參數調整
- ✅ `instructions.md`: 新增流程A章節、更新流程B說明
- ✅ `batch_processor.py`: 支援單個PDF文件
- ✅ `WORKFLOWS_REDESIGN_FEASIBILITY.md`: 完整可行性評估報告
- ✅ `KB_MANAGER_WORKFLOW_REVIEW.md`: 工作流程確認報告

#### **驗收標準**:
- ✅ 流程A支援批次和單篇處理
- ✅ 流程B只生成簡報，不提示Zettelkasten
- ✅ domain支援自定義領域名稱
- ✅ 參數互不衝突，職責分離清晰
- ✅ 向後兼容，保留原有結構

#### **影響範圍**:
- 用戶體驗: 更清晰的工作流選擇
- Agent引導: 明確的意圖識別和引導邏輯
- 系統架構: 職責分離，易於維護

#### **下一步**:
- 準備進入 Phase 2 開發（relation-finder、concept-mapper）
- 基於新的工作流結構開發後續功能
- 持續優化用戶體驗和系統穩定性

---

**更新時間**: 2025-10-30 22:00
**實施工作量**: 3小時（符合預估）
**狀態**: ✅ **工作流重新設計完成**
- 設計及測試Agent, Skill的工作告一段落，要更新AGENT—SKILL—DESIGN.md的“當前狀態摘要”到"目錄“之間摘要及建議內容，並以此做為整理工作過程產生之檔案的整理參考。
- bib file path = "D:\core\Research\Program_verse\+\My Library.bib"
- Create and update code in English. 用繁體中文輸出給人類用戶的說明及報告。