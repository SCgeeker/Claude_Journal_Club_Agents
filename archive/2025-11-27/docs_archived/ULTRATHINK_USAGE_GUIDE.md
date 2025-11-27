# 🎨 Ultrathink 使用指南

**版本**: 1.0
**創建日期**: 2025-11-06
**整合方式**: Slash Command + Skill

---

## 📖 概述

Ultrathink 是一個深度思考與優雅設計模式，融合 Steve Jobs 的設計哲學和 Leonardo da Vinci 的工藝精神，專門用於處理複雜的軟體開發任務。

**核心理念**: "We're not here to write code. We're here to make a dent in the universe."

---

## 🎯 完整使用場景矩陣

### 場景分類系統

| 場景類別 | 複雜度 | 代碼量 | 使用建議 | 預期時間 |
|---------|--------|--------|---------|---------|
| **🚀 Architecture** | ⭐⭐⭐⭐⭐ | 500+ 行 | ✅ 強烈推薦 | 4-8 小時 |
| **🎨 Feature Dev** | ⭐⭐⭐⭐ | 100-500 行 | ✅ 推薦 | 2-4 小時 |
| **🔧 Refactoring** | ⭐⭐⭐ | 50-100 行 | ⚠️ 視情況 | 1-2 小時 |
| **🐛 Bug Fix** | ⭐⭐ | 10-50 行 | ⚠️ 視複雜度 | 30分-1小時 |
| **📝 Documentation** | ⭐ | 0 行代碼 | ❌ 不推薦 | 即時 |
| **🔍 Query/Search** | ⭐ | 0 行代碼 | ❌ 不推薦 | 即時 |

---

## 📋 詳細使用場景

### ✅ 場景 1: 系統架構設計（強烈推薦）

**特徵**:
- 影響整個系統的設計決策
- 需要考慮多個模組間的交互
- 長期維護和擴展性至關重要

**觸發關鍵詞**:
- "設計 XXX 系統"
- "架構重構"
- "如何優雅地實作 XXX"
- "最佳實踐"

**實際案例**:

#### 案例 1.1: RelationFinder 改進設計

```markdown
用戶請求:
"設計 RelationFinder 的改進方案，提升關係識別的信度評分"

使用流程:
/ultrathink

[Phase 1: Deep Understanding]
✅ 閱讀 RELATION_FINDER_TECHNICAL_DETAILS.md
✅ 分析當前 4 維度評分系統
✅ 質疑：為什麼只有 4 個維度？
✅ 發現關鍵問題：明確連結覆蓋率僅 11.6%

[Phase 2: Da Vinci Planning]
✅ 設計 5 個改進方案（多層次連結檢測、擴展共同概念等）
✅ 創建 TodoWrite 三階段實施計畫
✅ 文檔化在 RELATION_FINDER_IMPROVEMENTS.md（1200+ 行）
✅ 效果預估：信度從 0.35 → 0.56 (+60%)

[Phase 3: Craftsman Implementation]
✅ Phase 1: 共同概念 + 領域矩陣（P0 優先級）
✅ Phase 2: 連結增強 + Prompt 改進（P1）
✅ Phase 3: 永久筆記生成器（P2）
✅ TDD 全程保證品質

[Phase 4: Verification]
✅ 704 張卡片基準測試
✅ 性能驗證（< 5 分鐘完成）
✅ 向後相容性測試

結果: 🌟 完整的設計文檔 + 可執行的實施計畫
時間: 6-8 小時（值得投資）
```

#### 案例 1.2: Concept Mapper 視覺化系統

```markdown
用戶請求:
"整合 Obsidian，實作概念網絡視覺化"

使用流程:
/ultrathink

[Think Different]
- 質疑：為什麼要「導出」到 Obsidian？
- 創新：能否直接生成 Obsidian 友好格式？
- 探索：Wiki Links vs Dataview vs Graph View？

[Plan]
- NetworkX 圖論分析
- Louvain 社群檢測
- PageRank 中心性
- D3.js 互動視覺化
- Obsidian MOC（Map of Content）生成

[Implementation]
- concept_mapper.py（1230 行）
- obsidian_exporter.py（700 行）
- 完整測試覆蓋率

結果: ✅ Phase 2.2 完整實作（OBSIDIAN_INTEGRATION_GUIDE.md）
```

