# Citekey 設計規格

**版本**: 1.0
**日期**: 2025-11-27
**狀態**: 設計確認

---

## 設計理念

> **「尊重使用者習慣，系統做好適配」**

使用者繼續用慣用的書目管理平台和 citekey 格式，系統負責解析、正規化和索引。

---

## 識別符架構

### 三層 Citekey 系統

| 層級 | 欄位名稱 | 說明 | 範例 |
|------|---------|------|------|
| **L1** | `original_citekey` | 原始 citekey（保持與書目平台一致） | `barsalou1999perceptual` |
| **L2** | `cite_key` | 正規化版本（用於檔案系統） | `Barsalou-1999` |
| **L3** | `doi` | DOI 備案索引 | `10.1017/S0140525X99002149` |

### 查詢優先順序

```
使用者查詢
    │
    ▼
┌─────────────────────┐
│ 1. cite_key 精確匹配 │ ──► 找到 ──► 返回結果
└─────────────────────┘
    │ 未找到
    ▼
┌─────────────────────────┐
│ 2. original_citekey 匹配 │ ──► 找到 ──► 返回結果
└─────────────────────────┘
    │ 未找到
    ▼
┌─────────────────────┐
│ 3. DOI 精確匹配      │ ──► 找到 ──► 返回結果
└─────────────────────┘
    │ 未找到
    ▼
┌─────────────────────────┐
│ 4. 標題模糊匹配 (>0.8)  │ ──► 找到 ──► 返回結果（含警告）
└─────────────────────────┘
    │ 未找到
    ▼
   錯誤：找不到論文
```

---

## Citekey 來源優先順序

解析新論文時的來源優先順序：

| 優先級 | 來源 | 說明 | CLI 參數 |
|--------|------|------|---------|
| 1 | 手動指定 | 使用者明確指定，最高優先 | `--citekey` |
| 2 | BibTeX | 從 .bib 檔案解析 entry key | `--bib` |
| 3 | RIS | 從 .ris 檔案解析 ID 欄位 | `--ris` |
| 4 | DOI 查詢 | 從 PDF 提取 DOI，查詢 CrossRef | 自動 |
| 5 | PDF 元數據 | 從 PDF 內嵌元數據推斷 | 自動 |
| 6 | 檔名推斷 | 從檔名模式推斷 | 自動 |
| 7 | 自動生成 | 依配置模板生成 | 自動 |

---

## 支援的書目格式

| 格式 | 副檔名 | 解析器 | Citekey 欄位 | DOI 欄位 |
|------|--------|--------|-------------|----------|
| **BibTeX** | `.bib` | bibtexparser | entry key | `doi` |
| **RIS** | `.ris` | rispy | `ID` | `DO` |
| **CSL JSON** | `.json` | json | `id` | `DOI` |

### RIS 欄位對應

```
TY  - 文獻類型 (JOUR, BOOK, CONF...)
AU  - 作者
TI  - 標題
PY  - 年份
DO  - DOI
ID  - 識別符（citekey）
ER  - 結束標記
```

---

## 配置選項

### config/settings.yaml

```yaml
citekey:
  # ===== 格式模板 =====
  # 自動生成 citekey 時使用的格式
  # 可用變數：
  #   {first_author}  - 第一作者姓氏
  #   {year}          - 出版年份
  #   {title_word}    - 標題第一個實詞
  #   {authors_short} - 作者縮寫（如 BZ = Barsalou & Zwaan）

  auto_format: "{first_author}-{year}"

  # 預設格式選項（供說明文件參考）
  format_examples:
    - pattern: "{first_author}-{year}"
      example: "Barsalou-1999"
      description: "推薦格式，簡潔易讀"
    - pattern: "{first_author}{year}"
      example: "Barsalou1999"
      description: "無分隔符，較緊湊"
    - pattern: "{first_author}_{year}"
      example: "Barsalou_1999"
      description: "底線分隔，程式友好"
    - pattern: "{first_author}{year}{title_word}"
      example: "barsalou1999perceptual"
      description: "Better BibTeX 預設格式"

  # ===== 正規化規則 =====
  normalize:
    # 是否強制小寫（false = 保持原始大小寫）
    lowercase: false

    # 分隔符號（用於自動生成）
    separator: "-"

    # 最大長度（超過則截斷）
    max_length: 50

    # 移除的特殊字元
    remove_chars: "[]{}()#$%^&*+=|\\<>?/"

  # ===== DOI 備案設定 =====
  doi:
    # 啟用 DOI 作為備案索引
    enabled: true

    # 從 DOI 查詢元數據（CrossRef API）
    crossref_lookup: true

    # 從 PDF 自動提取 DOI
    extract_from_pdf: true

  # ===== 書目檔自動偵測 =====
  auto_detect:
    enabled: true
    # 搜尋順序
    patterns:
      - "{pdf_stem}.bib"      # paper.pdf → paper.bib
      - "{pdf_stem}.ris"      # paper.pdf → paper.ris
      - "library.bib"         # 同目錄 library.bib
      - "references.bib"      # 同目錄 references.bib
      - "../*.bib"            # 上層目錄的 .bib
```

---

## 資料庫 Schema

### papers 表擴展

