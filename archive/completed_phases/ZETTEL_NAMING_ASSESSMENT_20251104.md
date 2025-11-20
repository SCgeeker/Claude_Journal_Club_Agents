# Zettel 資料夾命名規則評估報告

**日期**: 2025-11-04
**評估人**: Claude Code
**優先級**: ⭐⭐⭐⭐⭐ 極高（必須在批量生成前修復）

---

## 🔍 問題發現

### 當前狀況

共有 **35 個 zettel 資料夾**，命名格式不一致：

#### 格式 A：`zettel_{short_title}_{date}` （32個） ✅ 較好
```
zettel_Her2012a_20251029
zettel_Zwaan2002_20251029
zettel_Glenberg2002_20251029
...
```
**優點**：
- 可透過 short_title 識別論文
- 不會重複

**缺點**：
- ❌ 缺少 paper_id（無法直接映射到知識庫）
- ❌ 缺少 domain（無法分類）

---

#### 格式 B：`zettel_{domain}_{date}` （3個） ❌ 嚴重問題
```
zettel_Research_20251029
zettel_Research_20251103
zettel_Research_20251104  ← 今天測試生成
zettel_Linguistics_20251029
```
**嚴重問題**：
- ❌ 完全無法識別是哪篇論文
- ❌ 缺少 paper_id 和 short_title
- ❌ 同一天同領域會衝突
- ❌ 批量生成 64 篇時會大量衝突

---

### 預期格式（根據執行計畫）

```
zettel_{paper_id}_{short_title}_{domain}_{date}
```

**範例**:
```
zettel_1_Taxonomy2007_Research_20251104
zettel_2_AllassoniereT2021_Linguistics_20251104
zettel_64_Guest2025_Research_20251104
```

**優點**:
- ✅ paper_id：直接映射到知識庫
- ✅ short_title：快速識別內容
- ✅ domain：領域分類
- ✅ date：時間追蹤
- ✅ 絕對不會衝突

---

## 🛠️ 根本原因分析

### 程式碼位置：`make_slides.py` 第 354-362 行

```python
# 當前錯誤邏輯
if args.output:
    output_dir = Path(args.output)
elif args.pdf:
    pdf_stem = Path(args.pdf).stem
    output_dir = Path(f"output/zettelkasten_notes/zettel_{pdf_stem}_{date_str}")
else:
    # ← 問題：從知識庫生成時只用 domain + date
    output_dir = Path(f"output/zettelkasten_notes/zettel_{args.domain}_{date_str}")
```

### 可用資訊（第 213-238 行已讀取）

當 `args.from_kb` 存在時，程式已經有：
- `paper['title']` - 完整標題
- `paper['authors']` - 作者列表
- `paper['year']` - 年份
- `args.from_kb` - **paper_id**（但未使用！）

---

## 📊 影響評估

### 立即影響

1. **批量生成風險** ⚠️
   - 即將批量生成 64 篇論文
   - 如果不修復，將產生 64 個 `zettel_Research_20251104` 資料夾（衝突！）
   - Windows 會自動加 `(1)`、`(2)` 等後綴，但會破壞資料庫映射

2. **知識庫品質下降** ⚠️
   - 無法追蹤 zettel 卡片對應的論文
   - `zettel_cards` 表中的 `paper_id` 欄位無法正確設置
   - Relation_Finder 無法建立論文-卡片關聯

3. **已存在的問題資料夾**
   - `zettel_Research_20251029` - 無法確定是哪篇論文
   - `zettel_Research_20251103` - 無法確定是哪篇論文
   - `zettel_Research_20251104` - 剛測試生成（Paper ID 1）
   - `zettel_Linguistics_20251029` - 無法確定是哪篇論文

---

## ✅ 修復方案

### 方案 A：完整修復（推薦） ⭐

#### Step 1: 修改 make_slides.py（15-20分鐘）

**位置**：第 354-369 行

```python
# 新邏輯
if args.output:
    output_dir = Path(args.output)
elif args.from_kb:
    # 從知識庫：使用 paper_id + short_title + domain + date
    short_title = _generate_short_title(paper['title'], paper.get('authors', []), paper.get('year'))
    output_dir = Path(f"output/zettelkasten_notes/zettel_{args.from_kb}_{short_title}_{args.domain}_{date_str}")
elif args.pdf:
    # 從PDF：保持原樣
    pdf_stem = Path(args.pdf).stem
    output_dir = Path(f"output/zettelkasten_notes/zettel_{pdf_stem}_{date_str}")
else:
    # 回退：使用 domain（僅作備用）
    output_dir = Path(f"output/zettelkasten_notes/zettel_{args.domain}_{date_str}")
```

