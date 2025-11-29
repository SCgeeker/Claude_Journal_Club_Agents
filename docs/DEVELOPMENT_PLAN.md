# 開發規劃文件 - Phase 1.0

**建立日期**: 2025-11-29
**狀態**: 規劃中

---

## 一、課題總覽

### 來源：RESUME_MEMO.md「其他優化建議及課題」

| # | 課題 | 類型 | 優先級 |
|---|------|------|--------|
| A | 各工具 --help 並列 `uv run` 與 `python` 指令格式 | UX | P3 |
| B | `make_slides.py` 主題參數改選填 | UX | P2 |
| C | 預設簡報格式改 Markdown，輸出路徑改 `output/slides/` | Config | P2 |
| D | Zettel 生成功能是否獨立出 `make_slides.py` | **架構** | **P1** |
| E | 知識庫新增 Zettel 卡片管理 | **架構** | **P1** |
| F | 其他未列出的考慮項目 | 設計 | P1 |

### 新增課題（討論中確認）

| # | 課題 | 類型 | 優先級 |
|---|------|------|--------|
| G | 自訂需求檔案支援（custom_requirements） | 功能 | **P1** |
| H | PDF 工具整合（MarkItDown） | 功能 | P2 |

---

## 二、課題依賴關係分析

```
                    ┌─────────────────────────────────────┐
                    │  D: Zettel 獨立為 generate_zettel   │
                    │     (架構決策 - 必須先決定)          │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ E: Zettel 入庫  │  │ G: 自訂需求檔案 │  │ B: 主題選填     │
    │   (知識庫整合)   │  │   (兩工具都需要) │  │   (slides 優化) │
    └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
             │                    │                    │
             │                    │                    │
             ▼                    ▼                    ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ F-1: 卡片更新   │  │ (兩工具可平行   │  │ C: 預設格式/    │
    │ F-2: ID 衝突    │  │  實作，無阻塞)   │  │    輸出路徑     │
    │ F-3: 向量嵌入   │  │                 │  │                 │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
             │
             ▼
    ┌─────────────────┐
    │ F-4: 刪除連動   │
    └─────────────────┘

    ════════════════════════════════════════════════════════════

    獨立課題（無依賴，可隨時實作）：

    ┌─────────────────┐  ┌─────────────────┐
    │ A: --help 格式  │  │ H: MarkItDown   │
    │   (純 UX 改善)   │  │   (新增後端)    │
    └─────────────────┘  └─────────────────┘
```

### 關鍵路徑

```
D (架構決策) → E (入庫機制) → F-1/F-2/F-3 (細節處理) → F-4 (刪除連動)
```

### 可平行開發

| 課題 | 可與哪些平行 | 說明 |
|------|-------------|------|
| G (自訂需求) | 全部 | 純功能新增，不影響架構 |
| A (--help) | 全部 | 純文字修改 |
| H (MarkItDown) | 全部 | 獨立後端，不改現有流程 |
| B (主題選填) | C | 都是 slides 參數調整 |
| C (預設格式) | B | 都是 slides 參數調整 |

---

## 三、課題詳細分析

### D: Zettel 獨立為 `generate_zettel.py`

**結論：建議獨立**

| 面向 | make_slides.py 現況 | 獨立後 |
|------|---------------------|--------|
| 責任 | 投影片 + Zettel 混合 | 單一職責 |
| 參數 | 27+ 參數，複雜 | 各自精簡 |
| 入庫 | 可選（常被忽略） | 強制（設計目標） |
| 維護 | 條件分支多 | 清晰分離 |

**獨立後的 CLI 設計**：

```bash
# 新指令
uv run zettel <pdf_path> [選項]
uv run zettel --from-kb <paper_id> [選項]

# 主要參數
--detail {minimal|brief|standard|detailed|comprehensive}
--add-to-kb          # 預設啟用
--cross-link         # 啟用跨論文連結
--no-custom          # 忽略預設自訂需求
```

**對 G (自訂需求) 的影響**：
- ✅ 無負面影響
- ✅ 獨立後可針對 zettel 設計更貼切的預設檔案結構

---

### E: 知識庫新增 Zettel 卡片管理

**現況**：

```
知識庫已有 Zettel 相關表：
├── zettel_cards         ← 存在但【未被使用】
├── zettel_links         ← 存在但【未被使用】
├── paper_zettel_links   ← 存在但【未被使用】
└── zettel_cards_fts     ← 全文搜索（已就緒）

問題：生成的卡片只寫到 output/ 目錄，沒有入庫！
```

**需要實作**：

| 功能 | 方法 | 說明 |
|------|------|------|
| 卡片入庫 | `kb.add_zettel_card()` | 已存在，需確認完整性 |
| 連結入庫 | `kb.add_zettel_link()` | 已存在，需整合 |
| 論文關聯 | `kb.link_paper_to_zettel()` | 已存在，需整合 |
| 向量嵌入 | `vector_db.upsert_zettel()` | 需加入流程 |

**對 G (自訂需求) 的影響**：
- ✅ 無影響，入庫是生成後的動作，與提示語無關

---

### F: 其他考慮項目

