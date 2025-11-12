# 故障排除指南 (Troubleshooting Guide)

本文檔收集知識生產器系統的常見問題和解決方案。

**最後更新**: 2025-11-07
**版本**: 1.0.0

---

## 目錄

- [環境設置問題](#環境設置問題)
- [PDF 處理問題](#pdf-處理問題)
- [知識庫問題](#知識庫問題)
- [向量搜索問題](#向量搜索問題)
- [LLM 連接問題](#llm-連接問題)
- [投影片生成問題](#投影片生成問題)
- [批次處理問題](#批次處理問題)
- [編碼和路徑問題](#編碼和路徑問題)

---

## 環境設置問題

### 問題 1: Python 版本不符

**症狀**:
```
SyntaxError: invalid syntax
```

**原因**: Python 版本 < 3.10

**解決方案**:
```bash
# 檢查版本
python --version

# 安裝 Python 3.10+
# Windows: 從 python.org 下載
# macOS: brew install python@3.10
# Linux: sudo apt install python3.10
```

---

### 問題 2: 依賴安裝失敗

**症狀**:
```
ERROR: Could not find a version that satisfies the requirement
```

**解決方案**:
```bash
# 更新 pip
python -m pip install --upgrade pip

# 清除快取重新安裝
pip cache purge
pip install -r requirements.txt

# 如果仍失敗，逐個安裝
pip install chromadb tqdm numpy
pip install google-generativeai anthropic openai
pip install python-pptx jinja2 pyyaml
```

---

### 問題 3: 環境變數未設置

**症狀**:
```
ValueError: GOOGLE_API_KEY not found
```

**解決方案**:

**方法 1: 環境變數（臨時）**
```bash
# Windows (PowerShell)
$env:GOOGLE_API_KEY="your-api-key"
$env:ANTHROPIC_API_KEY="your-api-key"

# macOS/Linux (Bash)
export GOOGLE_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
```

**方法 2: .env 文件（永久）**
```bash
# 複製範例文件
cp .env.example .env

# 編輯 .env 文件
# 添加你的 API keys
GOOGLE_API_KEY=your-api-key-here
ANTHROPIC_API_KEY=your-api-key-here
OPENAI_API_KEY=your-api-key-here
```

---

## PDF 處理問題

### 問題 1: PDF 提取失敗

**症狀**:
```
Error: Unable to extract text from PDF
```

**原因**: PDF 格式問題或提取方法不適合

**解決方案**:

```python
# 方法 1: 切換提取方法
from src.extractors.pdf_extractor import PDFExtractor

# 嘗試 pdfplumber（默認，推薦）
extractor = PDFExtractor(method="pdfplumber")

# 如果失敗，嘗試 PyPDF2
extractor = PDFExtractor(method="pypdf2")
```

```bash
# 方法 2: 使用 CLI 指定方法
python analyze_paper.py paper.pdf --method pypdf2
```

---

### 問題 2: PDF 包含圖片文字

**症狀**: 提取的文本缺少圖片中的文字

**原因**: PDF 掃描版，文字嵌入在圖片中

**解決方案**:

目前系統不支援 OCR。建議：
1. 使用其他工具先進行 OCR（如 Adobe Acrobat、Tesseract）
2. 使用有文字層的 PDF 版本

---

### 問題 3: PDF 字元限制

**症狀**:
```
Warning: PDF content truncated to 50000 characters
```

**原因**: PDF 內容超過字元限制（50,000 字元）

**解決方案**:

```yaml
# 修改 config/settings.yaml
pdf:
  char_limit: 100000  # 增加限制（注意 LLM token 限制）
```

---

## 知識庫問題

### 問題 1: 知識庫索引錯誤

**症狀**:
```
sqlite3.OperationalError: no such table: papers
```

**原因**: 數據庫未初始化或損壞

**解決方案**:

```bash
# 方法 1: 重新初始化數據庫（危險：會刪除所有數據）
rm index.db
python -c "from src.knowledge_base import KnowledgeBaseManager; KnowledgeBaseManager()"

# 方法 2: 從備份恢復
cp knowledge_base_backup/index.db ./index.db
```

---

### 問題 2: 論文重複導入

**症狀**: 相同論文被重複加入知識庫

**解決方案**:

```bash
# 使用質量檢查器檢測重複
python check_quality.py --detect-duplicates --threshold 0.85

# 手動刪除重複
python kb_manage.py delete-paper <paper_id>
```

---

### 問題 3: 元數據缺失

**症狀**: 論文標題、作者、年份等為空

**原因**: PDF 提取失敗或 metadata 未正確解析

**解決方案**:

```bash
# 使用質量檢查器識別問題
python check_quality.py --critical-only

# 手動修復單篇論文
python kb_manage.py update-paper <paper_id> \
    --title "正確標題" \
    --authors "作者" \
    --year 2025
```

---

## 向量搜索問題

### 問題 1: ChromaDB 未安裝

**症狀**:
```
ModuleNotFoundError: No module named 'chromadb'
```

**解決方案**:
```bash
pip install chromadb tqdm numpy
```

---

### 問題 2: Gemini API 錯誤

**症狀**:
```
google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded
```

**原因**: API 免費配額用盡或速率限制

**解決方案**:

```bash
# 方法 1: 切換到 Ollama（本地免費）
python generate_embeddings.py --provider ollama

# 方法 2: 等待配額重置（每分鐘 60 次請求）
# 方法 3: 升級 Gemini API 計畫
```

---

### 問題 3: 搜索結果相似度過低

**症狀**: 搜索結果相似度 < 20%

**可能原因和解決方案**:

1. **語言不一致**
   ```bash
   # 確保查詢和文檔語言一致
   python kb_manage.py semantic-search "cognitive science"  # 英文查詢
   python kb_manage.py semantic-search "認知科學"          # 中文查詢
   ```

2. **查詢詞不夠具體**
   ```bash
   # 不夠具體
   python kb_manage.py semantic-search "研究"

   # 更具體
   python kb_manage.py semantic-search "認知科學中的視覺注意機制研究"
   ```

3. **嵌入向量未更新**
   ```bash
   # 重新生成嵌入
   python generate_embeddings.py
   ```

4. **使用混合搜索**
   ```bash
   # 結合關鍵詞匹配
   python kb_manage.py hybrid-search "認知科學"
   ```

**詳細指南**: [docs/modules/VECTOR_SEARCH.md#故障排除](modules/VECTOR_SEARCH.md#故障排除)

---

## LLM 連接問題

### 問題 1: Ollama 連接失敗

**症狀**:
```
ConnectionError: Unable to connect to Ollama at http://localhost:11434
```

**解決方案**:

```bash
# 步驟 1: 檢查 Ollama 是否運行
curl http://localhost:11434/api/tags

# 步驟 2: 啟動 Ollama
ollama serve

# 步驟 3: 確認模型已下載
ollama list

# 步驟 4: 如果模型不存在，下載
ollama pull gemma2:latest
ollama pull qwen3-embedding:4b
```

---

### 問題 2: Gemini API 連接超時

**症狀**:
```
TimeoutError: Request timed out
```

**解決方案**:

```bash
# 方法 1: 檢查網絡連接
ping google.com

# 方法 2: 使用代理
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"

# 方法 3: 切換到其他 LLM
python make_slides.py "主題" --llm-provider anthropic
```

---

### 問題 3: API Key 無效

**症狀**:
```
google.api_core.exceptions.PermissionDenied: 403 API key not valid
```

**解決方案**:

```bash
# 步驟 1: 驗證 API Key
echo $GOOGLE_API_KEY

# 步驟 2: 從 Google AI Studio 重新生成
# https://makersuite.google.com/app/apikey

# 步驟 3: 更新 .env 文件
nano .env
# 確認 GOOGLE_API_KEY=your-new-key

# 步驟 4: 重新載入環境變數
source .env  # macOS/Linux
# 或重新啟動終端
```

---

## 投影片生成問題

### 問題 1: 投影片內容溢出

**症狀**: 文字超出投影片邊界

**原因**: 內容過多或字體過大

**解決方案**:

系統已內建智能排版，會自動調整。如仍有問題：

```bash
# 方法 1: 使用更簡潔的詳細程度
python make_slides.py "主題" --detail minimal

# 方法 2: 減少投影片數量（增加每張密度）
python make_slides.py "主題" --slides 10

# 方法 3: 手動編輯生成的 PPTX
```

---

### 問題 2: LLM 生成的內容不準確

**症狀**: 投影片內容與 PDF 原文不符

**原因**: 使用「快速模式」直接從 PDF 生成

**解決方案**:

```bash
# 使用「知識驅動模式」（推薦）
# 步驟 1: 先分析 PDF
python analyze_paper.py paper.pdf --add-to-kb

# 步驟 2: 從知識庫生成（更準確）
python make_slides.py "主題" --from-kb <paper_id>
```

---

### 問題 3: 模型選擇錯誤

**症狀**: 使用了不想要的 LLM 模型

**解決方案**:

```bash
# 明確指定 LLM
python make_slides.py "主題" --llm-provider gemini --model gemini-2.0-flash-exp

# 查看可用模型
python make_slides.py --help
```

---

## 批次處理問題

### 問題 1: PDF 處理超時

**症狀**:
```
TimeoutError: Processing exceeded 300 seconds
```

**原因**: PDF 過大或 LLM 響應慢

**解決方案**:

```bash
# 方法 1: 增加 timeout
python batch_process.py <folder> --timeout 600

# 方法 2: 減少 worker 數量（避免資源競爭）
python batch_process.py <folder> --workers 1

# 方法 3: 跳過失敗文件
python batch_process.py <folder> --error-handling skip
```

---

### 問題 2: 批次處理中斷

**症狀**: 處理到一半程序停止

**原因**: 錯誤處理策略為 `stop`

**解決方案**:

```bash
# 使用 skip 策略（跳過失敗文件）
python batch_process.py <folder> --error-handling skip

# 或使用 retry 策略
python batch_process.py <folder> --error-handling retry --max-retries 3
```

---

### 問題 3: 內存不足

**症狀**:
```
MemoryError: Unable to allocate memory
```

**原因**: 平行處理過多文件

**解決方案**:

```bash
# 減少 worker 數量
python batch_process.py <folder> --workers 1

# 分批處理
python batch_process.py <folder> --limit 10
```

---

## 編碼和路徑問題

### 問題 1: Windows 路徑錯誤

**症狀**:
```
FileNotFoundError: No such file or directory: 'D:\folder\file.pdf'
```

**原因**: Windows 反斜線 `\` 轉義問題

**解決方案**:

```python
# 方法 1: 使用 raw string
path = r"D:\folder\file.pdf"

# 方法 2: 使用正斜線
path = "D:/folder/file.pdf"

# 方法 3: 使用 pathlib（推薦）
from pathlib import Path
path = Path("D:/folder/file.pdf")
```

---

### 問題 2: 中文路徑問題

**症狀**:
```
UnicodeDecodeError: 'gbk' codec can't decode byte
```

**原因**: Windows 默認編碼不是 UTF-8

**解決方案**:

系統已內建 UTF-8 處理，如仍有問題：

```python
# 在腳本開頭添加
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

---

### 問題 3: Emoji 顯示錯誤

**症狀**:
```
UnicodeEncodeError: 'cp950' codec can't encode character '✅'
```

**原因**: Windows 終端編碼問題

**解決方案**:

```bash
# 方法 1: 使用 Windows Terminal（推薦）
# https://aka.ms/terminal

# 方法 2: 設置終端編碼
chcp 65001

# 方法 3: 使用 --no-emoji 參數（如果工具支援）
python kb_manage.py list --no-emoji
```

---

## 其他常見問題

### 問題 1: Git 操作失敗

**症狀**:
```
fatal: not a git repository
```

**解決方案**:

```bash
# 初始化 Git
git init

# 或確認在正確的專案目錄
cd /path/to/claude_lit_workflow
```

---

### 問題 2: 配置文件錯誤

**症狀**:
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**原因**: YAML 語法錯誤

**解決方案**:

```bash
# 驗證 YAML 語法
python -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"

# 使用 YAML 驗證工具
# https://www.yamllint.com/
```

---

### 問題 3: 權限錯誤

**症狀**:
```
PermissionError: [Errno 13] Permission denied
```

**解決方案**:

```bash
# Windows: 以管理員身份運行
# macOS/Linux: 添加執行權限
chmod +x script.py

# 或使用 python 明確執行
python script.py
```

---

## 獲取幫助

如果以上方法都無法解決問題：

1. **查看詳細錯誤信息**
   ```bash
   # 使用 --verbose 參數
   python kb_manage.py command --verbose

   # 查看完整堆疊追蹤
   python -u script.py 2>&1 | tee error.log
   ```

2. **檢查相關文檔**
   - [CLAUDE.md](../CLAUDE.md) - 主文檔
   - [docs/modules/](modules/) - 模組文檔
   - [examples/](../examples/) - 範例代碼

3. **提交 Issue**
   - 到專案 GitHub 提交 issue
   - 附上錯誤信息、環境信息（Python 版本、OS）

4. **查看 Changelog**
   - [CHANGELOG.md](../CHANGELOG.md) - 可能已在新版本修復

---

**最後更新**: 2025-11-07
**版本**: 1.0.0
