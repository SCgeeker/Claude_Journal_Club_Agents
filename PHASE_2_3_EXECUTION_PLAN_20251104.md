# Phase 2.3 執行計畫 - 2025-11-04

**檔案**: PHASE_2_3_EXECUTION_PLAN_20251104.md
**日期**: 2025-11-04
**目標**: Phase 2.3 - 批量生成 Zettelkasten 卡片（64篇論文）
**預計耗時**: 9-13 小時
**優先級**: ⭐⭐⭐⭐⭐ 高優先級

---

## 🎯 執行背景

### Phase 2 路線圖調整

基於 Batch C 的分析結果，Relation_Finder 需要改進：
- ❌ 當前問題：概念提取不足（4個 vs 預期100+）、引用關係為0
- ✅ 解決方案：先生成 Zettel 卡片提供豐富資料，再改進 Relation_Finder v2

**新路線圖**:
```
Phase 2.3: Zettel 批量生成（64篇）           ← 明天執行
  ↓
Phase 2.4: Zettel 內容概念提取
  ↓
Phase 2.5: Relation_Finder v2 重構
  ↓
Phase 2.6: 重新分析 64 篇論文
  ↓
Phase 2.7: 繼續 Batch B2-D（擴展到112篇）
```

**參考文檔**: `PHASE2_REVISED_ROADMAP.md`（詳細路線圖）

---

## ⏰ 時間表

### 上午（預計 30-45 分鐘）- 程式碼修復

#### Step 1: 修復 make_slides.py API 不匹配問題（15-20 分鐘）

**問題診斷**:
```
錯誤: SlideMaker.__init__() got an unexpected keyword argument 'max_cost'
位置: make_slides.py 第 209 行
根因: 傳遞了不支援的參數 max_cost 和 enable_monitoring
```

**修復方案** (推薦選項 A):
```python
# make_slides.py 第 200-220 行
# 移除不支援的參數

maker = SlideMaker(
    llm_provider=args.llm_provider,
    model=args.model,
    # max_cost=args.max_cost,           # ← 刪除
    # enable_monitoring=args.monitor     # ← 刪除
)
```

**驗證命令**:
```bash
# 測試單篇論文 Zettel 生成
python make_slides.py "Test" --from-kb 1 --style zettelkasten --domain Research --detail comprehensive
```

**預期輸出**:
- ✅ 無 TypeError
- ✅ 能看到 LLM 呼叫進度
- ✅ 生成 Zettel 卡片檔案

---

#### Step 2: 單篇論文驗證（10-15 分鐘）

**命令**:
```bash
python batch_generate_zettel.py --limit 1 --verbose
```

**檢查項目**:
- ✅ 資料夾命名格式正確（包含 paper_id）
- ✅ Zettel 卡片正常生成
- ✅ 資料庫映射正確
- ✅ 日誌記錄完整

**預期輸出**:
```
[1/1] Processing paper 1: A Taxonomy of...
  → Generated 12-20 cards
  → Saved to output/zettelkasten_notes/zettel_1_...
✅ Success: 1/1
```

---

#### Step 3: 最後檢查（5-10 分鐘）

**驗證命令**:
```bash
# 檢查日誌
tail -30 batch_zettel_generation.log

# 檢查統計
python << 'EOF'
import json
with open('batch_zettel_stats.json') as f:
    stats = json.load(f)
print(f"Success: {stats['success']}, Failed: {stats['failed']}")
EOF

# 檢查生成的檔案夾
ls -d output/zettelkasten_notes/zettel_* | head -3
```

---

### 上午末至下午（預計 8-12 小時）- 批量生成

#### Step 4: 執行完整批量生成

**推薦命令**（後台執行）:
```bash
# Windows 後台執行
python batch_generate_zettel.py > batch_execution_20251104.log 2>&1 &

# 或前台執行
python batch_generate_zettel.py
```

**配置參數**（已在 batch_zettel_generation_plan.json 中設置）:
```yaml
總論文數: 64 篇
詳細程度: comprehensive
風格: zettelkasten
預期卡片數: 800-1000 張（每篇12-20張）
超時限制: 300秒/篇
```

