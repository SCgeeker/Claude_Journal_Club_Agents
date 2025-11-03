# 明日執行計劃 - 2025-11-04

**日期**: 2025-11-04
**目標**: Phase 2.3 數據質量修復 - 為 64 篇論文批量生成 Zettel 卡片
**預計耗時**: 9-13 小時（包含代碼修改驗證）

---

## ⏰ 時間表

### 上午（預計 1-1.5 小時）- 代碼準備

#### Step 1: 更新 Zettel 資料夾命名規則（30 分鐘）

**問題**: 當前命名 `zettel_Research_20251103/` 無法區分論文，無法回溯 paper_id

**改進方案**:
```
zettel_{paper_id}_{citekey_clean}_{domain}_{date}
例: zettel_1_Taxonomy2007_Research_20251104/
    zettel_2_AllassoniereT2021_Linguistics_20251104/
    zettel_64_Guest2025_Research_20251104/
```

**修改位置**:
- `batch_generate_zettel.py` 第 60-80 行
- 添加 citekey 提取邏輯
- 添加 `--output` 參數傳遞

**代碼變更**:
```python
# 新增邏輯
citekey = paper.get('citekey', '')  # 從 DB 查詢
citekey_clean = citekey.replace('-', '').replace('_', '')[:20]  # 清潔化

# 新命名規則
output_dir = f"output/zettelkasten_notes/zettel_{pid}_{citekey_clean}_{domain}_{date_str}"

# 傳遞給 make_slides.py
cmd.extend(['--output', output_dir])
```

---

#### Step 2: 驗證新命名規則（30 分鐘）

**命令**:
```bash
python3 batch_generate_zettel.py --limit 1 --verbose
```

**檢查項目**:
- ✅ 資料夾名稱格式正確
- ✅ 包含 paper_id（可回溯）
- ✅ 包含 citekey（文獻參考）
- ✅ 包含 domain（分類）
- ✅ 包含日期（版本控制）
- ✅ Zettel 卡片正常生成

**預期輸出**:
```
output/zettelkasten_notes/zettel_1_Taxonomy2007_Research_20251104/
✅ 成功生成 12 張卡片
```

---

#### Step 3: 最後檢查（5-10 分鐘）

```bash
# 檢查日誌
tail -30 batch_zettel_generation.log

# 檢查統計
python3 << 'EOF'
import json
with open('batch_zettel_stats.json') as f:
    stats = json.load(f)
print(f"Success: {stats['success']}, Failed: {stats['failed']}")
EOF
```

---

### 上午末至下午（預計 8-12 小時）- 批量生成

#### Step 4: 執行完整批量生成

**命令**:
```bash
# 推薦：後台執行
python3 batch_generate_zettel.py > batch_execution_20251104.log 2>&1 &

# 或前台執行（Windows）
python3 batch_generate_zettel.py
```

**監控命令**（每 30 分鐘執行一次）:
```bash
# 查看實時進度
tail -f batch_zettel_generation.log

# 查看統計
python3 << 'EOF'
import json
with open('batch_zettel_stats.json') as f:
    stats = json.load(f)
progress = stats['success'] + stats['failed']
print(f"進度: {progress}/64 ({progress/64*100:.1f}%)")
print(f"成功: {stats['success']}, 失敗: {stats['failed']}")
EOF
```

**預期進度**:
- 每篇論文：90-150 秒（基於單篇測試結果）
- 10 篇論文：15-25 分鐘
- 全 64 篇：8-12 小時

**時間估算**:
```
開始時間: ~10:00 AM
10篇完成: ~10:30 AM  (檢查點 1)
30篇完成: ~12:00 PM  (檢查點 2)
50篇完成: ~02:00 PM  (檢查點 3)
完成時間: ~6:00-10:00 PM
```

---

### 傍晚/晚上（預計 15-30 分鐘）- 驗證

#### Step 5: 驗證生成結果

**命令 1: 檢查資料夾數量**
```bash
ls -d output/zettelkasten_notes/zettel_* | wc -l
# 預期: 接近 64 個
```

**命令 2: 檢查卡片總數**
```bash
find output/zettelkasten_notes -name "*.md" -type f | wc -l
# 預期: 800-1000 個
```

**命令 3: 驗證資料庫映射**
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
python3 << 'EOF'
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
| 項目 | 當前 | 預期 | 改進 |
|------|------|------|------|
| Zettel 文件夾 | 1 個 | 64 個 | **+63x** |
| Zettel 卡片 | 12 張 | 800-1000 張 | **+67-83x** |
| 論文覆蓋率 | 1.6% | 100% | **+62.4x** |
| 概念數量 | 157 | 300+ | **+1.9x** |
| 概念關聯 | 318 | 800+ | **+2.5x** |

### 資料夾結構
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
- 手動運行失敗的論文：`python3 make_slides.py "Title" --from-kb <pid>`
- 重新執行批處理不會覆蓋已成功的卡片

### 風險 2: API 速率限制
**處理**:
- 暫停執行（Ctrl+C）
- 等待 5-10 分鐘
- 批腳本會自動恢復

### 風險 3: 磁盤空間不足
**處理**:
- 預期生成 ~500MB-1GB 文件
- 提前檢查可用空間：`df -h`
- 如果不足，清理舊日誌或備份

---

## ✅ 完成檢查清單

**明天上午 (代碼準備)**:
- [ ] 更新 Zettel 命名規則
- [ ] 修改 batch_generate_zettel.py
- [ ] 執行 --limit 1 驗證
- [ ] 檢查日誌和統計

**上午末至下午 (批量生成)**:
- [ ] 啟動批量生成
- [ ] 監控進度（每 30 分鐘）
- [ ] 記錄完成時間

**傍晚/晚上 (驗證)**:
- [ ] 檢查資料夾數量（應為 64）
- [ ] 檢查卡片總數（應為 800-1000）
- [ ] 驗證資料庫覆蓋率（應為 100%）
- [ ] 檢查失敗論文清單

**完成後**:
- [ ] 執行 cleanup_session.py --auto --git-commit
- [ ] 更新 SESSION_SUMMARY_20251104.md
- [ ] 準備 Phase 2.4 (Markdown 內容分析)

---

## 📞 重要聯繫信息

### 如果遇到問題，參考
1. `PHASE_2_3_PROGRESS_REPORT.md` - 詳細故障排除
2. `batch_zettel_generation.log` - 實時日誌（每條命令都記錄）
3. `batch_zettel_stats.json` - 統計和錯誤記錄

### 關鍵文件位置
```
D:\core\research\claude_lit_workflow\
├── batch_generate_zettel.py           # 執行腳本
├── make_slides.py                     # Zettel 生成器
├── batch_zettel_generation.log        # 執行日誌
├── batch_zettel_stats.json            # 統計數據
└── output/zettelkasten_notes/         # 輸出目錄
```

---

**準備狀態**: ✅ **所有基礎設施已就緒**
**預計總耗時**: **9-13 小時**（包括代碼修改驗證）
**預期完成時間**: **2025-11-04 晚上 6-10 點**

**加油！明天就要完成 Phase 2.3！🚀**
