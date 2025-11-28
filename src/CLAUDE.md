# src/ - 源碼模組

## 模組結構

```
src/
├── extractors/      # PDF 提取
├── generators/      # 內容生成
├── knowledge_base/  # 知識庫管理
├── embeddings/      # 向量嵌入
├── integrations/    # 外部整合
├── analyzers/       # 分析器（暫停）
├── checkers/        # 品質檢查
└── utils/           # 工具函數
```

## 核心模組

### extractors/
- `pdf_extractor.py` - PDF 文本提取（pdfplumber/PyPDF2）

### generators/
- `slide_maker.py` - 多風格投影片生成
- `zettel_maker.py` - Zettelkasten 卡片解析與生成

### knowledge_base/
- `kb_manager.py` - 混合式知識庫（Markdown + SQLite）

### embeddings/
- `vector_db.py` - ChromaDB 向量資料庫
- `providers/` - Gemini/Ollama embedder

### integrations/
- `bibtex_parser.py` - BibTeX 解析
- `zotero_scanner.py` - Zotero 整合
- `ris_parser.py` - RIS 解析 ✅
- `doi_resolver.py` - DOI/CrossRef 查詢 ✅

### utils/
- `citekey_resolver.py` - Citekey 解析 ✅

## 暫停模組

### analyzers/
- `concept_mapper.py` - 概念網絡分析
- `relation_finder.py` - 關係識別器
- `obsidian_exporter.py` - Obsidian 格式導出

> 概念網絡分析功能已暫停，待後續開發
