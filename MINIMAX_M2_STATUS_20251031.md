# MiniMax-M2 狀態報告

**測試日期**: 2025-10-31
**測試環境**: Windows 11, Ollama v0.12.7

---

## 📊 測試結果總覽

| 測試項目 | 結果 | 說明 |
|---------|------|------|
| **簡單調用** | ✅ 成功 | `echo "Hello" \| ollama run minimax-m2:cloud` |
| **短Prompt** | ✅ 成功 | 19字元 |
| **中Prompt** | ✅ 成功 | 237字元 |
| **長Prompt** | ✅ 成功 | 5,128字元 |
| **Zettelkasten生成** | ❌ 失敗 | 複雜JSON格式 |

---

## 🔍 問題診斷

### 1. MiniMax-M2 只支援CLI調用
- ✅ **可行**: `ollama run minimax-m2:cloud` (命令行)
- ❌ **不可行**: API調用 (`/api/generate`)
- **原因**: 根據OLLAMA_USAGE_EVALUATION.md，MiniMax-M2僅支援本地CLI

### 2. 成功的修復
已在`slide_maker.py`中實現CLI調用支援：
```python
# 特殊處理 MiniMax-M2:cloud - 使用CLI方式
if model.lower() == "minimax-m2:cloud":
    # 使用臨時文件和subprocess調用
    cmd = f'type "{temp_file}" | ollama run {model}'
```

### 3. 仍存在的問題
**Zettelkasten生成失敗原因**：
- 複雜的JSON格式輸出要求
- 特殊字符和轉義問題
- Prompt模板可能包含MiniMax無法處理的格式

### 4. 錯誤模式
```
Error: 500 Internal Server Error:
unmarshal: invalid character 'I' looking for beginning of value
```
此錯誤出現在：
- 使用複雜JSON格式的prompt時
- 包含大量特殊字符的prompt時

---

## 💡 解決方案

### 方案A：簡化Prompt格式（短期）
為MiniMax-M2創建專用的簡化版prompt模板：
- 移除複雜的JSON格式要求
- 使用純文本格式
- 減少特殊字符使用

### 方案B：使用其他模型（立即可行）
已測試可用的替代方案：
1. **Google Gemini** - ⭐ 推薦
   - 免費額度充足
   - 品質優秀
   - 穩定可靠

2. **Claude 3 Haiku** - 備選
   - 成本低廉（$0.02/篇）
   - 品質穩定
   - API可靠

3. **GPT-OSS:20b-cloud** - 可考慮
   - Ollama雲端模型
   - API調用正常
   - 品質可接受

### 方案C：等待修復（長期）
- 等待Ollama或MiniMax官方修復
- 關注免費期（至2025/11/7）後的替代方案

---

## 🎯 建議行動

### 立即行動
1. **主要使用Google Gemini**
   ```bash
   python make_slides.py "主題" --pdf paper.pdf \
     --llm-provider google --model gemini-2.0-flash-exp
   ```

2. **備用Claude Haiku**
   ```bash
   python make_slides.py "主題" --pdf paper.pdf \
     --llm-provider anthropic --model claude-3-haiku-20240307
   ```

### 後續優化
1. 為MiniMax-M2創建簡化版prompt模板
2. 實施自動故障轉移機制
3. 監控MiniMax服務狀態

---

## 📈 效能對比

| 模型 | 可用性 | 品質 | 成本 | 速度 | 建議優先級 |
|------|--------|------|------|------|-----------|
| **Google Gemini** | ✅ | ⭐⭐⭐⭐⭐ | 免費 | 快 | 1 |
| **Claude Haiku** | ✅ | ⭐⭐⭐⭐ | $0.02 | 快 | 2 |
| **MiniMax-M2** | ⚠️ | ⭐⭐⭐⭐⭐ | 免費(限時) | 慢 | 3 |
| **GPT-OSS:20b** | ✅ | ⭐⭐⭐ | 免費 | 快 | 4 |

---

## 📋 技術細節

### 成功的CLI調用流程
1. 將prompt寫入臨時文件（UTF-8編碼）
2. 使用`type`命令管道傳輸到ollama
3. 處理thinking輸出和ANSI控制字符
4. 提取實際回應內容

### 已實現的代碼改進
- ✅ CLI調用支援
- ✅ ANSI控制字符清理
- ✅ Thinking部分提取
- ✅ 編碼錯誤處理

### 未解決的技術問題
- JSON格式prompt導致錯誤
- 某些特殊字符引起解析失敗
- 長時間thinking可能超時

---

## 💬 結論

**MiniMax-M2目前不適合生產環境使用**

雖然我們成功實現了CLI調用支援，但MiniMax-M2在處理複雜prompt時仍然不穩定。建議：

1. **短期策略**：使用Google Gemini作為主要LLM
2. **中期策略**：評估Claude API的成本效益
3. **長期策略**：等待MiniMax-M2修復或尋找其他免費方案

---

**報告撰寫**: Claude Code
**狀態**: ⚠️ 部分可用，建議使用替代方案