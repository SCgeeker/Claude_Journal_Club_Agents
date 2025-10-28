# 快速開始指南

## 🚀 啟動 analyze-paper 功能

有**兩種方式**使用論文分析功能：

### 方式1：直接使用Python腳本（推薦）✅

```bash
# 進入專案目錄
cd D:\core\research\claude_lit_workflow

# 基本分析
python analyze_paper.py <你的PDF路徑>

# 分析並加入知識庫
python analyze_paper.py <你的PDF路徑> --add-to-kb

# 生成JSON格式
python analyze_paper.py <你的PDF路徑> --format json

# 完整選項
python analyze_paper.py <你的PDF路徑> --add-to-kb --format both --output-json result.json
```

### 方式2：在Claude Code中使用Slash Command

在Claude Code聊天中輸入：

```
/analyze-paper <你的PDF路徑>
```

或

```
/analyze-paper <你的PDF路徑> --add-to-kb
```

## 📦 首次使用前準備

### 1. 安裝依賴

```bash
cd D:\core\research\claude_lit_workflow
pip install -r requirements.txt
```

或單獨安裝核心依賴：

```bash
pip install PyPDF2 pdfplumber pyyaml
```

### 2. 測試安裝

```bash
python -c "from src.extractors import PDFExtractor; print('✅ PDF提取器已就緒')"
python -c "from src.knowledge_base import KnowledgeBaseManager; print('✅ 知識庫已就緒')"
```

### 3. 初始化知識庫

```bash
python -c "from src.knowledge_base import KnowledgeBaseManager; kb = KnowledgeBaseManager(); print('✅ 知識庫已初始化')"
```

## 📖 使用示例

### 示例1：快速分析論文

```bash
python analyze_paper.py "D:\core\research\Program_verse\+\pdf\sample.pdf"
```

**輸出內容**：
- 論文標題、作者
- 摘要（前500字）
- 章節結構
- 關鍵詞
- 字元統計

### 示例2：分析並保存到知識庫

```bash
python analyze_paper.py "D:\core\research\Program_verse\+\pdf\sample.pdf" --add-to-kb
```

**額外功能**：
- 創建Markdown筆記（保存在 `knowledge_base/papers/`）
- 建立數據庫索引（支援全文搜索）
- 顯示知識庫統計信息

### 示例3：生成JSON報告

```bash
python analyze_paper.py "D:\core\research\Program_verse\+\pdf\sample.pdf" --format json --output-json analysis_result.json
```

**生成文件**：包含完整結構化數據的JSON文件

### 示例4：完整工作流

```bash
# 分析論文 + 加入知識庫 + 生成JSON
python analyze_paper.py "paper.pdf" --add-to-kb --format both --output-json "paper_analysis.json"
```

## 🔍 查看知識庫內容

### 方法1：使用Python

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager()

# 查看統計
stats = kb.get_stats()
print(f"論文總數: {stats['total_papers']}")

# 搜索論文
results = kb.search_papers("deep learning")
for paper in results:
    print(f"- {paper['title']}")

# 列出所有論文
papers = kb.list_papers(limit=10)
for paper in papers:
    print(f"{paper['id']}: {paper['title']}")
```

### 方法2：直接查看文件

```bash
# 查看Markdown筆記
ls knowledge_base/papers/

# 查看數據庫
sqlite3 knowledge_base/index.db "SELECT title, authors FROM papers;"
```

## 🛠️ 常見問題

### Q1: "Unknown slash command: analyze-paper"

**解決方案**：
- 使用直接Python腳本：`python analyze_paper.py <pdf_path>`
- 或在Claude Code中等待slash command註冊（可能需要重啟會話）

### Q2: "ModuleNotFoundError: No module named 'pdfplumber'"

**解決方案**：
```bash
pip install pdfplumber PyPDF2
```

### Q3: PDF提取失敗

**解決方案**：
```bash
# 嘗試切換提取方法
python analyze_paper.py paper.pdf  # 默認使用pdfplumber

# 或編輯 config/settings.yaml，設置：
# pdf:
#   extraction_method: "pypdf2"
```

### Q4: 中文顯示亂碼

**解決方案**：確保終端支援UTF-8編碼
```bash
# Windows PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 或使用 Windows Terminal
```

## 📊 輸出示例

運行 `python analyze_paper.py paper.pdf --add-to-kb` 後的輸出：

```
============================================================
📄 分析論文: deep_learning_medical.pdf
============================================================

🔍 正在提取PDF內容...
✅ PDF已提取: 25,432 字元

============================================================
📊 基本信息
============================================================
📖 標題: Deep Learning for Medical Image Analysis
👥 作者: John Smith, Jane Doe, Bob Johnson
🏷️ 關鍵詞: deep learning, medical imaging, CNN, diagnosis

📑 論文結構 (6 個章節):
   1. Introduction
   2. Related Work
   3. Methods
   4. Results
   5. Discussion
   6. Conclusion

📝 摘要:
This paper presents a novel deep learning approach for automated
medical image analysis. We propose a convolutional neural network
architecture that achieves state-of-the-art performance...

============================================================
📚 加入知識庫
============================================================
📝 筆記已創建: knowledge_base/papers/Deep_Learning_for_Medical_Image.md
✅ 已加入知識庫 (ID: 1)

📊 知識庫統計:
   論文總數: 1
   主題總數: 0

============================================================
✅ 分析完成！
============================================================
```

## 🎯 下一步

1. **批量處理**: 編寫腳本批量處理多個PDF
2. **搜索功能**: 使用 `kb.search_papers()` 搜索知識庫
3. **主題管理**: 為論文添加主題標籤
4. **生成簡報**: 使用slide-maker（待開發）生成Journal Club風格簡報

## 📚 更多資源

- **完整文檔**: [CLAUDE.md](CLAUDE.md)
- **專案說明**: [README.md](README.md)
- **Skills文檔**: `.claude/skills/` 目錄
- **配置文件**: `config/settings.yaml`

---

**提示**: 如果遇到問題，請查看 [CLAUDE.md](CLAUDE.md:src/extractors/pdf_extractor.py) 中的「故障排除」章節
