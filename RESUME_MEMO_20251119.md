# Resume Memo - 2025-11-19 Session

**Status**: ✅ Option A Completed | 📋 Option B Documented for Next Session

---

## 執行摘要 (Executive Summary)

**完成任務**:
- ✅ 成功導入 6 篇正式項目論文（首批 AI Literacy 研究文獻）
- ✅ 生成並導入 144 張 Zettelkasten 原子卡片到知識庫
- ✅ 生成向量嵌入（Vector Embeddings）用於語義搜索
- ✅ 修復知識庫數據庫模式問題（添加 cite_key 欄位）
- ✅ 創建手動導入工具 `import_existing_zettel.py`

**待處理任務**:
- 🔄 生成概念網絡和 Obsidian 連結（需使用 UTF-8 terminal）
- 📝 修復 `batch_processor.py` 自動導入卡片功能（Option B）
- 🔧 改進 Zettelkasten 生成 Prompt（支援跨論文連結）

---

## Session 詳細記錄

### 1. 初始狀態

**知識庫狀態**: 已清空
- `knowledge_base/` 目錄已清理
- `output/` 目錄已清理
- 準備匯入首批 6 篇論文

**論文清單**:
1. Crockett-2025: "Teaching AI Literacy to Psychology Undergraduates"
2. Guest-2025 2: "What Does Human-Centred AI Mean?"
3. Guest-2025a: "Critical Artificial Intelligence Literacy for Psychology Researchers"
4. Günther-2025a: "LLMs in Psycholinguistics"
5. vanRooij-2025: "Combining Psychology with AI"
6. Vigly-2025: "Comprehension Effort as the Cost of Inference"

### 2. 執行流程（Option A: 分步處理）

#### 步驟 1: API Keys 驗證 ✅

**測試結果**:
```
✅ Google Gemini API (gemini-2.0-flash-exp)
✅ Anthropic Claude API (claude-3-5-sonnet-20241022)
✅ OpenRouter API (42 free models available)
```

**決策**: 使用 Gemini 2.0 Flash 進行批次處理（速度快、成本低）

#### 步驟 2: 批次 PDF 提取和 Zettelkasten 生成 ✅

**執行命令**:
```bash
python batch_process.py \
  --files \
    "D:/core/research/Program_verse/+/pdf/Crockett-2025.pdf" \
    "D:/core/research/Program_verse/+/pdf/Guest-2025 2.pdf" \
    "D:/core/research/Program_verse/+/pdf/Guest-2025a.pdf" \
    "D:/core/research/Program_verse/+/pdf/Günther-2025a.pdf" \
    "D:/core/research/Program_verse/+/pdf/vanRooij-2025.pdf" \
    "D:/core/research/Program_verse/+/pdf/Vigly-2025.pdf" \
  --domain "AI_literacy" \
  --add-to-kb \
  --generate-zettel \
  --detail comprehensive \
  --cards 20 \
  --llm-provider google \
  --model gemini-2.0-flash-exp \
  --workers 2 \
  --error-handling skip \
  --report "output/batch_import_report.json"
```

**處理結果**:
- ✅ 6/6 PDFs processed successfully (100% success rate)
- ⏱️ Processing time: 4 minutes 49 seconds
- 📁 Generated 6 Zettelkasten directories (~23 cards per paper)
- 📝 Generated 6 Markdown papers

**問題發現**:
- ❌ `papers_added_to_kb: 0` (論文未加入數據庫)
- ❌ Zettelkasten 卡片生成文件但未導入數據庫

#### 步驟 3: 修復數據庫模式 ✅

**問題**: Papers 表缺少 `cite_key` 欄位

**解決方案**:
```python
import sqlite3
conn = sqlite3.connect('knowledge_base/index.db')
cursor = conn.cursor()
cursor.execute('ALTER TABLE papers ADD COLUMN cite_key TEXT')
conn.commit()
conn.close()
```

**結果**: ✅ 成功添加欄位

#### 步驟 4: 手動導入論文 ✅

**執行命令** (每篇論文):
```bash
python analyze_paper.py --from-pdf <pdf_path> --add-to-kb
```

**結果**: 6 篇論文成功導入數據庫（paper_id 1-6）

#### 步驟 5: 生成向量嵌入 ✅

**執行命令**:
```bash
python generate_embeddings.py
```

