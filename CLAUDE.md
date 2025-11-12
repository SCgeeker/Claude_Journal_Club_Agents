# CLAUDE.md | Developer Guide

This file provides guidance to Claude Code and developers when working with this repository.

本文檔為 Claude Code 和開發者提供代碼庫使用指南。

---

## Project Overview | 專案概述

**Knowledge Production System** is an AI-powered academic literature processing system built on Claude Code, with a focus on generating high-quality Zettelkasten atomic note cards from research papers.

**知識生產系統** 是一個基於 Claude Code 的 AI 驅動學術文獻處理系統，專注於從研究論文生成高品質的 Zettelkasten 原子筆記卡片。

### Core Mission | 核心使命

Enable researchers to transform academic papers into interconnected knowledge cards automatically, preserving original concepts while building semantic networks.

幫助研究者自動將學術論文轉換為相互連結的知識卡片，保留原始概念同時建立語義網絡。

---

## Core Architecture | 核心架構

```
claude_lit_workflow/
├── src/
│   └── generators/
│       └── zettel_maker.py        # Core Zettelkasten generator | 核心 Zettelkasten 生成器 (500+ lines)
├── templates/
│   └── prompts/
│       └── zettelkasten_template.jinja2  # Card generation prompt | 卡片生成提示詞 (200+ lines)
├── make_slides.py                 # Main CLI entry point | 主要命令列入口
└── config/
    └── settings.yaml              # System configuration | 系統配置
```

### Key Components | 核心組件

**1. Zettelkasten Generator** (`src/generators/zettel_maker.py`)
- Card generation logic | 卡片生成邏輯
- Link network construction | 連結網絡建構
- Master index creation | 主索引生成

**2. Prompt Template** (`templates/prompts/zettelkasten_template.jinja2`)
- Structured card generation instructions | 結構化卡片生成指令
- Multi-language support | 多語言支持
- Domain-specific customization | 領域特定客製化

---

## Zettelkasten Card Generator | Zettelkasten 卡片生成器

The heart of this system is the `ZettelkastenMaker` class in `src/generators/zettel_maker.py`.

系統的核心是 `src/generators/zettel_maker.py` 中的 `ZettelkastenMaker` 類。

### Key Methods | 核心方法

#### `generate_zettelkasten()`
Main method that orchestrates the entire card generation process.

主方法，協調整個卡片生成流程。

**Process | 流程**:
1. Extract paper content | 提取論文內容
2. Call LLM with prompt template | 使用提示詞模板呼叫 LLM
3. Parse LLM output into card files | 解析 LLM 輸出為卡片文件
4. Generate master index with network graph | 生成包含網絡圖的主索引

#### `_parse_llm_output()`
Parses structured LLM response into individual card markdown files.

將 LLM 的結構化回應解析為個別卡片 Markdown 文件。

**Key Features | 核心功能**:
- YAML frontmatter extraction | YAML 前置資料提取
- Section parsing (concept, notes, links, context) | 章節解析（概念、筆記、連結、脈絡）
- Link validation and normalization | 連結驗證與正規化

#### `_extract_links()`
Extracts and validates inter-card links from card content.

從卡片內容提取並驗證卡片間連結。

**Relationship Types | 關係類型**:
- 基於 (Based on)
- 導向 (Leads to)
- 相關 (Related to)
- 對比 (Contrasts with)

#### `_generate_master_index()`
Creates the master index file with Mermaid network visualization.

生成包含 Mermaid 網絡視覺化的主索引文件。

---

## Multi-LLM Integration | 多 LLM 整合

The system supports 4 LLM providers with automatic fallback.

系統支援 4 個 LLM 提供者，並具備自動故障轉移。

### Supported Providers | 支援的提供者

| Provider | Model Examples | Use Case |
|----------|----------------|----------|
| **Ollama** | gemma2, llama3 | Local, privacy-focused<br/>本地運行，注重隱私 |
| **Google Gemini** | gemini-2.0-flash-exp | Fast, high quality<br/>快速，高品質 |
| **OpenAI** | gpt-4, gpt-3.5-turbo | Best reasoning<br/>最佳推理能力 |
| **Anthropic Claude** | claude-3-opus | Long context analysis<br/>長文本分析 |

### Configuration | 配置

Create `.env` file with API keys:

創建包含 API 密鑰的 `.env` 文件：

```bash
# Google Gemini
GOOGLE_API_KEY=your-google-api-key

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-api-key

# Ollama (local, no API key needed)
OLLAMA_URL=http://localhost:11434
```

---

## Card Generation Workflow | 卡片生成工作流

### Basic Usage | 基本使用

```bash
# Generate Zettelkasten cards from PDF
# 從 PDF 生成 Zettelkasten 卡片
python make_slides.py "Paper Title" \
  --pdf paper.pdf \
  --style zettelkasten \
  --domain YourDomain \
  --detail comprehensive
```