**新增輔助函數**：
```python
def _generate_short_title(title: str, authors: list, year: int) -> str:
    """
    生成簡短標題用於資料夾命名

    邏輯：
    - 如果標題包含作者姓氏+年份格式（如 "Her2012a"），直接使用
    - 否則嘗試從作者和年份生成（FirstAuthor{year}）
    - 否則使用標題前15個字元（去除特殊字元）

    範例：
    - "Taxonomy of..." + ["Her", "Wu"] + 2007 → "Her2007"
    - "Deep Learning" + [] + 2024 → "DeepLearning"
    """
    # 實作邏輯（見下方詳細程式碼）
```

---

#### Step 2: 處理已存在的問題資料夾（10-15分鐘）

**選項 2A：查詢並重新命名（推薦）**

```bash
# 查詢資料庫找出對應的 paper_id
python << 'EOF'
import sqlite3
from pathlib import Path
from datetime import datetime

conn = sqlite3.connect("knowledge_base/index.db")
cursor = conn.cursor()

# 需要修復的資料夾
problem_folders = [
    ("zettel_Research_20251029", "20251029"),
    ("zettel_Research_20251103", "20251103"),
    ("zettel_Research_20251104", "20251104"),  # 已知是 Paper 1
    ("zettel_Linguistics_20251029", "20251029")
]

# 根據 zettel_cards 表找出 paper_id
for folder, date_str in problem_folders:
    cursor.execute("""
        SELECT DISTINCT paper_id
        FROM zettel_cards
        WHERE file_path LIKE ?
    """, (f"%{folder}%",))

    result = cursor.fetchone()
    if result:
        paper_id = result[0]
        # 查詢論文資訊
        cursor.execute("SELECT title, authors, year FROM papers WHERE id = ?", (paper_id,))
        paper = cursor.fetchone()

        print(f"{folder} → Paper {paper_id}: {paper[0][:50]}")
        # 生成新名稱並重新命名
        # ...
    else:
        print(f"❌ {folder} - 無法找到對應的 paper_id")

conn.close()
EOF
```

**選項 2B：手動處理（備用）**

如果資料庫查詢失敗，手動檢查：
1. 讀取每個資料夾的 `zettel_index.md` 找到論文標題
2. 在知識庫中搜索對應的 paper_id
3. 重新命名資料夾
4. 更新資料庫中的 `file_path` 欄位

---

#### Step 3: 驗證修復（5分鐘）

```bash
# 測試單篇論文生成
python make_slides.py "Test" --from-kb 1 --style zettelkasten --domain Research --detail comprehensive --llm-provider google --model gemini-2.0-flash-exp

# 檢查資料夾名稱是否正確
# 預期：zettel_1_Taxonomy2007_Research_20251104
```

---

### 方案 B：最小修復（不推薦）

僅修改 make_slides.py，不處理舊資料夾。

**缺點**：
- 資料庫中仍有錯誤映射
- Relation_Finder 仍無法正常運作
- 知識庫品質未改善

---

## 📈 價值評估

### 修復的價值

| 項目 | 修復前 | 修復後 | 改進 |
|------|--------|--------|------|
| **命名唯一性** | ❌ 會衝突 | ✅ 絕對唯一 | **質的飛躍** |
| **可追溯性** | ❌ 無法追蹤 | ✅ 完全可追蹤 | **+100%** |
| **資料庫映射** | ❌ 錯誤/缺失 | ✅ 完全正確 | **+100%** |
| **批量生成可行性** | ❌ 不可行 | ✅ 可行 | **關鍵差異** |
| **Relation_Finder 準確性** | ❌ 無法運作 | ✅ 正常運作 | **+100%** |

### 成本評估

| 階段 | 預估時間 | 風險 |
|------|----------|------|
| 修改程式碼 | 15-20 分鐘 | 低 |
| 處理舊資料夾 | 10-15 分鐘 | 中（需小心資料庫更新） |
| 測試驗證 | 5-10 分鐘 | 低 |
| **總計** | **30-45 分鐘** | **中** |

---

## 🎯 建議行動

### 優先級順序

