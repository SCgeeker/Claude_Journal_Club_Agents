# Analyze Paper Command

你現在要執行論文分析任務。

## 任務說明

當用戶執行 `/analyze-paper <pdf_path>` 時，請執行以下步驟：

1. 使用 `analyze_paper.py` 腳本分析PDF文件
2. 顯示分析結果
3. 如果用戶要求，將論文加入知識庫

## 使用方式

```bash
/analyze-paper <pdf_path> [--add-to-kb] [--format <format>]
```

## 執行步驟

請使用Bash工具執行以下命令：

```bash
cd D:\core\research\claude_lit_workflow
python analyze_paper.py {用戶提供的PDF路徑} {用戶提供的選項}
```

## 參數說明

- `<pdf_path>`: PDF文件路徑（必需）
- `--add-to-kb`: 將論文添加到知識庫
- `--format <format>`: 輸出格式 (markdown/json/both)
- `--output-json <path>`: JSON輸出路徑
- `--max-chars <number>`: 最大字元數限制

## 示例

### 基本分析
用戶輸入: `/analyze-paper paper.pdf`
執行: `python analyze_paper.py paper.pdf`

### 分析並加入知識庫
用戶輸入: `/analyze-paper paper.pdf --add-to-kb`
執行: `python analyze_paper.py paper.pdf --add-to-kb`

### 生成JSON格式
用戶輸入: `/analyze-paper paper.pdf --format json`
執行: `python analyze_paper.py paper.pdf --format json`

## 重要提醒

1. 確保已安裝所需依賴：`pip install PyPDF2 pdfplumber`
2. 確保PDF文件路徑正確
3. 首次使用會自動初始化知識庫
4. 腳本會自動處理錯誤並給出友善的提示