### Output Structure | 輸出結構

```
output/zettelkasten_notes/zettel_PaperTitle_20251112/
├── zettel_index.md              # Master index | 主索引
│   ├── Paper metadata           # 論文元數據
│   ├── Card list                # 卡片列表
│   └── Mermaid network graph    # Mermaid 網絡圖
└── zettel_cards/
    ├── Domain-20251112-001.md   # Individual cards | 個別卡片
    ├── Domain-20251112-002.md
    └── ...
```

### Card File Format | 卡片文件格式

Each card follows this structure:

每張卡片遵循以下結構：

```markdown
---
id: Domain-YYYYMMDD-NNN
domain: Domain
card_number: N
core_concept: "Concept Name"
---

## 核心概念 | Core Concept
> "Direct quote from paper"
> 「論文原文直接引用」

**中文說明**: Explanation in Chinese

## AI筆記 | AI Notes
[AI Agent] AI-generated insights and analysis
[AI Agent] AI 生成的洞見和分析

## 我的筆記 | My Notes
[Human] TODO: Your annotations here
[Human] TODO: 你的註解在這裡

## 連結網絡 | Link Network
- **基於** [[Domain-YYYYMMDD-XXX|Concept Name]]
- **導向** [[Domain-YYYYMMDD-YYY|Another Concept]]
- **相關** [[Domain-YYYYMMDD-ZZZ|Related Concept]]

## 來源脈絡 | Source Context
- **來源**: Author (Year)
- **段落**: Section X.X, p.XXX
```

---

## Development Guidelines | 開發指南

### Testing Card Generation | 測試卡片生成

Always test with a sample paper before processing large batches.

在處理大批次前，始終使用範例論文測試。

```bash
# Test with a single paper
# 使用單篇論文測試
python make_slides.py "Test Paper" \
  --pdf test_paper.pdf \
  --style zettelkasten \
  --domain Test \
  --slides 5
```

### Code Style | 代碼風格

- **Python 3.10+** required | 需要 Python 3.10+
- Follow PEP 8 style guidelines | 遵循 PEP 8 風格指南
- Use type hints for function parameters | 使用類型提示
- Document complex logic with comments | 為複雜邏輯添加註釋

### Adding New Features | 添加新功能

When contributing new features:

貢獻新功能時：

1. **Create a feature branch** | 創建功能分支
   ```bash
   git checkout -b feature/YourFeature
   ```

2. **Implement with tests** | 實作並測試
   - Add unit tests for new functions | 為新功能添加單元測試
   - Test with real papers | 使用真實論文測試
   - Validate output format | 驗證輸出格式

3. **Document your changes** | 記錄你的更改
   - Update relevant markdown files | 更新相關 Markdown 文件
   - Add usage examples | 添加使用範例
   - Comment code thoroughly | 徹底註釋代碼

4. **Submit pull request** | 提交 Pull Request
   - Describe the problem solved | 描述解決的問題
   - Show before/after examples | 展示前後對比範例
   - Link to related issues | 連結相關 Issue

---

## Contribution Areas | 貢獻領域

We especially welcome contributions in these areas:

我們特別歡迎在以下領域的貢獻：

### 🎯 High Priority | 高優先級

**1. Optimize Card Generation Prompt** | 優化卡片生成提示詞
- Improve concept extraction accuracy | 提升概念提取準確性
- Enhance link network detection | 增強連結網絡檢測
- Better handling of domain-specific terminology | 更好地處理領域特定術語

**Location**: `templates/prompts/zettelkasten_template.jinja2`

**2. Multi-language Card Generation** | 多語言卡片生成
- Add support for more languages | 支援更多語言
- Improve translation quality | 改進翻譯品質
- Preserve technical terms correctly | 正確保留技術術語

**3. Domain-specific Optimizations** | 領域特定優化
- Cognitive Science | 認知科學
- Linguistics | 語言學
- AI/Machine Learning | AI/機器學習
- Biology | 生物學
- Physics | 物理學

### 🔧 Medium Priority | 中優先級

**4. Link Network Improvements** | 連結網絡改進
- Better relationship type detection | 更好的關係類型檢測
- Confidence scoring for links | 連結信度評分
- Cross-paper concept linking | 跨論文概念連結

**5. Output Format Enhancements** | 輸出格式增強
- Obsidian integration improvements | 改進 Obsidian 整合
- Roam Research format support | 支援 Roam Research 格式
- Notion export support | 支援 Notion 匯出

### 💡 Long-term | 長期

**6. Batch Processing** | 批次處理
- Process multiple papers efficiently | 高效處理多篇論文
- Detect duplicate concepts | 檢測重複概念
- Build cross-paper knowledge network | 建立跨論文知識網絡