---

### ✅ 場景 2: 複雜功能開發（推薦）

**特徵**:
- 新功能需求清晰但實作路徑多樣
- 需要權衡多種設計方案
- 對代碼品質有高要求

**觸發關鍵詞**:
- "實作 XXX 功能"
- "新增 XXX 模組"
- "優雅地處理 XXX"

**實際案例**:

#### 案例 2.1: 批次處理器（Batch Processor）

```markdown
用戶請求:
"實作批次處理大量 PDF 的功能，要求穩定且支援平行處理"

使用流程:
/ultrathink

[Deep Understanding]
- 研究 ThreadPoolExecutor 最佳實踐
- 分析 Windows 路徑處理問題
- 理解 timeout 和錯誤處理需求

[Planning]
TodoWrite:
1. 設計 BatchProcessor 類架構
2. 實作 ProcessResult 和 BatchResult 數據結構
3. 支援 skip/retry/stop 三種錯誤策略
4. 整合知識庫和 Zettelkasten 生成
5. CLI 工具和 Python API

[Implementation]
- batch_processor.py（570 行，優雅設計）
- 完整的錯誤處理和進度追蹤
- Windows 路徑支援（pathlib.Path）
- 測試：2 篇 PDF（1 成功，1 timeout）

[Iteration]
- 修復 sys.stdin.isatty() 檢測問題
- 優化 worker 數量建議（2-4 個）
- 添加 cleanup 整合

結果: ✅ batch_processor.py + batch_process.py CLI
文檔: .claude/skills/batch-processor.md
```

#### 案例 2.2: 向量搜索系統（Vector Search）

```markdown
用戶請求:
"整合向量嵌入，實作語義搜索功能"

使用流程:
/ultrathink

[Think Different]
- 質疑：為什麼要用 ChromaDB？（評估其他向量資料庫）
- 探索：Gemini vs Ollama 嵌入器的權衡
- 創新：混合搜索（FTS + 向量）

[Design]
- 提供者模式：GeminiEmbedder + OllamaEmbedder
- VectorDatabase 抽象層
- 三個強大命令：semantic-search, similar, hybrid-search
- 成本追蹤和估算

[Implementation]
src/embeddings/
├── providers/
│   ├── gemini_embedder.py
│   └── ollama_embedder.py
├── vector_db.py
└── __init__.py

[Testing]
- 31 篇論文 + 52 張卡片 = 83 個向量
- 成本: ~$0.0173
- 查詢時間: 3-8 秒

結果: ✅ Phase 1.5 完整實作
文檔: VECTOR_SEARCH_TEST_REPORT.md
```

---

### ⚠️ 場景 3: 代碼重構（視情況使用）

**何時使用 Ultrathink**:
- ✅ 大規模重構（影響多個模組）
- ✅ 需要設計新的抽象
- ✅ 性能優化需要演算法改進

**何時不使用**:
- ❌ 簡單的函數重命名
- ❌ 格式調整（PEP 8 等）
- ❌ 局部小改動

**實際案例**:

#### 案例 3.1: 適合使用（知識庫架構重構）

```markdown
任務: 重構知識庫管理器，從單一類拆分為多個模組

/ultrathink

[Analysis]
- 當前 kb_manager.py 過於龐大（1500+ 行）
- 違反 Single Responsibility Principle
- 測試困難

[Design]
拆分為:
- PaperManager (論文 CRUD)
- TopicManager (主題管理)
- SearchEngine (全文搜索)
- MetadataExtractor (元數據提取)

[Implementation with TDD]
- 先寫測試確保行為一致
- 逐步遷移功能
- 保持向後相容

結果: ✅ 模組化、可測試、可維護
```

#### 案例 3.2: 不適合使用（變數重命名）

