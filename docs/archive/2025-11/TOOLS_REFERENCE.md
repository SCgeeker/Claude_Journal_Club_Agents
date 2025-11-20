# CLI 工具速查表

**最後更新**: 2025-11-04
**當前版本**: 1.1 (Phase 1.5 + Phase 2 準備版)
**工具總數**: 11個核心工具 + 6個元數據修復工具

---

## 🚀 快速命令

### 📊 分析與入庫

```bash
# 單篇論文分析 + 入庫 + 自動生成 Zettelkasten
python analyze_paper.py paper.pdf --add-to-kb --validate --generate-zettel

# 只分析不入庫
python analyze_paper.py paper.pdf --validate --min-score 60

# 分析 + 入庫 + 生成簡報
python analyze_paper.py paper.pdf --add-to-kb --make-slides --style modern_academic
```

### 📚 知識庫管理（最常用）

```bash
# 全文搜索
python kb_manage.py search "深度學習" --limit 10

# 語義搜索 (需先生成 embeddings)
python kb_manage.py semantic-search "AI literacy 應用" --type papers --limit 5

# 混合搜索 (FTS5 + Vector)
python kb_manage.py hybrid-search "認知科學與決策" --limit 10

# 尋找相似論文
python kb_manage.py similar 14 --limit 5

# 查看知識庫統計
python kb_manage.py stats

# 查看特定論文詳情
python kb_manage.py show 14

# 查看所有論文列表
python kb_manage.py list --sort year --descending
```

### 📦 批次處理

```bash
# 批次導入 PDF + 入庫 + 生成 Zettelkasten
python batch_process.py --folder "D:/pdfs/CogSci" --domain CogSci --add-to-kb --generate-zettel --workers 3

# 只導入知識庫（不生成 Zettelkasten）
python batch_process.py --folder "D:/pdfs" --domain Research --add-to-kb

# 指定特定 PDF 文件
python batch_process.py --files paper1.pdf paper2.pdf --add-to-kb

# 詳細錯誤報告
python batch_process.py --folder "D:/pdfs" --add-to-kb --report batch_report.txt
```

### ✅ 質量檢查

```bash
# 檢查所有論文 + 檢測重複
python check_quality.py --detect-duplicates --threshold 0.85

# 只查看有嚴重問題的論文
python check_quality.py --critical-only

# 詳細檢查報告
python check_quality.py --detail comprehensive --output quality_report.txt

# JSON 格式輸出
python check_quality.py --format json --output quality_report.json

# 檢查特定論文
python check_quality.py --paper-id 27
```

### 🔢 向量嵌入與語義搜索

```bash
# 生成所有論文和 Zettelkasten 的 embeddings (需 GOOGLE_API_KEY)
python generate_embeddings.py --provider gemini --yes

# 只生成論文 embeddings
python generate_embeddings.py --papers-only --provider gemini

# 只生成 Zettelkasten embeddings
python generate_embeddings.py --zettel-only --provider ollama

# 查看統計信息
python generate_embeddings.py --stats
```

### 🧹 工作清理與維護

```bash
# 自動清理工作階段（刪除臨時檔案 + 備份知識庫）
python cleanup_session.py --auto

# 互動式清理（詢問後執行）
python cleanup_session.py

# 只備份不刪除
python cleanup_session.py --backup-only
```

### 🔧 元數據修復（高級用途）

```bash
# 互動式從 PDF 修復元數據
python interactive_repair.py

# 修復特定 PDF 資料夾
python interactive_repair.py --folder "D:/pdfs" --mode batch

# 修復特定論文 (by paper_id)
python fix_metadata.py --paper-id 23 --from-pdf

# 同步 YAML 標題到數據庫
python sync_yaml_titles.py
```

### 🎨 簡報生成

```bash
# 從 PDF 生成簡報（教學導向）
python make_slides.py "論文主題" --pdf paper.pdf --style teaching --slides 20

# 從知識庫論文生成簡報
python make_slides.py "AI 相關研究" --from-kb 14 --style modern_academic --language bilingual

# 先分析再生成（推薦）
python make_slides.py "主題" --pdf paper.pdf --analyze-first --style literature_review

# 生成 Markdown 格式簡報
python make_slides.py "主題" --pdf paper.pdf --format markdown --style research_methods
```

---

## 📊 工具功能矩陣

| # | 工具名稱 | 主要功能 | 模式 | 狀態 | 優先級 |
|----|---------|--------|------|------|--------|
| 1 | **analyze_paper.py** | PDF 分析 + 入庫 + Zettelkasten | CLI/API | ✅ | P0 |
| 2 | **kb_manage.py** | 知識庫管理（搜索、語義搜索） | CLI | ✅ | P0 |
| 3 | **make_slides.py** | 簡報生成（8種風格、多LLM） | CLI | ✅ | P1 |
| 4 | **batch_process.py** | 批次處理（平行、知識庫+Zettel） | CLI | ✅ | P0 |
| 5 | **check_quality.py** | 質量檢查（5大項目、79行規則） | CLI | ✅ | P1 |
| 6 | **generate_embeddings.py** | 向量嵌入生成（Gemini/Ollama） | CLI | ✅ | P1 |
| 7 | **cleanup_session.py** | 工作清理 + 備份 | CLI | ✅ | P2 |
| 8 | **fix_metadata.py** | 元數據修復 (v2.0) | CLI | ✅ | P2 |
| 9 | **interactive_repair.py** | 互動式 PDF 修復（11篇成功） | CLI | ✅ | P2 |
| 10 | **enhanced_fuzzy_match.py** | 模糊匹配工具（測試用） | CLI | ⚠️ | P3 |
| 11 | **standardize_zettel_index.py** | Zettelkasten 索引標準化 | CLI | ✅ | P1 |

