# 知識生產器 (Knowledge Production System)

以Claude Code為核心、Agents與Skills驅動的學術文獻處理系統

## 🎯 專案特色

- 🤖 **AI驅動**: 整合Claude Code與Ollama本地LLM
- 📚 **智能知識庫**: Markdown + SQLite混合架構，支援全文搜索
- 🎨 **多風格輸出**: 7種學術風格 × 5種詳細程度 × 3種語言
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
| **pdf-extractor** | PDF提取與結構分析 | ✅ 已完成 |
| **kb-connector** | 知識庫管理與索引 | ✅ 已完成 |
| **slide-maker** | 多風格簡報生成（支援自動模型選擇） | ✅ 已完成 |
| **model-monitor** | LLM使用監控與成本控制 | ✅ 已完成 |
| **usage-reporter** | 使用報告生成器 | ✅ 已完成 |
| **note-writer** | 結構化筆記撰寫 | 📅 計劃中 |
| **viz-generator** | 科學視覺化生成 | 📅 計劃中 |

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

### v0.1.0 ✅
- [x] 基礎架構建立
- [x] PDF提取器實作
- [x] 知識庫管理系統
- [x] /analyze-paper命令

### v0.2.0 (當前) 🚀
- [x] slide-maker Skill
- [x] 自動模型選擇系統
- [x] 成本控制與監控
- [x] 使用報告生成器
- [ ] note-writer Skill
- [ ] literature-analyzer Agent

### v0.3.0 (計劃中)
- [ ] 批量處理功能
- [ ] viz-generator Skill
- [ ] 知識圖譜視覺化
- [ ] 向量搜索整合
- [ ] Web介面

## 🤝 貢獻

歡迎貢獻！請參考 [CLAUDE.md](CLAUDE.md) 了解開發指南。

## 📄 授權

MIT License

## 🙏 致謝

- 基於SciMaker的Journal Club模組逆向工程成果
- 感謝Claude Code提供的AI驅動開發環境
- 感謝Ollama提供的本地LLM推理能力

---

**最後更新**: 2025-11-01
**版本**: 0.6.0-alpha
**維護者**: Claude Code Agent
