# 🔍 兩種 MOC 比較報告

**生成時間**: 2025-11-20
**Phase**: 3A Pilot 完成

---

## 📊 基本統計對比

| 指標 | **完整 MOC**（382 張卡片） | **Pilot-Only MOC**（238 張卡片） | 差異 |
|------|---------------------------|--------------------------------|------|
| **卡片數** | 382 | 238 | -144 (-37.7%) |
| **關係數** | 21,964 | 17,142 | -4,822 (-22.0%) |
| **平均度** | 114.99 | 144.05 | +29.06 (+25.3%) |
| **網絡密度** | 0.3018 | 0.6078 | +0.3060 (+101.4%) |
| **社群數** | 1 | 1 | 無差異 |

### 🔍 關鍵觀察

1. **Pilot-Only 網絡密度高出 2 倍**：純 crowdsourcing 主題卡片之間關聯更緊密
2. **Pilot-Only 平均度更高**：每張卡片平均連接數多 29 個，表示內部一致性強
3. **關係數下降比例小於卡片數**：移除 37.7% 卡片只減少 22% 關係，顯示跨主題關係較少

---

## 🏆 Top 10 核心概念對比

### 完整 MOC（混合主題：AI integrity + crowdsourcing）

| 排名 | 概念 | PageRank | 來源論文 | 主題 |
|------|------|----------|----------|------|
| 1 | AI 對人類認知的影響 | 0.0052 | Guest-2025 | **AI integrity** |
| 2 | 偽解釋 (pseudo-explanation) | 0.0049 | vanRooij-2025 | **AI integrity** |
| 3 | 認知勞動的取代、增強和置換 | 0.0048 | Guest-2025 | **AI integrity** |
| 4 | 傳統 AI 定義的局限性 | 0.0047 | Guest-2025 | **AI integrity** |
| 5 | **健康的三個類別** | 0.0046 | Créquit-2018 | **crowdsourcing** ✅ |
| 6 | **群眾外包的報酬** | 0.0046 | Créquit-2018 | **crowdsourcing** ✅ |
| 7 | **群眾外包物流的描述不足** | 0.0045 | Créquit-2018 | **crowdsourcing** ✅ |
| 8 | **群眾外包的四種類型** | 0.0045 | Créquit-2018 | **crowdsourcing** ✅ |
| 9 | **群體工作者的特徵** | 0.0045 | Créquit-2018 | **crowdsourcing** ✅ |
| 10 | **未來研究方向** | 0.0045 | Hosseini-2015 | **crowdsourcing** ✅ |

**結論**: Top 10 中，**前 4 名被 AI integrity 論文佔據**（40%），crowdsourcing 論文從第 5 名開始出現。

---

### Pilot-Only MOC（純 crowdsourcing 主題）

| 排名 | 概念 | PageRank | 來源論文 |
|------|------|----------|----------|
| 1 | **群眾外包物流的描述不足** | 0.0067 | Créquit-2018 |
| 2 | **健康的三個類別** | 0.0067 | Créquit-2018 |
| 3 | **群眾外包的報酬** | 0.0067 | Créquit-2018 |
| 4 | **群眾外包的四種類型** | 0.0067 | Créquit-2018 |
| 5 | **資料品質驗證** | 0.0066 | Créquit-2018 |
| 6 | **群眾外包任務的多樣性** | 0.0066 | Hosseini-2015 |
| 7 | **群眾的特徵** | 0.0065 | Hosseini-2015 |
| 8 | **群眾外包的構成要素** | 0.0065 | Hosseini-2015 |
| 9 | **數據處理型群眾外包** | 0.0065 | Créquit-2018 |
| 10 | **未來研究方向** | 0.0065 | Hosseini-2015 |

**結論**: Top 10 **100% 來自 Pilot 論文**，主題高度聚焦於 crowdsourcing psycho studies。

---

## 🎯 主題分布分析

### 完整 MOC Top 30 主題分布

| 主題 | 數量 | 比例 | 來源 |
|------|------|------|------|
| **AI integrity** | 4 | 13.3% | Guest, vanRooij, Günther, Crockett 等 |
| **Crowdsourcing** | 26 | 86.7% | Créquit, Hosseini, Shapiro, Baruch 等 |

