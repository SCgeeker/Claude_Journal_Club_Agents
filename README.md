# Knowledge Production System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**學術文獻處理與知識生產系統** - 基於Claude Code與多LLM的智能化學術工作流

## 🎯 核心功能

### 📄 PDF文獻分析
- 智能提取論文結構（標題、作者、摘要、章節）
- 支援兩種提取引擎（pdfplumber、PyPDF2）
- 字元限制：50,000（可配置）

### 📊 多風格學術簡報生成
支援8種學術風格 × 5種詳細程度 × 3種語言：

**學術風格**：
- Classic Academic（經典學術）
- Modern Academic（現代學術）⭐ 推薦
- Clinical（臨床導向）
- Research Methods（研究方法）
- Literature Review（文獻回顧）
- Case Analysis（案例分析）
- Teaching（教學導向）
- Zettelkasten（原子筆記）

**輸出格式**：
- PowerPoint (PPTX) - 16:9寬螢幕，智能排版
- Markdown - 相容Marp/reveal.js
- Both - 同時生成兩種格式

### 🗂️ Zettelkasten原子筆記系統

創新功能：
- ✅ **核心概念直接擷取原文**（不翻譯、不改寫）
- ✅ **語義化ID格式**（`領域-日期-序號`）
- ✅ **AI/人類筆記分離**（`[AI Agent]` + `[Human] TODO`）
- ✅ **概念連結網絡**（基於/導向/相關/對比）
- ✅ **Mermaid視覺化**（概念網絡圖）
- ✅ **雙檔案輸出**（索引 + 獨立卡片）

### 🤖 多LLM後端支持

- **Ollama**（本地）：完全離線、數據隱私
- **Google Gemini**：速度快、品質高
- **OpenAI**：GPT-4、GPT-3.5
- **Anthropic Claude**：推理能力強

自動故障轉移與提供者偵測。

### 📚 混合式知識庫

- Markdown筆記 + SQLite索引
- 全文搜索（FTS5）
- 主題分類與標籤
- 論文引用關係

---

## 🚀 快速開始

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/your-username/knowledge-production-system.git
cd knowledge-production-system

# 安裝依賴
pip install -r requirements.txt

# 初始化知識庫
python -c "from src.knowledge_base import KnowledgeBaseManager; KnowledgeBaseManager()"
```

### 配置API密鑰

創建 `.env` 文件：

```bash
# 選擇一個或多個LLM提供者
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Ollama（本地，無需API key）
OLLAMA_URL=http://localhost:11434
```

### 基本使用

```bash
# 1. 分析論文
python analyze_paper.py paper.pdf --add-to-kb

# 2. 生成簡報（現代學術風格）
python make_slides.py "研究主題" --pdf paper.pdf --style modern_academic --format both

# 3. 生成Zettelkasten筆記
python make_slides.py "論文標題" --pdf paper.pdf --style zettelkasten --domain YourField

# 4. 從知識庫生成
python make_slides.py "主題" --from-kb 1 --style teaching --format markdown
```

---

## 📖 詳細文檔

- [快速開始指南](QUICKSTART.md)
- [專案結構](PROJECT_STRUCTURE.md)
- [開發文檔](CLAUDE.md)（包含完整設計理念）

---

## 🎨 使用範例

### 範例1：教學簡報

```bash
python make_slides.py "深度學習基礎" \
  --pdf paper.pdf \
  --style teaching \
  --detail comprehensive \
  --language chinese \
  --format markdown \
  --slides 25
```

**輸出**：535行Markdown簡報，循序漸進、概念詳解

### 範例2：Zettelkasten筆記

```bash
python make_slides.py "Cognitive Science Research" \
  --pdf paper.pdf \
  --style zettelkasten \
  --domain CogSci \
  --detail standard
```

**輸出**：
```
output/zettel_CogSci_20251028/
├── zettel_index.md          # 索引+網絡圖
└── zettel_cards/
    ├── CogSci-20251028-001.md
    ├── CogSci-20251028-002.md
    └── ...
```

每張卡片包含：
- 英文原文核心概念（直接擷取）
- 中文詳細說明
- AI批判性思考
- 人類筆記TODO區域
- 概念連結網絡

---

## 🏗️ 系統架構

```
claude_lit_workflow/
├── src/
│   ├── extractors/          # PDF提取
│   ├── generators/          # 簡報與筆記生成
│   └── knowledge_base/      # 知識庫管理
├── templates/
│   ├── markdown/            # Markdown模板
│   ├── prompts/             # LLM Prompt
│   └── styles/              # 學術風格定義
├── config/
│   └── settings.yaml        # 系統配置
└── knowledge_base/          # 知識儲存
    ├── papers/              # Markdown筆記
    └── index.db             # SQLite索引
```

---

## 🤝 貢獻

歡迎貢獻！請遵循以下步驟：

1. Fork本倉庫
2. 創建功能分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 開啟Pull Request

---

## 📄 授權

本專案採用 MIT License - 詳見 [LICENSE](LICENSE) 文件

---

## 🙏 致謝

- 基於Claude Code開發環境
- Prompt工程參考學術簡報最佳實踐
- Zettelkasten方法論

---

## 📧 聯繫

有問題或建議？歡迎開啟Issue討論！

**專案狀態**：Alpha v0.4.0 - 積極開發中
