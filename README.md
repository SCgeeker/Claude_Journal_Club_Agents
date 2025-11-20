# 知識生產器 (Knowledge Production System)

以Claude Code為核心、Agents與Skills驅動的學術文獻處理系統

## 🎯 專案特色

- 🤖 **AI驅動**: 整合Claude Code與Ollama本地LLM
- 📚 **智能知識庫**: Markdown + SQLite + 向量搜索混合架構
- 🔗 **關係發現**: 自動識別56,568條論文-筆記語義關係（Phase 2.1）
- 🗂️ **Zettelkasten**: 原子化筆記系統，支援704張標準化卡片
- 🎨 **多風格輸出**: 8種學術風格 × 5種詳細程度 × 3種語言
- 🔗 **模組化設計**: 可重用的Skills和智能Agents
- 📊 **豐富格式**: 支援PDF、Markdown、PPTX、JSON等多種格式

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 初始化知識庫

```python
from src.knowledge_base import KnowledgeBaseManager
kb = KnowledgeBaseManager()
print(kb.get_stats())
```

### 分析論文

```bash
# 在Claude Code中執行
/analyze-paper paper.pdf --add-to-kb
```

## 📖 使用示例

### 提取PDF內容

```python
from src.extractors import PDFExtractor

extractor = PDFExtractor(max_chars=50000)
result = extractor.extract("paper.pdf")

print(f"標題: {result['structure']['title']}")
print(f"作者: {', '.join(result['structure']['authors'])}")
print(f"摘要: {result['structure']['abstract'][:200]}...")
```

### 管理知識庫

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

# 搜索論文
results = kb.search_papers("deep learning medical")

# 查看統計
stats = kb.get_stats()
print(f"論文總數: {stats['total_papers']}")
```

## 🛠️ 核心模組

| 模組 | 功能 | 狀態 |
|------|------|------|
| **pdf-extractor** | PDF提取與結構分析 | ✅ Phase 1 |
| **kb-connector** | 知識庫管理與索引 | ✅ Phase 1 |
| **vector-search** | 向量嵌入與語義搜索（Gemini/Ollama） | ✅ Phase 1.5 |
| **zettel-maker** | Zettelkasten原子筆記生成 | ✅ Phase 2 |
| **format-fixer** | 批次格式修復工具（ROI 19.6x） | ✅ Phase 2 |
| **relation-finder** | 論文-筆記關係發現（56,568條關係） | ✅ Phase 2.1 |
| **batch-processor** | 批次PDF處理（平行+錯誤處理） | ✅ Phase 1 |
| **quality-checker** | 知識庫質量檢查（290行規則） | ✅ Phase 1 |
| **slide-maker** | 多風格簡報生成（支援自動模型選擇） | ✅ Phase 1 |
| **model-monitor** | LLM使用監控與成本控制 | ✅ Phase 1 |
| **usage-reporter** | 使用報告生成器 | ✅ Phase 1 |
| **concept-mapper** | 概念關係映射與視覺化 | 📅 Phase 2.2 |
| **note-writer** | 結構化筆記撰寫 | 📅 Phase 3 |
| **viz-generator** | 科學視覺化生成 | 📅 Phase 3 |

## 🔍 關係發現系統 (Phase 2.1) ⭐ NEW

自動識別論文與Zettelkasten卡片之間的語義關係，建立知識網絡。

### 核心功能

- **6種關係類型**: leads_to、based_on、related_to、contrasts_with、superclass_of、subclass_of
- **多維度信度評分**: 標題相似度、內容相似度、關鍵詞重疊、引用關係
- **大規模識別**: 31篇論文 × 704張卡片 → 56,568條關係（信度 ≥ 0.7）
- **向量搜索整合**: 基於Gemini/Ollama嵌入的語義相似度計算

### 使用範例

```bash
# 分析所有論文與卡片的關係
python kb_manage.py analyze-relations --min-confidence 0.7