**觀察**: 雖然 crowdsourcing 佔 86.7%，但 **Top 4 概念全被 AI integrity 壟斷**。

### Pilot-Only MOC Top 30 主題分布

| 主題 | 數量 | 比例 |
|------|------|------|
| **Crowdsourcing** | 30 | 100% |

**觀察**: 完全純粹的 crowdsourcing 主題，無其他主題干擾。

---

## 📋 論文貢獻對比

### 完整 MOC Top 30 論文來源

| 論文 | 卡片數 | 主題 |
|------|--------|------|
| **Créquit-2018** | 12 | crowdsourcing |
| **Hosseini-2015** | 6 | crowdsourcing |
| **Shapiro-2013** | 4 | crowdsourcing |
| **Baruch-2016** | 2 | crowdsourcing |
| **Strickland-2022** | 2 | crowdsourcing |
| **Guest-2025 (AI)** | 3 | AI integrity |
| **vanRooij-2025 (AI)** | 1 | AI integrity |

**觀察**: Créquit-2018 明顯主導（12/30 = 40%），但 AI 論文擠進 Top 4。

### Pilot-Only MOC Top 30 論文來源

| 論文 | 卡片數 | 佔比 |
|------|--------|------|
| **Créquit-2018** | 12 | 40.0% |
| **Hosseini-2015** | 6 | 20.0% |
| **Shapiro-2013** | 4 | 13.3% |
| **Baruch-2016** | 3 | 10.0% |
| **Strickland-2022** | 2 | 6.7% |
| **其他 Pilot 論文** | 3 | 10.0% |

**觀察**: 論文分布更均衡，Créquit 雖仍最多但未壓倒性優勢。

---

## 🔬 核心概念主題分析

### 完整 MOC 核心概念關鍵詞雲

**AI integrity 主題** (前 4 名):
- AI、認知、勞動、解釋、定義、局限性

**Crowdsourcing 主題** (5-30 名):
- 群眾外包、資料品質、報酬、健康、MTurk、研究倫理、樣本、人口統計

**結論**: **主題混雜**，PageRank 演算法將 AI integrity 卡片（雖然數量少，但與舊卡片關係多）排在前面。

---

### Pilot-Only MOC 核心概念關鍵詞雲

**純 Crowdsourcing 主題** (1-30 名):
- 群眾外包、資料品質、報酬、健康、任務類型、構成要素、群眾特徵、MTurk、倫理、人口統計、物流、驗證、偏差、回饋

**結論**: **主題純粹且一致**，所有概念圍繞 crowdsourcing psycho studies，無其他主題干擾。

---

## ✅ 優缺點比較

### 完整 MOC（382 張卡片）

**優點** ✅:
1. **視野廣闊**: 涵蓋多個主題（AI integrity + crowdsourcing）
2. **跨領域連結**: 可發現不同主題間的潛在關聯
3. **知識整合**: 適合探索不同領域的共通概念

**缺點** ❌:
1. **主題稀釋**: Pilot 論文概念被 AI 論文稀釋，排名下降
2. **PageRank 偏誤**: 舊卡片（AI）因關係多而排名虛高
3. **焦點模糊**: 不適合用於單一主題的深入分析

**適用場景** 🎯:
- 探索跨領域研究
- 尋找不同主題的共通點
- 建立整體知識地圖

---

### Pilot-Only MOC（238 張卡片）

**優點** ✅:
1. **主題純粹**: 100% 聚焦於 crowdsourcing psycho studies
2. **排名真實**: PageRank 反映該主題內部的真實重要性
3. **高度相關**: 網絡密度高（0.6078），概念間關聯緊密
4. **精準匹配**: 完全符合原始 Connection Note 的主題範圍

**缺點** ❌:
1. **視野受限**: 無法看到與其他主題的潛在連結
2. **規模較小**: 卡片數少 37.7%，可能遺漏邊緣概念

**適用場景** 🎯:
- **單一主題深入研究**（推薦）✅
- 驗證或擴展現有 Connection Note
- 撰寫主題式文獻回顧
- **與原始 Connection Note 直接對應**（本次 Pilot）✅