```markdown
任務: 重命名變數 calc_sim → calculate_similarity

❌ 錯誤做法:
/ultrathink
[開始分析整個相似度計算系統...]

✅ 正確做法:
直接使用 Edit 工具全局替換

時間: 30 秒 vs 10 分鐘（浪費）
```

---

### ⚠️ 場景 4: Bug 修復（視複雜度使用）

**何時使用 Ultrathink**:
- ✅ 根本原因不明，需要深度調查
- ✅ 修復涉及架構問題
- ✅ 需要預防類似 bug

**何時不使用**:
- ❌ 明顯的拼寫錯誤
- ❌ 簡單的邏輯錯誤
- ❌ 緊急修復（時間壓力）

**實際案例**:

#### 案例 4.1: 適合使用（神秘的測試失敗）

```markdown
問題: 704 張卡片測試中，隨機出現 5-10 張相似度異常低

/ultrathink

[Systematic Debugging]
✅ 使用 superpowers:systematic-debugging
✅ 分析向量嵌入過程
✅ 檢查 ChromaDB 索引
✅ 發現：某些卡片 description 欄位為 None

[Root Cause]
- _extract_shared_concepts() 未處理 None 值
- 導致共同概念評分異常

[Elegant Fix]
def _extract_shared_concepts_enhanced(self, card):
    description = card.get('description') or ''  # Handle None
    # ... rest of implementation

[Prevention]
- 添加測試覆蓋 None 值情況
- 文檔化 schema 要求

結果: ✅ Bug 修復 + 預防機制
```

#### 案例 4.2: 不適合使用（TypeError: missing argument）

```markdown
錯誤: TypeError: calculate_similarity() missing 1 required positional argument

❌ 錯誤做法:
/ultrathink
[深入分析整個類型系統...]

✅ 正確做法:
閱讀錯誤訊息 → 發現呼叫時少傳一個參數 → 修正

時間: 1 分鐘 vs 15 分鐘
```

---

### ❌ 場景 5: 文檔更新（不推薦）

**特徵**:
- 純粹的文字編寫
- 不涉及代碼邏輯
- 已有明確內容

**替代方案**: 標準模式即可

**案例**:

```markdown
任務: 更新 README.md 添加新功能說明

❌ 不要使用 /ultrathink
[會過度分析文檔結構、設計信息架構等]

✅ 直接使用 Edit 工具
- 讀取現有 README
- 添加新段落
- 保持一致格式

時間: 2 分鐘 vs 20 分鐘
```

---

### ❌ 場景 6: 簡單查詢/操作（不推薦）

**特徵**:
- 讀取文件
- 搜索代碼
- 列出目錄
- 簡單查詢

**案例**:

```markdown
任務: 找出所有 .py 文件

❌ /ultrathink
[設計優雅的文件搜索系統...]

✅ Glob "**/*.py"

任務: 讀取 CLAUDE.md

❌ /ultrathink
[分析文檔架構...]

✅ Read("CLAUDE.md")
```

---

## 🔧 與 Superpowers Skills 整合

### 推薦組合工作流

#### Workflow 1: 綠地專案（全新功能）

```mermaid
graph LR
    A[/ultrathink] --> B[superpowers:brainstorming]
    B --> C[superpowers:writing-plans]
    C --> D[/ultrathink + TDD]
    D --> E[superpowers:requesting-code-review]
    E --> F[superpowers:verification-before-completion]
```

**詳細步驟**:

```markdown
1. /ultrathink
   - Deep understanding of requirements
   - Read CLAUDE.md and related docs
   - Question assumptions

2. Skill: superpowers:brainstorming
   - Explore 3-5 different approaches
   - Evaluate pros/cons
   - Select best approach

3. Skill: superpowers:writing-plans
   - Create detailed implementation plan
   - Break into phases
   - Document design decisions

4. /ultrathink (Implementation)
   - TDD: Write tests first
   - Craft elegant code
   - Handle edge cases

5. Skill: superpowers:requesting-code-review
   - Get quality validation
   - Refine based on feedback

6. Skill: superpowers:verification-before-completion
   - Run all tests
   - Verify documentation
   - Confirm completion
```

