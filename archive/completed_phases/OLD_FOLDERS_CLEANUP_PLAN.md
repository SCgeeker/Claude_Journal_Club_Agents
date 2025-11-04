# 舊資料夾清理方案

**日期**: 2025-11-04
**狀態**: 待執行

---

## 📋 檢查結果摘要

### 1. 錯誤命名資料夾 (1 個)

| 資料夾 | 對應論文 | 狀態 | 建議 |
|--------|---------|------|------|
| `zettel_1_paper_1_Research_20251104` | Paper 1 (Her-2012b) | ❌ 命名錯誤 | **刪除**（已有正確版本） |

- **原因**: 命名格式錯誤，應為 `zettel_{cite_key}_date`
- **正確版本**: `zettel_Her-2012b_20251104` 已存在
- **影響**: 無，可安全刪除

---

### 2. 無對應論文的舊資料夾 (5 個)

| 資料夾 | 卡片數 | 對應論文 | 建議 |
|--------|--------|---------|------|
| `zettel_Kemmerer2019_20251029` | 20 | ❌ 無 | **刪除**（歸檔） |
| `zettel_Rommers2013_20251029` | 20 | ❌ 無 | **刪除**（歸檔） |
| `zettel_Speed2025_20251029` | 20 | ❌ 無 | **刪除**（歸檔） |
| `zettel_Wu2020_20251029` | 20 | ❌ 無 | **刪除**（歸檔） |
| `zettel_Zeelenberg2024_20251029` | 20 | ❌ 無 | **刪除**（歸檔） |

**原因**: 這些論文已從知識庫刪除或從未存在
- 可能是 Phase 2.3 之前的測試資料
- 可能是已刪除的論文
- 總卡片數: 100 張

**建議**: 移至歸檔資料夾，不需要重新生成

---

### 3. 有對應論文的舊資料夾 (2 個)

#### 3.1 Allassonniere2021 - 需要處理

| 資料夾 | 對應論文 | 狀態 | 建議 |
|--------|---------|------|------|
| `zettel_Allassonniere2021_20251029` | Paper 43 (Allassonniere-Tang-2021) | ⚠️ 失敗論文 | **保留或重新生成** |

- **對應論文**: Paper 43 (Allassonniere-Tang-2021)
- **新 cite_key**: `Allassonniere-Tang-2021` (有連字符)
- **Phase 2.4 狀態**: 重新生成失敗
- **卡片數**: 20 張

**選項 A**: 保留舊版本
- 優點: 至少有 Zettel 可用
- 缺點: 命名格式不一致（無連字符）

**選項 B**: 按新格式重命名
```bash
mv zettel_Allassonniere2021_20251029 zettel_Allassonniere-Tang-2021_20251029
```
- 優點: 格式統一
- 缺點: 仍是舊版本（10/29）

**選項 C**: 重新生成 ⭐ **推薦**
```bash
python make_slides.py "Paper 43 Zettelkasten" --from-kb 43 --style zettelkasten --domain Research --detail comprehensive --llm-provider google --model gemini-2.0-flash-exp
```
- 優點: 獲得新版本，命名正確
- 缺點: 需要時間（~30秒）

#### 3.2 Altmann2019 & Setic2017 - 保留

| 資料夾 | 對應論文 | 狀態 | 建議 |
|--------|---------|------|------|
| `zettel_Altmann2019_20251029` | Paper 38 (Altmann-2019) | ⚠️ 失敗論文 | **保留** ✅ |
| `zettel_Setic2017_20251029` | Paper 42 (Setic-2017) | ⚠️ 失敗論文 | **保留** ✅ |

- **原因**: Phase 2.4 重新生成失敗，這些是唯一可用版本
- **命名**: 已接近新格式（差異僅在連字符）
- **行動**: 不需處理，保持現狀

---

### 4. 非論文資料夾 (1 個)

| 資料夾 | 說明 | 建議 |
|--------|------|------|
| `zettel_Linguistics_20251029` | 測試或範例資料夾 | **刪除**（歸檔） |

- **原因**: 非論文，可能是測試資料
- **行動**: 移至歸檔

---

## 🎯 推薦執行方案

### 方案 A: 完全清理 ⭐ **推薦**

**目標**: 清理所有無用資料夾，重新生成 Paper 43

**步驟**:

1. **刪除錯誤命名資料夾** (1 個)
   ```bash
   rm -rf "output/zettelkasten_notes/zettel_1_paper_1_Research_20251104"
   ```

2. **歸檔無對應論文的資料夾** (6 個)
   ```bash
   # Kemmerer2019, Rommers2013, Speed2025, Wu2020, Zeelenberg2024, Linguistics
   # 移至 _archive_old_format_20251029/
   ```

3. **重新生成 Paper 43**
   ```bash
   python make_slides.py "Paper 43 Zettelkasten" --from-kb 43 --style zettelkasten --domain Research --detail comprehensive --llm-provider google --model gemini-2.0-flash-exp
   ```