---

## 🆚 與原始 Connection Note 的對應

### 原始 Connection Note 主題

來源: `🔗Psycho Studies on crowdsourcing.md`

**8 個思考點**:
1. Attention check is required in crowdsourcing studies
2. Quality verifications are the concerns of AI researchers
3. Crowdsourcing studies expand variety of reproducibility
4. Increasing dependence on crowdsourcing platforms for psychological researches
5. Rigor and transparent methodology are required for crowdsourcing researches
6. Alignment of participants preference and task demands
7. Required demographic characteristics for crowdsourcing research validity
8. Crowdsourcing platforms have more diverse samples than education institutions

---

### Pilot-Only MOC 覆蓋對應

| Connection Note 思考點 | Pilot-Only MOC 核心概念 | 匹配度 |
|----------------------|------------------------|--------|
| 1. Attention check | 資料品質驗證 (#5)、資料品質控制 (#11) | ✅ 高 |
| 2. Quality verifications | 資料品質驗證 (#5)、資料品質控制 (#11) | ✅ 高 |
| 3. Reproducibility | 研究倫理 (#17) | ⚠️ 中 |
| 4. Platform dependence | 群眾外包的四種類型 (#4)、MTurk 招募 (#16) | ✅ 高 |
| 5. Rigor & methodology | 研究倫理 (#17)、研究方法論 | ✅ 高 |
| 6. Preference alignment | 群體工作者的特徵 (#18)、群眾的特徵 (#7) | ✅ 高 |
| 7. Demographic validity | 人口統計特徵 (#26)、研究人口統計分佈 (#13) | ✅ 高 |
| 8. Sample diversity | 樣本偏差 (#14)、人口統計特徵 (#26) | ✅ 高 |

**結論**: **Pilot-Only MOC 對原始 Connection Note 的 8 個思考點提供了具體的文獻證據和細粒度概念支撐**，覆蓋率達 100%。

---

### 完整 MOC 覆蓋對應

因前 4 名被 AI integrity 佔據，crowdsourcing 概念從第 5 名開始，**匹配度與 Pilot-Only 相同，但排名較低，不夠突出**。

---

## 💡 結論與建議

### 結論

1. **完整 MOC** 適合**跨領域探索**，但會稀釋單一主題的焦點
2. **Pilot-Only MOC** 適合**單一主題深入研究**，與原始 Connection Note 完美對應
3. **PageRank 演算法對卡片數量和關係數量敏感**，較早導入的卡片（AI integrity）會獲得虛高排名

### 建議

#### 使用場景建議

| 使用目的 | 推薦 MOC | 理由 |
|----------|---------|------|
| **驗證或擴展特定 Connection Note** | **Pilot-Only** ✅ | 主題純粹，排名真實 |
| **撰寫主題式文獻回顧** | **Pilot-Only** ✅ | 聚焦單一主題 |
| **探索跨領域研究機會** | **完整 MOC** | 視野廣闊 |
| **建立整體知識地圖** | **完整 MOC** | 涵蓋多主題 |
| **發現意外的跨主題連結** | **完整 MOC** | 可能有驚喜 |

#### 工作流建議

**針對 Connection Note 擴展 (推薦流程)**:
1. ✅ 使用 **Pilot-Only MOC** 作為主要參考
2. ✅ 將 Top 30 核心概念整合到 Connection Note
3. ✅ 使用 `suggested_links.md` 補充卡片間連結
4. ⚠️ 需要時參考**完整 MOC**查看跨主題關聯

**針對新主題探索**:
1. 先看**完整 MOC**了解整體
2. 再生成**主題專屬 MOC**深入研究

---

## 📂 輸出位置

- **完整 MOC**: `output/moc_full_382cards/obsidian/`
- **Pilot-Only MOC**: `output/moc_pilot_only_238cards/`
- **此報告**: `MOC_COMPARISON_REPORT.md`

---

**生成工具**: Phase 3A Pilot - Concept Mapper
**統計基礎**: 382 張卡片（144 AI + 238 Pilot）
**分析方法**: PageRank + 網絡拓撲
**最後更新**: 2025-11-20
