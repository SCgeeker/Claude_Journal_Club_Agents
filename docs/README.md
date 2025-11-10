# 📚 文檔目錄

本目錄包含專案的完整文檔和指南。

---

## 📖 文檔列表

### 快速開始

- **[QUICKSTART.md](QUICKSTART.md)** - 快速開始指南
  - 安裝步驟
  - 基本使用
  - 常見範例

### 專案結構

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - 專案架構說明
  - 目錄結構
  - 模組功能
  - 依賴關係

### 程式碼範例

- **[examples/README.md](../examples/README.md)** - 程式碼範例目錄
  - 快速開始範例
  - PDF 提取範例
  - 知識庫管理範例
  - 批次處理範例
  - 質量檢查範例
  - 向量搜索範例
  - 投影片生成範例

### 模板系統

- **[templates/README.md](../templates/README.md)** - 模板庫總覽
  - [templates/prompts/README.md](../templates/prompts/README.md) - Prompt 模板
  - [templates/styles/README.md](../templates/styles/README.md) - 學術風格定義
  - [templates/markdown/README.md](../templates/markdown/README.md) - Markdown 模板

### 向量搜索與概念網絡

- **[VECTOR_SEARCH_TEST_REPORT.md](VECTOR_SEARCH_TEST_REPORT.md)** - 向量搜索測試報告 (Phase 1.5)
  - 系統架構說明
  - 測試結果分析
  - 效能與成本評估

- **[ZETTELKASTEN_SIMILARITY_CALCULATION.md](ZETTELKASTEN_SIMILARITY_CALCULATION.md)** - 相似度計算說明
  - 向量嵌入原理
  - 相似度計算方法

- **[OBSIDIAN_INTEGRATION_GUIDE.md](OBSIDIAN_INTEGRATION_GUIDE.md)** - Obsidian 整合指南 (Phase 2.2)
  - 概念網絡分析
  - Wiki Links 使用
  - Graph View 設定

- **[OBSIDIAN_INTEGRATION_TEST_REPORT.md](OBSIDIAN_INTEGRATION_TEST_REPORT.md)** - Obsidian 整合測試報告
  - 功能驗證結果
  - 使用場景測試

- **[BASELINE_RELATION_ANALYSIS.md](BASELINE_RELATION_ANALYSIS.md)** - 關係識別基準分析 (Phase 2.3)
  - 當前系統狀態
  - 問題診斷

- **[RELATION_FINDER_IMPROVEMENTS.md](RELATION_FINDER_IMPROVEMENTS.md)** - RelationFinder 改進方案
  - 改進設計
  - 實施計畫

- **[RELATION_FINDER_TECHNICAL_DETAILS.md](RELATION_FINDER_TECHNICAL_DETAILS.md)** - 技術細節文檔
  - 演算法說明
  - 實作細節

### GitHub發布相關

- **[BRANCH_WORKFLOW.md](BRANCH_WORKFLOW.md)** - 雙分支工作流指南
  - 分支策略
  - 日常開發流程
  - 安全最佳實踐

- **[PUBLISH_CHECKLIST.md](PUBLISH_CHECKLIST.md)** - 發布前檢查清單
  - 安全檢查項目
  - 執行步驟
  - 驗證方法

- **[DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md)** - 發布成功報告
  - 發布記錄
  - 分支狀態
  - 統計資料

- **[PRIVACY_CONFIRMED.md](PRIVACY_CONFIRMED.md)** - 隱私保護確認
  - 安全措施
  - 驗證結果
  - 開發指南

---

## 🗂️ 文檔層級

```
根目錄/
├── README.md                    # 專案概述（公開版）
├── CLAUDE.md                    # 完整開發文檔（含設計理念）
└── docs/                        # 詳細文檔目錄
    ├── README.md                # 本文件
    ├── QUICKSTART.md            # 快速開始
    ├── PROJECT_STRUCTURE.md     # 專案架構
    ├── BRANCH_WORKFLOW.md       # 分支工作流
    ├── PUBLISH_CHECKLIST.md     # 發布檢查清單
    ├── DEPLOYMENT_SUCCESS.md    # 發布報告
    └── PRIVACY_CONFIRMED.md     # 隱私確認
```

---

## 🎯 閱讀順序建議

### 新用戶
1. [README.md](../README.md) - 了解專案
2. [QUICKSTART.md](QUICKSTART.md) - 快速上手
3. [examples/README.md](../examples/README.md) - 實用範例
4. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 理解架構

### 開發者
1. [CLAUDE.md](../CLAUDE.md) - 完整開發文檔
2. [examples/README.md](../examples/README.md) - 程式碼範例
3. [templates/README.md](../templates/README.md) - 模板系統
4. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 技術架構
5. [BRANCH_WORKFLOW.md](BRANCH_WORKFLOW.md) - 工作流程

### 進階功能使用者

**向量搜索與語義檢索**:
1. [VECTOR_SEARCH_TEST_REPORT.md](VECTOR_SEARCH_TEST_REPORT.md) - 了解系統架構
2. [examples/vector_search/](../examples/vector_search/) - 實作範例
3. [ZETTELKASTEN_SIMILARITY_CALCULATION.md](ZETTELKASTEN_SIMILARITY_CALCULATION.md) - 理解相似度計算

**概念網絡與 Obsidian**:
1. [OBSIDIAN_INTEGRATION_GUIDE.md](OBSIDIAN_INTEGRATION_GUIDE.md) - 完整使用指南
2. [OBSIDIAN_INTEGRATION_TEST_REPORT.md](OBSIDIAN_INTEGRATION_TEST_REPORT.md) - 測試結果
3. [BASELINE_RELATION_ANALYSIS.md](BASELINE_RELATION_ANALYSIS.md) - 關係識別現狀
4. [RELATION_FINDER_IMPROVEMENTS.md](RELATION_FINDER_IMPROVEMENTS.md) - 改進計畫

**批次處理與質量控制**:
1. [examples/batch_processing/](../examples/batch_processing/) - 批次處理範例
2. [examples/quality_checker/](../examples/quality_checker/) - 質量檢查範例

### 發布管理
1. [PUBLISH_CHECKLIST.md](PUBLISH_CHECKLIST.md) - 發布前檢查
2. [BRANCH_WORKFLOW.md](BRANCH_WORKFLOW.md) - 分支管理
3. [PRIVACY_CONFIRMED.md](PRIVACY_CONFIRMED.md) - 隱私驗證

---

**最後更新**: 2025-11-06
**版本**: v0.6.0-alpha

## ✅ 最近更新 (2025-11-06)
- ✅ 完成程式碼範例外部化（移至 [examples/](../examples/) 目錄）
- ✅ 完成模板說明移動（移至各 templates/ 子目錄的 README.md）
- ✅ CLAUDE.md 程式碼改為外部連結
- ⏳ RELATION_FINDER_IMPROVEMENTS.md 用戶編輯中（部分文字和變數名稱）
