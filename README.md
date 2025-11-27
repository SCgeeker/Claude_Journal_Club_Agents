# Claude Lit Workflow

學術文獻處理系統 - 論文分析、投影片生成、Zettelkasten 卡片管理

## 功能

- **論文分析** - PDF 提取、元數據解析
- **投影片生成** - 8 種學術風格、多 LLM 支援
- **Zettelkasten** - 原子化卡片生成
- **知識庫** - 全文搜索、語義搜索

## 快速開始

```bash
# 安裝
cd claude_lit_workflow
uv sync

# 分析論文
uv run analyze paper.pdf --add-to-kb

# 知識庫查詢
uv run kb list
uv run kb search "關鍵詞"

# 生成投影片
uv run slides "主題" --pdf paper.pdf
```

## CLI 指令

| 指令 | 功能 |
|------|------|
| `uv run analyze` | 論文分析 |
| `uv run kb` | 知識庫管理 |
| `uv run slides` | 投影片生成 |
| `uv run embeddings` | 向量嵌入 |

詳見 [docs/CLI_GUIDE.md](docs/CLI_GUIDE.md)

## 文檔

- [CLI 操作指南](docs/CLI_GUIDE.md)
- [快速開始](docs/QUICKSTART.md)
- [故障排除](docs/TROUBLESHOOTING.md)
- [Citekey 設計規格](docs/CITEKEY_DESIGN_SPEC.md)

## 技術棧

- Python 3.10+
- uv (套件管理)
- SQLite + ChromaDB
- Gemini / OpenAI / Ollama

## 授權

MIT License

---

**版本**: 0.8.0 | **更新**: 2025-11-27
