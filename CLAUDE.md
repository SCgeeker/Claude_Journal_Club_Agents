# CLAUDE.md

本文件為 Claude Code 提供專案指引。

## 專案概述

**知識生產器 (Claude Lit Workflow)** 是一個以 Claude Code 為核心的學術文獻處理系統。

### 核心功能

- **論文分析**: PDF 提取、元數據解析、知識庫管理
- **內容生成**: 投影片生成、Zettelkasten 卡片生成
- **知識查詢**: 全文搜索、語義搜索、相似內容發現

### 目前開發重點

1. **單篇論文處理流程優化** - 手動 uv 指令操作
2. **Citekey 系統** - 支援多種書目管理平台
3. **ProgramVerse 整合** - 匯出/匯入 Zettelkasten 卡片

> **暫停功能**: 概念網絡分析（Phase 2.4 RelationFinder 改進）

---

## 專案架構

```
claude_lit_workflow/
├── analyze_paper.py       # 論文分析 CLI
├── make_slides.py         # 投影片生成 CLI
├── kb_manage.py           # 知識庫管理 CLI
├── generate_embeddings.py # 向量嵌入 CLI
├── generate_zettel_batch.py # Zettel 生成腳本
├── pyproject.toml         # uv 專案配置
│
├── src/                   # 源碼模組 → src/CLAUDE.md
├── knowledge_base/        # 知識庫 → knowledge_base/CLAUDE.md
├── output/                # 輸出 → output/CLAUDE.md
├── templates/             # 模板 → templates/CLAUDE.md
├── config/                # 配置 → config/CLAUDE.md
└── docs/                  # 文檔 → docs/CLAUDE.md
```

> 各目錄詳細說明請參見對應的 `CLAUDE.md`

---

## CLI 指令

### 環境設置

```bash
cd D:\core\research\claude_lit_workflow
uv sync
```

### 核心指令

```bash
# 論文分析
uv run analyze paper.pdf --add-to-kb

# 知識庫管理
uv run kb list
uv run kb search "關鍵詞"
uv run kb semantic-search "語義查詢"

# 投影片生成
uv run slides "主題" --pdf paper.pdf

# 向量嵌入
uv run embeddings
```

### 完整指令說明

參見 [docs/CLI_GUIDE.md](docs/CLI_GUIDE.md)

---

## 技術棧

- **Python 3.10+**
- **uv**: 套件管理
- **SQLite**: 知識庫索引
- **ChromaDB**: 向量資料庫
- **Jinja2**: Prompt 模板
- **LLM**: Gemini, OpenAI, Anthropic, Ollama

---

## 多 LLM 支援

| Provider | 模型 | 用途 |
|----------|------|------|
| **Google Gemini** | gemini-2.0-flash-exp | 預設推薦 |
| **Ollama** | llama3.3:70b | 本地運行 |
| **OpenAI** | gpt-4 | 高品質輸出 |
| **Anthropic** | claude-3-haiku | 快速低成本 |

---

## 開發規範

### 新增功能

1. 在 `src/` 中實作模組
2. 在 `pyproject.toml` 中定義 CLI 入口（如需要）
3. 更新 `docs/CLI_GUIDE.md`

### Citekey 規範

- 預設格式: `Author-Year`（如 `Barsalou-1999`）
- 支援從 BibTeX/RIS 匯入
- 詳見 [docs/CITEKEY_DESIGN_SPEC.md](docs/CITEKEY_DESIGN_SPEC.md)

### 輸出規範

Zettelkasten 輸出結構：
```
output/zettelkasten_notes/
└── zettel_{citekey}_{date}_{model}/
    ├── zettel_index.md
    └── zettel_cards/
        ├── {citekey}-001.md
        ├── {citekey}-002.md
        └── ...
```

---

## ProgramVerse 整合

本專案與 ProgramVerse 採用**平行開發**模式。

### 整合流程

```
Claude Lit Workflow          ProgramVerse
────────────────────         ────────────
output/zettelkasten_notes/
        │
        └──► import_zettel.py ──► 0️⃣Annotation/{citekey}/
             (ProgramVerse 端)
```

### 相關文檔

- [docs/EXPORT_FORMAT_SPEC.md](docs/EXPORT_FORMAT_SPEC.md) - 輸出格式規範
- [docs/IMPORT_TOOL_SPEC.md](docs/IMPORT_TOOL_SPEC.md) - 匯入工具規格

---

## 待實作功能

| 功能 | 優先級 | 說明 |
|------|--------|------|
| `uv run zettel` | P1 | 單篇 Zettel 生成 CLI |
| citekey_resolver.py | P1 | Citekey 解析模組 |
| ris_parser.py | P1 | RIS 格式支援 |
| doi_resolver.py | P1 | DOI 查詢支援 |

---

## 相關資源

- **CLI 指南**: [docs/CLI_GUIDE.md](docs/CLI_GUIDE.md)
- **快速開始**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **故障排除**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

**版本**: 0.8.0
**更新日期**: 2025-11-27