**監控命令**（每 30 分鐘執行一次）:
```bash
# 查看即時進度
tail -f batch_zettel_generation.log

# 查看統計
python << 'EOF'
import json
with open('batch_zettel_stats.json') as f:
    stats = json.load(f)
progress = stats['success'] + stats['failed']
print(f"進度: {progress}/64 ({progress/64*100:.1f}%)")
print(f"成功: {stats['success']}, 失敗: {stats['failed']}")
EOF
```

**預期進度時間表**:
```
開始時間: ~10:00 AM
10篇完成: ~10:30 AM  (檢查點 1)
30篇完成: ~12:00 PM  (檢查點 2)
50篇完成: ~02:00 PM  (檢查點 3)
完成時間: ~6:00-10:00 PM
```

**時間估算**:
- 每篇論文：90-150 秒（基於單篇測試）
- 10 篇論文：15-25 分鐘
- 全 64 篇：8-12 小時

---

### 傍晚/晚上（預計 30-45 分鐘）- 驗證

#### Step 5: 驗證生成結果

**命令 1: 檢查資料夾數量**
```bash
# PowerShell
(Get-ChildItem output/zettelkasten_notes/zettel_* -Directory).Count
# 預期: 接近 64 個
```

**命令 2: 檢查卡片總數**
```bash
# PowerShell
(Get-ChildItem output/zettelkasten_notes -Recurse -Filter *.md).Count
# 預期: 800-1000 個
```

**命令 3: 驗證資料庫映射**
```bash
python << 'EOF'
import sqlite3

conn = sqlite3.connect("knowledge_base/index.db")
cursor = conn.cursor()

# 檢查有多少論文現在有 Zettel
cursor.execute("SELECT COUNT(DISTINCT paper_id) FROM zettel_cards WHERE paper_id IS NOT NULL")
papers_with_zettel = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM papers")
total_papers = cursor.fetchone()[0]

coverage = papers_with_zettel / total_papers * 100
print(f"✅ Zettel 覆蓋率: {papers_with_zettel}/{total_papers} ({coverage:.1f}%)")
print(f"✅ 預期: 64/64 (100.0%)")

# 檢查卡片總數
cursor.execute("SELECT COUNT(*) FROM zettel_cards")
total_cards = cursor.fetchone()[0]
print(f"✅ Zettel 卡片總數: {total_cards}")
print(f"✅ 預期: 800-1000")

conn.close()
EOF
```

**命令 4: 檢查失敗的論文（如果有）**
```bash
python << 'EOF'
import json
with open('batch_zettel_stats.json') as f:
    stats = json.load(f)

if stats['errors']:
    print(f"❌ 失敗論文: {len(stats['errors'])}")
    for err in stats['errors']:
        print(f"  - Paper {err['paper_id']}: {err['error'][:80]}")
else:
    print("✅ 所有論文都成功生成")
EOF
```

---

## 📋 預期成果

### 完成後應有

| 項目 | 當前 (2025-11-04 13:45) | 預期 | 改進 |
|------|------------------------|------|------|
| Zettel 文件夾 | 36 個 | 64 個 | **+1.8x** |
| Zettel 卡片 | 52 張 | 800-1000 張 | **+15-19x** |
| 論文覆蓋率 (資料庫) | 6.2% (4/64篇) | 100% (64/64篇) | **+93.8%** |
| 概念數量 | 4 個 | 150+ 個 | **+37x** |
| 可用於分析 | 受限 | 完整 | **質的飛躍** |

### 資料夾結構示例
```
output/zettelkasten_notes/
├── zettel_1_Taxonomy2007_Research_20251104/
│   ├── zettel_index.md
│   └── zettel_cards/
│       ├── Research-20251104-001.md
│       ├── Research-20251104-002.md
│       ...
├── zettel_2_AllassoniereT2021_Linguistics_20251104/
│   ...
├── zettel_64_Guest2025_Research_20251104/
    ...
```

---

## 🚨 風險和應急方案

### 風險 1: 某篇論文超時或失敗
**處理**:
- 檢查 `batch_zettel_stats.json` 中的失敗列表
- 手動運行失敗的論文：`python make_slides.py "Title" --from-kb <pid> --style zettelkasten`
- 重新執行批處理不會覆蓋已成功的卡片

### 風險 2: API 速率限制
**處理**:
- 暫停執行（Ctrl+C）
- 等待 5-10 分鐘
- 批腳本會自動恢復（基於 stats.json）