---

## 🎯 使用工作流

### 工作流 A: 新增單篇論文

```
1. 分析論文
   python analyze_paper.py paper.pdf --add-to-kb --validate

2. 檢查質量
   python check_quality.py --paper-id <new_id>

3. 生成簡報（可選）
   python make_slides.py "論文主題" --from-kb <paper_id>
```

### 工作流 B: 批次導入

```
1. 批次處理
   python batch_process.py --folder "D:/pdfs" --domain CogSci --add-to-kb --generate-zettel

2. 質量檢查
   python check_quality.py --critical-only

3. 生成向量（一次性）
   python generate_embeddings.py --provider gemini --yes

4. 清理環境
   python cleanup_session.py --auto
```

### 工作流 C: 知識庫查詢

```
1. 全文搜索
   python kb_manage.py search "關鍵詞"

2. 語義搜索（深度）
   python kb_manage.py semantic-search "概念描述"

3. 尋找相似
   python kb_manage.py similar <paper_id> --limit 5
```

---

## 🔧 環境配置

### API 密鑰設置

在專案根目錄創建 `.env` 文件：

```bash
# Google Gemini (用於向量搜索和簡報生成)
GOOGLE_API_KEY=your-google-api-key-here

# OpenAI (可選，用於簡報生成)
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic Claude (可選，用於簡報生成)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Ollama (本地免費選項)
OLLAMA_URL=http://localhost:11434
```

### 環境變數驗證

```bash
# 驗證配置
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

print('API Key 狀態:')
print(f'  GOOGLE_API_KEY: {'✅' if os.getenv('GOOGLE_API_KEY') else '❌'}')
print(f'  OPENAI_API_KEY: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}')
print(f'  ANTHROPIC_API_KEY: {'✅' if os.getenv('ANTHROPIC_API_KEY') else '❌'}')
print(f'  OLLAMA_URL: {'✅' if os.getenv('OLLAMA_URL') else '❌'}')
"
```

---

## 📈 常見任務快速查詢

| 任務 | 命令 | 預期時間 |
|------|------|---------|
| 分析 1 篇 PDF | `analyze_paper.py` | 30-60 秒 |
| 入庫 1 篇論文 | `--add-to-kb` flag | 10 秒 |
| 生成 Zettelkasten (12 卡片) | `--generate-zettel` | 60-120 秒 |
| 批次處理 10 篇 PDF | `batch_process.py` (3 workers) | 5-10 分鐘 |
| 檢查 30 篇論文質量 | `check_quality.py` | 10 秒 |
| 生成所有 embeddings (675 項) | `generate_embeddings.py` | 3-5 分鐘 |
| 語義搜索 1 次查詢 | `kb_manage.py semantic-search` | <1 秒 |
| 生成 15 張簡報 | `make_slides.py` | 60-120 秒 |

---

## ⚠️ 常見問題與解決方案

### Q1: `GOOGLE_API_KEY` 未設置
```bash
# 解決方案
export GOOGLE_API_KEY="your-api-key-here"
# 或在 .env 文件中設置
```

### Q2: Ollama 連接失敗
```bash
# 檢查服務
curl http://localhost:11434/api/tags

# 啟動 Ollama
ollama serve

# 下載模型
ollama pull qwen3-embedding:4b
```

### Q3: 向量搜索結果精準度低
```bash
# 使用混合搜索而不是純語義搜索
python kb_manage.py hybrid-search "查詢詞"

# 或調整相似度閾值
python kb_manage.py semantic-search "查詢詞" --threshold 0.65
```

### Q4: 批次處理超時
```bash
# 減少 workers 數量
python batch_process.py --folder "D:/pdfs" --workers 2 --timeout 600

# 或分批處理
python batch_process.py --files paper1.pdf paper2.pdf --add-to-kb
```

---

## 📚 參考資源

### 內部文檔
- **CLAUDE.md** - 完整的專案說明和 API 文檔
- **AGENT_SKILL_DESIGN.md** - 架構設計和實施路線圖
- **README.md** - 使用說明和快速開始

### 外部資源
- [Google Gemini API 文檔](https://ai.google.dev/gemini-api/docs/)
- [ChromaDB 文檔](https://docs.trychroma.com/)
- [python-pptx 文檔](https://python-pptx.readthedocs.io/)
- [SQLite FTS5](https://www.sqlite.org/fts5.html)

---

## 🔄 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.1 | 2025-11-04 | Phase 1.5 完成，新增向量搜索和混合搜索命令 |
| 1.0 | 2025-10-31 | 初始版本，覆蓋 Phase 1 的所有工具 |

---

**最後提醒**: 所有命令都支援 `--help` 參數查看詳細選項。例如：
```bash
python kb_manage.py semantic-search --help
python batch_process.py --help
python make_slides.py --help
```