```sql
-- 新增欄位
ALTER TABLE papers ADD COLUMN original_citekey TEXT;
ALTER TABLE papers ADD COLUMN citekey_source TEXT;
ALTER TABLE papers ADD COLUMN doi TEXT UNIQUE;

-- 索引
CREATE INDEX idx_papers_original_citekey ON papers(original_citekey);
CREATE INDEX idx_papers_doi ON papers(doi);

-- citekey_source 可能值
-- 'manual'   - 使用者手動指定
-- 'bibtex'   - 從 BibTeX 解析
-- 'ris'      - 從 RIS 解析
-- 'doi'      - 從 DOI 查詢
-- 'pdf'      - 從 PDF 元數據
-- 'filename' - 從檔名推斷
-- 'auto'     - 自動生成
```

---

## CLI 使用範例

### 基本使用

```bash
# 自動偵測（尋找同目錄 .bib/.ris）
uv run analyze paper.pdf --add-to-kb

# 指定書目檔
uv run analyze paper.pdf --bib library.bib --add-to-kb
uv run analyze paper.pdf --ris references.ris --add-to-kb

# 手動指定 citekey（覆蓋所有來源）
uv run analyze paper.pdf --citekey "Barsalou-1999" --add-to-kb

# 指定 DOI（用於查詢元數據）
uv run analyze paper.pdf --doi "10.1017/S0140525X99002149" --add-to-kb
```

### 批次處理

```bash
# 從書目檔批次處理
uv run analyze --from-bib library.bib --pdf-dir ./pdfs/

# 處理整個資料夾（自動配對 PDF 與書目條目）
uv run analyze --batch ./papers/ --add-to-kb
```

### 查詢與管理

```bash
# 用 citekey 查詢
uv run kb get Barsalou-1999

# 用 DOI 查詢（備案）
uv run kb get --doi "10.1017/S0140525X99002149"

# 列出 citekey 來源統計
uv run kb stats --citekey-sources
```

---

## 初級使用者設定建議

### 推薦配置：Zotero + Better BibTeX

1. **安裝 Better BibTeX 插件**
   - https://retorque.re/zotero-better-bibtex/

2. **設定 Citekey 格式**
   - 設定 → Better BibTeX → Citation key format
   - 推薦格式：`[auth]-[year]`
   - 產生結果：`Barsalou-1999`

3. **匯出書目檔**
   - 右鍵 → Export Collection → Better BibTeX
   - 勾選 "Keep updated"（自動同步）

4. **使用 claude-lit-workflow**
   ```bash
   # 將 .bib 放在 PDF 同目錄，自動偵測
   uv run analyze paper.pdf --add-to-kb
   ```

### 其他書目管理平台

| 平台 | 匯出格式 | Citekey 處理 |
|------|----------|-------------|
| **Mendeley** | BibTeX | 使用預設 citekey |
| **EndNote** | RIS | 建議手動指定 `--citekey` |
| **Papers** | BibTeX | 使用預設 citekey |
| **無平台** | - | 自動生成，或手動指定 |

---

## 實作模組

### 需要建立/修改的檔案

| 檔案 | 狀態 | 說明 |
|------|------|------|
| `src/utils/citekey_resolver.py` | 新建 | 核心解析邏輯 |
| `src/integrations/ris_parser.py` | 新建 | RIS 格式解析 |
| `src/integrations/doi_resolver.py` | 新建 | DOI → CrossRef 查詢 |
| `src/integrations/bibtex_parser.py` | 修改 | 整合 citekey_resolver |
| `src/knowledge_base/kb_manager.py` | 修改 | 支援多重索引查詢 |
| `migrations/add_citekey_columns.py` | 新建 | DB schema 更新 |
| `config/settings.yaml` | 修改 | 新增 citekey 區塊 |

### CitykeyResolver 類別設計

```python
class CitykeyResolver:
    """Citekey 解析與正規化"""

    def resolve(
        self,
        pdf_path: Path,
        bib_path: Path = None,
        ris_path: Path = None,
        manual_citekey: str = None,
        doi: str = None
    ) -> dict:
        """
        依優先順序解析 citekey

        Returns:
            {
                'cite_key': 正規化 citekey,
                'original_citekey': 原始值,
                'doi': DOI（如有）,
                'source': 來源標記
            }
        """

    def normalize(self, citekey: str) -> str:
        """正規化 citekey（用於檔案系統）"""

    def generate(self, authors: list, year: int, title: str = None) -> str:
        """自動生成 citekey"""

    def match_pdf_to_bib(
        self,
        pdf_path: Path,
        bib_entries: list
    ) -> dict | None:
        """將 PDF 與書目條目配對（模糊匹配）"""
```

---

## 向後相容性

- 現有 `cite_key` 欄位保留，作為正規化版本
- 新增欄位允許 NULL，不影響現有資料
- 現有工作流程不受影響
- 升級時自動將現有 cite_key 複製到 original_citekey

---

## 相關文件

- [EXPORT_FORMAT_SPEC.md](EXPORT_FORMAT_SPEC.md) - 輸出格式規範
- [IMPORT_TOOL_SPEC.md](IMPORT_TOOL_SPEC.md) - ProgramVerse 匯入工具
- [CLI_GUIDE.md](CLI_GUIDE.md) - CLI 操作指引（待建立）

---

*本規格由 Claude Code 協助設計，2025-11-27*
