# Claude Lit Workflow

學術文獻處理系統 - 論文分析、投影片生成、Zettelkasten 卡片管理

## 功能

- **論文分析** - PDF 提取、元數據解析、自動加入知識庫
- **投影片生成** - 7 種學術風格、自動推斷主題
- **Zettelkasten** - 原子化卡片生成、跨論文連結
- **知識庫** - 全文搜索、語義搜索、向量嵌入

## 快速開始

```bash
# 安裝
cd claude_lit_workflow
uv sync
```

### 生成簡報

```bash
# 從 PDF 生成投影片（主題自動從檔名推斷）
uv run slides --pdf paper.pdf

# 指定風格和詳細程度
uv run slides --pdf paper.pdf --style modern_academic --detail comprehensive
```

### 生成 Zettel 卡片

```bash
# 從 PDF 生成原子化筆記卡片
uv run zettel --pdf paper.pdf

# 從知識庫論文生成
uv run zettel --from-kb 1
```

### 分析論文

```bash
# 分析 PDF 並加入知識庫
uv run analyze paper.pdf --add-to-kb

# 僅分析不加入知識庫
uv run analyze paper.pdf
```

### 管理知識庫

```bash
# 列出所有論文
uv run kb list

# 搜索論文
uv run kb search "關鍵詞"

# 語義搜索
uv run kb semantic-search "概念描述"
```

## CLI 指令總覽

| 指令 | 功能 | 常用參數 |
|------|------|----------|
| `uv run slides` | 投影片生成 | `--pdf`, `--style`, `--detail` |
| `uv run zettel` | Zettel 卡片生成 | `--pdf`, `--from-kb` |
| `uv run analyze` | 論文分析 | `--add-to-kb`, `--doi` |
| `uv run kb` | 知識庫管理 | `list`, `search`, `import-zettel` |

**進階功能**：[docs/CLI_GUIDE.md](docs/CLI_GUIDE.md)

## 文檔

- [CLI 操作指南](docs/CLI_GUIDE.md) - 完整指令說明
- [快速開始](docs/QUICKSTART.md)
- [故障排除](docs/TROUBLESHOOTING.md)

## 技術棧

- Python 3.10+ / uv
- SQLite + ChromaDB
- Gemini / OpenAI / Ollama

## 授權

MIT License

---

**版本**: 0.10.1 | **更新**: 2025-11-29
