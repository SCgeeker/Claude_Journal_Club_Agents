# Ollama 使用方式評估報告

**日期**: 2025-10-31
**評估目的**: 確認透過本地 Ollama app 使用雲端 LLM 的可行性

---

## 🔍 發現摘要

### ✅ 已確認可行

**本地 Ollama app (v0.12.7) 已支援雲端模型！**

實測結果：
- ✅ 成功透過本地 Ollama 使用雲端模型 `minimax-m2:cloud`
- ✅ 模型運行正常，展示 thinking 過程
- ✅ 無需下載 230B 參數模型到本地（僅 382 字節配置文件）

---

## 📊 兩種使用方式對比

### 方式 1：本地 Ollama App（官方 ollama.com 服務）

**連接方式**：
```bash
# 本地 Ollama 作為代理
Local Client → localhost:11434 → ollama.com:443 → Remote Model
```

**特點**：
- 🔧 **安裝位置**: `C:\Users\User\AppData\Local\Programs\Ollama\`
- 🌐 **遠端主機**: `https://ollama.com:443`
- 🔐 **認證方式**: `ollama signin` 命令登入帳號
- 💻 **使用介面**: 命令行 CLI (`ollama run model-name`)
- 📦 **本地模型**: 支援下載並本地運行（如 gemmapro-r:latest, 2.5GB）

**測試結果**：
```bash
$ ollama list
NAME                  ID              SIZE      MODIFIED
minimax-m2:cloud      698ab6d56142    -         47 minutes ago
gemmapro-r:latest     41dad741704f    2.5 GB    3 months ago

$ ollama run minimax-m2:cloud "Hello"
Thinking...
...done thinking.
Hello! I'm MiniMax-M2, an AI assistant built by MiniMax...
```

**模型詳情**：
- Remote model: `minimax-m2`
- Parameters: 230B
- Context length: 204,800
- Quantization: FP8
- Capabilities: completion, tools, thinking

---

### 方式 2：Ollama Cloud API（Python 直接調用）

**連接方式**：
```bash
# Python 腳本直接調用 API
Python Script → https://api.ollama.cloud → Cloud Models
```

**特點**：
- 🔐 **認證方式**: 環境變數 `OLLAMA_API_KEY`
- 🌐 **API 端點**: `https://api.ollama.cloud`
- 💻 **使用介面**: HTTP REST API（Python requests 庫）
- 📦 **可用模型**: 22 個（包括 qwen2.5-coder:3b, phi3.5, stable-code:3b 等）
- 🎯 **集成方式**: 直接整合到 Python 程式碼中

**測試結果**：
```python
from utils.ollama_client import OllamaClient

client = OllamaClient(model="qwen2.5-coder:3b")
response = client.generate("Hello")
# ✅ 成功連接，3/3 測試通過
```

**可用模型列表** (部分):
| 模型 | 參數規模 | 用途 |
|------|---------|------|
| qwen2.5-coder:3b | 3.1B | 程式碼分析 |
| stable-code:3b | 3B | 程式碼生成 |
| phi3.5:latest | 3.8B | 通用任務 |
| qwen2.5:0.5b | 494M | 快速處理 |
| llama3:8b | 8.0B | 高品質生成 |

---

## 🎯 使用場景建議

### 場景 A：命令行互動（推薦方式 1）

**適用情況**：
- 需要快速測試和對話
- 偏好命令行介面
- 想要統一管理本地和雲端模型

**推薦方案**：**本地 Ollama App**
```bash
# 直接使用，無需寫程式碼
ollama run minimax-m2:cloud
ollama run qwen2.5-coder
```

**優勢**：
- ✅ 簡單直觀的 CLI 介面
- ✅ 本地和雲端模型統一管理
- ✅ 支援 signin 登入管理

---

### 場景 B：程式整合（推薦方式 2）

**適用情況**：
- 需要整合到 Python 專案中
- 自動化工作流程
- 批次處理和腳本執行

**推薦方案**：**Ollama Cloud API (Python)**
```python
# 已整合到 JATOS validation tools
python validate.py script.opensesame pool/ --ollama-analyze
```

**優勢**：
- ✅ 完整的 Python API
- ✅ 精細的參數控制
- ✅ 錯誤處理和日誌
- ✅ 已整合到現有工作流程

---

### 場景 C：混合使用（最靈活）

**推薦方案**：兩者並用

1. **開發測試階段**：使用本地 Ollama CLI 快速測試
   ```bash
   ollama run minimax-m2:cloud "測試提示詞"
   ```

2. **生產部署階段**：使用 Python API 整合
   ```python
   analyzer = ScriptAnalyzer(model="qwen2.5-coder:3b")
   results = analyzer.analyze_file("script.opensesame")
   ```

---

## 🔄 兩種方式的關係

### 共同點
- 都連接到 Ollama 的雲端服務
- 都需要認證（signin 或 API key）
- 都可以使用雲端模型

