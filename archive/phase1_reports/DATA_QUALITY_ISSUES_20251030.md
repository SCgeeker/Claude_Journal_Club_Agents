# 數據質量問題追蹤清單
## 2025-10-30

---

## 📋 問題總覽

**發現來源**: auto_link_v2 測試失敗分析（0% 成功率）
**影響範圍**: Zettelkasten 自動關聯功能、知識庫元數據質量
**優先級**: P0 (Critical)

---

## 🔴 Critical Issues (P0)

### Issue #1: Zettel ID 格式不匹配

**問題描述**:
- 算法預期格式: `zettel_Her2012a_20251029`
- 實際數據格式: `Linguistics-20251029-013`
- 無法從 zettel_id 提取 cite_key

**影響**:
- auto_link_v2 的方法 1（O(1) 精確匹配）完全失效
- 644 張卡片無法使用高效匹配算法

**根本原因**:
- Zettelkasten 生成器使用語義化 ID 格式（Domain-Date-Num）
- 算法設計時假設使用 cite_key 格式

**解決方案**:

**方案 A: 修改算法適應現有格式** ⭐ 推薦
```python
# 從卡片的 YAML frontmatter 提取 cite_key
# 而非從 zettel_id 提取
def auto_link_zettel_papers_v3():
    for card in cards:
        # 獲取完整卡片數據（包含 frontmatter）
        card_data = parse_zettel_card(card.file_path)

        # 從 frontmatter 提取 cite_key
        cite_key = card_data['metadata'].get('cite_key')

        if cite_key and cite_key in cite_key_to_paper_id:
            # O(1) 精確匹配
            paper_id = cite_key_to_paper_id[cite_key]
            link_card_to_paper(card.id, paper_id)
```

**優點**:
- 無需修改 644 張現有卡片
- 保留語義化 ID 格式的優點（可讀性高）
- frontmatter 已包含結構化元數據

**缺點**:
- 需要完整讀取卡片內容（性能稍降）
- 需要 Zettelkasten frontmatter 包含 cite_key 欄位

**方案 B: 數據遷移到新格式**
```bash
# 批次重命名 644 張卡片
Linguistics-20251029-013.md → zettel_Ahrens2016_20251029.md
```

**優點**:
- 符合原始算法設計
- 無需修改算法

**缺點**:
- 需要修改 644 個檔案名
- 需要更新所有連結引用
- 風險高、工作量大

**決定**: 採用**方案 A**

**時間估計**: 1 小時
**負責人**: Claude Code
**狀態**: ⏳ 待實作

---

### Issue #2: source_info 格式不符

**問題描述**:
- 算法預期格式: `"Paper Title Here" (2021)`
- 實際數據格式: `"Ahrens2016_Reference_Grammar"`
- 無法提取論文標題進行模糊匹配

**影響**:
- auto_link_v2 的方法 2（標題模糊匹配 fallback）失效
- 40 張有 source_info 的卡片無法匹配

**根本原因**:
- Zettelkasten 生成器使用識別碼而非完整標題
- source_info 格式未標準化

**解決方案**:

**短期**: 修改算法從 source_info 提取識別碼
```python
# 嘗試多種 source_info 格式
def extract_title_from_source(source_info: str) -> str:
    # 格式 1: "Paper Title" (2021)
    match = re.match(r'"([^"]+)"\s*\((\d{4})\)', source_info)
    if match:
        return match.group(1)

    # 格式 2: "Ahrens2016_Reference_Grammar"
    match = re.match(r'"([A-Za-z]+\d{4}[a-z]?)_.*"', source_info)
    if match:
        cite_key = match.group(1)
        # 使用 cite_key 查詢 BibTeX 獲取完整標題
        return get_title_from_cite_key(cite_key)

    return None
```

**中長期**: 修改 Zettelkasten 生成器
```python
# 在 zettel_maker.py 中修改 source_info 生成邏輯
source_info = f'"{paper_title}" ({year}), cite_key: {cite_key}'
```