**結果**:
- ✅ Generated embeddings for 6 papers
- 💰 Cost: ~$0.0012
- 📊 Model: Gemini embedding-001 (768 dimensions)
- 💾 Stored in: `chroma_db/`

#### 步驟 6: 創建手動導入工具 ✅

**問題**: `batch_processor.py` 生成 Zettelkasten 文件但未導入到 `zettel_cards` 表

**根本原因** (src/processors/batch_processor.py:356-362):
```python
# 步驟 2: 生成 Zettelkasten（如果需要）
if generate_zettel:
    zettel_dir = self._generate_zettelkasten(
        pdf_path_obj,
        domain=domain,
        paper_id=paper_id,
        config=zettel_config
    )
# ❌ Missing: No call to import cards to database after generation
```

**解決方案**: 創建 `import_existing_zettel.py` 手動導入工具

**工具特性**:
- 解析 Zettelkasten Markdown 卡片（標題、類型、核心概念、描述、標籤）
- 映射 cite_key 到 paper_id
- 批次導入到 `zettel_cards` 表
- 自動關聯卡片到對應論文（使用 `link_zettel_to_paper()`）

**導入結果**:
```
Total imported: 144 cards

Cards by paper:
  Paper 1 (Crockett-2025): 23 cards
  Paper 2 (Guest-2025 2): 23 cards
  Paper 3 (Guest-2025a): 23 cards
  Paper 4 (Günther-2025a): 24 cards
  Paper 5 (vanRooij-2025): 27 cards
  Paper 6 (Vigly-2025): 24 cards
```

**編碼問題修復**:
- Windows cp950 無法編碼 Unicode emoji (📥, ✅, ❌, ⚠️)
- 解決方案: 替換為 ASCII markers ([IMPORT], [OK], [ERROR], [WARN])
- Unicode cite_key (Günther) 使用 try-except 處理

#### 步驟 7: 驗證知識庫完整性 ✅

**最終統計**:
```json
{
  "total_papers": 6,
  "total_topics": 0,
  "total_citations": 0,
  "total_zettel_cards": 144,
  "total_zettel_links": 0,
  "total_zettel_domains": 1,
  "total_zettel_folders": 6
}
```

**驗證結果**:
- ✅ 6 Papers in database
- ✅ 144 Zettelkasten cards in database
- ✅ All cards linked to correct papers (paper_id 1-6)
- ⚠️ 0 zettel_links (links exist in Markdown content but not extracted)

**Links 狀態說明**:
- 卡片 Markdown 內容包含 `## 連結網絡` 區塊
- `import_existing_zettel.py` 未解析連結（傳遞空 `links` 列表）
- Phase 2.2 Concept Mapper 可以從 Markdown 提取連結（不影響功能）

---

## Option B: 需要修復的問題（下次 Session）

### 問題 1: batch_processor.py 未導入 Zettelkasten 卡片 ⭐⭐⭐⭐⭐

**優先級**: 極高（P0）

**問題描述**:
`batch_processor.py` 的 `_generate_zettelkasten()` 方法只生成文件，不導入到數據庫。

**當前行為**:
```python
# src/processors/batch_processor.py
def _generate_zettelkasten(self, pdf_path, domain, paper_id, config):
    # ... 生成 Zettelkasten 文件到 output/zettelkasten_notes/
    return zettel_dir  # ❌ 只返回目錄，未導入數據庫
```

**期望行為**:
```python
def _generate_zettelkasten(self, pdf_path, domain, paper_id, config):
    # ... 生成 Zettelkasten 文件

    # ✅ 添加: 導入到數據庫
    stats = self._import_zettel_to_kb(zettel_dir, paper_id, domain)

    return zettel_dir, stats
```

**修復步驟**:

1. **添加新方法** `_import_zettel_to_kb()`

```python
def _import_zettel_to_kb(self, zettel_dir: Path, paper_id: int, domain: str) -> Dict[str, int]:
    """
    導入 Zettelkasten 卡片到知識庫

    Args:
        zettel_dir: Zettelkasten 目錄路徑
        paper_id: 論文 ID
        domain: 領域代碼

    Returns:
        統計結果: {'imported': int, 'failed': int}
    """
    from src.knowledge_base import KnowledgeBaseManager

    kb = KnowledgeBaseManager()

    cards_dir = zettel_dir / 'zettel_cards'
    if not cards_dir.exists():
        return {'imported': 0, 'failed': 0}

    card_files = list(cards_dir.glob('*.md'))
    imported = 0
    failed = 0

    for card_file in card_files:
        try:
            # 使用 kb.parse_zettel_card() 解析
            card_data = kb.parse_zettel_card(str(card_file))

            if card_data:
                # 導入到數據庫
                card_id = kb.add_zettel_card(card_data)

                # 關聯到論文
                if card_id > 0:
                    kb.link_zettel_to_paper(card_id, paper_id)
                    imported += 1
                else:
                    failed += 1
            else:
                failed += 1

        except Exception as e:
            print(f"[ERROR] Failed to import {card_file.name}: {e}")
            failed += 1

    return {'imported': imported, 'failed': failed}
```

