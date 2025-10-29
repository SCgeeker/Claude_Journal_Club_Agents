# Zettelkasten 原子筆記生成指令範例

本文檔記錄基於 2025-10-29 工作流程的實用指令範例，方便日後快速生成 Zettelkasten 原子筆記。

---

## 📚 目錄

1. [基本使用](#基本使用)
2. [批量處理](#批量處理)
3. [進階選項](#進階選項)
4. [知識庫查詢](#知識庫查詢)
5. [輸出驗證](#輸出驗證)
6. [常見問題](#常見問題)

---

## 基本使用

### 1. 單篇論文生成（標準流程）

```bash
python make_slides.py "論文主題_簡短描述" \
  --pdf "D:\core\Research\Program_verse\+\pdf\Author-Year.pdf" \
  --style zettelkasten \
  --domain CogSci \
  --detail detailed \
  --slides 20 \
  --analyze-first \
  --llm-provider google \
  --model gemini-2.0-flash-exp \
  --output "output\zettel_AuthorYear_YYYYMMDD"
```

**參數說明**:
- `"論文主題_簡短描述"`: 簡報主題（會作為檔名的一部分）
- `--pdf`: PDF 來源路徑（完整絕對路徑）
- `--style zettelkasten`: 使用 Zettelkasten 原子筆記風格
- `--domain CogSci`: 領域代碼（`CogSci` 或 `Linguistics`）
- `--detail detailed`: 詳細程度（5-6 點/張，3-4 句/點）
- `--slides 20`: 最大卡片數量（實際會是 18-21 張）
- `--analyze-first`: 先分析 PDF 並加入知識庫，再生成筆記
- `--llm-provider google`: 使用 Google Gemini（速度快、品質高）
- `--model gemini-2.0-flash-exp`: 使用實驗版模型（最新、最快）
- `--output`: 輸出資料夾路徑

### 2. 實際範例：語言學論文

```bash
python make_slides.py "Huang-2003_Classifiers" \
  --pdf "D:\core\Research\Program_verse\+\pdf\Huang-2003.pdf" \
  --style zettelkasten \
  --domain Linguistics \
  --detail detailed \
  --slides 20 \
  --analyze-first \
  --llm-provider google \
  --model gemini-2.0-flash-exp \
  --output "output\zettel_Huang2003_20251029"
```

### 3. 實際範例：認知科學論文

```bash
python make_slides.py "Zwaan-2002_Mental_Simulation" \
  --pdf "D:\core\Research\Program_verse\+\pdf\Zwaan-2002.pdf" \
  --style zettelkasten \
  --domain CogSci \
  --detail detailed \
  --slides 20 \
  --analyze-first \
  --llm-provider google \
  --model gemini-2.0-flash-exp \
  --output "output\zettel_Zwaan2002_20251029"
```

---

## 批量處理

### 方法 1：PowerShell 循環（推薦）

```powershell
# 設定工作目錄
cd "D:\core\Research\claude_lit_workflow"

# 論文清單
$papers = @(
    "Altmann-2019",
    "Bocanegra-2022",
    "DeKoning-2017",
    "Glenberg-2002"
)

# 批量處理
foreach ($paper in $papers) {
    Write-Host "處理: $paper" -ForegroundColor Green
    python make_slides.py "${paper}_Mental_Simulation" `
        --pdf "D:\core\Research\Program_verse\+\pdf\${paper}.pdf" `
        --style zettelkasten `
        --domain CogSci `
        --detail detailed `
        --slides 20 `
        --analyze-first `
        --llm-provider google `
        --model gemini-2.0-flash-exp `
        --output "output\zettel_${paper}_$(Get-Date -Format 'yyyyMMdd')"
}
```

### 方法 2：Bash 循環（Git Bash）

```bash
cd "D:/core/Research/claude_lit_workflow"

# 論文清單（使用實際檔名）
papers=(
    "Altmann-2019"
    "Bocanegra-2022"
    "DeKoning-2017"
)

# 批量處理
for paper in "${papers[@]}"; do
    echo "處理: $paper"
    python make_slides.py "${paper}_MS" \
        --pdf "D:/core/Research/Program_verse/+/pdf/${paper}.pdf" \
        --style zettelkasten \
        --domain CogSci \
        --detail detailed \
        --slides 20 \
        --analyze-first \
        --llm-provider google \
        --model gemini-2.0-flash-exp \
        --output "output/zettel_${paper}_$(date +%Y%m%d)"
done
```

### 方法 3：從 Obsidian 連結筆記提取 PDF 路徑

假設您有一個連結筆記（如 `🔗Topic.md`），可以用以下指令提取所有 PDF 路徑：

```bash
# 提取 PDF 路徑
grep -h "Source pdf" "D:/core/Research/Program_verse/ACT/0️⃣Annotation/"*.md | \
    grep -o '\[Source pdf\]([^)]*)' | \
    sed 's/\[Source pdf\](\(.*\))/\1/' | \
    sort -u

# 如果要過濾特定連結主題的論文
grep -l "conn:.*Mental Simulation" "D:/core/Research/Program_verse/ACT/0️⃣Annotation/"*.md | \
    xargs grep -h "Source pdf" | \
    grep -o '([^)]*.pdf)' | \
    sed 's/[()]//g'
```

---

## 進階選項

### 1. 使用不同 LLM 提供者

**Ollama（本地，完全離線）**:
```bash
python make_slides.py "主題" \
  --pdf "path/to/paper.pdf" \
  --style zettelkasten \
  --domain CogSci \
  --detail detailed \
  --slides 20 \
  --analyze-first \
  --llm-provider ollama \
  --model gemma2:latest
```

**OpenAI（需要 API key）**:
```bash
# 設定環境變數
export OPENAI_API_KEY="your-api-key"

python make_slides.py "主題" \
  --pdf "path/to/paper.pdf" \
  --style zettelkasten \
  --llm-provider openai \
  --model gpt-4 \
  --analyze-first
```

**Anthropic Claude（需要 API key）**:
```bash
# 設定環境變數
export ANTHROPIC_API_KEY="your-api-key"

python make_slides.py "主題" \
  --pdf "path/to/paper.pdf" \
  --style zettelkasten \
  --llm-provider anthropic \
  --model claude-3-opus \
  --analyze-first
```

### 2. 調整詳細程度

```bash
# 極簡（2-3 點/張，1 句話/點）
--detail minimal

# 簡要（3-4 點/張，1-2 句話/點）
--detail brief

# 標準（4-5 點/張，2-3 句話/點）⭐ 默認
--detail standard

# 詳細（5-6 點/張，3-4 句話/點）⭐ 推薦用於 Zettelkasten
--detail detailed

# 完整（6-8 點/張，4-5 句話/點）
--detail comprehensive
```

### 3. 自訂卡片數量

```bash
# 少量卡片（快速瀏覽）
--slides 10

# 標準數量
--slides 15

# 詳細筆記（推薦用於重要論文）⭐
--slides 20

# 超詳細（長篇論文）
--slides 30
```

### 4. 從知識庫已有論文重新生成

```bash
# 先查詢論文 ID
python -c "from src.knowledge_base import KnowledgeBaseManager; \
kb = KnowledgeBaseManager(); \
results = kb.search_papers('mental simulation'); \
print('\n'.join([f'{r[0]}: {r[1]}' for r in results]))"

# 從知識庫 ID 生成（無需重新分析 PDF）
python make_slides.py "重新生成_主題" \
  --from-kb 15 \
  --style zettelkasten \
  --detail detailed \
  --slides 20
```

---

## 知識庫查詢

### 1. 搜索論文

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager()

# 全文搜索
results = kb.search_papers("mental simulation visual", limit=10)
for paper in results:
    print(f"ID: {paper[0]}, 標題: {paper[1]}, 作者: {paper[2]}, 年份: {paper[3]}")

# 依作者搜索
results = kb.search_papers("Zwaan")

# 依關鍵字搜索
results = kb.search_papers("embodied cognition")
```

### 2. 查看知識庫統計

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager()
stats = kb.get_stats()

print(f"論文總數: {stats['total_papers']}")
print(f"主題總數: {stats['total_topics']}")
```

### 3. 查詢特定論文詳情

```python
from src.knowledge_base import KnowledgeBaseManager

kb = KnowledgeBaseManager()

# 透過 ID 獲取論文
paper = kb.get_paper(15)
print(f"標題: {paper['title']}")
print(f"作者: {paper['authors']}")
print(f"年份: {paper['year']}")
print(f"關鍵字: {paper['keywords']}")
print(f"檔案路徑: {paper['file_path']}")
```

---

## 輸出驗證

### 1. 檢查生成的資料夾

```bash
# 列出今日生成的所有 Zettelkasten 資料夾
ls -la "D:\core\Research\claude_lit_workflow\output" | grep "zettel_.*_20251029"

# 計數今日生成的資料夾
ls "D:\core\Research\claude_lit_workflow\output" | grep "zettel_.*_20251029" | wc -l

# 列出所有資料夾名稱
ls "D:\core\Research\claude_lit_workflow\output" | grep "zettel_.*_20251029"
```

### 2. 驗證索引檔完整性

```bash
# 檢查特定論文的索引檔
ls -lh "D:\core\Research\claude_lit_workflow\output\zettel_Zwaan2002_20251029\zettel_index.md"

# 查看檔案行數（確認內容完整）
wc -l "D:\core\Research\claude_lit_workflow\output\zettel_Zwaan2002_20251029\zettel_index.md"

# 查看卡片數量
find "D:\core\Research\claude_lit_workflow\output\zettel_Zwaan2002_20251029\zettel_cards" -name "*.md" | wc -l
```

### 3. 批量驗證所有生成的筆記

```bash
# 檢查所有今日生成的索引檔
for dir in D:/core/Research/claude_lit_workflow/output/zettel_*_20251029; do
    name=$(basename "$dir")
    index="$dir/zettel_index.md"
    if [ -f "$index" ]; then
        lines=$(wc -l < "$index")
        cards=$(find "$dir/zettel_cards" -name "*.md" 2>/dev/null | wc -l)
        echo "$name: $lines 行, $cards 張卡片"
    else
        echo "$name: ❌ 索引檔缺失"
    fi
done
```

### 4. 讀取索引檔元數據

```bash
# 提取論文標題
head -20 "D:\core\Research\claude_lit_workflow\output\zettel_Zwaan2002_20251029\zettel_index.md" | grep "來源論文"

# 提取卡片總數
head -20 "D:\core\Research\claude_lit_workflow\output\zettel_Zwaan2002_20251029\zettel_index.md" | grep "卡片總數"

# 查看前 5 張卡片清單
sed -n '/📚 卡片清單/,/##/p' "D:\core\Research\claude_lit_workflow\output\zettel_Zwaan2002_20251029\zettel_index.md" | head -30
```

---

## 常見問題

### Q1: 如何決定使用哪個領域代碼？

**A**:
- `--domain Linguistics`: 語言學、句法、語義、語用學相關論文
- `--domain CogSci`: 認知科學、心理學、神經科學、具身認知相關論文
- 可自訂領域代碼（會反映在卡片 ID 中，如 `Linguistics-20251029-001`）

### Q2: `--analyze-first` 有什麼作用？

**A**:
- 有：先使用 `analyze_paper.py` 分析 PDF，提取結構化資訊（標題、作者、章節），儲存到知識庫，再從結構化內容生成筆記。**品質最高，推薦使用**。
- 無：直接從 PDF 文字生成筆記，速度較快但品質較低。

### Q3: 為什麼有些論文生成的卡片數超過 20 張？

**A**: `--slides 20` 是建議值，LLM 可能根據內容複雜度生成 18-22 張卡片。如需嚴格控制，可在生成後手動刪減。

### Q4: 如何處理 PDF 路徑包含空格的情況？

**A**: 使用雙引號包裹路徑：
```bash
--pdf "D:\core\Research\Program_verse\+\pdf\Author Name-2024.pdf"
```

### Q5: Google Gemini API 配額用完怎麼辦？

**A**: 切換到其他 LLM 提供者：
```bash
# 使用 Ollama（免費、本地）
--llm-provider ollama --model gemma2:latest

# 或使用 OpenAI（需付費 API key）
--llm-provider openai --model gpt-4
```

### Q6: 如何避免重複生成？

**A**:
1. 使用唯一的 `--output` 資料夾名稱（包含日期和論文名稱）
2. 生成前檢查資料夾是否已存在：
```bash
if [ ! -d "output/zettel_Zwaan2002_20251029" ]; then
    python make_slides.py ...
else
    echo "已存在，跳過"
fi
```

### Q7: 可以更改輸出語言嗎？

**A**: 可以，但 Zettelkasten 風格預設僅支援繁體中文。如需其他語言，修改 `--language` 參數：
```bash
--language english    # 英文
--language bilingual  # 中英雙語
```

### Q8: 生成失敗如何除錯？

**A**:
1. 檢查 PDF 是否存在且可讀取
2. 檢查 LLM 服務是否正常（Ollama 需先啟動，API key 需有效）
3. 查看完整錯誤訊息（移除 `| grep` 過濾器）
4. 測試簡單案例：
```bash
python make_slides.py "測試" --pdf "path/to/simple.pdf" --style zettelkasten --slides 5
```

---

## 快速參考：今日處理的 31 篇論文

### Linguistics 領域（11 篇）

1. Wu-2020
2. Yi-2009
3. Huang-2003
4. Kemmerer-2019
5. ChenYiRu-2020
6. Her-2023
7. Her-2012a
8. Her-2022
9. Ahrens-2016
10. Huang-2015
11. Allassonnière-Tang-2021

### CogSci 領域（20 篇）

1. Altmann-2019
2. Bocanegra-2022
3. DeKoning-2017
4. Glenberg-2002
5. Horchak-2024
6. Jones-2024a
7. Kang-2020
8. Liu-2024b
9. Ostarek-2019a
10. Pecher-2009
11. Potter-1979
12. Rommers-2013
13. Setic-2017
14. Speed-2025
15. vanZuijlen-2024
16. Xu-2022
17. Zeelenberg-2024
18. Zwaan-2002
19. Zwaan-2012
20. Zwaan-2018

---

## 版本記錄

- **v1.0** (2025-10-29): 初始版本，基於今日工作流程整理
- 生成環境: claude_lit_workflow v0.4.0-alpha
- 使用 LLM: Google Gemini 2.0 Flash Experimental
- 總處理論文: 31 篇
- 總生成卡片: 約 620 張（平均每篇 20 張）

---

**最後更新**: 2025-10-29
**作者**: Claude Code Agent
**專案**: claude_lit_workflow
**參考**: [CLAUDE.md](CLAUDE.md), [slide-maker.md](.claude/skills/slide-maker.md)