1. **⭐⭐⭐⭐⭐ 立即執行**（今天上午，批量生成前）
   - 修改 make_slides.py 命名邏輯
   - 驗證修復有效

2. **⭐⭐⭐⭐ 高優先級**（批量生成前或同時）
   - 處理 4 個問題資料夾
   - 確保資料庫映射正確

3. **⭐⭐⭐ 中優先級**（批量生成後）
   - 檢查所有 32 個格式 A 資料夾
   - 考慮是否統一加上 paper_id 前綴

---

## 🔄 後續影響

### 對 Phase 2.3 的影響

- ✅ **必須完成才能批量生成**
- ✅ 修復時間（30-45分鐘）遠少於重新生成時間（8-12小時）
- ✅ 避免批量生成後需要手動修正 64 個資料夾

### 對 Phase 2.4-2.7 的影響

- ✅ Zettel 概念提取能正確映射到論文
- ✅ Relation_Finder v2 能建立正確的論文-卡片關聯
- ✅ 知識庫品質大幅提升

---

## 📝 實作細節

### `_generate_short_title()` 函數實作

```python
import re

def _generate_short_title(title: str, authors: list, year: int) -> str:
    """
    生成簡短標題用於資料夾命名

    優先順序：
    1. 如果標題已包含 AuthorYYYY 格式（如 "Her2012a"），直接使用
    2. 從第一作者姓氏 + 年份生成（如 "Her2007"）
    3. 使用標題前15字元（去除特殊字元）
    """
    # 檢查標題是否已包含 AuthorYYYY 格式
    author_year_pattern = r'^[A-Z][a-z]+\d{4}[a-z]?'
    match = re.search(author_year_pattern, title)
    if match:
        return match.group(0)

    # 嘗試從作者和年份生成
    if authors and len(authors) > 0 and year:
        first_author = authors[0].split()[-1]  # 取姓氏
        # 清理特殊字元
        first_author = re.sub(r'[^A-Za-z]', '', first_author)
        if first_author:
            return f"{first_author}{year}"

    # 回退：使用標題前15個字元
    # 移除特殊字元，保留字母數字
    clean_title = re.sub(r'[^A-Za-z0-9]', '', title)
    return clean_title[:15] if clean_title else "Untitled"

# 測試
print(_generate_short_title("Taxonomy of Numeral Classifiers:", ["Her", "Wu"], 2007))
# → "Her2007"

print(_generate_short_title("Deep Learning for NLP", ["Smith", "Jones"], 2024))
# → "Smith2024"

print(_generate_short_title("Her2012a: Classifier Semantics", [], 2012))
# → "Her2012a"
```

---

## ✅ 決策檢查清單

**修復前確認**：
- [ ] 備份知識庫資料庫（`knowledge_base/index.db`）
- [ ] 確認有足夠時間（30-45分鐘）
- [ ] 確認理解修改邏輯

**修復後驗證**：
- [ ] 測試單篇論文生成（`--from-kb 1`）
- [ ] 檢查資料夾名稱格式正確（包含 paper_id）
- [ ] 檢查資料庫 `zettel_cards` 表的 `paper_id` 欄位
- [ ] 檢查問題資料夾已處理或記錄

**批量生成前最後確認**：
- [ ] 所有 zettel 資料夾命名規則一致
- [ ] 資料庫映射完整正確
- [ ] 測試生成無錯誤

---

## 📞 結論

**評估結果**：⭐⭐⭐⭐⭐ **極高優先級，必須立即修復**

**原因**：
1. 批量生成 64 篇論文在即（8-12小時）
2. 不修復會導致大量命名衝突
3. 影響知識庫品質和後續所有 Phase
4. 修復成本低（30-45分鐘）vs 收益高（避免重新生成）

**建議**：
- ✅ 採用**方案 A：完整修復**
- ✅ 在今天上午完成修復
- ✅ 驗證通過後再執行批量生成

---

**報告完成時間**: 2025-11-04 08:45 AM
**下一步**：等待用戶確認後開始實作修復

## 用戶的測試回饋

- cite_key對應失敗是CLI根據知識庫已存的資訊?還是無法根據"My_Library.bib"的資訊回溯原始PDF?
- 部分zettel卡片的Alias有含“”，會導致mermaid顯示錯誤？
- 確認zettel卡片命名的修改方案，目前影響部分zettel_index.md的mermaid結構？
- 部分zettel_index未取得文獻年份
- 重覆的zettel資料夾只要保留最新生成