#### F-1: Zettel 更新機制

**問題**：重新生成同一論文的卡片時，如何處理舊卡片？

**選項**：

| 策略 | 說明 | 建議 |
|------|------|------|
| 覆蓋 | 刪除舊卡片，寫入新卡片 | ⭐ 簡單直接 |
| 版本控制 | 保留歷史版本 | 複雜，暫不需要 |
| 合併 | 智慧合併新舊內容 | 過度工程 |

**建議實作**：

```python
def regenerate_zettel(paper_id):
    # 1. 刪除該論文的舊卡片
    kb.delete_zettel_cards_by_paper(paper_id)

    # 2. 生成新卡片
    cards = generate_new_cards(paper_id)

    # 3. 入庫
    for card in cards:
        kb.add_zettel_card(card)
```

**對 G 的影響**：無

---

#### F-2: 卡片 ID 衝突

**問題**：同一論文重新生成時，`{citekey}-001` 會重複

**解決方案**：

| 方案 | 說明 | 建議 |
|------|------|------|
| 時間戳後綴 | `Barsalou-1999-001-20251129` | 冗長 |
| 版本號 | `Barsalou-1999-001-v2` | 需追蹤版本 |
| 覆蓋策略 | 搭配 F-1，直接覆蓋 | ⭐ 簡單 |

**建議**：採用覆蓋策略（F-1），ID 保持簡潔

**對 G 的影響**：無

---

#### F-3: 向量嵌入時機

**問題**：何時生成卡片的向量嵌入？

**選項**：

| 時機 | 優點 | 缺點 |
|------|------|------|
| 生成時立即 | 即時可搜索 | 增加生成時間 |
| 批次處理 | 效率高 | 需額外執行 |
| 按需生成 | 節省資源 | 首次搜索慢 |

**建議**：

```python
# generate_zettel.py
parser.add_argument('--embed', action='store_true', default=True,
                   help='生成後立即建立向量嵌入（預設：是）')
parser.add_argument('--no-embed', action='store_true',
                   help='跳過向量嵌入（稍後用 uv run embeddings 補上）')
```

**對 G 的影響**：無

---

#### F-4: 刪除連動

**問題**：刪除論文時，關聯的 Zettel 卡片如何處理？

**建議**：

```python
# kb_manage.py delete 指令
def delete_paper(paper_id, cascade=False):
    if cascade:
        # 同時刪除關聯卡片
        kb.delete_zettel_cards_by_paper(paper_id)
    else:
        # 僅刪除論文，卡片保留（成為孤立卡片）
        pass

    kb.delete_paper(paper_id)
```

**CLI 設計**：

```bash
uv run kb delete 14                    # 僅刪論文，卡片保留
uv run kb delete 14 --cascade          # 連同卡片一起刪除
uv run kb delete 14 --cascade --force  # 強制刪除（不確認）
```

**對 G 的影響**：無

---

### G: 自訂需求檔案支援

**設計決策**：

| 工具 | 方案 | 參數設計 |
|------|------|---------|
| `make_slides.py` | 1 + 3 | `--custom-file` + 預設 `config/custom_slides.md` |
| `generate_zettel.py` | 2 | 預設 `config/custom_zettel.md`，`--no-custom` 跳過 |

**共用模組**：

```python
# src/utils/prompt_loader.py

def load_custom_requirements(
    custom_arg: str = None,           # --custom 命令行字串
    custom_file_arg: str = None,      # --custom-file 檔案路徑
    default_file: str = None          # 預設檔案路徑
) -> str | None:
    """
    優先順序：
    1. custom_file_arg（明確指定檔案）
    2. custom_arg（命令行字串）
    3. default_file（預設檔案，若存在）
    """
    ...
```

**對其他課題的影響**：

| 課題 | 影響 | 說明 |
|------|------|------|
| D (獨立 zettel) | ✅ 正向 | 獨立後可針對性設計 |
| E (入庫) | ⚪ 無 | 入庫與提示語無關 |
| F-* | ⚪ 無 | 都是生成後的處理 |

---

## 四、實作優先順序

### Phase 1.0：核心架構（本次）

```
Week 1: 架構決策與基礎建設
├── D: 建立 generate_zettel.py（從 make_slides.py 分離）
├── G: 實作自訂需求檔案支援
│   ├── src/utils/prompt_loader.py
│   ├── make_slides.py 修改
│   └── generate_zettel.py 整合
└── 更新 zettelkasten_template.jinja2（支援 custom_requirements）

Week 2: 知識庫整合
├── E: Zettel 入庫流程
│   ├── 確認 kb.add_zettel_card() 完整性
│   ├── 整合到 generate_zettel.py
│   └── 測試入庫 → 搜索流程
├── F-1: 更新機制（覆蓋策略）
└── F-3: 向量嵌入整合
```

### Phase 1.1：使用體驗優化

```
├── B: 主題參數改選填
├── C: 預設格式/路徑調整
├── A: --help 格式統一
└── F-4: 刪除連動
```

### Phase 1.2：PDF 工具整合

```
└── H: MarkItDown 整合（RESUME_MEMO 原本待辦）
```

---

## 五、風險評估