---

## File Naming Conventions | 文件命名規範

### Card IDs | 卡片 ID

Format: `Domain-YYYYMMDD-NNN`

格式：`領域-年月日-序號`

**Examples | 範例**:
- `CogSci-20251112-001`
- `Linguistics-20251112-042`
- `AI-20251112-015`

### Domain Codes | 領域代碼

Common domain codes:

常用領域代碼：

| Code | Field | 中文 |
|------|-------|------|
| CogSci | Cognitive Science | 認知科學 |
| Ling | Linguistics | 語言學 |
| AI | Artificial Intelligence | 人工智慧 |
| Bio | Biology | 生物學 |
| Phys | Physics | 物理學 |
| Psych | Psychology | 心理學 |

### Output Directories | 輸出目錄

```
output/zettelkasten_notes/zettel_{CitationKey}_{Date}/
```

**Example | 範例**:
```
output/zettelkasten_notes/zettel_Jones-2024_20251112/
```

---

## Troubleshooting | 故障排除

### Common Issues | 常見問題

**Issue 1**: Card generation produces malformed markdown

**問題 1**: 卡片生成產生格式錯誤的 Markdown

**Solution | 解決方案**:
- Check LLM model temperature (should be < 0.7) | 檢查 LLM 溫度參數（應 < 0.7）
- Verify prompt template syntax | 驗證提示詞模板語法
- Test with different LLM provider | 測試不同的 LLM 提供者

---

**Issue 2**: Links not detected in output

**問題 2**: 輸出中未檢測到連結

**Solution | 解決方案**:
- Ensure paper has sufficient content | 確保論文有足夠內容
- Increase `--detail` level | 增加 `--detail` 層級
- Check if domain is appropriate | 檢查領域是否合適

---

**Issue 3**: LLM connection timeout

**問題 3**: LLM 連接超時

**Solution | 解決方案**:
```bash
# Try different provider
# 嘗試不同提供者
python make_slides.py "Title" --pdf paper.pdf \
  --style zettelkasten \
  --llm-provider google \
  --model gemini-2.0-flash-exp
```

---

## Testing | 測試

### Manual Testing Workflow | 手動測試工作流

1. **Select test paper** | 選擇測試論文
   - Use a paper you're familiar with | 使用你熟悉的論文
   - Ideally 10-30 pages | 最好 10-30 頁

2. **Generate cards** | 生成卡片
   ```bash
   python make_slides.py "Test Paper" \
     --pdf test.pdf \
     --style zettelkasten \
     --domain Test \
     --slides 10
   ```

3. **Validate output** | 驗證輸出
   - Check card structure | 檢查卡片結構
   - Verify links are valid | 驗證連結有效
   - Review concept extraction quality | 審查概念提取品質
   - Test in Obsidian/your note-taking app | 在 Obsidian 或你的筆記應用中測試

4. **Compare with original paper** | 與原論文比較
   - Are key concepts captured? | 關鍵概念是否被捕捉？
   - Are quotes accurate? | 引用是否準確？
   - Are relationships meaningful? | 關係是否有意義？

---

## Community & Support | 社群與支援

### Get Help | 獲取幫助

- **GitHub Issues**: Report bugs and request features | 報告 Bug 和請求功能
- **GitHub Discussions**: Ask questions and share ideas | 提問和分享想法

### Share Your Work | 分享你的成果

We love to see how you're using this system!

我們很想看到你如何使用這個系統！

- Share example outputs | 分享範例輸出
- Post domain-specific optimizations | 發布領域特定優化
- Contribute prompt improvements | 貢獻提示詞改進

---

## Related Resources | 相關資源

### Zettelkasten Method | Zettelkasten 方法

- Niklas Luhmann's original system | Niklas Luhmann 的原始系統
- *How to Take Smart Notes* by Sönke Ahrens | Sönke Ahrens 的《How to Take Smart Notes》
- Zettelkasten.de community | Zettelkasten.de 社群

### Note-taking Tools | 筆記工具

- **Obsidian**: Recommended for viewing generated cards | 推薦用於查看生成的卡片
- **Logseq**: Alternative with graph view | 帶圖形視圖的替代方案
- **Roam Research**: Web-based option | 基於網頁的選項

---

## License | 授權

MIT License - See LICENSE file for details

MIT 授權 - 詳見 LICENSE 文件

---

## Acknowledgments | 致謝

Built with Claude Code | 使用 Claude Code 開發

Inspired by the Zettelkasten methodology | 受 Zettelkasten 方法論啟發

Powered by multiple LLM providers | 由多個 LLM 提供者驅動

---

**Last Updated | 最後更新**: 2025-11-12

**Version | 版本**: v0.3.0

**Status | 狀態**: Stable for community use | 穩定版本，適合社群使用