4. **刪除舊的 Allassonniere2021** (Paper 43 重新生成成功後)
   ```bash
   mv "output/zettelkasten_notes/zettel_Allassonniere2021_20251029" "_archive_old_format_20251029/"
   ```

5. **保留 Paper 38 和 42 的舊版本**
   - `zettel_Altmann2019_20251029` → 保留
   - `zettel_Setic2017_20251029` → 保留

**預期結果**:
- 清理 7 個無用/重複資料夾
- 重新生成 1 篇論文（Paper 43）
- 保留 2 個必要的舊版本（Paper 38, 42）
- **最終覆蓋率**: 62/63 (98.4%)

---

### 方案 B: 保守方案

**目標**: 只清理明確無用的資料夾，保留所有可能有用的

**步驟**:

1. **刪除錯誤命名資料夾** (1 個)
   ```bash
   rm -rf "output/zettelkasten_notes/zettel_1_paper_1_Research_20251104"
   ```

2. **歸檔無對應論文的資料夾** (6 個)
   - 同方案 A

3. **保留所有其他資料夾**
   - `zettel_Allassonniere2021_20251029` → 保留
   - `zettel_Altmann2019_20251029` → 保留
   - `zettel_Setic2017_20251029` → 保留

**預期結果**:
- 清理 7 個無用/重複資料夾
- 保留 3 個舊版本（Paper 38, 42, 43）
- **最終覆蓋率**: 61/63 (96.8%)

---

## 📊 方案對比

| 指標 | 方案 A (完全清理) | 方案 B (保守) |
|------|------------------|--------------|
| **清理資料夾數** | 8 個（7歸檔 + 1新生成後刪除） | 7 個 |
| **重新生成** | 1 篇（Paper 43） | 0 篇 |
| **最終覆蓋率** | 62/63 (98.4%) | 61/63 (96.8%) |
| **執行時間** | ~2 分鐘 | ~30 秒 |
| **風險** | 低（Paper 43 可能再次失敗） | 無 |

---

## 🔧 執行腳本

### 方案 A 執行腳本

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理舊資料夾並重新生成 Paper 43
"""

import sys
import shutil
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

output_dir = Path('output/zettelkasten_notes')
archive_dir = output_dir / '_archive_old_format_20251029'

# Step 1: Delete incorrectly named folder
print('步驟 1: 刪除錯誤命名資料夾')
error_folder = output_dir / 'zettel_1_paper_1_Research_20251104'
if error_folder.exists():
    shutil.rmtree(error_folder)
    print(f'✓ 已刪除: {error_folder.name}')

# Step 2: Archive folders without corresponding papers
print('\n步驟 2: 歸檔無對應論文的資料夾')
to_archive = [
    'zettel_Kemmerer2019_20251029',
    'zettel_Rommers2013_20251029',
    'zettel_Speed2025_20251029',
    'zettel_Wu2020_20251029',
    'zettel_Zeelenberg2024_20251029',
    'zettel_Linguistics_20251029'
]

for folder_name in to_archive:
    folder = output_dir / folder_name
    if folder.exists():
        dest = archive_dir / folder_name
        shutil.move(str(folder), str(dest))
        print(f'✓ 已歸檔: {folder_name}')

# Step 3: Regenerate Paper 43
print('\n步驟 3: 重新生成 Paper 43')
cmd = [
    'python', 'make_slides.py',
    'Paper 43 Zettelkasten',
    '--from-kb', '43',
    '--style', 'zettelkasten',
    '--domain', 'Research',
    '--detail', 'comprehensive',
    '--llm-provider', 'google',
    '--model', 'gemini-2.0-flash-exp'
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode == 0:
        print('✓ Paper 43 重新生成成功')

        # Step 4: Archive old Allassonniere2021
        print('\n步驟 4: 歸檔舊的 Allassonniere2021')
        old_folder = output_dir / 'zettel_Allassonniere2021_20251029'
        if old_folder.exists():
            dest = archive_dir / old_folder.name
            shutil.move(str(old_folder), str(dest))
            print(f'✓ 已歸檔: {old_folder.name}')
    else:
        print('✗ Paper 43 重新生成失敗，保留舊版本')
except Exception as e:
    print(f'✗ 錯誤: {e}')

print('\n完成！')
```

---

## ✅ 我的建議

**推薦方案 A（完全清理）**，理由：

1. **徹底清理**: 移除所有無用資料夾（7個），釋放空間
2. **提升覆蓋率**: 從 96.8% → 98.4%
3. **格式一致**: Paper 43 將有正確命名的新版本
4. **風險可控**: 即使 Paper 43 再次失敗，仍保留舊版本備份
5. **時間成本低**: 只需額外 ~30 秒生成 Paper 43

**執行時機**: 現在（Phase 2.4 清理階段）

**後續行動**:
- 如 Paper 43 再次失敗，從歸檔恢復舊版本
- Paper 38, 40, 41, 42 可作為 Phase 2.5 任務處理

---

**報告生成時間**: 2025-11-04 17:30
**狀態**: 待用戶確認
**建議**: 執行方案 A
