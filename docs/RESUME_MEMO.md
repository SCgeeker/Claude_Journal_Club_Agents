# Resume Memo - PDF 工具整合

**日期**: 2025-11-28
**狀態**: 待實作

---

## 決策摘要

### 選擇：輕量方案

整合 **PDFExtractor** + **MarkItDown** 兩種後端：

| 後端 | 用途 | 特點 |
|------|------|------|
| `pdfplumber` | 現有預設 | 結構解析（標題/作者/摘要/章節） |
| `markitdown` | 新增 | 多格式支援、OCR、原生 Markdown |

### 目標

支援兩個核心功能：
1. **簡報生成** (`make_slides.py`)
2. **原子卡片生成** (Zettelkasten)

---

## 待實作項目

### 1. 安裝 MarkItDown

```bash
uv add "markitdown[pdf]"
```

### 2. 新增 MarkItDownExtractor

檔案：`src/extractors/markitdown_extractor.py`

```python
from markitdown import MarkItDown

class MarkItDownExtractor:
    def extract(self, file_path: str) -> dict:
        md = MarkItDown()
        result = md.convert(file_path)

        return {
            "markdown": result.text_content,
            "structure": self._parse_structure(result.text_content),
        }

    def _parse_structure(self, text: str) -> dict:
        # 複用 PDFExtractor 的結構解析邏輯
        pass
```

### 3. 更新 CLI 介面

```bash
# make_slides.py 新增 --backend 參數
uv run slides "主題" --pdf paper.pdf --backend markitdown

# 預設仍使用 pdfplumber
uv run slides "主題" --pdf paper.pdf
```

### 4. 更新 Skill 文檔

檔案：`.claude/skills/pdf-extractor.md`
- 新增 MarkItDown 後端說明
- 更新使用範例

---

## 排除的選項

| 工具 | 排除原因 |
|------|----------|
| Marker | 依賴大（~2GB）、GPL 授權 |
| MinerU | 依賴大（~5GB）、AGPL 授權 |
| Pix2Text | 專注公式，非通用 |

---

## 相關文件

- `src/extractors/pdf_extractor.py` - 現有實作
- `make_slides.py` - 簡報生成 CLI
- `generate_zettel_batch.py` - 批次卡片生成
- `.claude/skills/pdf-extractor.md` - Skill 文檔

---

## 參考資料

- [MarkItDown GitHub](https://github.com/microsoft/markitdown)
- [Marker GitHub](https://github.com/datalab-to/marker)
- [MinerU GitHub](https://github.com/opendatalab/MinerU)
