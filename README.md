# Knowledge Production System | 知識生產系統

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Community](https://img.shields.io/badge/join-community-blue.svg)](https://github.com/yourusername/claude_lit_workflow/discussions)

> **AI-Powered Zettelkasten Card Generation for Academic Research**
> **學術研究的 AI 驅動 Zettelkasten 原子卡片生成系統**

Transform academic papers into atomic knowledge cards automatically. Community-driven optimization for better card generation methods.

自動將學術論文轉換為原子化知識卡片。社群驅動優化卡片生成方法。

---

## 🎯 Core Feature | 核心功能

### 🗂️ Zettelkasten Atomic Card Generation | Zettelkasten 原子卡片生成

**The essential tool for academic note-taking**
**學術筆記的必備工具**

#### What makes it special? | 為什麼特別？

✅ **Direct Quote Extraction | 直接擷取原文**
- Preserves original English concepts without translation
- 保留英文原始概念，不翻譯不改寫

✅ **Semantic ID System | 語義化 ID 系統**
- Format: `Domain-YYYYMMDD-NNN` (e.g., `CogSci-20251028-001`)
- 格式：`領域-日期-序號`（例如：`CogSci-20251028-001`）

✅ **AI/Human Note Separation | AI/人類筆記分離**
- `[AI Agent]` for AI-generated insights
- `[Human] TODO` for your own annotations
- `[AI Agent]` 標記 AI 生成的洞見
- `[Human] TODO` 標記你的個人註解

✅ **Concept Link Network | 概念連結網絡**
- Relationship types: Based on, Leads to, Related, Contrasts with
- 關係類型：基於、導向、相關、對比

✅ **Visual Network Graph | 視覺化網絡圖**
- Mermaid diagrams for concept relationships
- 使用 Mermaid 圖表展示概念關係

#### Output Structure | 輸出結構

```
output/zettelkasten_notes/zettel_PaperTitle_20251112/
├── zettel_index.md          # Master index with network graph | 主索引+網絡圖
└── zettel_cards/
    ├── Domain-20251112-001.md
    ├── Domain-20251112-002.md
    └── ...
```

#### Example Card | 卡片範例

```markdown
---
id: CogSci-20251028-001
domain: CogSci
card_number: 1
core_concept: "Embodied Cognition"
---

## 核心概念 | Core Concept
> "Embodied cognition suggests that cognitive processes are deeply rooted
> in the body's interactions with the world"

**中文說明**：具身認知理論認為，認知過程深植於身體與世界的互動中...

## AI筆記 | AI Notes
[AI Agent] 這個理論挑戰了傳統的「心智即計算」觀點...

## 我的筆記 | My Notes
[Human] TODO: 連結到 Barsalou 的知覺符號理論

## 連結網絡 | Link Network
- **基於** [[CogSci-20251028-003|Symbol Grounding]]
- **導向** [[CogSci-20251028-005|Motor Simulation]]
- **對比** [[CogSci-20251028-010|Abstract Cognition]]

## 來源脈絡 | Source Context
- **來源**: Wilson & Golonka (2013)
- **段落**: Section 2.1, p.245
```

---

## 🤖 Multi-LLM Support | 多 LLM 支持

**Choose your preferred AI backend** | **選擇您偏好的 AI 後端**

| Provider | Pros | Use Case |
|----------|------|----------|
| **Ollama** | 🔒 Fully offline, privacy | 完全離線，隱私保護 |
| **Google Gemini** | ⚡ Fast & high quality | 速度快，品質高 |
| **OpenAI** | 🧠 GPT-4, best reasoning | GPT-4，推理最佳 |
| **Anthropic Claude** | 📚 Long context, analysis | 長文本，深度分析 |

**Automatic fallback** if one provider fails.
**自動故障轉移** 當某個提供者失敗時。

---

## 🚀 Quick Start | 快速開始

### 1. Installation | 安裝

```bash
# Clone the repository | 克隆倉庫
git clone https://github.com/yourusername/claude_lit_workflow.git
cd claude_lit_workflow

# Install dependencies | 安裝依賴
pip install -r requirements.txt
```

### 2. Configure API Keys | 配置 API 密鑰

Create a `.env` file | 創建 `.env` 文件：

```bash
# Choose one or more LLM providers | 選擇一個或多個 LLM 提供者
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Ollama (local, no API key needed) | Ollama（本地，無需 API 密鑰）
OLLAMA_URL=http://localhost:11434
```

### 3. Generate Your First Zettelkasten | 生成您的第一個 Zettelkasten

```bash
# Basic usage | 基本用法
python make_slides.py "Paper Title" \
  --pdf paper.pdf \
  --style zettelkasten \
  --domain YourField

# Example with cognitive science paper | 認知科學論文範例
python make_slides.py "Embodied Cognition" \
  --pdf wilson2013.pdf \
  --style zettelkasten \
  --domain CogSci \
  --detail comprehensive
```

**Output | 輸出**:
- 20 atomic cards by default | 預設 20 張原子卡片
- One master index with concept network graph | 一個包含概念網絡圖的主索引
- Ready for Obsidian or any Markdown editor | 可用於 Obsidian 或任何 Markdown 編輯器

---

## 📊 Additional Features | 其他功能

### Academic Slide Generation | 學術簡報生成

Generate presentation slides in multiple styles:
以多種風格生成簡報投影片：

```bash
python make_slides.py "Research Topic" \
  --pdf paper.pdf \
  --style modern_academic \
  --format pptx \
  --language chinese
```

**8 Academic Styles | 8 種學術風格**:
- Classic Academic | 經典學術
- Modern Academic | 現代學術 ⭐
- Clinical | 臨床導向
- Research Methods | 研究方法
- Literature Review | 文獻回顧
- Case Analysis | 案例分析
- Teaching | 教學導向
- Zettelkasten | 原子筆記

### Knowledge Base | 知識庫

Built-in hybrid knowledge base:
內建混合式知識庫：

- Markdown notes + SQLite index | Markdown 筆記 + SQLite 索引
- Full-text search (FTS5) | 全文搜索 (FTS5)
- Topic classification | 主題分類
- Citation relationships | 引用關係

---

## 🤝 Community & Contribution | 社群與貢獻

**We welcome contributions!** Especially for optimizing card generation methods.
**歡迎貢獻！**特別是優化卡片生成方法的貢獻。

### How to Contribute | 如何貢獻

1. **Fork this repository** | Fork 本倉庫
2. **Create a feature branch** | 創建功能分支
   ```bash
   git checkout -b feature/BetterCardGeneration
   ```
3. **Make your improvements** | 進行改進
   - Optimize prompt templates | 優化 prompt 模板
   - Enhance concept extraction | 增強概念提取
   - Improve link detection | 改進連結檢測
4. **Submit a pull request** | 提交 Pull Request

### Discussion Topics | 討論主題

- 💬 Best practices for card generation | 卡片生成最佳實踐
- 💬 Domain-specific optimizations | 領域特定優化
- 💬 Multi-language support | 多語言支持
- 💬 Integration with other tools | 與其他工具整合

Join our discussions: [GitHub Discussions](https://github.com/yourusername/claude_lit_workflow/discussions)
加入討論: [GitHub Discussions](https://github.com/yourusername/claude_lit_workflow/discussions)

---

## 📖 Documentation | 文檔

### English
- [Quick Start Guide](docs/QUICKSTART.md)
- [Developer Documentation](CLAUDE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)

### 中文
- [快速開始指南](docs/QUICKSTART.md)
- [開發者文檔](CLAUDE.md)
- [專案結構](docs/PROJECT_STRUCTURE.md)

---

## 🏗️ System Architecture | 系統架構

```
claude_lit_workflow/
├── src/
│   ├── extractors/          # PDF extraction | PDF 提取
│   ├── generators/          # Card & slide generation | 卡片與簡報生成
│   │   └── zettel_maker.py  # Core Zettelkasten generator | 核心 Zettelkasten 生成器
│   └── knowledge_base/      # Knowledge base manager | 知識庫管理
├── templates/
│   ├── prompts/             # LLM prompts | LLM 提示詞
│   │   └── zettelkasten_template.jinja2
│   └── styles/              # Academic styles | 學術風格
└── config/
    └── settings.yaml        # System configuration | 系統配置
```

---

## 📄 License | 授權

MIT License - see [LICENSE](LICENSE) file
MIT 授權 - 詳見 [LICENSE](LICENSE) 文件

---

## 🙏 Acknowledgments | 致謝

- Built with [Claude Code](https://claude.ai/code) | 使用 Claude Code 開發
- Inspired by Zettelkasten methodology | 受 Zettelkasten 方法論啟發
- Powered by multiple LLM providers | 由多個 LLM 提供者驅動

---

## 📧 Contact | 聯繫

**Questions or suggestions?** Open an issue!
**有問題或建議？** 開啟一個 Issue！

**Project Status** | **專案狀態**: v0.3.0 - Stable for community use
**專案狀態**: v0.3.0 - 穩定版本，適合社群使用

---

**⭐ Star this repo if you find it useful!**
**⭐ 如果覺得有用請給個星星！**