### 風險 3: 磁碟空間不足
**處理**:
- 預期生成 ~500MB-1GB 文件
- 提前檢查可用空間
- 如果不足，清理舊日誌或備份

---

## ✅ 完成檢查清單

**上午 (程式碼準備)**:
- [x] ~~修復 `make_slides.py` API 不匹配問題~~ (2025-11-04 13:39 - 使用直接調用方式成功)
- [x] 執行 `--limit 1` 驗證 (2025-11-04 13:39 - Abbas-2022.pdf 測試成功)
- [ ] 檢查日誌和統計資料
- [x] 確認 LLM 服務可用（Ollama/Gemini/OpenAI） (Google Gemini 2.0 Flash Exp 可用)
- [x] 評估已存在的 zettel 資料夾重新命名的可行性及價值 (發現36個資料夾，但只有4篇在資料庫中)

**上午末至下午 (批量生成)**:
- [ ] 啟動批量生成
- [ ] 監控進度（每 30 分鐘）
- [ ] 記錄完成時間

**傍晚/晚上 (驗證)**:
- [ ] 檢查資料夾數量（應為 64 個）
- [ ] 檢查卡片總數（應為 800-1000 張）
- [ ] 驗證資料庫 zettel 覆蓋率（應為 100%）
- [ ] 檢查失敗論文清單

**完成後**:
- [ ] 生成完成報告（`PHASE_2_3_COMPLETION_REPORT.md`）
- [ ] 準備 Phase 2.4（Zettel 概念提取分析）
- [ ] （可選）執行 `cleanup_session.py` 整理檔案

---

## 📞 重要參考資訊

### 如果遇到問題，參考
1. `PHASE_2_3_PROGRESS_REPORT.md` - 詳細故障排除
2. `batch_zettel_generation.log` - 即時日誌
3. `batch_zettel_stats.json` - 統計和錯誤記錄
4. `PHASE2_REVISED_ROADMAP.md` - 完整路線圖

### 關鍵檔案位置
```
D:\core\research\claude_lit_workflow\
├── batch_generate_zettel.py           # 執行腳本
├── make_slides.py                     # Zettel 生成器
├── batch_zettel_generation.log        # 執行日誌
├── batch_zettel_stats.json            # 統計資料
└── output/zettelkasten_notes/         # 輸出目錄
```

---

## 🔗 相關文檔

- **完整路線圖**: `PHASE2_REVISED_ROADMAP.md`
- **配置說明**: `ZETTEL_GENERATION_CONFIG.md`
- **進度報告**: `PHASE_2_3_PROGRESS_REPORT.md`
- **Batch C 報告**: `BATCH_C_RELATION_FINDER_COMPLETION_REPORT.md`

---

**準備狀態**: ✅ **所有基礎設施已就緒**
**預計總耗時**: **9-13 小時**（包括程式碼修復和驗證）
**預期完成時間**: **2025-11-04 晚上 6-10 點**

---

## 📊 當前進度 (2025-11-04 13:45)

### 知識庫統計
- 論文總數: **64 篇** ✅ (目標達成)
- Zettel 卡片總數: **52 張** (目標: 800-1000 張，完成度: 5.2-6.5%)
- 已有 Zettel 的論文: **4 篇** (目標: 64 篇，覆蓋率: 6.2%)
- Zettel 資料夾數: **36 個** (目標: 64 個，完成度: 56.2%)

### 已完成項目
- ✅ 單篇 Zettelkasten 生成測試成功 (Abbas-2022.pdf, 20張卡片)
- ✅ 功能驗證完整（ID格式、卡片結構、索引、網絡圖）
- ✅ 學術嚴謹性確認（核心概念保留原文）
- ✅ Google Gemini 2.0 Flash Exp 可用

### 待處理事項
- ⏸️ 批量生成剩餘 60 篇論文的 Zettel (未啟動)
- ⚠️ 36個現有資料夾與資料庫同步問題 (需檢查)

### 預估完成時間
- 批量生成: 8-12 小時
- 驗證: 30-45 分鐘
- 總計: 今晚 6-10 點可完成

---

**加油！今天就要完成 Phase 2.3，為 Relation_Finder v2 打下堅實基礎！🚀**