2. **修改 `_generate_zettelkasten()` 調用**

```python
# 在 process_single() 中
if generate_zettel:
    zettel_dir = self._generate_zettelkasten(
        pdf_path_obj,
        domain=domain,
        paper_id=paper_id,
        config=zettel_config
    )

    # ✅ 新增: 導入卡片到數據庫
    if zettel_dir:
        import_stats = self._import_zettel_to_kb(
            Path(zettel_dir),
            paper_id,
            domain
        )
        print(f"  [DB] Imported {import_stats['imported']} cards to database")
```

3. **更新 batch_import_report.json 格式**

```json
{
  "results": [
    {
      "file_path": "...",
      "paper_id": 1,
      "zettel_dir": "...",
      "zettel_imported_to_db": 23,  // ✅ 新增
      "zettel_failed_import": 0      // ✅ 新增
    }
  ]
}
```

**測試計畫**:
1. 清空 `zettel_cards` 表
2. 重新運行 `batch_process.py --generate-zettel`
3. 驗證 `zettel_cards` 表有 144 張卡片
4. 驗證 `zettel_links` 表有正確的連結數量

**預期結果**:
- ✅ 自動導入卡片到數據庫（無需手動工具）
- ✅ 自動提取並導入連結關係
- ✅ batch_import_report.json 包含導入統計

---

### 問題 2: Zettelkasten Prompt 不支援跨論文連結 ⭐⭐⭐

**優先級**: 高（P1）

**問題描述**:
當前 Prompt Template 只提供當前論文內容，無法生成跨論文的概念連結。

**當前行為**:
```jinja2
{% if pdf_content %}
參考論文內容（請優先依據以下論文內容提取原子化概念）：
{{ pdf_content | truncate(50000) }}
{% endif %}
```
- ❌ 只有當前論文的 50,000 字元內容
- ❌ 無知識庫上下文
- ❌ 無相關概念提示

**期望行為**:
```jinja2
{% if pdf_content %}
參考論文內容：
{{ pdf_content | truncate(40000) }}
{% endif %}

{% if existing_related_cards %}
**知識庫相關概念** (供參考建立跨論文連結):
{% for card in existing_related_cards %}
- [[{{ card.zettel_id }}]]: {{ card.title }} ({{ card.core_concept[:100] }})
{% endfor %}
{% endif %}
```

**修復步驟**:

1. **修改 `templates/prompts/zettelkasten_template.jinja2`**

在 Prompt 中添加知識庫上下文區塊：

```jinja2
{# 在 pdf_content 之後添加 #}

{% if existing_related_cards and existing_related_cards|length > 0 %}
---

**知識庫現有相關概念** (供建立跨論文連結參考):

以下是知識庫中與本論文主題相關的現有概念卡片，生成新卡片時可適當建立連結：

{% for card in existing_related_cards %}
- **[[{{ card.zettel_id }}]]**: {{ card.title }}
  - 核心: {{ card.core_concept[:150] }}
  - 類型: {{ card.card_type }}
  - 來源: {{ card.source_paper }}
{% endfor %}

**建立連結指引**:
- 如果新概念**基於**或**延伸**自上述任何概念，請在「連結網絡」中標註
- 如果新概念與上述概念**相關**或**對比**，也可建立連結
- 跨論文連結使用相同格式: `[[zettel_id]]`

---
{% endif %}
```

2. **修改 `src/generators/zettel_maker.py`**

在生成 Prompt 前查詢相關卡片：

```python
def generate_zettelkasten(self, paper_content, cite_key, ...):
    # ... 現有代碼

    # ✅ 新增: 查詢相關卡片
    related_cards = self._query_related_cards(
        paper_content,
        cite_key,
        limit=10
    )

    # ✅ 新增: 添加到 template 變數
    template_vars = {
        'topic': topic,
        'card_count': card_count,
        'pdf_content': paper_content,
        'cite_key': cite_key,
        'language': language,
        'existing_related_cards': related_cards  # ✅ 新增
    }

    # ... 生成 Prompt
```

