# 明天快速開始指南

**日期**: 2025-11-04
**目標**: 完成 Phase 2.3 - 為 64 篇論文批量生成 Zettel 卡片

---

## ⚡ 5 分鐘快速修復

### 步驟 1：修復 make_slides.py

打開 `make_slides.py`，找到第 **200-220 行**：

```python
# 當前（錯誤）
maker = SlideMaker(
    llm_provider=args.llm_provider,
    model=args.model,
    max_cost=args.max_cost,           # ← 移除這行
    enable_monitoring=args.monitor     # ← 移除這行
)
```

改為：

```python
# 修復後
maker = SlideMaker(
    llm_provider=args.llm_provider,
    model=args.model
)
```

### 步驟 2：驗證修復

```bash
python3 make_slides.py "Test" --from-kb 1 --style zettelkasten --domain Research --detail comprehensive
```

**預期輸出**：應看到進度提示（不是 TypeError）

---

## 🚀 執行批量生成

### 選項 A：簡單執行（推薦）

```bash
python3 batch_generate_zettel.py
```

執行時間：8-12 小時（取決於 LLM 速度）

### 選項 B：後台執行（推薦用於長期運行）

```bash
# Windows PowerShell
Start-Process -FilePath python3 -ArgumentList batch_generate_zettel.py -NoNewWindow

# 或 Linux/Mac
nohup python3 batch_generate_zettel.py > batch_execution.log 2>&1 &
```

### 選項 C：測試模式（先驗證沒有其他問題）

```bash
# 只生成前 3 篇論文
python3 batch_generate_zettel.py --limit 3
```

---

## 📊 監控進度

### 實時查看日誌

```bash
# Windows
type batch_zettel_generation.log | tail -20

# Linux/Mac
tail -f batch_zettel_generation.log
```

### 檢查進度

每 10 篇論文會輸出進度行：

```
[2025-11-04 10:15:23] Progress: 10/64 (15.6%) - Success: 10, Failed: 0
```

### 生成統計

```bash
python3 << 'EOF'
import json
with open('batch_zettel_stats.json') as f:
    stats = json.load(f)
print(f"Success: {stats['success']}")
print(f"Failed: {stats['failed']}")
print(f"Total: {stats['total']}")
if stats['errors']:
    print(f"\nErrors: {len(stats['errors'])}")
    for err in stats['errors'][:5]:
        print(f"  - Paper {err['paper_id']}: {err['error'][:50]}")
EOF
```

---

## ✅ 完成後驗證

### 1. 檢查生成的 Zettel 文件夾

```bash
# 應該看到 64 個文件夾（或接近）
ls -d output/zettelkasten_notes/zettel_* | wc -l
```

**預期**: 接近 64 個

### 2. 檢查卡片總數

```bash
# 計算所有生成的 .md 文件
find output/zettelkasten_notes -name "*.md" -type f | wc -l
```

**預期**: 800-1000 個卡片文件

### 3. 驗證資料庫映射

```bash
python3 << 'EOF'
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

# 檢查卡片總數
cursor.execute("SELECT COUNT(*) FROM zettel_cards")
total_cards = cursor.fetchone()[0]
print(f"✅ Zettel 卡片總數: {total_cards}")

conn.close()
EOF
```

**預期**:
```
Zettel 覆蓋率: 64/64 (100.0%)
Zettel 卡片總數: 800-1000
```

---

## 🔧 如果遇到問題

### 問題 1：某些論文生成失敗

**原因**: 可能是 LLM 超時或 API 配額限制

**解決**:
1. 檢查 `batch_zettel_stats.json` 看哪些論文失敗
2. 調整 timeout（在 `batch_generate_zettel.py` 第 120 行，預設 600 秒）
3. 重新執行失敗的論文（編輯腳本添加 `--paper-ids` 過濾）

### 問題 2：執行速度太慢

**原因**: 使用的 LLM 模型太大或網路慢

**解決**:
1. 檢查使用的 LLM (`--llm-provider` 默認 auto)
2. 如果使用 Ollama，考慮換更小的模型
3. 增加 `batch_generate_zettel.py` 中的 worker 數量

### 問題 3：磁盤空間不足

**原因**: 生成的 Markdown 文件很大

**解決**:
1. 預留至少 1GB 磁盤空間
2. 清理舊的 `output/zettelkasten_notes/` 目錄（如果有重複生成）

---

## 📝 下一步計劃（生成完成後）

1. **Markdown 內容分析** (Phase 2.4)
   - 從卡片 Markdown 文件提取隱含概念
   - 分析 AI Agent 批判性思考

2. **概念網絡重新計算** (Phase 2.5)
   - 基於完整的 Zettel 數據重新構建概念圖
   - 改進概念關聯強度

3. **視覺化和報告** (Phase 2.6)
   - 生成改進版的 `zettel_concept_network.md`
   - 創建多維度知識圖譜

---

## 🎯 目標回顧

| 項目 | 當前 | 目標 |
|------|------|------|
| 論文覆蓋率 | 6.2% (4 篇) | 100% (64 篇) |
| Zettel 卡片 | 52 張 | 800-1000 張 |
| 概念提取 | 157 個 | 300+ 個 |
| 概念關聯 | 318 條 | 800+ 條 |

---

## ⏰ 時間估算

| 任務 | 時間 |
|------|------|
| 修復代碼 | 5 分鐘 |
| 驗證修復 | 5 分鐘 |
| 批量生成 | 8-12 小時 |
| 驗證結果 | 15 分鐘 |
| **總計** | **8-12.5 小時** |

---

## 💡 建議

1. **不要**在執行期間關閉終端或電腦
2. **監控** `batch_zettel_generation.log` 每隔 30 分鐘
3. **備份** 重要文件（防止意外中斷）
4. **記錄** 完成時間和最終統計數據

---

## 🚨 緊急聯絡

如果遇到無法解決的問題：

1. 檢查 `batch_zettel_generation.log` 最後 50 行
2. 檢查 `batch_zettel_stats.json` 的錯誤記錄
3. 停止執行（Ctrl+C）
4. 重新評估方案

---

**準備好了嗎？** 按照上面的步驟執行即可！

**祝您生成順利！** 🚀