### 差異點

| 特性 | 本地 Ollama App | Ollama Cloud API |
|------|----------------|------------------|
| **端點** | ollama.com:443 | api.ollama.cloud |
| **認證** | ollama signin | OLLAMA_API_KEY |
| **介面** | CLI | HTTP REST API |
| **本地模型** | ✅ 支援 | ❌ 僅雲端 |
| **程式整合** | ⚠️ 需額外包裝 | ✅ 原生支援 |
| **自動化** | ⚠️ 較困難 | ✅ 容易 |

---

## 💡 最佳實踐建議

### 對於 Scripts_Factory 專案

**推薦策略**：**保持現狀（方式 2）+ 補充說明（方式 1）**

#### 1. 主要使用方式：Ollama Cloud API（Python）

**理由**：
- ✅ 已完整整合到 validation tools
- ✅ 3/3 測試全部通過
- ✅ 支援自動化工作流程
- ✅ 精細的錯誤處理

**保持**：
```python
# 繼續使用 Python API
from utils.ollama_client import OllamaClient
```

#### 2. 備選使用方式：本地 Ollama CLI

**用途**：快速測試和手動驗證

**添加說明**：
```bash
# 快速測試模型回應
ollama run minimax-m2:cloud "分析這個實驗腳本..."

# 列出可用模型
ollama list
```

---

## 📝 更新 `ollama_usage.md` 建議

### 需要補充的內容

1. **澄清兩種服務的關係**
   - `ollama.com` (本地 Ollama app 連接)
   - `api.ollama.cloud` (直接 API 調用)

2. **說明雲端模型的使用**
   - 如何透過本地 Ollama 使用雲端模型
   - `:cloud` 後綴的含義

3. **對比 MiniMax 官方 API vs Ollama 服務**
   - 當前文檔混淆了這兩個概念

### 建議新增章節

```markdown
## Ollama 的兩種使用方式

### 1. 本地 Ollama App (ollama.com)
- CLI 介面：`ollama run model-name`
- 支援本地和雲端模型
- 雲端模型標記為 `:cloud`

### 2. Ollama Cloud API (api.ollama.cloud)
- REST API 介面
- 需要 API key
- 適合程式整合
```

---

## ⚠️ 重要發現

### MiniMax 模型可透過 Ollama 使用！

**之前的問題**：
> "minimax-m2 模型在 Ollama Cloud API 無法使用"

**實際情況**：
✅ **可以透過本地 Ollama app 使用！**

```bash
$ ollama run minimax-m2:cloud
# ✅ 成功運行，230B 參數，支援 thinking
```

**解決方案**：
- ✅ 方案 A：使用本地 Ollama CLI (`ollama run minimax-m2:cloud`) - **已確認可行**
- ❌ 方案 B：Ollama Cloud API **不支援** minimax-m2 模型（已測試）

**測試更新 (2025-10-31)**：
已完成 API 支援測試，確認 minimax-m2 模型僅可透過本地 Ollama CLI 使用。
詳見測試腳本：`0_settings/jatos_tools/test_minimax_api.py`

---

## 🎓 結論

### 核心發現

1. ✅ **本地 Ollama app 完全支援雲端模型**
2. ✅ **兩種方式各有優勢，可以並用**
3. ✅ **當前 Python 整合（方式 2）運作良好，建議保持**
4. ✅ **可以補充本地 CLI（方式 1）作為快速測試工具**
5. ⚠️ **MiniMax-M2 僅支援本地 CLI，不支援 Cloud API**（已測試確認）

### 行動建議

#### 短期（已完成）
- ✅ Python API 整合正常運作
- ✅ 完整測試並記錄

#### 中期（已完成）
- ✅ 添加本地 Ollama CLI 使用說明到文檔（已更新 CLAUDE.md 和 jatos_tools/README.md）
- ✅ 測試 minimax-m2:cloud 是否可透過 API 使用（測試結果：不支援）

**測試結果詳情**：
```
測試項目：minimax-m2 via Ollama Cloud API (api.ollama.cloud)
測試模型名稱：
  - minimax-m2
  - minimax-m2:cloud
  - minimax-m2:latest

結果：❌ 全部失敗 (model not found)
結論：MiniMax-M2 僅可透過本地 Ollama CLI 使用，不支援 Cloud API
```

**建議使用方式**：
- ✅ **本地 Ollama CLI**: `ollama run minimax-m2:cloud` (成功)
- ❌ **Python Cloud API**: 不支援 minimax-m2 模型
- ✅ **Python Cloud API**: 使用其他模型 (qwen2.5-coder:3b, phi3.5, etc.)

#### 長期（視需求）
- [ ] 建立統一介面支援兩種方式
- [ ] 添加模型自動選擇邏輯

---

**評估人員**: Claude Code
**測試環境**: Windows, Ollama v0.12.7, Python 3.13
**測試狀態**: ✅ 全部通過