---

#### Workflow 2: 複雜重構

```mermaid
graph LR
    A[/ultrathink] --> B[superpowers:systematic-debugging]
    B --> C[/ultrathink Design]
    C --> D[superpowers:test-driven-development]
    D --> E[superpowers:verification-before-completion]
```

**詳細步驟**:

```markdown
1. /ultrathink (Understanding)
   - Understand current architecture
   - Identify pain points
   - Document technical debt

2. Skill: superpowers:systematic-debugging
   - Trace root causes
   - Find all related issues
   - Plan comprehensive fix

3. /ultrathink (Design)
   - Design elegant replacement
   - Plan migration path
   - Ensure backward compatibility

4. Skill: superpowers:test-driven-development
   - Maintain behavior consistency
   - Test-driven migration
   - Incremental refactoring

5. Skill: superpowers:verification-before-completion
   - All tests pass
   - Performance not degraded
   - Documentation updated
```

---

#### Workflow 3: 架構決策

```mermaid
graph LR
    A[/ultrathink] --> B[superpowers:brainstorming]
    B --> C[/ultrathink Selection]
    C --> D[superpowers:executing-plans]
```

**詳細步驟**:

```markdown
1. /ultrathink (Deep Dive)
   - Understand constraints
   - Research best practices
   - Analyze tradeoffs

2. Skill: superpowers:brainstorming
   - Generate multiple solutions
   - Explore unconventional approaches
   - Challenge "the obvious" solution

3. /ultrathink (Decision)
   - Evaluate against criteria
   - Select best approach
   - Document decision rationale

4. Skill: superpowers:executing-plans
   - Implement in controlled batches
   - Review between batches
   - Adjust based on learnings
```

---

## 📊 決策樹

使用以下決策樹判斷是否使用 Ultrathink：

```
任務開始
    ↓
是否為代碼任務？
├─ 否 → 標準模式
└─ 是 ↓
    任務複雜度？
    ├─ 簡單（<5 分鐘）→ 標準模式
    ├─ 中等（5-30 分鐘）→ 視情況（詢問用戶）
    └─ 複雜（>30 分鐘）↓
        是否需要創新設計？
        ├─ 否 → 標準模式 + Superpowers
        └─ 是 ↓
            是否有時間壓力？
            ├─ 是（ASAP）→ 標準模式
            └─ 否 → ✅ /ultrathink
```

---

## 🎯 最佳實踐

### ✅ DO（推薦做法）

1. **明確任務範圍**
   ```markdown
   ✅ "使用 ultrathink 設計 RelationFinder 改進方案"
   ❌ "幫我寫代碼"（太模糊）
   ```

2. **設置時間預期**
   ```markdown
   ✅ "我有 4 小時時間，希望深度思考這個問題"
   ❌ "快點完成"（時間壓力與 ultrathink 衝突）
   ```

3. **結合 Superpowers**
   ```markdown
   ✅ /ultrathink → brainstorming → writing-plans
   ❌ 只用 ultrathink 包辦所有（應善用協作）
   ```

4. **文檔化思考過程**
   ```markdown
   ✅ 創建 docs/XXX_DESIGN.md 記錄決策
   ❌ 只在腦中思考（無法追溯）
   ```

5. **迭代優化**
   ```markdown
   ✅ MVP → 測試 → 優化 → 完美
   ❌ 追求一次完美（分析癱瘓）
   ```

---

### ❌ DON'T（避免做法）

1. **所有任務都用 ultrathink**
   ```markdown
   ❌ /ultrathink
       讀取 README.md
   ```

2. **過度設計簡單功能**
   ```markdown
   ❌ 用戶：添加一個配置選項
       AI：設計完整的插件系統（5 個類、3 個介面）
   ```

3. **忽略時間成本**
   ```markdown
   ❌ 花 8 小時優化一個每月運行 1 次的腳本
   ✅ 花 30 分鐘寫清楚的代碼即可
   ```