**影響**: 僅對新生成的卡片生效，舊卡片需手動更新

**時間估計**:
- 短期方案: 2 小時
- 中長期方案: 3 小時（含測試）

**負責人**: Claude Code
**狀態**: ⏳ 待實作

---

### Issue #3: cite_key 覆蓋率過低

**問題描述**:
- 當前狀態: 2/30 論文有 cite_key (6.7%)
- 所需狀態: >25/30 論文有 cite_key (>80%)

**影響**:
- 即使算法正確，cite_key 匹配成功率仍然極低
- 644 張卡片中大部分無法找到匹配目標

**根本原因**:
1. 標題格式不一致（知識庫 vs BibTeX）
2. 某些論文標題為 URL 或無效格式
3. BibTeX 中缺少對應條目

**詳細數據**:
```
知識庫論文標題範例:
- "https://www.sciencedirect.com/science/article/pii/..."  (URL)
- "Journal Pre-proof"  (佔位符)
- "Neural Networks for Language Processing"  (正常)

BibTeX 標題範例:
- "Neural networks for language processing"  (小寫)
- "Neural Networks for NLP"  (縮寫)
- "Language Processing Using Neural Networks"  (順序不同)
```

**解決方案**:

**立即行動** (1-2 天):
1. **手動填充前 10 篇論文**
```sql
-- 優先處理有對應 Zettelkasten 的論文
UPDATE papers
SET cite_key = 'Her2012a'
WHERE title LIKE '%Chinese Classifiers%';

UPDATE papers
SET cite_key = 'Ahrens2016'
WHERE title LIKE '%Reference Grammar%';

-- ... (重複 10 次)
```

**短期行動** (1-2 週):
2. **開發半自動填充工具**
```python
# fill_cite_keys_interactive.py
def suggest_cite_key_matches(paper_title: str, bibtex_entries: List) -> List[Tuple]:
    """
    使用模糊匹配算法提供候選 cite_key
    """
    candidates = []
    for entry in bibtex_entries:
        similarity = SequenceMatcher(None,
                                     paper_title.lower(),
                                     entry.title.lower()).ratio()
        if similarity >= 0.7:
            candidates.append((entry.cite_key, entry.title, similarity))

    return sorted(candidates, key=lambda x: x[2], reverse=True)[:5]

# 互動式確認
for paper in papers_without_cite_key:
    print(f"\n論文標題: {paper.title}")
    candidates = suggest_cite_key_matches(paper.title, bibtex_entries)

    for i, (cite_key, title, sim) in enumerate(candidates, 1):
        print(f"{i}. {cite_key} - {title} ({sim:.2%})")

    choice = input("選擇候選項 (1-5) 或跳過 (s): ")
    if choice.isdigit():
        selected = candidates[int(choice)-1]
        update_paper_cite_key(paper.id, selected[0])
```

**中期行動** (1-2 個月):
3. **整合外部 API**
```python
# API 1: CrossRef (DOI 查詢)
def get_cite_key_from_doi(doi: str) -> str:
    response = requests.get(f"https://api.crossref.org/works/{doi}")
    # 解析響應，構建 cite_key

# API 2: Semantic Scholar (標題查詢)
def get_cite_key_from_title(title: str) -> str:
    response = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={"query": title, "limit": 5}
    )
    # 解析響應，提取作者和年份，構建 cite_key
```

**時間估計**:
- 立即行動: 2 小時
- 短期行動: 8 小時
- 中期行動: 16 小時

**負責人**: Claude Code
**狀態**: ⏳ 待實作

---

## 🟡 High Priority Issues (P1)

### Issue #4: 論文元數據質量低

**來源**: 質量檢查報告（check_quality.py）

**問題描述**:
- 100% 論文缺少年份
- 67% 論文關鍵詞不足（<3 個）
- 53% 論文摘要缺失
- 平均質量評分: 68.2/100

