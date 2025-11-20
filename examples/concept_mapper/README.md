# Concept Mapper Examples

概念網絡分析範例和工具。

## 範例腳本

### run_concept_analysis.py

**用途**: 直接執行概念網絡分析的獨立腳本

**使用場景**:
- 繞過 kb_manage.py CLI 的 stdout 問題
- 調試 ConceptMapper 功能
- 快速測試分析參數

**使用方式**:
```bash
python examples/concept_mapper/run_concept_analysis.py
```

**輸出位置**: `output/concept_analysis_fixed/`

**配置選項** (腳本內修改):
- `output_dir`: 輸出目錄
- `suggested_links_min_confidence`: 最小信度閾值（默認 0.4）
- `suggested_links_top_n`: 建議連結數量（默認 50）
- `moc_top_n`: MOC 顯示概念數（默認 20）
- `max_communities`: 最多社群數（默認 10）
- `path_top_n`: 路徑分析數量（默認 10）

## 推薦使用方式

**正常使用** (推薦):
```bash
# 使用 kb_manage.py CLI
python kb_manage.py visualize-network --obsidian
```

**調試/測試**:
```bash
# 使用獨立腳本
python examples/concept_mapper/run_concept_analysis.py
```

## 相關文檔

- **完整使用指南**: `docs/OBSIDIAN_INTEGRATION_GUIDE.md` (已歸檔)
- **Concept Mapper 文檔**: `src/analyzers/concept_mapper.py` 頂部注釋
- **CLAUDE.md**: Phase 2.2 Concept Mapper 章節