3. **添加 `_query_related_cards()` 方法**

```python
def _query_related_cards(
    self,
    paper_content: str,
    cite_key: str,
    limit: int = 10
) -> List[Dict]:
    """
    查詢知識庫中與當前論文相關的卡片

    策略：
    1. 使用向量搜索查詢語義相似的卡片
    2. 排除同一論文的卡片（避免自我引用）
    3. 返回 Top N 最相關的卡片

    Args:
        paper_content: 論文內容
        cite_key: 當前論文 cite_key
        limit: 返回數量上限

    Returns:
        相關卡片列表
    """
    from src.knowledge_base import KnowledgeBaseManager
    import chromadb

    kb = KnowledgeBaseManager()

    # 方案 A: 使用向量搜索（需要 ChromaDB）
    try:
        chroma_client = chromadb.PersistentClient(path="chroma_db")
        collection = chroma_client.get_collection("zettel_cards")

        # 提取論文摘要（前 1000 字）用於查詢
        query_text = paper_content[:1000]

        results = collection.query(
            query_texts=[query_text],
            n_results=limit * 2  # 多查一些，因為要過濾
        )

        # 過濾掉同一論文的卡片
        related_cards = []
        for i, zettel_id in enumerate(results['ids'][0]):
            # 排除同一 cite_key 的卡片
            if not zettel_id.startswith(cite_key):
                card = kb.get_zettel_by_id(zettel_id)
                if card:
                    # 添加來源論文信息
                    if card['paper_id']:
                        paper = kb.get_paper_by_id(card['paper_id'])
                        card['source_paper'] = paper['cite_key'] if paper else 'Unknown'
                    related_cards.append(card)

                    if len(related_cards) >= limit:
                        break

        return related_cards

    except Exception as e:
        print(f"[WARN] Failed to query related cards: {e}")
        return []

    # 方案 B: Fallback 到關鍵詞匹配（如果向量搜索失敗）
    # ... (使用 FTS5 全文搜索)
```

**使用場景範例**:

假設已有卡片:
- `Crockett-2025-003`: "AI Literacy Frameworks"
- `Guest-2025a-005`: "Critical AI Thinking Skills"

生成新論文 `Günther-2025a` 的卡片時，LLM 看到：

```
**知識庫現有相關概念**:
- [[Crockett-2025-003]]: AI Literacy Frameworks
  - 核心: "AI literacy requires understanding both technical capabilities and societal implications"
  - 類型: concept
  - 來源: Crockett-2025
```

LLM 可能生成:
```markdown
## 連結網絡
**基於** ← [[Crockett-2025-003]]  # 跨論文連結！
**導向** → [[Günther-2025a-002]]
```

**測試計畫**:
1. 使用現有 6 篇論文測試
2. 生成第 7 篇論文的卡片（應自動建立跨論文連結）
3. 驗證 `zettel_links` 表包含 `is_cross_paper=TRUE` 的記錄

**預期效果**:
- ✅ 自動建立跨論文概念連結
- ✅ 知識網絡更加緊密和完整
- ✅ 支援 Phase 2.4 RelationFinder 改進

---

### 問題 3: 概念網絡生成需要 UTF-8 Terminal ⭐⭐

**優先級**: 中（P2）

**問題**:
`kb_manage.py visualize-network` 在 Windows CMD (cp950) 中失敗

**錯誤信息**:
```
ValueError('I/O operation on closed file.')
```

**解決方案**:
1. 使用 Windows Terminal (UTF-8)
2. 或設定環境變數: `set PYTHONIOENCODING=utf-8`
3. 或修改 `kb_manage.py` 強制使用 UTF-8 輸出

**執行命令** (下次 Session):
```bash
# 在 Windows Terminal 中執行
python kb_manage.py visualize-network --obsidian \
    --output output/concept_analysis \
    --min-confidence 0.4 \
    --top-n 50
```

**預期輸出**:
- `output/concept_analysis/concept_network.html` (D3.js 互動圖)
- `output/concept_analysis/obsidian/` (Obsidian 格式)
  - `suggested_links.md`
  - `key_concepts_moc.md`
  - `community_summaries/`