**影響**:
- 搜索準確性降低
- 自動關聯效果不佳
- 使用者體驗差

**根本原因**:
- analyze_paper.py 未充分提取 PDF 元數據
- 缺少外部 API 增強（CrossRef、Semantic Scholar）
- 沒有質量驗證機制

**解決方案**:

**實作 enrich_paper_from_bibtex()**:
```python
def enrich_paper_from_bibtex(paper_id: int, bib_file: str) -> bool:
    """
    從 BibTeX 檔案增強論文元數據
    """
    paper = get_paper_by_id(paper_id)

    # 查找 BibTeX 條目（使用 cite_key 或模糊標題匹配）
    bib_entry = find_bibtex_entry(paper.title, bib_file)

    if bib_entry:
        # 更新缺失欄位
        update_fields = {}

        if not paper.year and bib_entry.year:
            update_fields['year'] = bib_entry.year

        if not paper.abstract and bib_entry.abstract:
            update_fields['abstract'] = bib_entry.abstract

        if not paper.keywords and bib_entry.keywords:
            update_fields['keywords'] = bib_entry.keywords

        if not paper.authors and bib_entry.authors:
            update_fields['authors'] = json.dumps(bib_entry.authors)

        # 批次更新
        update_paper(paper_id, **update_fields)
        return True

    return False
```

**整合到 quality_checker**:
```python
# 在 check_quality.py 中添加 --auto-fix 選項
if auto_fix:
    for report in reports:
        if report.has_critical_issues():
            # 嘗試從 BibTeX 修復
            success = enrich_paper_from_bibtex(report.paper_id, bib_file)
            if success:
                print(f"[FIXED] 論文 {report.paper_id} 已從 BibTeX 增強")
```

**預期成果**:
- 年份填充率: 0% → 90%+
- 關鍵詞完整性: 33% → 80%+
- 摘要完整性: 47% → 70%+
- 平均質量評分: 68.2 → 85+

**時間估計**: 6 小時
**負責人**: Claude Code
**狀態**: ⏳ 待實作

---

### Issue #5: Zettelkasten frontmatter 缺少 cite_key

**問題描述**:
- 644 張卡片的 YAML frontmatter 未包含 cite_key 欄位
- 影響 Issue #1 的方案 A 實施

**影響**:
- 即使修改算法從 frontmatter 提取，也無數據可提取

**解決方案**:

**方案 A: 批次添加 cite_key 到 frontmatter**
```python
# add_cite_key_to_zettel.py
def add_cite_key_to_zettel_frontmatter(zettel_file: str, cite_key: str):
    """
    在 YAML frontmatter 中添加 cite_key 欄位
    """
    with open(zettel_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 分離 frontmatter 和內容
    match = re.match(r'^---\n(.+?)\n---\n(.*)', content, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        markdown_content = match.group(2)

        # 解析 YAML
        metadata = yaml.safe_load(yaml_content)

        # 添加 cite_key
        metadata['cite_key'] = cite_key

        # 重新生成檔案
        new_yaml = yaml.dump(metadata, allow_unicode=True, sort_keys=False)
        new_content = f"---\n{new_yaml}---\n{markdown_content}"

        with open(zettel_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

# 批次處理
for folder in zettel_folders:
    cite_key = extract_cite_key_from_folder_name(folder)  # 如: zettel_Her2012a_20251029
    for card_file in glob(f"{folder}/*.md"):
        add_cite_key_to_zettel_frontmatter(card_file, cite_key)
```

**方案 B: 修改 zettel_maker.py 對新卡片生效**
```python
# 在 zettel_maker.py 的 YAML 生成邏輯中添加
yaml_frontmatter = f"""---
id: {zettel_id}
title: "{title}"
tags: {tags}
source: "{source_info}"
cite_key: {cite_key}  # ← 新增此欄位
created: {date}
type: {card_type}
---
"""
```