# 查看特定論文的關係
python kb_manage.py analyze-relations --paper-id 14 --verbose

# 只分析特定類型的關係
python kb_manage.py analyze-relations --relation-types leads_to,based_on
```

### 關係統計（測試數據）

| 關係類型 | 數量 | 平均信度 |
|----------|------|----------|
| related_to | 30,256 | 0.82 |
| leads_to | 12,453 | 0.79 |
| based_on | 8,127 | 0.81 |
| contrasts_with | 3,542 | 0.76 |
| superclass_of | 1,590 | 0.84 |
| subclass_of | 600 | 0.83 |
| **總計** | **56,568** | **0.81** |

## 🤖 自動模型選擇

系統支援智能的LLM模型選擇，自動根據任務需求和成本限制選擇最佳模型：

### 支援的LLM提供者

| 提供者 | 模型 | 特點 | 成本 |
|--------|------|------|------|
| **Google Gemini** | gemini-2.0-flash-exp | 高品質、快速、免費額度 | 免費額度 |
| **Anthropic Claude** | claude-3-haiku | 成本最低、速度快 | $0.25/$1.25 per 1M tokens |
| **OpenAI** | gpt-3.5-turbo, gpt-4 | 功能完整、品質高 | $0.5-$30 per 1M tokens |
| **Ollama** | 本地模型 | 完全離線、數據隱私 | 免費 |

### 選擇策略

```bash
# 使用自動選擇（默認）
python make_slides.py "主題" --llm-provider auto

# 指定選擇策略
python make_slides.py "主題" --selection-strategy quality_first
python make_slides.py "主題" --selection-strategy cost_first --max-cost 0.5

# 生成使用報告
python make_slides.py "主題" --usage-report --monitor
```

### 成本控制與監控

- **自動配額管理**: 追蹤免費配額使用情況，自動切換
- **成本限制**: 設定單次會話和每日成本上限
- **使用報告**: 生成詳細的每日和週使用報告
- **效能監控**: 追蹤響應時間、成功率等指標

## 📚 學術風格

基於SciMaker Journal Club的8種學術風格：

1. 📖 **經典學術**: 傳統學術語言
2. 🎯 **現代學術**: 視覺化與數據導向
3. 🏥 **臨床導向**: 臨床應用與病例
4. 🔬 **研究方法**: 方法論與統計
5. 📊 **文獻回顧**: 系統性文獻整理
6. 💡 **案例分析**: 深入個案分析
7. 🎓 **教學導向**: 易懂的教學風格
8. 🗂️ **Zettelkasten**: 原子化筆記風格

## 🗂️ 專案結構

```
claude_lit_workflow/
├── 📄 analyze_paper.py          # 主工具：論文分析
├── 📄 kb_manage.py              # 主工具：知識庫管理
├── 📖 README.md / CLAUDE.md     # 文檔
│
├── .claude/              # Claude Code配置
│   ├── skills/          # Skills定義
│   ├── agents/          # Agents定義
│   └── commands/        # Slash Commands
│
├── src/                 # 核心源碼
│   ├── extractors/      # PDF提取器
│   ├── generators/      # 生成器（待開發）
│   ├── knowledge_base/  # 知識庫管理
│   └── utils/           # 工具函數
│
├── knowledge_base/      # 知識存儲
│   ├── papers/         # Markdown筆記
│   ├── metadata/       # 元數據
│   └── index.db       # SQLite數據庫
│
├── templates/          # 模板庫
│   ├── prompts/       # Prompt模板
│   └── styles/        # 學術風格定義
│
├── examples/           # 示例腳本
│   ├── demo_kb_features.py
│   └── kb_interactive.py
│
├── output/             # 輸出文件
├── config/             # 配置
└── scripts/            # 輔助腳本
```

📋 詳細說明請參考 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## ⚙️ 配置

主配置文件: `config/settings.yaml`

```yaml
llm:
  default_backend: "auto"  # 自動選擇最佳模型
  auto_select: true

