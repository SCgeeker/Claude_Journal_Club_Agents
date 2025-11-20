# 📚 程式碼範例目錄

本目錄包含知識生產器系統的所有程式碼範例，從 CLAUDE.md 中提取並整理。

---

## 📁 目錄結構

```
examples/
├── quickstart/              # 快速開始範例
├── pdf_extraction/          # PDF 提取範例
├── knowledge_base/          # 知識庫管理範例
├── batch_processing/        # 批次處理範例
├── quality_checker/         # 質量檢查範例
├── vector_search/           # 向量搜索範例
├── slide_maker/             # 投影片生成範例
├── configuration/           # 配置範例
└── README.md               # 本文件
```

---

## 🚀 快速開始 (quickstart/)

### 環境設置
- **setup_environment.sh**: 安裝依賴和初始化知識庫
  ```bash
  bash examples/quickstart/setup_environment.sh
  ```

### 基本使用
- **basic_usage.sh**: 分析論文的基本命令
  ```bash
  bash examples/quickstart/basic_usage.sh
  ```

### 知識庫查詢
- **kb_query.py**: Python API 查詢知識庫
  ```bash
  python examples/quickstart/kb_query.py
  ```

---

## 📄 PDF 提取 (pdf_extraction/)

### PDF 提取器
- **extract_pdf.py**: 從 PDF 提取文本和結構
  ```bash
  python examples/pdf_extraction/extract_pdf.py
  ```

**功能**:
- 提取標題、作者、摘要
- 自動識別章節結構
- 支援兩種提取方法（pdfplumber / PyPDF2）

---

## 💾 知識庫管理 (knowledge_base/)

### 知識庫管理
- **kb_management.py**: 完整的知識庫管理 API
  ```bash
  python examples/knowledge_base/kb_management.py
  ```

**功能**:
- 新增論文到知識庫
- 全文搜索論文
- 主題管理和分類
- 創建 Markdown 筆記

---

## 🔄 批次處理 (batch_processing/)

### CLI 批次處理
- **batch_cli_usage.sh**: 批次處理命令行範例
  ```bash
  bash examples/batch_processing/batch_cli_usage.sh
  ```

### Python API 批次處理
- **batch_api_usage.py**: 批次處理器 Python API
  ```bash
  python examples/batch_processing/batch_api_usage.py
  ```

**功能**:
- 批次處理資料夾中的所有 PDF
- 平行處理（ThreadPoolExecutor）
- 自動加入知識庫
- 生成 Zettelkasten 卡片
- 錯誤處理和重試機制

---

## ✅ 質量檢查 (quality_checker/)

### CLI 質量檢查
- **quality_check_cli.sh**: 質量檢查命令行範例
  ```bash
  bash examples/quality_checker/quality_check_cli.sh
  ```

### Python API 質量檢查
- **quality_check_api.py**: 質量檢查器 Python API
  ```bash
  python examples/quality_checker/quality_check_api.py
  ```

**功能**:
- 檢查論文元數據質量（標題、作者、年份、摘要、關鍵詞）
- 質量評分系統（0-100 分）
- 檢測重複論文
- 生成詳細報告

---

## 🔍 向量搜索 (vector_search/)

### 嵌入器使用
- **embedder_usage.py**: Gemini 和 Ollama 嵌入器範例
  ```bash
  python examples/vector_search/embedder_usage.py
  ```

### 向量數據庫
- **vector_db_usage.py**: ChromaDB 向量數據庫操作
  ```bash
  python examples/vector_search/vector_db_usage.py
  ```

### 語義搜索 CLI
- **semantic_search_cli.sh**: 語義搜索命令行範例
  ```bash
  bash examples/vector_search/semantic_search_cli.sh
  ```

**功能**:
- 生成向量嵌入（Gemini / Ollama）
- 語義搜索論文和 Zettelkasten 卡片
- 尋找相似內容
- 混合搜索（FTS + 向量搜索）

---

## 📊 投影片生成 (slide_maker/)

### 投影片生成器
- **slide_maker_usage.sh**: 投影片生成命令行範例
  ```bash
  bash examples/slide_maker/slide_maker_usage.sh
  ```

**功能**:
- 8 種學術風格（classic_academic, modern_academic, clinical, research_methods, literature_review, case_analysis, teaching, zettelkasten）
- 5 種詳細程度（minimal, brief, standard, detailed, comprehensive）
- 3 種語言模式（chinese, english, bilingual）
- 多 LLM 後端支持（Ollama, Gemini, OpenAI, Claude）
- 三種工作流模式（快速、知識驅動、重用）

---

## ⚙️ 配置 (configuration/)

### 配置範例
- **settings_example.yaml**: 主要配置項說明
  ```bash
  cat examples/configuration/settings_example.yaml
  ```

**配置項**:
- LLM 後端設定
- PDF 處理配置
- 簡報生成配置
- 知識庫配置
- 批次處理配置
- 向量搜索配置

---

## 📝 使用建議

### 新手入門順序
1. 閱讀 **quickstart/** 範例了解基本功能
2. 嘗試 **pdf_extraction/** 提取單篇論文
3. 使用 **knowledge_base/** 管理論文
4. 探索 **vector_search/** 進行語義搜索
5. 使用 **slide_maker/** 生成簡報

### 進階使用
1. 使用 **batch_processing/** 處理大量論文
2. 使用 **quality_checker/** 維護知識庫質量
3. 自定義 **configuration/** 優化系統行為

### 開發者
- 參考各範例了解 API 使用方式
- 修改範例代碼適應自己的需求
- 查閱 CLAUDE.md 獲取完整文檔

---

## 🔗 相關文檔

- **完整開發文檔**: [CLAUDE.md](../CLAUDE.md)
- **專案結構**: [docs/PROJECT_STRUCTURE.md](../docs/PROJECT_STRUCTURE.md)
- **快速開始指南**: [docs/QUICKSTART.md](../docs/QUICKSTART.md)

---

**最後更新**: 2025-11-06
**版本**: v0.6.0-alpha