### 低風險（可安心實作）

| 課題 | 風險等級 | 理由 |
|------|----------|------|
| G (自訂需求) | 🟢 低 | 純新增功能，不改現有邏輯 |
| A (--help) | 🟢 低 | 純文字修改 |
| B (主題選填) | 🟢 低 | 參數預設值調整 |
| C (預設格式) | 🟢 低 | 可透過 config 控制 |

### 中等風險（需謹慎測試）

| 課題 | 風險等級 | 理由 | 緩解措施 |
|------|----------|------|---------|
| D (獨立 zettel) | 🟡 中 | 程式碼分離，可能遺漏邏輯 | 完整測試案例 |
| E (入庫) | 🟡 中 | 資料庫操作，可能資料不一致 | 交易機制 |
| F-1 (更新) | 🟡 中 | 刪除操作，可能誤刪 | 備份 + 確認 |

### 需注意

| 課題 | 注意事項 |
|------|---------|
| F-4 (刪除連動) | 需明確定義「孤立卡片」的處理策略 |
| H (MarkItDown) | 需測試與 pdfplumber 的輸出差異 |

---

## 六、結論

### G (自訂需求) 與其他課題的關係

```
✅ G 可以獨立實作，不受其他課題阻塞
✅ G 與 D 配合最佳（獨立後可針對性設計）
✅ G 對 E/F 無影響（入庫是生成後的動作）
```

### 建議實作順序

```
1. D + G 同時進行
   ├── D: 分離 generate_zettel.py
   └── G: 實作 prompt_loader.py + 整合

2. E: Zettel 入庫（依賴 D 完成）

3. F-1/F-2/F-3: 細節處理（依賴 E 完成）

4. B/C/A: UX 優化（隨時可做）

5. H: MarkItDown（獨立，隨時可做）
```

---

## 七、新增課題：現有 Zettel 卡片匯入

### 現況

```
output/zettelkasten_notes/
├── zettel_Barsalou-1999_20251125_gemini_2.0_flash_exp/
├── zettel_Adams-2020_20251123/
├── ... (共 26 個論文資料夾，約 400+ 張卡片)
└── 這些卡片【尚未入庫】！
```

### 解決方案：`uv run kb import-zettel`

```bash
# 匯入單一資料夾
uv run kb import-zettel output/zettelkasten_notes/zettel_Barsalou-1999_*/

# 批次匯入所有現有卡片
uv run kb import-zettel-all

# 預覽模式
uv run kb import-zettel-all --dry-run
```

### 匯入流程

```
1. 讀取 zettel_index.md → 解析 cite_key、論文資訊
2. 比對 papers 表
   ├── 找到 paper_id → 使用
   └── 未找到 → 警告 / 建立新記錄
3. 遍歷 zettel_cards/*.md
   ├── 解析 YAML + Markdown
   ├── 提取連結關係
   └── 寫入 zettel_cards + zettel_links 表
4. 生成向量嵌入（--embed 選項）
```

### 卡片欄位對照

| Markdown 區塊 | 資料庫欄位 |
|---------------|-----------|
| YAML `title` | `title` |
| YAML `summary` | `core_concept` |
| `## 說明` | `content` |
| `## 連結網絡` | → `zettel_links` 表 |
| `## 來源脈絡` | `source_info` |
| `🤖 AI:` | `ai_notes` |
| `✍️ Human:` | `human_notes` |
| `## 待解問題` | 可存入 `description` 或新增欄位 |

### 對其他課題的影響

| 課題 | 影響 |
|------|------|
| D (獨立 zettel) | ⚪ 無，匯入是獨立功能 |
| E (入庫機制) | ✅ 共用，可先實作 E 再做匯入 |
| G (自訂需求) | ⚪ 無 |

### 實作優先級

**建議放在 Phase 1.0 後期**（E 完成後）

```
Phase 1.0 順序調整：
1. D: 獨立 generate_zettel.py
2. G: 自訂需求檔案
3. E: Zettel 入庫機制 ← 先完成這個
4. I: import-zettel 指令 ← 複用 E 的入庫邏輯
```

---

## 八、檔案清單

### 新增檔案

| 檔案 | 說明 |
|------|------|
| `generate_zettel.py` | Zettel 生成 CLI（新） |
| `src/utils/prompt_loader.py` | 自訂需求載入模組 |
| `src/utils/zettel_importer.py` | Zettel 匯入模組（新） |
| `config/custom_slides.md` | 投影片預設需求（範例） |
| `config/custom_zettel.md` | Zettel 預設需求（範例） |

### 修改檔案

| 檔案 | 修改內容 |
|------|---------|
| `make_slides.py` | 移除 zettelkasten 邏輯，新增 `--custom-file` |
| `templates/prompts/zettelkasten_template.jinja2` | 新增 `custom_requirements` 區塊 |
| `pyproject.toml` | 新增 `zettel` CLI 入口 |
| `src/knowledge_base/kb_manager.py` | 確認 zettel 相關方法完整性 |
| `docs/CLI_GUIDE.md` | 更新指令說明 |

---

**下一步**：確認此規劃後，開始實作 Phase 1.0