---

## 技術發現 (Technical Discoveries)

### 1. KnowledgeBaseManager API 說明

**正確的 `add_zettel_card()` 用法**:

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager()

# ✅ 正確: 傳遞字典參數
card_data = {
    'zettel_id': 'Crockett-2025-001',
    'title': '卡片標題',
    'content': '完整 Markdown 內容',
    'core_concept': '核心概念（從原文擷取）',
    'description': '說明段落',
    'card_type': 'concept',  # or 'method', 'finding', 'question'
    'domain': 'AI_literacy',
    'tags': ['tag1', 'tag2'],
    'file_path': '/path/to/card.md',
    'source_info': '"Paper Title" (2025)',
    'ai_notes': 'AI 生成的批判性筆記',
    'human_notes': '',
    'created_at': None,
    'links': [
        {
            'relation_type': '導向',
            'target_ids': ['Crockett-2025-002', 'Crockett-2025-003']
        }
    ]
}

card_id = kb.add_zettel_card(card_data)

# ✅ 關聯到論文
kb.link_zettel_to_paper(card_id, paper_id)
```

**錯誤用法** (會失敗):
```python
# ❌ 錯誤: 使用 keyword arguments
kb.add_zettel_card(
    card_id='Crockett-2025-001',
    paper_id=1,
    title='標題',
    ...
)
# TypeError: add_zettel_card() got an unexpected keyword argument 'card_id'
```

### 2. Windows 編碼問題處理

**問題**: Windows CMD 預設使用 cp950 編碼，無法處理 Unicode

**解決方案**:

**方法 1: 移除 Unicode 字元**
```python
# 替換 emoji 為 ASCII
print("[IMPORT] 導入中...")  # 而非 print("📥 導入中...")
```

**方法 2: Try-Except 處理**
```python
try:
    print(f"Processing: {cite_key}")
except UnicodeEncodeError:
    print(f"Processing: {cite_key.encode('ascii', 'replace').decode('ascii')}")
```

**方法 3: 使用 UTF-8 Terminal**
- Windows Terminal (推薦)
- 或設定 `set PYTHONIOENCODING=utf-8`

### 3. Zettelkasten Markdown 格式

**標準格式** (LLM 生成):
```markdown
---
id: Crockett-2025-001
title: 卡片標題
type: concept
tags: [tag1, tag2]
source: "Paper Title" (2025)
created: 2025-11-19
---

# 卡片標題

> **核心**: "Direct quote from the original paper in English or Chinese"

## 說明

詳細解釋此概念... (2-3 段落)

## 連結網絡

**基於** ← [[Crockett-2025-前置ID]]
**導向** → [[Crockett-2025-002]], [[Crockett-2025-003]]
**相關** ↔ [[Crockett-2025-005]]

## 來源脈絡

- **文獻**: [[Crockett-2025.pdf|Crockett (2025)]]
- **位置**: Introduction
- **情境**: 在介紹研究動機時提出

## 個人筆記

🤖 **AI**: [AI 生成的批判性思考，包含至少 1 個連結]

✍️ **Human**:

## 待解問題

[此概念引發的研究方向]
```

**解析規則**:
- YAML frontmatter: `id`, `title`, `type`, `tags`, `source`, `created`
- 核心概念: 正則表達式 `>\s*\*\*核心\*\*:\s*"(.+?)"`
- 說明: 正則表達式 `## 說明\n(.+?)(?=\n##|\Z)`
- 連結: `parse_zettel_links()` 方法提取
- AI 筆記: `\*\*\[AI Agent\]\*\*:\s*(.+?)`

### 4. Gemini 2.0 Flash 性能數據

**批次處理統計** (6 篇論文):
- ⏱️ 總時間: 4 分 49 秒
- 📄 平均每篇: 48 秒
- 💰 估計成本: ~$0.10 (API 調用)
- 📊 卡片生成: 144 張 (平均 24 張/篇)

**品質評估**:
- ✅ 中文輸出流暢
- ✅ 核心概念準確擷取原文
- ✅ 連結網絡結構完整
- ✅ AI 筆記包含批判性思考
- ⚠️ 偶爾需要手動調整卡片類型分配

---

## 下次 Session 檢查清單

### 啟動前檢查

- [ ] 確認知識庫狀態: `python check_db.py`
- [ ] 確認向量嵌入存在: `ls chroma_db/`
- [ ] 確認 6 篇論文和 144 張卡片都在數據庫中

