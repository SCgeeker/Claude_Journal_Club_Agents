# CLI 操作指南

**版本**: 0.8.0
**更新日期**: 2025-11-27

本指南說明如何使用 `uv run` 操作 claude-lit-workflow 的各項工具。

---

## 環境設置

### 首次安裝

```bash
cd D:\core\research\claude_lit_workflow

# 安裝 uv（如果尚未安裝）
# Windows PowerShell:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 同步專案依賴
uv sync
```

### 驗證安裝

```bash
# 測試 CLI 是否可用
uv run analyze --help
uv run kb --help
uv run slides --help
```

---

## 指令速查表

### 可用指令

| 指令 | 功能 | 狀態 |
|------|------|------|
| `uv run analyze` | 論文分析與入庫 | ✅ 可用 |
| `uv run kb` | 知識庫管理 | ✅ 可用 |
| `uv run slides` | 投影片生成 | ✅ 可用 |
| `uv run embeddings` | 向量嵌入生成 | ✅ 可用 |
| `uv run zettel` | 單篇 Zettel 生成 | 🚧 待實作 |

---

## analyze - 論文分析

分析 PDF 論文並加入知識庫。

### 基本使用

```bash
# 分析論文（僅顯示結果）
uv run analyze paper.pdf

# 分析並加入知識庫
uv run analyze paper.pdf --add-to-kb

# 輸出 JSON 格式
uv run analyze paper.pdf --format json --output-json result.json
```

### 書目檔整合

```bash
# 指定 BibTeX 檔案（自動取得 citekey）
uv run analyze paper.pdf --bib library.bib --add-to-kb

# 🚧 [待實作] 指定 RIS 檔案
uv run analyze paper.pdf --ris references.ris --add-to-kb

# 手動指定 citekey（覆蓋書目檔）
uv run analyze paper.pdf --citekey "Barsalou-1999" --add-to-kb

# 🚧 [待實作] 指定 DOI
uv run analyze paper.pdf --doi "10.1017/S0140525X99002149" --add-to-kb
```

### 參數說明

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `<pdf_path>` | PDF 檔案路徑 | 必填 |
| `--add-to-kb` | 加入知識庫 | False |
| `--format` | 輸出格式 (text/json/both) | text |
| `--output-json` | JSON 輸出路徑 | - |
| `--bib` | BibTeX 檔案路徑 | 自動偵測 |
| `--ris` | RIS 檔案路徑 🚧 | - |
| `--citekey` | 手動指定 citekey | - |
| `--doi` | 指定 DOI 🚧 | - |
| `--validate` | 驗證元數據品質 | False |

---

## kb - 知識庫管理

管理和查詢知識庫。

### 基本查詢

```bash
# 顯示知識庫統計
uv run kb stats

# 列出所有論文
uv run kb list
uv run kb list --limit 20

# 關鍵詞搜索
uv run kb search "embodied cognition"
uv run kb search "視覺模擬" --limit 10
```

### 語義搜索

```bash
# 語義搜索（需先執行 embeddings）
uv run kb semantic-search "認知科學的基礎理論"

# 尋找相似論文
uv run kb similar 42  # 依 paper_id

# 混合搜索（關鍵詞 + 語義）
uv run kb hybrid-search "grounded cognition"
```

### 論文管理

```bash
# 查看單篇論文詳情
uv run kb get 42              # 依 paper_id
uv run kb get Barsalou-1999   # 依 citekey

# 🚧 [待實作] 依 DOI 查詢
uv run kb get --doi "10.1017/S0140525X99002149"

# 刪除論文
uv run kb delete 42
```

### 子指令一覽

| 子指令 | 說明 | 狀態 |
|--------|------|------|
| `stats` | 顯示統計 | ✅ |
| `list` | 列出論文 | ✅ |
| `search` | 關鍵詞搜索 | ✅ |
| `semantic-search` | 語義搜索 | ✅ |
| `similar` | 相似論文 | ✅ |
| `hybrid-search` | 混合搜索 | ✅ |
| `get` | 查看詳情 | ✅ |
| `delete` | 刪除論文 | ✅ |
| `visualize-network` | 概念網絡 | ✅ (暫停使用) |

---

## slides - 投影片生成

生成學術風格投影片。

### 基本使用

```bash
# 從 PDF 生成投影片
uv run slides "論文主題" --pdf paper.pdf

# 從知識庫論文生成
uv run slides "知覺符號系統" --from-kb 42

# 先分析再生成（推薦）
uv run slides "Embodied Cognition" --pdf paper.pdf --analyze-first
```

### 風格與格式

```bash
# 指定學術風格
uv run slides "主題" --pdf paper.pdf --style modern_academic
uv run slides "主題" --pdf paper.pdf --style zettelkasten

# 指定詳細程度
uv run slides "主題" --pdf paper.pdf --detail comprehensive

# 指定語言
uv run slides "主題" --pdf paper.pdf --language chinese
uv run slides "主題" --pdf paper.pdf --language bilingual

# 指定投影片數量
uv run slides "主題" --pdf paper.pdf --slides 20
```

### LLM 選擇

```bash
# 使用 Gemini（預設）
uv run slides "主題" --pdf paper.pdf --llm-provider google

# 使用 Ollama 本地模型
uv run slides "主題" --pdf paper.pdf --llm-provider ollama --model llama3.3

# 使用 OpenAI
uv run slides "主題" --pdf paper.pdf --llm-provider openai --model gpt-4
```

