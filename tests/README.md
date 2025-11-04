# 測試套件

本目錄包含所有測試，分為單元測試和整合測試。

## 結構

```
tests/
├── unit/              # 單元測試
│   └── test_*.py     # 各模組測試
├── integration/       # 整合測試
│   └── test_*.py
├── fixtures/          # 測試數據
│   ├── sample_papers/
│   ├── sample_zettel/
│   └── test_configs/
├── conftest.py        # pytest 配置
└── README.md          # 本檔案
```

## 執行測試

```bash
# 執行所有測試
pytest tests/ -v

# 只執行單元測試
pytest tests/unit/ -v

# 執行整合測試
pytest tests/integration/ -v

# 顯示測試覆蓋率
pytest tests/ --cov=src --cov-report=html
```

## 待實施

### Unit Tests (Phase 2.1)
- [ ] test_kb_manager.py - 知識庫管理器
- [ ] test_batch_processor.py - 批次處理器
- [ ] test_quality_checker.py - 質量檢查器
- [ ] test_embeddings.py - 向量嵌入

### Integration Tests (Phase 2.2)
- [ ] test_pdf_to_zettel.py - PDF → Zettelkasten 流程
- [ ] test_semantic_search.py - 語義搜索整合
- [ ] test_batch_workflow.py - 完整批次工作流

## 測試覆蓋目標

| 模組 | 覆蓋率目標 | 當前 | 優先級 |
|------|-----------|------|--------|
| kb_manager | 80% | 0% | P1 |
| batch_processor | 70% | 0% | P1 |
| quality_checker | 75% | 0% | P1 |
| embeddings | 80% | 0% | P1 |
| relation_finder | 70% | 0% | P2 |
| concept_mapper | 70% | 0% | P2 |

**整體目標**: 60%+ 測試覆蓋率 (Phase 2.1+)