**決定**: 兩種方案都實作
- 方案 A: 修復現有 644 張卡片
- 方案 B: 確保新卡片包含 cite_key

**時間估計**:
- 方案 A: 3 小時（含測試和備份）
- 方案 B: 1 小時

**負責人**: Claude Code
**狀態**: ⏳ 待實作

---

## 🟢 Medium Priority Issues (P2)

### Issue #6: 測試覆蓋率不足

**問題描述**:
- 當前覆蓋率: ~40%
- 缺少單元測試（kb_manager, bibtex_parser, zotero_scanner）
- 缺少整合測試
- 缺少 CI/CD 自動化

**影響**:
- 回歸風險高
- 重構困難
- 無法保證代碼品質

**解決方案**:

**建立測試框架**:
```python
# tests/conftest.py
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_kb():
    """臨時知識庫 fixture"""
    temp_dir = tempfile.mkdtemp()
    kb = KnowledgeBaseManager(root_dir=temp_dir)
    yield kb
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_papers():
    """範例論文數據"""
    return [
        {
            'title': 'Neural Networks for NLP',
            'authors': ['John Doe', 'Jane Smith'],
            'year': 2021,
            'cite_key': 'Doe2021'
        },
        # ... 更多範例
    ]
```

**單元測試優先級**:
1. kb_manager.py (核心功能)
2. bibtex_parser.py (數據輸入)
3. quality_checker.py (數據質量)
4. batch_processor.py (批次處理)
5. zettel_maker.py (Zettelkasten 生成)

**時間估計**: 20 小時
**負責人**: Claude Code
**狀態**: ⏳ 待實作

---

## 📊 問題優先級矩陣

| Issue | 影響範圍 | 嚴重程度 | 實作複雜度 | 優先級 | 時間估計 |
|-------|---------|---------|-----------|--------|---------|
| #1 Zettel ID 格式 | 644 張卡片 | 高 | 低 | P0 | 1h |
| #2 source_info 格式 | 40 張卡片 | 中 | 中 | P0 | 5h |
| #3 cite_key 覆蓋率 | 30 篇論文 | 高 | 高 | P0 | 26h |
| #4 元數據質量 | 30 篇論文 | 中 | 中 | P1 | 6h |
| #5 Zettel cite_key | 644 張卡片 | 中 | 中 | P1 | 4h |
| #6 測試覆蓋率 | 全系統 | 低 | 高 | P2 | 20h |

**總計**: 62 小時 (約 8 個工作日)

---

## 🎯 實施路線圖

### Phase 1: 快速修復 (1-2 天)
- [ ] Issue #1: 修改算法從 frontmatter 提取 cite_key (1h)
- [ ] Issue #3.1: 手動填充前 10 篇論文 cite_key (2h)
- [ ] 測試驗證: 預期成功率 20-30% (1h)

### Phase 2: 數據質量提升 (3-5 天)
- [ ] Issue #5: 批次添加 cite_key 到 Zettelkasten frontmatter (3h)
- [ ] Issue #2: 改進 source_info 格式提取 (5h)
- [ ] Issue #3.2: 開發半自動 cite_key 填充工具 (8h)
- [ ] Issue #4: 實作 enrich_paper_from_bibtex (6h)
- [ ] 測試驗證: 預期成功率 60-70% (2h)

### Phase 3: 完善與優化 (1-2 週)
- [ ] Issue #3.3: 整合外部 API (16h)
- [ ] Issue #6: 補充單元測試 (20h)
- [ ] 性能優化和文檔更新 (4h)
- [ ] 測試驗證: 預期成功率 80-90% (2h)

---

## 📝 追蹤日誌

### 2025-10-30
- ✅ 發現並分析 5 個數據質量問題
- ✅ 創建本追蹤文檔
- ✅ 制定 3 階段實施路線圖
- ⏳ 待執行: Phase 1 快速修復

---

**文檔創建時間**: 2025-10-30 21:45
**負責人**: Claude Code
**下次更新**: Phase 1 完成後
