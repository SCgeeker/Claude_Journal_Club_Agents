# 圖表來源提取指引

本檔案指導 LLM 如何從學術論文中提取圖表的重製資訊。

---

## Figure 處理

當遇到論文中的 Figure 時，請執行以下步驟：

### 1. 基本資訊提取
- 編號（Figure 1, Figure 2, ...）
- 標題（Figure caption）
- 所在頁碼或章節

### 2. 來源資訊檢查

請在論文中搜尋以下關鍵位置：

**Data Availability Statement（資料可用性聲明）**
- 通常在論文末尾、參考文獻之前
- 關鍵詞：「Data availability」「Data and materials」「Code availability」

**Supplementary Materials（補充材料）**
- 關鍵詞：「Supplementary」「Supporting Information」「SI Appendix」
- 記錄連結 URL

**程式碼倉庫**
- GitHub: `github.com/...`
- OSF: `osf.io/...`
- Zenodo: `zenodo.org/...`
- Figshare: `figshare.com/...`

**資料庫來源**
- 若數據來自公開資料庫，記錄：
  - 資料庫名稱（如 NHANES, UK Biobank, ImageNet）
  - 存取方式或 DOI

### 3. 重製程式碼識別

若論文提供重製程式碼，請記錄：

```
語言：R / Python / MATLAB / Julia / 其他
主要套件：
  - 統計分析：ggplot2, matplotlib, seaborn
  - 機器學習：scikit-learn, tensorflow, pytorch
  - 資料處理：pandas, tidyverse, numpy
執行環境：如有 Docker/conda 環境檔
```

---

## Table 處理

### 1. 表格結構保留
- 完整保留欄位名稱和數據
- 保留表格註腳（通常包含重要說明）

### 2. 資料來源追蹤
- 檢查表格註腳中的資料來源說明
- 若為彙整多篇研究，記錄各來源文獻

### 3. 統計資訊
- 記錄使用的統計方法
- 記錄顯著性標準（如 *p<0.05, **p<0.01）

---

## 輸出格式

對每個圖表，請生成以下結構化資訊：

```markdown
### [Figure/Table X]: [標題]

**來源類型**：原創分析 / 重製他人 / 外部資料庫

**資料來源**：
- URL: [連結]
- DOI: [若有]
- 資料庫: [名稱]

**重製需求**：
- 語言: [R/Python/...]
- 套件: [列表]
- 資料檔: [檔名或連結]

**備註**：[其他重要資訊]
```

---

## 注意事項

1. **若無法找到來源資訊**，請標記為「來源未標註」
2. **付費/限制存取資料**，請標記存取限制
3. **隱私敏感資料**（如臨床數據），通常不會公開原始資料，請標記「受限存取」
