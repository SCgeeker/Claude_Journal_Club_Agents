# PDF Extractor Skill

## 功能描述

從PDF學術論文中提取文本、結構化信息和元數據。

## 能力

- 📄 提取完整PDF文本內容（最多50,000字元）
- 🔍 識別論文結構：標題、作者、摘要、章節
- 🏷️ 提取關鍵詞和元數據
- 📊 支援兩種提取方法：pdfplumber（推薦）和PyPDF2
- 💾 輸出JSON格式的結構化數據

## 使用方式

### 基本用法

```python
from src.extractors import PDFExtractor

# 初始化提取器
extractor = PDFExtractor(max_chars=50000, method="pdfplumber")

# 提取PDF
result = extractor.extract("path/to/paper.pdf")

# 訪問提取結果
print(f"標題: {result['structure']['title']}")
print(f"字元數: {result['char_count']}")
print(f"摘要: {result['structure']['abstract']}")
```

### 快速提取

```python
from src.extractors import extract_pdf_text

# 直接獲取文本
text = extract_pdf_text("paper.pdf", max_chars=50000)
```

### 命令行使用

```bash
python src/extractors/pdf_extractor.py paper.pdf
```

## 輸出格式

```json
{
  "file_path": "paper.pdf",
  "file_name": "paper.pdf",
  "full_text": "完整文本內容...",
  "char_count": 25000,
  "truncated": false,
  "structure": {
    "title": "論文標題",
    "authors": ["作者1", "作者2"],
    "abstract": "摘要內容...",
    "sections": [
      {"title": "Introduction", "position": 1234}
    ],
    "keywords": ["關鍵詞1", "關鍵詞2"],
    "references_found": true
  },
  "extraction_method": "pdfplumber"
}
```

## 配置選項

- `max_chars`: 最大字元數限制（默認：50,000）
- `method`: 提取方法 - "pdfplumber"（推薦）或 "pypdf2"

## 依賴項

```bash
pip install pdfplumber PyPDF2
```

## 注意事項

1. pdfplumber對於複雜排版的處理更好，但需要額外依賴
2. PyPDF2作為備選方案，速度更快但準確性略低
3. 對於超過50,000字元的文檔會自動截斷
4. 結構識別基於常見的學術論文格式

## 與Journal Club的兼容性

此Skill完全兼容Journal Club的PDF處理流程，並擴展了以下功能：
- 字元限制從10k提升到50k（5倍）
- 增加結構化元數據提取
- 支援多種提取方法
- JSON格式輸出便於後續處理