### 立即執行任務

#### 任務 1: 生成概念網絡（5 分鐘）

**環境要求**: Windows Terminal (UTF-8)

```bash
# 切換到 Windows Terminal
python kb_manage.py visualize-network --obsidian \
    --output output/concept_analysis_20251119 \
    --min-confidence 0.4 \
    --top-n 50 \
    --moc-top 20
```

**驗收標準**:
- [ ] 生成 `concept_network.html` (可在瀏覽器打開)
- [ ] 生成 `obsidian/suggested_links.md` (至少 20 條連結)
- [ ] 生成 `obsidian/key_concepts_moc.md` (Top 20 概念)

#### 任務 2: 修復 batch_processor.py（30 分鐘）

**步驟**:
1. [ ] 添加 `_import_zettel_to_kb()` 方法
2. [ ] 修改 `process_single()` 調用導入方法
3. [ ] 更新 `batch_import_report.json` 格式
4. [ ] 撰寫單元測試

**測試流程**:
```bash
# 1. 清空測試數據
python -c "import sqlite3; conn = sqlite3.connect('knowledge_base/index.db'); conn.execute('DELETE FROM zettel_cards'); conn.commit(); conn.close()"

# 2. 重新運行批次處理（測試模式，只處理 1 篇）
python batch_process.py \
  --files "D:/core/research/Program_verse/+/pdf/Crockett-2025.pdf" \
  --domain "AI_literacy" \
  --add-to-kb \
  --generate-zettel \
  --detail standard \
  --cards 10

# 3. 驗證導入
python check_db.py
# 預期: Total cards: 10
```

**驗收標準**:
- [ ] `zettel_cards` 表有正確數量的卡片
- [ ] `zettel_links` 表有正確的連結關係
- [ ] `batch_import_report.json` 包含 `zettel_imported_to_db` 欄位
- [ ] 單元測試通過

#### 任務 3: 實作跨論文連結提示（60 分鐘）

**步驟**:
1. [ ] 修改 `zettelkasten_template.jinja2` 添加知識庫上下文
2. [ ] 實作 `_query_related_cards()` 方法（向量搜索）
3. [ ] 修改 `generate_zettelkasten()` 傳遞 `existing_related_cards`
4. [ ] 測試生成新論文卡片（應包含跨論文連結）

**測試流程**:
```bash
# 準備測試：添加第 7 篇論文
python analyze_paper.py \
  --from-pdf "path/to/paper7.pdf" \
  --add-to-kb

# 生成 Zettelkasten（使用改進的 Prompt）
python regenerate_zettel_with_openrouter.py \
  --cite-key "Paper7-2025" \
  --cards 15 \
  --llm-provider google \
  --model gemini-2.0-flash-exp

# 驗證跨論文連結
python -c "from src.knowledge_base import KnowledgeBaseManager; kb = KnowledgeBaseManager(); cards = kb.get_zettel_by_paper(7); import re; cross_links = [card for card in cards if any(not link.startswith('Paper7') for link in re.findall(r'\[\[([A-Za-z]+-\d{4}-\d{3})\]\]', card['content']))]; print(f'Cards with cross-paper links: {len(cross_links)}')"
```

**驗收標準**:
- [ ] 新生成的卡片包含跨論文連結（至少 20%）
- [ ] 連結指向語義相關的概念
- [ ] `zettel_links` 表包含 `is_cross_paper=TRUE` 記錄

### 後續規劃

#### Phase 3: Zotero + Obsidian 整合

**參考文檔**: `D:/core/research/Program_verse/2025-11-09-Zotero-Obsidian-Integration-Design.md`

**試點計畫**:
- 選定 2 個高品質 Connection notes（~25 篇論文）
- 從 Zotero BibTeX 批次導入
- 生成 Papers + Zettelkasten（~500 張卡片）
- 驗證 MOC 自動生成功能

**前置條件**:
- ✅ Phase 2.3 完成（Zettelkasten 穩定）
- ✅ Phase 0 清理完成（知識庫重置）
- 🔄 等待 Option B 修復完成

#### Phase 2.4: RelationFinder 改進

**參考文檔**: `docs/RELATION_FINDER_IMPROVEMENTS.md`

**目標**: 修復高信度關係數 = 0 的問題

**改進方向**:
1. 多層次明確連結檢測
2. 擴展共同概念提取（加入 description 欄位）
3. 領域相關性矩陣
4. AI Notes 連結生成

