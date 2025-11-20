# Phase 2.3 測試報告 - 2025-11-09

## 📊 測試概要

**測試日期**: 2025-11-09
**測試目標**: 驗證 Phase 2.3 改進 - AI notes 連結生成
**測試論文**: Jones-2024 (Multimodal Language Models Show Evidence of Embodied Simulation)
**使用模型**: Google Gemini 2.0 Flash Exp (直接 API)

---

## ✅ 測試執行結果

### 1. API 連接測試

| 測試項目 | 狀態 | 詳情 |
|---------|------|------|
| **Google Gemini 直接 API** | ✅ 成功 | 回應正常，速度快 |
| **OpenRouter** | ❌ 仍受限 | 429 Too Many Requests |

**結論**: Google Gemini 可用，OpenRouter 需等待 24 小時重置。

### 2. Zettelkasten 生成測試

- **生成數量**: 20 張卡片 ✅
- **生成時間**: ~2 分鐘
- **LLM 回應長度**: 28,165 字符
- **輸出目錄**: `output/zettelkasten_notes/zettel_Jones-2024_20251109_gemini/`

### 3. 連結生成分析 ❌

#### 關鍵發現

**問題 1: 連結網絡區塊完全為空**

檢查 20 張卡片，所有卡片的「連結網絡」區塊都是空的：

```markdown
## 連結網絡





```

**搜索結果**:
```bash
grep -r "\[\[Jones-2024-" zettel_cards/
# 無結果 - 沒有任何卡片間連結
```

**問題 2: AI notes 格式錯誤**

預期格式：
```markdown
個人筆記:

🤖 **AI**: [批判性思考，包含至少1個 [[Jones-2024-XXX]] 連結]

✍️ **Human**:
```

實際格式：
```markdown
個人筆記:


**[AI Agent]**: ✍️ **Human**:


**[Human]**: (TODO) <!-- 請在此處添加您的個人思考、批判性評論或延伸想法 -->
```

**分析**: 格式完全錯亂，沒有 AI 批判性思考內容，也沒有連結。

---

## 🔍 根本原因分析

### 可能原因 1: Prompt 遵循度不足

檢查 `templates/prompts/zettelkasten_template.jinja2`：

✅ Prompt 中**確實有明確要求**（第 48, 77, 114-117 行）：

```jinja2
個人筆記:

🤖 **AI**: [AI生成的批判性思考，至少包含1個 [[{{ cite_key }}-相關ID]] 連結]

✍️ **Human**:
```

以及第 114-117 行的明確指令：
> **必須包含至少1個其他卡片的連結**

**結論**: Prompt 設計正確，但 LLM 沒有遵循。

### 可能原因 2: LLM 輸出解析問題

需要檢查：
1. LLM 是否真的生成了連結（但被解析器丟棄）
2. `zettel_maker.py` 的解析邏輯是否有 bug

### 可能原因 3: Few-shot 範例不足

當前 Prompt 只有 2 個 few-shot 範例（第 26-83 行）。

建議：
- 增加到 3-5 個範例
- 每個範例都明確展示「連結網絡」和「AI notes 連結」

### 可能原因 4: Prompt 長度過長

當前 Prompt 長度: ~3,253 字符

LLM 可能忽略了中間的細節指令。

---

## 📈 與基準對比

| 指標 | 基準（舊卡片） | 本次測試 | 目標 | 達成率 |
|------|--------------|---------|------|--------|
| **明確連結覆蓋率** | 11.6% (82/704) | **0%** (0/20) | 50%+ | ❌ 0% |
| **平均連結數/卡片** | ~0.1 | **0** | 2-3 | ❌ 0% |
| **AI notes 連結數** | 0 | **0** | 20+ | ❌ 0% |
| **格式正確率** | N/A | **0%** | 90%+ | ❌ 0% |

**結論**: **Phase 2.3 測試失敗** - 沒有達成任何目標。

---

## 🎯 待解決問題清單

### 優先級 P0（緊急）

1. **診斷 LLM 原始輸出**
   - [ ] 檢查 LLM 生成的原始文本（未經解析前）
   - [ ] 確認問題在於 LLM 生成還是解析器

2. **修復 zettel_maker.py 解析邏輯**
   - [ ] 檢查 `generate_zettelkasten()` 方法
   - [ ] 檢查 Markdown 解析邏輯
   - [ ] 確保「連結網絡」和「個人筆記」區塊正確保存

3. **改進 Prompt**
   - [ ] 在開頭就明確要求（不只在範例中）
   - [ ] 增加 few-shot 範例到 3-5 個
   - [ ] 使用**粗體**和 `MUST` 強調必須包含連結
   - [ ] 簡化 Prompt，移除冗餘指令

### 優先級 P1（重要）

4. **測試不同模型**
   - [ ] 24 小時後重試 OpenRouter（DeepSeek R1, Claude, Llama）
   - [ ] 對比不同模型的連結生成能力

5. **實作 Phase 2.3 完整改進**
   - [ ] RelationFinder 多層次連結檢測
   - [ ] 擴展共同概念提取（加入 description）
   - [ ] 領域相關性矩陣

---

## 📋 明日待辦事項

見 `TODO_20251110.md`

---

## 📚 相關文檔

- **原始計劃**: `RESUME_AFTER_RATE_LIMIT.md`
- **Prompt Template**: `templates/prompts/zettelkasten_template.jinja2`
- **生成結果**: `output/zettelkasten_notes/zettel_Jones-2024_20251109_gemini/`
- **Phase 2.3 設計**: `docs/RELATION_FINDER_IMPROVEMENTS.md`

---

## 🔄 下次測試建議

1. **先修復解析器**，再重新測試
2. **使用相同論文**（Jones-2024）以便對比
3. **保存 LLM 原始輸出**到文件，方便診斷
4. **測試多個模型**，驗證是否為模型特定問題

---

**測試結論**: ❌ **未達成目標，需要診斷和修復**