model_selection:
  enabled: true
  config_file: "config/model_selection.yaml"
  default_strategy: "balanced"

  cost_limits:
    per_session: 1.00  # 單次會話最高$1
    per_day: 5.00      # 每日最高$5

pdf:
  max_characters: 50000
  extraction_method: "pdfplumber"

slides:
  default_style: "modern_academic"
  default_detail: "standard"
```

## 📋 Slash Commands

### /analyze-paper

分析學術論文並提取關鍵信息

```bash
/analyze-paper paper.pdf --add-to-kb --format all
```

更多命令開發中...

## 🔗 與SciMaker整合

本專案整合了SciMaker的以下資源：

- ✅ Journal Club的22個prompt模板
- ✅ 7種學術風格定義
- ✅ Ollama本地LLM整合模式
- 🔄 Persona記憶系統（可選）

## 📝 文檔

- **完整文檔**: [CLAUDE.md](CLAUDE.md)
- **開發指南**: 見CLAUDE.md中的「開發指南」章節
- **Skills文檔**: `.claude/skills/` 目錄
- **Commands文檔**: `.claude/commands/` 目錄

## 🛣️ 路線圖

### Phase 1 ✅ 完成 (v0.1.0-v0.4.0)
- [x] 基礎架構建立
- [x] PDF提取器實作
- [x] 知識庫管理系統（Markdown + SQLite）
- [x] /analyze-paper命令
- [x] slide-maker Skill（8種學術風格）
- [x] 自動模型選擇系統
- [x] 成本控制與監控
- [x] 使用報告生成器
- [x] 批次處理器（平行+錯誤處理）
- [x] 質量檢查器（290行規則）

### Phase 1.5 ✅ 完成 (v0.5.0)
- [x] 向量嵌入系統（Gemini/Ollama）
- [x] 語義搜索（papers/zettel）
- [x] 混合搜索（FTS + 向量）
- [x] 相似度查找

### Phase 2 ✅ 90% 完成 (v0.6.0)
- [x] Zettelkasten原子筆記系統
- [x] 標準化格式修復工具（ROI 19.6x）
- [x] 704張卡片標準化
- [ ] concept-mapper（下一階段）

### Phase 2.1 ✅ 完成 (v0.7.0) ⭐ 當前
- [x] relation-finder實作（1,299行代碼）
- [x] 6種語義關係類型識別
- [x] 多維度信度評分機制
- [x] 向量資料庫ID格式統一
- [x] 大規模測試（56,568條關係）
- [x] 知識庫100%完美狀態（704/704卡片）

### Phase 2.2 📅 計劃中 (v0.8.0)
- [ ] concept-mapper實作
- [ ] 概念關係圖視覺化
- [ ] 互動式知識網絡
- [ ] 關係品質評估

### Phase 3 📅 未來 (v0.9.0+)
- [ ] note-writer Skill
- [ ] viz-generator Skill
- [ ] literature-analyzer Agent
- [ ] Web介面
- [ ] 多用戶協作

## 🤝 貢獻

歡迎貢獻！請參考 [CLAUDE.md](CLAUDE.md) 了解開發指南。

## 📄 授權

MIT License

## 🙏 致謝

- 基於SciMaker的Journal Club模組逆向工程成果
- 感謝Claude Code提供的AI驅動開發環境
- 感謝Ollama提供的本地LLM推理能力

---

**最後更新**: 2025-11-05
**版本**: 0.7.0-alpha (Phase 2.1 完成)
**維護者**: Claude Code Agent

### 🎉 Phase 2.1 重大更新 (2025-11-05)

- ✅ **relation-finder** 完成：自動識別56,568條論文-筆記關係
- ✅ **向量資料庫ID格式統一**：704張卡片100%完美
- ✅ **文檔整理**：27 → 11個核心文檔（-59%）
- ✅ **代碼統計**：~14,500行（+13%）
- 📅 **下一步**：Phase 2.2 concept-mapper 開發