---

## 附錄: 文件清單

### 創建的文件

1. **import_existing_zettel.py** (214 行)
   - 功能: 手動導入 Zettelkasten 卡片到知識庫
   - 用途: 修復 batch_processor.py 未導入卡片的問題

2. **check_db.py** (14 行)
   - 功能: 快速檢查知識庫統計
   - 用途: 驗證導入結果

3. **RESUME_MEMO_20251119.md** (本文件)
   - 功能: Session 記錄和下次啟動指南

### 修改的文件

1. **knowledge_base/index.db**
   - 添加 `cite_key` 欄位到 `papers` 表
   - 導入 6 篇論文記錄
   - 導入 144 張卡片記錄

2. **templates/prompts/zettelkasten_template.jinja2**
   - 待修改: 添加知識庫上下文區塊

3. **src/processors/batch_processor.py**
   - 待修改: 添加 `_import_zettel_to_kb()` 方法

### 輸出目錄結構

```
output/
├── zettelkasten_notes/
│   ├── zettel_Crockett-2025_20251119/
│   │   ├── zettel_index.md
│   │   └── zettel_cards/
│   │       ├── Crockett-2025-001.md
│   │       ├── Crockett-2025-002.md
│   │       └── ... (23 cards total)
│   ├── zettel_Guest-2025 2_20251119/
│   ├── zettel_Guest-2025a_20251119/
│   ├── zettel_Günther-2025a_20251119/
│   ├── zettel_vanRooij-2025_20251119/
│   └── zettel_Vigly-2025_20251119/
├── batch_import_report.json
└── concept_analysis_20251119/  (待生成)
    ├── concept_network.html
    ├── concept_network.dot
    ├── analysis_report.md
    └── obsidian/
        ├── README.md
        ├── suggested_links.md
        ├── key_concepts_moc.md
        └── community_summaries/

knowledge_base/
├── papers/
│   ├── TICS2778NoofPages13.md
│   ├── What_Does_Human_Centred_AI_Mean.md
│   ├── Critical_Artificial_Intelligence_Literacy_for_Psyc.md
│   ├── LLMS_IN_PSYCHOLINGUISTICS_1.md
│   ├── Combining_Psychology_with_Artificial_Intelligence.md
│   └── Comprehension_effort_as_the_cost_of_inference.md
└── index.db

chroma_db/
└── (向量嵌入數據)
```

---

## Session 成果總結

### 定量指標

| 指標 | 數值 |
|------|------|
| 論文導入 | 6 篇 |
| Zettelkasten 卡片 | 144 張 |
| 向量嵌入 | 6 個 paper embeddings |
| 處理時間 | ~30 分鐘 |
| 估計成本 | ~$0.12 |
| 創建工具 | 2 個 Python 腳本 |
| 修復問題 | 2 個（數據庫模式 + 手動導入）|

### 定性成果

✅ **成功完成**:
- 首批正式項目論文完整導入
- 知識庫基礎架構就緒
- Zettelkasten 生成流程驗證
- 向量搜索基礎設施部署
- 問題診斷和解決方案文檔化

📋 **待完成** (下次 Session):
- 概念網絡生成和視覺化
- batch_processor.py 自動導入修復
- 跨論文連結 Prompt 改進

### 技術債務

⚠️ **高優先級**:
1. batch_processor.py 未導入卡片到數據庫（需修復）
2. Zettelkasten Prompt 不支援跨論文連結（需改進）

⚠️ **中優先級**:
1. import_existing_zettel.py 未解析連結（可用 Concept Mapper 代替）
2. Windows 編碼問題（需使用 UTF-8 terminal）

✅ **已解決**:
1. 數據庫模式缺少 cite_key 欄位
2. 論文未導入到數據庫
3. Unicode emoji 編碼錯誤

---

**文件版本**: v1.0
**創建時間**: 2025-11-19
**最後更新**: 2025-11-19
**作者**: Claude Code + User
**狀態**: ✅ 完成

---

**下次 Session 立即執行**:
```bash
# 1. 檢查知識庫狀態
python check_db.py

# 2. (在 Windows Terminal) 生成概念網絡
python kb_manage.py visualize-network --obsidian --output output/concept_analysis_20251119

# 3. 開始修復 batch_processor.py
# 參考本文檔 "Option B: 問題 1" 章節
```