4. **犧牲實用性**
   ```markdown
   ❌ 追求完美抽象，導致代碼難以理解
   ✅ 簡單直接，99% 情況適用
   ```

5. **跳過測試**
   ```markdown
   ❌ 覺得代碼太優雅不需要測試
   ✅ TDD 全程，測試覆蓋率 100%
   ```

---

## 📈 效果評估

### 成功指標

完成 Ultrathink 任務後，應檢查：

| 指標 | 目標 | 如何驗證 |
|------|------|---------|
| **代碼優雅度** | 8/10+ | 代碼審查、同行評分 |
| **測試覆蓋率** | 100% | pytest --cov |
| **性能** | 無退化或提升 | Benchmark 比較 |
| **文檔完整性** | 所有決策記錄 | docs/ 目錄檢查 |
| **可維護性** | 新人 30 分鐘內理解 | 邀請他人審查 |
| **簡潔性** | 無冗餘代碼 | 人工審查、Lint |

### 失敗指標（警告）

如果出現以下情況，可能過度使用了 ultrathink：

- ⚠️ 簡單任務花費 >30 分鐘
- ⚠️ 過度抽象導致代碼難懂
- ⚠️ 創建了未使用的"優雅"功能
- ⚠️ 團隊成員難以理解設計
- ⚠️ 測試變得比實作更複雜

---

## 🔄 迭代改進

### 第一次使用

1. 選擇中等複雜度任務（100-200 行代碼）
2. 跟隨 4 個階段嚴格執行
3. 記錄時間和成果
4. 反思：什麼有效？什麼可改進？

### 熟練後

1. 內化原則，無需刻意遵循每個步驟
2. 快速判斷何時需要 ultrathink
3. 靈活調整，保留核心哲學
4. 教導他人使用

---

## 📚 學習資源

### 推薦閱讀

1. **Clean Code** by Robert C. Martin
   - 代碼整潔之道

2. **Design Patterns** by Gang of Four
   - 理解優雅抽象

3. **The Pragmatic Programmer**
   - 實用主義與完美主義的平衡

### 內部範例

1. **RELATION_FINDER_IMPROVEMENTS.md**
   - 完美的 ultrathink 案例
   - 深度分析 + 優雅設計 + 詳細規劃

2. **OBSIDIAN_INTEGRATION_GUIDE.md**
   - 複雜功能的優雅實作

3. **batch_processor.py**
   - 工藝級代碼範例

---

## 🎓 常見問題

### Q1: Ultrathink 會讓開發變慢嗎？

**A**: 短期看是，長期看否。

- 短期：單個任務時間 +50-100%
- 長期：減少 bug、重構、技術債，總時間 -30%

### Q2: 所有任務都應該追求完美嗎？

**A**: 否。遵循 80/20 法則。

- 20% 的核心代碼：ultrathink（架構、關鍵演算法）
- 80% 的支援代碼：標準模式（工具腳本、一次性任務）

### Q3: 與敏捷開發衝突嗎？

**A**: 不衝突，是增強。

- Ultrathink 確保每個 sprint 交付高品質代碼
- 減少 sprint 之間的技術債累積
- 與"快速迭代"並行不悖（MVP 可以優雅）

### Q4: 團隊協作怎麼用？

**A**: 關鍵決策時使用。

- 架構會議前：用 ultrathink 準備方案
- Code Review：評估代碼是否符合 ultrathink 標準
- Pair Programming：一人 ultrathink，一人實作

---

## 🎯 總結

### 核心原則

1. **選擇性使用**：不是所有任務都需要 ultrathink
2. **深度思考**：質疑假設，探索最優解
3. **優雅設計**：代碼應該是藝術品
4. **無情迭代**：第一版永遠不夠好
5. **實用平衡**：完美主義 + 實用主義

### 一句話總結

> **Ultrathink 不是關於寫更多代碼，而是寫更少但更好的代碼。**

---

**Remember**:

> "The people who are crazy enough to think they can change the world are the ones who do."
> — Steve Jobs

讓我們用代碼改變世界。🚀