### 參數說明

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `<topic>` | 簡報主題 | 必填 |
| `--pdf` | PDF 檔案路徑 | - |
| `--from-kb` | 知識庫論文 ID | - |
| `--analyze-first` | 先分析再生成 | False |
| `--style` | 學術風格 | modern_academic |
| `--detail` | 詳細程度 | standard |
| `--language` | 語言 | chinese |
| `--slides` | 投影片數量 | 15 |
| `--llm-provider` | LLM 提供者 | auto |
| `--model` | 模型名稱 | - |
| `--output` | 輸出路徑 | 自動生成 |

### 可用風格

| 風格 | 說明 |
|------|------|
| `classic_academic` | 經典學術 |
| `modern_academic` | 現代學術（推薦）|
| `clinical` | 臨床導向 |
| `research_methods` | 研究方法 |
| `literature_review` | 文獻回顧 |
| `case_analysis` | 案例分析 |
| `teaching` | 教學導向 |
| `zettelkasten` | 原子化筆記 |

### 詳細程度

| 程度 | 說明 |
|------|------|
| `minimal` | 極簡（2-3 點/張）|
| `brief` | 簡要（3-4 點/張）|
| `standard` | 標準（4-5 點/張）|
| `detailed` | 詳細（5-6 點/張）|
| `comprehensive` | 完整（6-8 點/張）|

---

## embeddings - 向量嵌入

生成知識庫的向量嵌入（用於語義搜索）。

### 基本使用

```bash
# 生成所有論文的嵌入
uv run embeddings

# 指定 Embedder
uv run embeddings --provider gemini    # 使用 Gemini（推薦）
uv run embeddings --provider ollama    # 使用 Ollama 本地

# 只處理新增的論文
uv run embeddings --incremental
```

### 參數說明

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--provider` | Embedder 提供者 | gemini |
| `--incremental` | 只處理新增 | False |
| `--batch-size` | 批次大小 | 10 |

---

## zettel - Zettelkasten 生成 🚧

> **狀態**: 待實作
>
> 目前請使用 `python generate_zettel_batch.py` 或在 Claude Code 中操作。

### 預計功能

```bash
# 🚧 [待實作] 從知識庫論文生成 Zettel
uv run zettel --paper-id 42
uv run zettel --citekey Barsalou-1999

# 🚧 [待實作] 指定 LLM
uv run zettel --citekey Barsalou-1999 --llm-provider google

# 🚧 [待實作] 指定卡片數量
uv run zettel --citekey Barsalou-1999 --cards 20
```

### 目前替代方案

```bash
# 使用現有批次腳本
python generate_zettel_batch.py

# 或在 Python 中操作
python -c "
from src.generators.zettel_maker import ZettelMaker
# ... 手動呼叫
"
```

---

## 常用工作流程

### 流程 A：單篇論文完整處理

```bash
# 1. 分析並入庫
uv run analyze paper.pdf --bib library.bib --add-to-kb

# 2. 生成 Zettel 卡片（目前使用 Python 腳本）
python generate_zettel_batch.py

# 3. 生成投影片（可選）
uv run slides "論文主題" --from-kb <paper_id>

# 4. 更新向量嵌入（可選）
uv run embeddings --incremental
```

### 流程 B：知識庫查詢

```bash
# 1. 關鍵詞搜索
uv run kb search "visual simulation"

# 2. 語義搜索（更智能）
uv run kb semantic-search "視覺模擬如何影響語言理解"

# 3. 查看詳情
uv run kb get <paper_id>
```

### 流程 C：批次處理多篇論文

```bash
# 1. 準備：將 PDF 和 .bib 放在同一資料夾

# 2. 逐一處理（目前方式）
for pdf in ./papers/*.pdf; do
    uv run analyze "$pdf" --add-to-kb
done

# 3. 批次生成 Zettel
python generate_zettel_batch.py

# 4. 更新嵌入
uv run embeddings
```

---

## 待實作功能一覽

| 功能 | 說明 | 優先級 |
|------|------|--------|
| `uv run zettel` | 單篇 Zettel 生成 CLI | P1 |
| `--ris` 參數 | RIS 格式書目檔支援 | P1 |
| `--doi` 參數 | DOI 指定與查詢 | P1 |
| `--from-bib` 批次 | 從書目檔批次處理 | P2 |
| `kb get --doi` | DOI 備案查詢 | P2 |

---

## 故障排除

### 問題：uv run 找不到指令

```bash
# 確認 pyproject.toml 存在
ls pyproject.toml

# 重新同步
uv sync
```

### 問題：ModuleNotFoundError

```bash
# 重新安裝依賴
uv sync --reinstall
```

### 問題：中文顯示亂碼

```powershell
# Windows PowerShell 設定 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

### 問題：LLM 連接失敗

```bash
# 檢查 API Key
echo $GOOGLE_API_KEY

# 測試 Ollama
curl http://localhost:11434/api/tags

# 切換 LLM 提供者
uv run slides "主題" --pdf paper.pdf --llm-provider ollama
```

---

## 相關文件

- [QUICKSTART.md](QUICKSTART.md) - 快速開始
- [CITEKEY_DESIGN_SPEC.md](CITEKEY_DESIGN_SPEC.md) - Citekey 設計規格
- [CLAUDE.md](../CLAUDE.md) - 完整專案文件
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排除指南

---

## 版本歷史

| 版本 | 日期 | 說明 |
|------|------|------|
| 0.8.0 | 2025-11-27 | 初版，建立 uv 整合 |

---

*本指南由 Claude Code 協助生成*
