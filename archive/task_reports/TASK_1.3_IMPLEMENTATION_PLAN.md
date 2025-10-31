# Task 1.3 實施計畫：整合 Zettelkasten 到知識庫

**文檔版本**: v1.0
**創建日期**: 2025-10-30
**預計完成時間**: 2天（16小時）
**狀態**: 規劃階段 → 實施中
**負責模組**: `src/knowledge_base/kb_manager.py`

---

## 📋 目錄

1. [任務概述](#任務概述)
2. [已完成基礎設施](#已完成基礎設施)
3. [詳細實施步驟](#詳細實施步驟)
4. [數據結構設計](#數據結構設計)
5. [單元測試清單](#單元測試清單)
6. [整合測試計畫](#整合測試計畫)
7. [風險管理](#風險管理)
8. [時間預估](#時間預估)

---

## 任務概述

### 目標
將現有的 660 張 Zettelkasten 原子卡片（33個資料夾）索引到知識庫，實現跨論文概念搜索和知識圖譜構建。

### 成功指標
- ✅ 644 張卡片成功索引到數據庫（>95% 成功率）
- ✅ 卡片與論文正確關聯（>80% 關聯成功率）
- ✅ 跨論文概念搜索可用（如 `kb.search_zettel("mental simulation")`）
- ✅ FTS5 全文搜索效能良好（<500ms 響應時間）
- ✅ CLI 命令完整可用

### 當前狀態總覽

| 組件 | 狀態 | 完成度 |
|------|------|--------|
| 數據表結構 | ✅ 完成 | 100% |
| BibTeX 解析器 | ✅ 完成 | 100% |
| Zotero 掃描器 | ✅ 完成 | 100% |
| Papers 表擴展 | ✅ 完成 | 100% |
| Zettel 數據表 | ✅ 完成 | 100% |
| 卡片解析器 | ❌ 待實作 | 0% |
| 連結解析器 | ❌ 待實作 | 0% |
| 批次索引器 | ❌ 待實作 | 0% |
| 論文關聯邏輯 | ❌ 待實作 | 0% |
| FTS5 搜索 | ❌ 待實作 | 0% |
| CLI 命令 | ❌ 待實作 | 0% |

---

## 已完成基礎設施

### 1. 數據表結構 ✅

**`zettel_cards` 表**（17 欄位）：
```sql
CREATE TABLE zettel_cards (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    zettel_id TEXT NOT NULL UNIQUE,           -- 如 "Linguistics-20251029-001"
    title TEXT NOT NULL,
    content TEXT NOT NULL,                     -- 完整 Markdown 內容
    core_concept TEXT,                         -- 核心概念（原文引用）
    description TEXT,                          -- 說明文字
    card_type TEXT DEFAULT 'concept',          -- concept/method/finding/question
    domain TEXT NOT NULL,                      -- CogSci/Linguistics/AI
    tags TEXT,                                 -- JSON 陣列字串
    paper_id INTEGER,                          -- 關聯論文 ID
    zettel_folder TEXT NOT NULL,               -- 資料夾路徑
    source_info TEXT,                          -- 來源論文信息
    file_path TEXT NOT NULL,                   -- 卡片文件路徑
    ai_notes TEXT,                             -- AI Agent 筆記
    human_notes TEXT,                          -- 人類筆記
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);
```

**`zettel_links` 表**（7 欄位）：
```sql
CREATE TABLE zettel_links (
    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_card_id INTEGER NOT NULL,           -- 來源卡片 ID
    target_zettel_id TEXT NOT NULL,            -- 目標卡片 zettel_id
    relation_type TEXT NOT NULL,               -- 基於/導向/相關/對比/上位/下位
    context TEXT,                              -- 連結上下文
    is_cross_paper BOOLEAN DEFAULT FALSE,      -- 是否跨論文連結
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_card_id) REFERENCES zettel_cards(card_id)
);
```

**`zettel_cards_fts` 全文搜索表**：
```sql
CREATE VIRTUAL TABLE zettel_cards_fts USING fts5(
    zettel_id, title, content, core_concept, description, tags, ai_notes,
    content=zettel_cards, content_rowid=card_id
);
```

### 2. 整合模組 ✅

- **BibTeX 解析器**: `src/integrations/bibtex_parser.py`
  - 已解析 7245 個 BibTeX 條目
  - 元數據完整性：年份 97%，DOI 43.5%，摘要 44.2%

- **Zotero 掃描器**: `src/integrations/zotero_scanner.py`
  - 掃描 583 個 PDF 文件
  - 匹配率 78.2%（456/583）
  - 主要透過 cite_key 匹配（453 個）

### 3. 數據資源 ✅

- **Zettelkasten 卡片**: 33 個資料夾，~660 張卡片
- **BibTeX 文件**: `D:\core\research\Program_verse\+\My Library.bib`
- **PDF 文件**: 583 個 PDF（`D:\core\research\Program_verse\+\pdf`）

---

## 詳細實施步驟

### **階段 1：卡片解析核心** (4-5 小時)

#### Task 1.1: 實作 `parse_zettel_card()` 方法

**功能描述**：解析單張 Zettelkasten Markdown 卡片，提取所有結構化信息。

**輸入**：
```python
file_path: str  # 如 "output/.../zettel_cards/Linguistics-20251029-001.md"
```

**輸出**：
```python
ZettelCard = {
    'zettel_id': 'Linguistics-20251029-001',
    'title': 'Mass Noun (Mass Noun)',
    'content': '<完整 Markdown 內容>',
    'core_concept': '"I use mass noun interchangeably with..."',
    'description': 'Mass Noun（不可數名詞）與 Non-Count Noun...',
    'card_type': 'concept',
    'domain': 'Linguistics',
    'tags': ['Mass Noun', 'Non-Count Noun', 'Common Noun'],
    'source_info': '"Chinese Classifiers and Count Nouns" (2025)',
    'file_path': '<絕對路徑>',
    'ai_notes': '[AI Agent] 這是一個重要的定義...',
    'human_notes': '(TODO) <!-- 請在此處添加... -->',
    'links': [  # 連結信息（供後續處理）
        {
            'relation_type': '導向',
            'target_ids': ['Linguistics-20251029-002', 'Linguistics-20251029-003']
        }
    ]
}
```

**實作細節**：

```python
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional

def parse_zettel_card(file_path: str) -> Optional[Dict]:
    """
    解析單張 Zettelkasten 卡片

    Returns:
        ZettelCard 字典，解析失敗返回 None
    """
    try:
        # 1. 讀取文件（UTF-8）
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 2. 提取 YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not yaml_match:
            raise ValueError(f"無效的 Zettelkasten 格式：{file_path}")

        yaml_content = yaml_match.group(1)
        markdown_content = yaml_match.group(2)

        # 3. 解析 YAML
        metadata = yaml.safe_load(yaml_content)

        # 4. 提取 Markdown 各區塊
        result = {
            'zettel_id': self._normalize_id(metadata.get('id', '')),
            'title': metadata.get('title', '').strip(),
            'content': content,  # 完整內容
            'card_type': metadata.get('type', 'concept'),
            'domain': self._extract_domain_from_id(metadata.get('id', '')),
            'tags': metadata.get('tags', []),
            'source_info': metadata.get('source', ''),
            'file_path': str(Path(file_path).resolve()),
            'created_at': metadata.get('created', None),
        }

        # 5. 提取核心概念（從 Markdown 內容）
        core_match = re.search(r'> \*\*核心\*\*:\s*"(.+?)"', markdown_content, re.DOTALL)
        result['core_concept'] = core_match.group(1).strip() if core_match else None

        # 6. 提取說明文字
        desc_match = re.search(r'## 說明\n(.+?)(?=\n##|\Z)', markdown_content, re.DOTALL)
        result['description'] = desc_match.group(1).strip() if desc_match else None

        # 7. 提取 AI 筆記
        ai_match = re.search(r'\*\*\[AI Agent\]\*\*:\s*(.+?)(?=\n\*\*\[Human\]|\n---|===|\Z)', markdown_content, re.DOTALL)
        result['ai_notes'] = ai_match.group(1).strip() if ai_match else None

        # 8. 提取人類筆記
        human_match = re.search(r'\*\*\[Human\]\*\*:\s*(.+?)(?=\n---|===|\Z)', markdown_content, re.DOTALL)
        result['human_notes'] = human_match.group(1).strip() if human_match else None

        # 9. 提取連結信息（供後續 parse_zettel_links 使用）
        result['links'] = self._extract_links_from_content(markdown_content)

        return result

    except Exception as e:
        self.logger.error(f"解析卡片失敗：{file_path}, 錯誤：{e}")
        return None

def _normalize_id(self, zettel_id: str) -> str:
    """
    正規化 Zettel ID 格式

    修復錯誤格式：
    - CogSci20251028001 → CogSci-20251028-001
    - AI_20251029_005 → AI-20251029-005
    """
    # 移除底線和多餘空白
    zettel_id = zettel_id.replace('_', '-').strip()

    # 正則表達式匹配並重組
    match = re.match(r'^([A-Za-z]+)[-]?(\d{8})[-]?(\d{3})$', zettel_id)
    if match:
        domain, date, num = match.groups()
        return f"{domain}-{date}-{num}"
    else:
        # 無法修復，記錄警告
        self.logger.warning(f"無法正規化 ID：{zettel_id}")
        return zettel_id

def _extract_domain_from_id(self, zettel_id: str) -> str:
    """從 ID 提取領域代碼"""
    match = re.match(r'^([A-Za-z]+)-', zettel_id)
    return match.group(1) if match else 'Unknown'

def _extract_links_from_content(self, markdown: str) -> List[Dict]:
    """
    提取連結網絡區塊的所有連結

    範例輸入：
    ## 連結網絡
    **導向** → [[Linguistics-20251029-002]], [[Linguistics-20251029-003]]
    **基於** → [[Linguistics-20251029-001]]

    返回：
    [
        {'relation_type': '導向', 'target_ids': ['Linguistics-20251029-002', ...]},
        {'relation_type': '基於', 'target_ids': ['Linguistics-20251029-001']}
    ]
    """
    links = []

    # 提取「連結網絡」區塊
    network_match = re.search(r'## 連結網絡\n(.+?)(?=\n##|\Z)', markdown, re.DOTALL)
    if not network_match:
        return links

    network_text = network_match.group(1)

    # 匹配每一行連結
    # 格式：**關係類型** → [[ID1]], [[ID2]]
    link_pattern = r'\*\*(基於|導向|相關|對比|上位|下位)\*\*\s*→\s*(.+?)(?=\n|$)'

    for match in re.finditer(link_pattern, network_text):
        relation_type = match.group(1)
        target_text = match.group(2)

        # 提取所有目標 ID
        target_ids = re.findall(r'\[\[([A-Za-z]+-\d{8}-\d{3})\]\]', target_text)

        if target_ids:
            links.append({
                'relation_type': relation_type,
                'target_ids': target_ids
            })

    return links
```

**單元測試**：見 [單元測試清單](#單元測試清單) - Test Suite 1

---

#### Task 1.2: 實作 `parse_zettel_links()` 方法

**功能描述**：將卡片解析結果中的連結信息插入 `zettel_links` 表。

**輸入**：
```python
card_data: Dict        # parse_zettel_card() 的輸出
source_card_id: int    # 已插入 zettel_cards 的 card_id
```

**輸出**：
```python
List[int]  # 插入的 link_id 列表
```

**實作細節**：

```python
def parse_zettel_links(
    self,
    card_data: Dict,
    source_card_id: int
) -> List[int]:
    """
    解析並插入卡片連結到數據庫

    Args:
        card_data: 卡片解析結果（包含 'links' 欄位）
        source_card_id: 來源卡片的 card_id

    Returns:
        插入的 link_id 列表
    """
    inserted_ids = []

    if 'links' not in card_data or not card_data['links']:
        return inserted_ids

    cursor = self.conn.cursor()

    for link_group in card_data['links']:
        relation_type = link_group['relation_type']
        target_ids = link_group['target_ids']

        for target_id in target_ids:
            try:
                # 檢查目標卡片是否存在
                cursor.execute(
                    'SELECT card_id, domain FROM zettel_cards WHERE zettel_id = ?',
                    (target_id,)
                )
                target_row = cursor.fetchone()

                # 判斷是否跨論文連結
                is_cross_paper = False
                if target_row:
                    target_domain = target_row[1]
                    source_domain = card_data.get('domain', '')
                    # 簡化判斷：domain 不同視為跨論文（實際可能需要更精確邏輯）
                    is_cross_paper = (target_domain != source_domain)

                # 插入連結
                cursor.execute('''
                    INSERT INTO zettel_links
                    (source_card_id, target_zettel_id, relation_type, is_cross_paper)
                    VALUES (?, ?, ?, ?)
                ''', (source_card_id, target_id, relation_type, is_cross_paper))

                inserted_ids.append(cursor.lastrowid)

            except sqlite3.Error as e:
                self.logger.warning(f"插入連結失敗：{source_card_id} → {target_id}, 錯誤：{e}")
                continue

    self.conn.commit()
    return inserted_ids
```

**單元測試**：見 [單元測試清單](#單元測試清單) - Test Suite 2

---

### **階段 2：批次索引器** (3-4 小時)

#### Task 2.1: 實作 `index_zettelkasten()` 方法

**功能描述**：掃描 Zettelkasten 資料夾，批次索引所有卡片到數據庫。

**輸入**：
```python
zettel_dirs: List[str]  # 資料夾路徑列表，或單個根目錄
update_existing: bool = False  # 是否更新已存在的卡片
link_to_papers: bool = True    # 是否建立論文關聯
progress_callback: callable = None  # 進度回調
```

**輸出**：
```python
IndexResult = {
    'total_folders': int,
    'total_cards': int,
    'success': int,
    'failed': int,
    'skipped': int,  # 已存在且未更新
    'links_created': int,
    'papers_linked': int,
    'errors': List[Dict],
    'processing_time': str
}
```

**實作細節**：

```python
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Callable, Optional
import time

def index_zettelkasten(
    self,
    zettel_dirs: List[str] | str,
    update_existing: bool = False,
    link_to_papers: bool = True,
    progress_callback: Optional[Callable] = None
) -> Dict:
    """
    批次索引 Zettelkasten 卡片

    工作流程：
    1. 掃描所有 zettel_cards/*.md 文件
    2. 解析每張卡片（parse_zettel_card）
    3. 插入或更新 zettel_cards 表
    4. 建立卡片連結（parse_zettel_links）
    5. （可選）關聯論文（link_card_to_paper）
    6. 更新 FTS5 全文搜索索引
    """
    start_time = time.time()

    # 1. 正規化輸入路徑
    if isinstance(zettel_dirs, str):
        zettel_dirs = [zettel_dirs]

    # 2. 掃描所有卡片文件
    all_card_files = []
    for dir_path in zettel_dirs:
        folder = Path(dir_path)
        if not folder.exists():
            self.logger.warning(f"資料夾不存在：{dir_path}")
            continue

        # 掃描 zettel_cards/*.md
        card_files = list(folder.glob('zettel_cards/*.md'))
        all_card_files.extend(card_files)

    total_cards = len(all_card_files)
    self.logger.info(f"發現 {total_cards} 張卡片，開始索引...")

    # 3. 初始化統計
    result = {
        'total_folders': len(zettel_dirs),
        'total_cards': total_cards,
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'links_created': 0,
        'papers_linked': 0,
        'errors': [],
        'processing_time': ''
    }

    # 4. 逐個處理卡片
    cursor = self.conn.cursor()

    for idx, card_file in enumerate(all_card_files, 1):
        try:
            # 進度回調
            if progress_callback:
                progress_callback(idx, total_cards, str(card_file.name))

            # 4.1 解析卡片
            card_data = self.parse_zettel_card(str(card_file))
            if not card_data:
                result['failed'] += 1
                result['errors'].append({
                    'file': str(card_file),
                    'error': '解析失敗'
                })
                continue

            zettel_id = card_data['zettel_id']

            # 4.2 檢查是否已存在
            cursor.execute('SELECT card_id FROM zettel_cards WHERE zettel_id = ?', (zettel_id,))
            existing = cursor.fetchone()

            if existing and not update_existing:
                result['skipped'] += 1
                continue

            # 4.3 插入或更新卡片
            if existing:
                card_id = existing[0]
                self._update_zettel_card(card_id, card_data)
            else:
                card_id = self._insert_zettel_card(card_data)

            # 4.4 建立連結
            link_ids = self.parse_zettel_links(card_data, card_id)
            result['links_created'] += len(link_ids)

            # 4.5（可選）關聯論文
            if link_to_papers:
                paper_id = self._link_card_to_paper(card_data, card_id)
                if paper_id:
                    result['papers_linked'] += 1

            result['success'] += 1

        except Exception as e:
            result['failed'] += 1
            result['errors'].append({
                'file': str(card_file),
                'error': str(e)
            })
            self.logger.error(f"處理卡片失敗：{card_file}, 錯誤：{e}")
            continue

    # 5. 更新 FTS5 索引
    try:
        self._rebuild_zettel_fts_index()
    except Exception as e:
        self.logger.warning(f"FTS5 索引更新失敗：{e}")

    # 6. 生成報告
    elapsed = time.time() - start_time
    result['processing_time'] = f"{elapsed:.2f}s"

    self.logger.info(
        f"索引完成：成功 {result['success']}/{total_cards}, "
        f"失敗 {result['failed']}, 跳過 {result['skipped']}, "
        f"耗時 {result['processing_time']}"
    )

    return result

def _insert_zettel_card(self, card_data: Dict) -> int:
    """插入新卡片"""
    cursor = self.conn.cursor()

    cursor.execute('''
        INSERT INTO zettel_cards (
            zettel_id, title, content, core_concept, description,
            card_type, domain, tags, zettel_folder, source_info,
            file_path, ai_notes, human_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        card_data['zettel_id'],
        card_data['title'],
        card_data['content'],
        card_data.get('core_concept'),
        card_data.get('description'),
        card_data.get('card_type', 'concept'),
        card_data['domain'],
        json.dumps(card_data.get('tags', []), ensure_ascii=False),
        str(Path(card_data['file_path']).parent.parent),  # zettel_folder
        card_data.get('source_info'),
        card_data['file_path'],
        card_data.get('ai_notes'),
        card_data.get('human_notes')
    ))

    self.conn.commit()
    return cursor.lastrowid

def _update_zettel_card(self, card_id: int, card_data: Dict):
    """更新已存在的卡片"""
    cursor = self.conn.cursor()

    cursor.execute('''
        UPDATE zettel_cards SET
            title = ?, content = ?, core_concept = ?, description = ?,
            card_type = ?, tags = ?, source_info = ?, file_path = ?,
            ai_notes = ?, human_notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE card_id = ?
    ''', (
        card_data['title'],
        card_data['content'],
        card_data.get('core_concept'),
        card_data.get('description'),
        card_data.get('card_type', 'concept'),
        json.dumps(card_data.get('tags', []), ensure_ascii=False),
        card_data.get('source_info'),
        card_data['file_path'],
        card_data.get('ai_notes'),
        card_data.get('human_notes'),
        card_id
    ))

    self.conn.commit()

def _rebuild_zettel_fts_index(self):
    """重建 FTS5 全文搜索索引"""
    cursor = self.conn.cursor()

    # 清空 FTS5 表
    cursor.execute('DELETE FROM zettel_cards_fts')

    # 從 zettel_cards 重新插入
    cursor.execute('''
        INSERT INTO zettel_cards_fts (
            rowid, zettel_id, title, content, core_concept, description, tags, ai_notes
        )
        SELECT card_id, zettel_id, title, content, core_concept, description, tags, ai_notes
        FROM zettel_cards
    ''')

    self.conn.commit()
    self.logger.info("FTS5 索引重建完成")
```

**單元測試**：見 [單元測試清單](#單元測試清單) - Test Suite 3

---

### **階段 3：論文關聯** (2-3 小時)

#### Task 3.1: 實作 `_link_card_to_paper()` 方法

**功能描述**：根據卡片的 `source_info` 匹配知識庫論文，建立關聯。

**實作細節**：

```python
def _link_card_to_paper(self, card_data: Dict, card_id: int) -> Optional[int]:
    """
    將卡片關聯到論文

    匹配策略：
    1. 優先使用 Zotero cite_key（從 source_info 提取）
    2. 模糊匹配論文標題
    3. 匹配作者 + 年份組合

    Returns:
        paper_id（成功）或 None（失敗）
    """
    source_info = card_data.get('source_info', '')
    if not source_info:
        return None

    cursor = self.conn.cursor()

    # 策略 1：從 source_info 提取可能的 cite_key
    # 格式範例："Chinese Classifiers and Count Nouns" (2025)
    #            → 查找 zotero_key 或 title 匹配

    # 提取標題和年份
    title_match = re.match(r'"(.+?)"\s*\((\d{4})\)', source_info)
    if title_match:
        title = title_match.group(1)
        year = int(title_match.group(2))

        # 嘗試標題模糊匹配（使用 LIKE）
        cursor.execute('''
            SELECT id FROM papers
            WHERE title LIKE ? AND (year = ? OR year IS NULL)
            LIMIT 1
        ''', (f'%{title}%', year))

        result = cursor.fetchone()
        if result:
            paper_id = result[0]

            # 更新 zettel_cards 的 paper_id
            cursor.execute(
                'UPDATE zettel_cards SET paper_id = ? WHERE card_id = ?',
                (paper_id, card_id)
            )
            self.conn.commit()

            return paper_id

    # 策略 2：使用 zettel_folder 名稱匹配
    # 格式：zettel_Her2012a_20251029 → cite_key: Her2012a
    folder_name = Path(card_data['file_path']).parent.parent.name
    cite_key_match = re.search(r'zettel_([A-Za-z]+\d{4}[a-z]?)_', folder_name)

    if cite_key_match:
        cite_key = cite_key_match.group(1)

        cursor.execute(
            'SELECT id FROM papers WHERE zotero_key = ? LIMIT 1',
            (cite_key,)
        )
        result = cursor.fetchone()
        if result:
            paper_id = result[0]
            cursor.execute(
                'UPDATE zettel_cards SET paper_id = ? WHERE card_id = ?',
                (paper_id, card_id)
            )
            self.conn.commit()
            return paper_id

    # 無法匹配
    self.logger.debug(f"無法匹配論文：{source_info}")
    return None
```

#### Task 3.2: 實作論文元數據增強

**功能描述**：從 BibTeX 補充缺失的論文元數據（年份、DOI、摘要）。

```python
def enrich_paper_metadata_from_bibtex(
    self,
    bib_file: str = None
) -> Dict:
    """
    從 BibTeX 增強論文元數據

    Args:
        bib_file: BibTeX 文件路徑（默認使用配置中的路徑）

    Returns:
        {
            'total_papers': int,
            'enriched': int,
            'fields_updated': {'year': int, 'doi': int, 'abstract': int}
        }
    """
    if bib_file is None:
        bib_file = "D:\\core\\research\\Program_verse\\+\\My Library.bib"

    # 使用已有的 BibTeXParser
    from integrations.bibtex_parser import BibTeXParser
    parser = BibTeXParser(bib_file)
    entries = parser.parse()  # 7245 個條目

    cursor = self.conn.cursor()
    cursor.execute('SELECT id, title, zotero_key, year, doi FROM papers')
    papers = cursor.fetchall()

    result = {
        'total_papers': len(papers),
        'enriched': 0,
        'fields_updated': {'year': 0, 'doi': 0, 'abstract': 0, 'url': 0}
    }

    for paper in papers:
        paper_id, title, zotero_key, current_year, current_doi = paper
        updated = False

        # 查找對應的 BibTeX 條目
        bib_entry = None
        if zotero_key:
            bib_entry = next((e for e in entries if e.get('ID') == zotero_key), None)

        if not bib_entry and title:
            # 模糊匹配標題
            bib_entry = next((e for e in entries if title.lower() in e.get('title', '').lower()), None)

        if bib_entry:
            # 更新缺失欄位
            updates = []
            values = []

            if not current_year and bib_entry.get('year'):
                updates.append('year = ?')
                values.append(int(bib_entry['year']))
                result['fields_updated']['year'] += 1
                updated = True

            if not current_doi and bib_entry.get('doi'):
                updates.append('doi = ?')
                values.append(bib_entry['doi'])
                result['fields_updated']['doi'] += 1
                updated = True

            if bib_entry.get('abstract'):
                updates.append('abstract = ?')  # 假設 papers 表有 abstract 欄位
                values.append(bib_entry['abstract'])
                result['fields_updated']['abstract'] += 1
                updated = True

            if bib_entry.get('url'):
                updates.append('url = ?')
                values.append(bib_entry['url'])
                result['fields_updated']['url'] += 1
                updated = True

            if updated:
                values.append(paper_id)
                cursor.execute(
                    f"UPDATE papers SET {', '.join(updates)} WHERE id = ?",
                    values
                )
                result['enriched'] += 1

    self.conn.commit()
    self.logger.info(
        f"元數據增強完成：{result['enriched']}/{result['total_papers']} 篇論文更新"
    )

    return result
```

**單元測試**：見 [單元測試清單](#單元測試清單) - Test Suite 4

---

### **階段 4：搜索與查詢** (2-3 小時)

#### Task 4.1: 實作 `search_zettel()` 方法

**功能描述**：使用 FTS5 全文搜索查詢 Zettelkasten 卡片。

**輸入**：
```python
query: str                # 搜索關鍵詞（支援 FTS5 語法）
filters: Dict = None      # 過濾條件
limit: int = 20           # 結果數量
include_content: bool = False  # 是否返回完整內容
```

**輸出**：
```python
List[ZettelSearchResult] = [
    {
        'card_id': int,
        'zettel_id': str,
        'title': str,
        'core_concept': str,
        'snippet': str,        # 搜索摘要（高亮）
        'domain': str,
        'tags': List[str],
        'paper_id': int,
        'paper_title': str,    # 關聯論文標題
        'rank': float,         # 相關性分數
        'content': str         # 完整內容（可選）
    }
]
```

**實作細節**：

```python
def search_zettel(
    self,
    query: str,
    filters: Dict = None,
    limit: int = 20,
    include_content: bool = False
) -> List[Dict]:
    """
    全文搜索 Zettelkasten 卡片

    Args:
        query: 搜索詞（FTS5 語法，如 "mental simulation" 或 "mental AND simulation"）
        filters: 過濾條件，可選：
            - domain: str (CogSci/Linguistics)
            - tags: List[str]
            - paper_id: int
            - card_type: str
        limit: 最多返回結果數
        include_content: 是否包含完整 Markdown 內容

    Returns:
        搜索結果列表（按相關性排序）

    範例：
        results = kb.search_zettel("mental simulation", filters={'domain': 'CogSci'})
    """
    filters = filters or {}

    # 1. 構建 FTS5 查詢
    cursor = self.conn.cursor()

    # 基礎 FTS5 查詢
    base_query = '''
        SELECT
            zc.card_id,
            zc.zettel_id,
            zc.title,
            zc.core_concept,
            snippet(zettel_cards_fts, 2, '<mark>', '</mark>', '...', 30) as snippet,
            zc.domain,
            zc.tags,
            zc.paper_id,
            p.title as paper_title,
            zf.rank
    '''

    if include_content:
        base_query += ', zc.content'

    base_query += '''
        FROM zettel_cards_fts zf
        JOIN zettel_cards zc ON zf.rowid = zc.card_id
        LEFT JOIN papers p ON zc.paper_id = p.id
        WHERE zettel_cards_fts MATCH ?
    '''

    # 2. 添加過濾條件
    conditions = []
    params = [query]

    if filters.get('domain'):
        conditions.append('zc.domain = ?')
        params.append(filters['domain'])

    if filters.get('card_type'):
        conditions.append('zc.card_type = ?')
        params.append(filters['card_type'])

    if filters.get('paper_id'):
        conditions.append('zc.paper_id = ?')
        params.append(filters['paper_id'])

    if filters.get('tags'):
        # JSON 陣列查詢（簡化版）
        tag_conditions = ' OR '.join(['zc.tags LIKE ?' for _ in filters['tags']])
        conditions.append(f'({tag_conditions})')
        params.extend([f'%{tag}%' for tag in filters['tags']])

    if conditions:
        base_query += ' AND ' + ' AND '.join(conditions)

    # 3. 排序和限制
    base_query += ' ORDER BY zf.rank LIMIT ?'
    params.append(limit)

    # 4. 執行查詢
    cursor.execute(base_query, params)
    rows = cursor.fetchall()

    # 5. 格式化結果
    results = []
    for row in rows:
        result = {
            'card_id': row[0],
            'zettel_id': row[1],
            'title': row[2],
            'core_concept': row[3],
            'snippet': row[4],
            'domain': row[5],
            'tags': json.loads(row[6]) if row[6] else [],
            'paper_id': row[7],
            'paper_title': row[8],
            'rank': row[9]
        }

        if include_content:
            result['content'] = row[10]

        results.append(result)

    self.logger.info(f"搜索 '{query}' 找到 {len(results)} 個結果")
    return results

def get_related_zettel(
    self,
    zettel_id: str,
    max_depth: int = 2,
    relation_types: List[str] = None
) -> Dict:
    """
    獲取相關卡片網絡（基於連結）

    Args:
        zettel_id: 起始卡片 ID
        max_depth: 最大連結深度（1=直接連結, 2=二階連結）
        relation_types: 限定連結類型（默認全部）

    Returns:
        {
            'center': ZettelCard,
            'related': List[ZettelCard],
            'links': List[ZettelLink],
            'graph': NetworkX Graph（可選）
        }
    """
    # TODO: 實作圖論遍歷演算法（BFS/DFS）
    pass
```

**單元測試**：見 [單元測試清單](#單元測試清單) - Test Suite 5

---

### **階段 5：CLI 工具** (1-2 小時)

#### Task 5.1: 擴展 `kb_manage.py`

新增以下命令：

```bash
# 1. 索引 Zettelkasten
python kb_manage.py index-zettel \
  --zettel-dir "output/zettelkasten_notes" \
  --update-existing \
  --link-papers \
  --report index_report.json

# 2. 同步 Zotero 元數據
python kb_manage.py sync-zotero \
  --bib-file "D:\core\research\Program_verse\+\My Library.bib" \
  --pdf-dir "D:\core\research\Program_verse\+\pdf" \
  --enrich-metadata

# 3. 搜索 Zettelkasten
python kb_manage.py search-zettel \
  --query "mental simulation" \
  --domain CogSci \
  --limit 10 \
  --format table

# 4. 生成概念網絡圖
python kb_manage.py concept-network \
  --zettel-id "CogSci-20251029-001" \
  --depth 2 \
  --output concept_network.html
```

**實作範例**（kb_manage.py 片段）：

```python
import argparse
from src.knowledge_base import KnowledgeBaseManager

def cmd_index_zettel(args):
    """索引 Zettelkasten 命令"""
    kb = KnowledgeBaseManager()

    # 進度回調
    def progress(current, total, filename):
        print(f"\r[{current}/{total}] 處理中: {filename}", end='', flush=True)

    result = kb.index_zettelkasten(
        zettel_dirs=args.zettel_dir,
        update_existing=args.update_existing,
        link_to_papers=args.link_papers,
        progress_callback=progress if not args.quiet else None
    )

    print(f"\n\n✅ 索引完成!")
    print(f"   成功: {result['success']}/{result['total_cards']}")
    print(f"   失敗: {result['failed']}")
    print(f"   跳過: {result['skipped']}")
    print(f"   連結: {result['links_created']}")
    print(f"   論文關聯: {result['papers_linked']}")
    print(f"   耗時: {result['processing_time']}")

    if args.report:
        import json
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"   報告: {args.report}")

def cmd_search_zettel(args):
    """搜索 Zettelkasten 命令"""
    kb = KnowledgeBaseManager()

    filters = {}
    if args.domain:
        filters['domain'] = args.domain
    if args.tags:
        filters['tags'] = args.tags.split(',')

    results = kb.search_zettel(
        query=args.query,
        filters=filters,
        limit=args.limit
    )

    if args.format == 'json':
        import json
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        # 表格輸出
        from tabulate import tabulate
        table = [
            [r['zettel_id'], r['title'][:50], r['domain'], r['paper_title'][:30] if r['paper_title'] else '-']
            for r in results
        ]
        print(tabulate(table, headers=['ID', '標題', '領域', '論文'], tablefmt='grid'))

# 主程式
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='知識庫管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # index-zettel 子命令
    parser_index = subparsers.add_parser('index-zettel', help='索引 Zettelkasten 卡片')
    parser_index.add_argument('--zettel-dir', required=True, help='Zettelkasten 根目錄')
    parser_index.add_argument('--update-existing', action='store_true', help='更新已存在的卡片')
    parser_index.add_argument('--link-papers', action='store_true', default=True, help='建立論文關聯')
    parser_index.add_argument('--report', help='輸出報告路徑 (JSON)')
    parser_index.add_argument('--quiet', action='store_true', help='靜默模式')
    parser_index.set_defaults(func=cmd_index_zettel)

    # search-zettel 子命令
    parser_search = subparsers.add_parser('search-zettel', help='搜索 Zettelkasten')
    parser_search.add_argument('--query', required=True, help='搜索關鍵詞')
    parser_search.add_argument('--domain', help='限定領域 (CogSci/Linguistics)')
    parser_search.add_argument('--tags', help='標籤過濾（逗號分隔）')
    parser_search.add_argument('--limit', type=int, default=20, help='結果數量')
    parser_search.add_argument('--format', choices=['table', 'json'], default='table', help='輸出格式')
    parser_search.set_defaults(func=cmd_search_zettel)

    # ... 其他子命令

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
```

---

## 數據結構設計

### 核心類別定義

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class ZettelCard:
    """Zettelkasten 卡片數據類"""
    card_id: Optional[int] = None
    zettel_id: str = ''
    title: str = ''
    content: str = ''
    core_concept: Optional[str] = None
    description: Optional[str] = None
    card_type: str = 'concept'
    domain: str = 'Unknown'
    tags: List[str] = None
    paper_id: Optional[int] = None
    zettel_folder: str = ''
    source_info: str = ''
    file_path: str = ''
    ai_notes: Optional[str] = None
    human_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict:
        """轉為字典（用於 JSON 序列化）"""
        return {k: v for k, v in self.__dict__.items() if v is not None}

@dataclass
class ZettelLink:
    """Zettelkasten 連結數據類"""
    link_id: Optional[int] = None
    source_card_id: int = 0
    target_zettel_id: str = ''
    relation_type: str = ''  # 基於/導向/相關/對比/上位/下位
    context: Optional[str] = None
    is_cross_paper: bool = False
    created_at: Optional[datetime] = None

@dataclass
class IndexResult:
    """索引結果數據類"""
    total_folders: int = 0
    total_cards: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0
    links_created: int = 0
    papers_linked: int = 0
    errors: List[Dict] = None
    processing_time: str = ''

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_report(self) -> str:
        """生成可讀報告"""
        report = f"""
📊 Zettelkasten 索引報告
========================

統計:
  - 資料夾數: {self.total_folders}
  - 總卡片數: {self.total_cards}
  - 成功: {self.success}
  - 失敗: {self.failed}
  - 跳過: {self.skipped}
  - 連結建立: {self.links_created}
  - 論文關聯: {self.papers_linked}
  - 處理時間: {self.processing_time}

成功率: {self.success / self.total_cards * 100:.1f}%
"""

        if self.errors:
            report += f"\n錯誤列表 ({len(self.errors)}):\n"
            for err in self.errors[:10]:  # 只顯示前10個
                report += f"  - {err['file']}: {err['error']}\n"

        return report
```

---

## 單元測試清單

### Test Suite 1: `parse_zettel_card()` 測試

**測試文件**: `tests/test_zettel_parser.py`

```python
import unittest
from pathlib import Path
from src.knowledge_base import KnowledgeBaseManager

class TestZettelCardParser(unittest.TestCase):
    """測試 Zettelkasten 卡片解析"""

    @classmethod
    def setUpClass(cls):
        cls.kb = KnowledgeBaseManager()
        cls.test_card_path = "output/zettelkasten_notes/zettel_Linguistics_20251029/zettel_cards/Linguistics-20251029-001.md"

    def test_parse_valid_card(self):
        """測試解析有效卡片"""
        result = self.kb.parse_zettel_card(self.test_card_path)

        self.assertIsNotNone(result)
        self.assertEqual(result['zettel_id'], 'Linguistics-20251029-001')
        self.assertEqual(result['title'], 'Mass Noun (Mass Noun)')
        self.assertEqual(result['domain'], 'Linguistics')
        self.assertEqual(result['card_type'], 'concept')
        self.assertIn('Mass Noun', result['tags'])
        self.assertIsNotNone(result['core_concept'])
        self.assertIn('mass noun interchangeably', result['core_concept'])

    def test_parse_invalid_path(self):
        """測試解析不存在的文件"""
        result = self.kb.parse_zettel_card("nonexistent.md")
        self.assertIsNone(result)

    def test_normalize_id(self):
        """測試 ID 正規化"""
        # 正確格式
        self.assertEqual(
            self.kb._normalize_id('Linguistics-20251029-001'),
            'Linguistics-20251029-001'
        )

        # 錯誤格式（需修復）
        self.assertEqual(
            self.kb._normalize_id('CogSci20251028001'),
            'CogSci-20251028-001'
        )

        self.assertEqual(
            self.kb._normalize_id('AI_20251030_005'),
            'AI-20251030-005'
        )

    def test_extract_links(self):
        """測試連結提取"""
        markdown = """
## 連結網絡

**導向** → [[Linguistics-20251029-002]], [[Linguistics-20251029-003]]

**基於** → [[Linguistics-20251029-001]]
"""
        links = self.kb._extract_links_from_content(markdown)

        self.assertEqual(len(links), 2)
        self.assertEqual(links[0]['relation_type'], '導向')
        self.assertEqual(len(links[0]['target_ids']), 2)
        self.assertEqual(links[1]['relation_type'], '基於')

    def test_extract_core_concept(self):
        """測試核心概念提取"""
        markdown = '''
> **核心**: "I use mass noun interchangeably with non-count noun."

## 說明
這是說明文字。
'''
        # 測試正則表達式
        import re
        match = re.search(r'> \*\*核心\*\*:\s*"(.+?)"', markdown)
        self.assertIsNotNone(match)
        self.assertIn('mass noun', match.group(1))

    def test_extract_ai_notes(self):
        """測試 AI 筆記提取"""
        markdown = '''
**[AI Agent]**: 這是 AI 的批判性思考。

**[Human]**: (TODO) 待補充
'''
        import re
        ai_match = re.search(r'\*\*\[AI Agent\]\*\*:\s*(.+?)(?=\n\*\*\[Human\]|\Z)', markdown, re.DOTALL)
        self.assertIsNotNone(ai_match)
        self.assertIn('批判性思考', ai_match.group(1))
```

### Test Suite 2: `parse_zettel_links()` 測試

```python
class TestZettelLinksParser(unittest.TestCase):
    """測試 Zettelkasten 連結解析"""

    def setUp(self):
        self.kb = KnowledgeBaseManager()
        # 創建測試數據（插入兩張測試卡片）
        self.test_card_1_id = self._insert_test_card('Test-001', 'Test Card 1')
        self.test_card_2_id = self._insert_test_card('Test-002', 'Test Card 2')

    def tearDown(self):
        # 清理測試數據
        self.kb.conn.execute('DELETE FROM zettel_cards WHERE zettel_id LIKE "Test-%"')
        self.kb.conn.execute('DELETE FROM zettel_links WHERE target_zettel_id LIKE "Test-%"')
        self.kb.conn.commit()

    def test_parse_links_basic(self):
        """測試基本連結插入"""
        card_data = {
            'links': [
                {'relation_type': '導向', 'target_ids': ['Test-002']}
            ],
            'domain': 'Test'
        }

        link_ids = self.kb.parse_zettel_links(card_data, self.test_card_1_id)

        self.assertEqual(len(link_ids), 1)

        # 驗證數據庫記錄
        cursor = self.kb.conn.cursor()
        cursor.execute('SELECT * FROM zettel_links WHERE link_id = ?', (link_ids[0],))
        row = cursor.fetchone()

        self.assertEqual(row[1], self.test_card_1_id)  # source_card_id
        self.assertEqual(row[2], 'Test-002')            # target_zettel_id
        self.assertEqual(row[3], '導向')                 # relation_type

    def test_parse_links_multiple_targets(self):
        """測試多個目標連結"""
        card_data = {
            'links': [
                {'relation_type': '相關', 'target_ids': ['Test-002', 'Test-003', 'Test-004']}
            ],
            'domain': 'Test'
        }

        link_ids = self.kb.parse_zettel_links(card_data, self.test_card_1_id)
        self.assertEqual(len(link_ids), 3)

    def test_parse_links_cross_paper(self):
        """測試跨論文連結偵測"""
        # 插入不同 domain 的卡片
        other_domain_id = self._insert_test_card('CogSci-001', 'Other Domain', domain='CogSci')

        card_data = {
            'links': [
                {'relation_type': '對比', 'target_ids': ['CogSci-001']}
            ],
            'domain': 'Linguistics'
        }

        link_ids = self.kb.parse_zettel_links(card_data, self.test_card_1_id)

        # 檢查 is_cross_paper 標記
        cursor = self.kb.conn.cursor()
        cursor.execute('SELECT is_cross_paper FROM zettel_links WHERE link_id = ?', (link_ids[0],))
        is_cross = cursor.fetchone()[0]

        self.assertTrue(is_cross)

    def _insert_test_card(self, zettel_id, title, domain='Test'):
        """輔助方法：插入測試卡片"""
        cursor = self.kb.conn.cursor()
        cursor.execute('''
            INSERT INTO zettel_cards (zettel_id, title, content, domain, file_path, zettel_folder)
            VALUES (?, ?, '', ?, '', '')
        ''', (zettel_id, title, domain))
        self.kb.conn.commit()
        return cursor.lastrowid
```

### Test Suite 3: `index_zettelkasten()` 測試

```python
class TestZettelIndexer(unittest.TestCase):
    """測試批次索引功能"""

    def setUp(self):
        self.kb = KnowledgeBaseManager()
        # 使用真實的測試資料夾（單個資料夾）
        self.test_folder = "output/zettelkasten_notes/zettel_Linguistics_20251029"

    def test_index_single_folder(self):
        """測試索引單個資料夾"""
        result = self.kb.index_zettelkasten(
            zettel_dirs=self.test_folder,
            update_existing=False,
            link_to_papers=False  # 暫時跳過論文關聯
        )

        self.assertGreater(result['total_cards'], 0)
        self.assertGreater(result['success'], 0)
        self.assertLessEqual(result['failed'], 2)  # 容許少量失敗

        # 驗證數據庫
        cursor = self.kb.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM zettel_cards WHERE domain = "Linguistics"')
        count = cursor.fetchone()[0]
        self.assertEqual(count, result['success'])

    def test_index_with_progress_callback(self):
        """測試進度回調"""
        progress_calls = []

        def progress(current, total, filename):
            progress_calls.append((current, total))

        result = self.kb.index_zettelkasten(
            zettel_dirs=self.test_folder,
            progress_callback=progress
        )

        self.assertEqual(len(progress_calls), result['total_cards'])
        self.assertEqual(progress_calls[-1][0], result['total_cards'])  # 最後一次是 total

    def test_index_skip_existing(self):
        """測試跳過已存在卡片"""
        # 第一次索引
        result1 = self.kb.index_zettelkasten(self.test_folder, update_existing=False)

        # 第二次索引（應該全部跳過）
        result2 = self.kb.index_zettelkasten(self.test_folder, update_existing=False)

        self.assertEqual(result2['skipped'], result1['success'])
        self.assertEqual(result2['success'], 0)

    def test_index_update_existing(self):
        """測試更新已存在卡片"""
        # 第一次索引
        result1 = self.kb.index_zettelkasten(self.test_folder, update_existing=False)

        # 第二次索引（更新模式）
        result2 = self.kb.index_zettelkasten(self.test_folder, update_existing=True)

        self.assertEqual(result2['success'], result1['success'])
        self.assertEqual(result2['skipped'], 0)

    def test_fts_index_rebuild(self):
        """測試 FTS5 索引重建"""
        # 索引卡片
        self.kb.index_zettelkasten(self.test_folder)

        # 檢查 FTS5 表
        cursor = self.kb.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM zettel_cards_fts')
        fts_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM zettel_cards')
        cards_count = cursor.fetchone()[0]

        self.assertEqual(fts_count, cards_count)
```

### Test Suite 4: 論文關聯測試

```python
class TestPaperLinking(unittest.TestCase):
    """測試卡片-論文關聯"""

    def setUp(self):
        self.kb = KnowledgeBaseManager()
        # 插入測試論文
        self.test_paper_id = self._insert_test_paper(
            title="Chinese Classifiers and Count Nouns",
            year=2021,
            zotero_key="Her2012a"
        )

    def tearDown(self):
        self.kb.conn.execute('DELETE FROM papers WHERE id = ?', (self.test_paper_id,))
        self.kb.conn.commit()

    def test_link_by_title(self):
        """測試通過標題匹配論文"""
        card_data = {
            'source_info': '"Chinese Classifiers and Count Nouns" (2021)',
            'domain': 'Linguistics'
        }

        # 插入測試卡片
        cursor = self.kb.conn.cursor()
        cursor.execute('''
            INSERT INTO zettel_cards (zettel_id, title, content, domain, file_path, zettel_folder)
            VALUES ('Test-001', 'Test', '', 'Linguistics', '', '')
        ''')
        card_id = cursor.lastrowid
        self.kb.conn.commit()

        # 執行關聯
        paper_id = self.kb._link_card_to_paper(card_data, card_id)

        self.assertEqual(paper_id, self.test_paper_id)

        # 驗證數據庫更新
        cursor.execute('SELECT paper_id FROM zettel_cards WHERE card_id = ?', (card_id,))
        linked_paper = cursor.fetchone()[0]
        self.assertEqual(linked_paper, self.test_paper_id)

        # 清理
        cursor.execute('DELETE FROM zettel_cards WHERE card_id = ?', (card_id,))
        self.kb.conn.commit()

    def test_link_by_cite_key(self):
        """測試通過 cite_key 匹配論文"""
        card_data = {
            'source_info': '"Some Paper" (2020)',
            'file_path': 'output/.../zettel_Her2012a_20251029/zettel_cards/Test-001.md',
            'domain': 'Linguistics'
        }

        # 插入測試卡片
        cursor = self.kb.conn.cursor()
        cursor.execute('''
            INSERT INTO zettel_cards (zettel_id, title, content, domain, file_path, zettel_folder)
            VALUES ('Test-002', 'Test', '', 'Linguistics', ?, '')
        ''', (card_data['file_path'],))
        card_id = cursor.lastrowid
        self.kb.conn.commit()

        # 執行關聯
        paper_id = self.kb._link_card_to_paper(card_data, card_id)

        self.assertEqual(paper_id, self.test_paper_id)

        # 清理
        cursor.execute('DELETE FROM zettel_cards WHERE card_id = ?', (card_id,))
        self.kb.conn.commit()

    def test_metadata_enrichment(self):
        """測試元數據增強"""
        # 創建缺少年份的論文
        cursor = self.kb.conn.cursor()
        cursor.execute('''
            INSERT INTO papers (title, year, zotero_key)
            VALUES ('Test Paper', NULL, 'TestKey2020')
        ''')
        test_id = cursor.lastrowid
        self.kb.conn.commit()

        # 模擬 BibTeX 數據
        # （實際測試需要真實的 BibTeX 文件或 mock）

        # 清理
        cursor.execute('DELETE FROM papers WHERE id = ?', (test_id,))
        self.kb.conn.commit()

    def _insert_test_paper(self, title, year, zotero_key):
        """輔助方法：插入測試論文"""
        cursor = self.kb.conn.cursor()
        cursor.execute('''
            INSERT INTO papers (title, year, zotero_key)
            VALUES (?, ?, ?)
        ''', (title, year, zotero_key))
        self.kb.conn.commit()
        return cursor.lastrowid
```

### Test Suite 5: 搜索功能測試

```python
class TestZettelSearch(unittest.TestCase):
    """測試 Zettelkasten 搜索"""

    @classmethod
    def setUpClass(cls):
        cls.kb = KnowledgeBaseManager()
        # 索引測試數據
        cls.kb.index_zettelkasten("output/zettelkasten_notes/zettel_Linguistics_20251029")

    def test_search_basic(self):
        """測試基本搜索"""
        results = self.kb.search_zettel("mass noun", limit=10)

        self.assertGreater(len(results), 0)
        self.assertIn('zettel_id', results[0])
        self.assertIn('title', results[0])
        self.assertIn('snippet', results[0])

    def test_search_with_domain_filter(self):
        """測試領域過濾"""
        results = self.kb.search_zettel(
            "noun",
            filters={'domain': 'Linguistics'},
            limit=10
        )

        for result in results:
            self.assertEqual(result['domain'], 'Linguistics')

    def test_search_with_tags_filter(self):
        """測試標籤過濾"""
        results = self.kb.search_zettel(
            "noun",
            filters={'tags': ['Mass Noun']},
            limit=10
        )

        for result in results:
            self.assertIn('Mass Noun', result['tags'])

    def test_search_fts_syntax(self):
        """測試 FTS5 語法"""
        # AND 查詢
        results = self.kb.search_zettel("mass AND noun")
        self.assertGreater(len(results), 0)

        # OR 查詢
        results = self.kb.search_zettel("mass OR count")
        self.assertGreater(len(results), 0)

        # 短語查詢
        results = self.kb.search_zettel('"mass noun"')
        self.assertGreater(len(results), 0)

    def test_search_performance(self):
        """測試搜索效能"""
        import time

        start = time.time()
        results = self.kb.search_zettel("noun", limit=100)
        elapsed = time.time() - start

        self.assertLess(elapsed, 0.5)  # 應在 500ms 內完成

    def test_search_ranking(self):
        """測試相關性排序"""
        results = self.kb.search_zettel("mass noun", limit=5)

        # 驗證 rank 遞減（FTS5 的 rank 是負數，越大越相關）
        for i in range(len(results) - 1):
            self.assertGreaterEqual(results[i]['rank'], results[i+1]['rank'])
```

### 測試執行指令

```bash
# 執行所有測試
pytest tests/test_zettel_*.py -v

# 執行特定測試套件
pytest tests/test_zettel_parser.py::TestZettelCardParser -v

# 生成覆蓋率報告
pytest tests/ --cov=src.knowledge_base --cov-report=html --cov-report=term

# 並行測試（加速）
pytest tests/ -n auto
```

---

## 整合測試計畫

### 整合測試 1：小規模端到端測試

**目標**: 驗證完整流程（1個資料夾，~20張卡片）

**步驟**:
1. 清空測試數據庫
2. 索引單個 Zettelkasten 資料夾
3. 驗證所有卡片成功索引
4. 驗證連結正確建立
5. 測試搜索功能
6. 生成測試報告

```python
def integration_test_small_scale():
    """小規模整合測試"""
    kb = KnowledgeBaseManager()

    # 1. 清空測試數據
    kb.conn.execute('DELETE FROM zettel_cards')
    kb.conn.execute('DELETE FROM zettel_links')
    kb.conn.commit()

    # 2. 索引單個資料夾
    result = kb.index_zettelkasten(
        "output/zettelkasten_notes/zettel_Linguistics_20251029",
        link_to_papers=True
    )

    # 3. 驗證統計
    assert result['success'] >= 10, "至少10張卡片成功"
    assert result['failed'] <= 2, "失敗數不超過2"
    assert result['links_created'] > 0, "至少建立一些連結"

    # 4. 驗證數據庫
    cursor = kb.conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM zettel_cards')
    cards_count = cursor.fetchone()[0]
    assert cards_count == result['success']

    # 5. 測試搜索
    results = kb.search_zettel("mass noun")
    assert len(results) > 0, "應該找到結果"

    print("✅ 小規模整合測試通過!")
```

### 整合測試 2：全量索引測試

**目標**: 索引所有33個資料夾，~660張卡片

**步驟**:
1. 備份現有數據庫
2. 執行全量索引
3. 驗證成功率 >95%
4. 驗證 FTS5 索引完整性
5. 效能測試（搜索響應時間）
6. 生成完整報告

```python
def integration_test_full_scale():
    """全量整合測試"""
    import shutil
    from datetime import datetime

    kb = KnowledgeBaseManager()

    # 1. 備份數據庫
    backup_path = f"knowledge_base/index_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy('knowledge_base/index.db', backup_path)
    print(f"數據庫已備份: {backup_path}")

    # 2. 執行全量索引
    result = kb.index_zettelkasten(
        "output/zettelkasten_notes",
        update_existing=True,
        link_to_papers=True
    )

    # 3. 驗證成功率
    success_rate = result['success'] / result['total_cards'] * 100
    assert success_rate >= 95, f"成功率過低: {success_rate:.1f}%"

    # 4. 驗證 FTS5
    cursor = kb.conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM zettel_cards_fts')
    fts_count = cursor.fetchone()[0]
    assert fts_count == result['success'], "FTS5 索引不完整"

    # 5. 效能測試
    import time
    queries = ["mental simulation", "noun", "concept", "embodied cognition"]
    total_time = 0

    for query in queries:
        start = time.time()
        results = kb.search_zettel(query, limit=20)
        elapsed = time.time() - start
        total_time += elapsed
        assert elapsed < 0.5, f"查詢 '{query}' 過慢: {elapsed:.3f}s"

    avg_time = total_time / len(queries)
    print(f"平均搜索時間: {avg_time*1000:.1f}ms")

    # 6. 生成報告
    report = f"""
🎉 全量整合測試完成

📊 索引統計:
  - 總卡片數: {result['total_cards']}
  - 成功: {result['success']} ({success_rate:.1f}%)
  - 失敗: {result['failed']}
  - 連結: {result['links_created']}
  - 論文關聯: {result['papers_linked']}
  - 處理時間: {result['processing_time']}

🔍 搜索效能:
  - 平均響應時間: {avg_time*1000:.1f}ms
  - FTS5 索引: {fts_count} 條記錄

✅ 所有測試通過!
"""

    print(report)

    # 保存報告
    with open('integration_test_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
```

### 整合測試 3：Zotero 同步測試

**目標**: 測試 BibTeX 解析和元數據增強

```python
def integration_test_zotero_sync():
    """Zotero 同步整合測試"""
    kb = KnowledgeBaseManager()

    # 1. 元數據增強
    result = kb.enrich_paper_metadata_from_bibtex(
        "D:\\core\\research\\Program_verse\\+\\My Library.bib"
    )

    # 2. 驗證增強效果
    assert result['enriched'] > 0, "應該至少增強一些論文"

    print(f"""
📚 Zotero 同步測試完成

  - 總論文數: {result['total_papers']}
  - 增強數: {result['enriched']}
  - 年份補充: {result['fields_updated']['year']}
  - DOI 補充: {result['fields_updated']['doi']}
  - 摘要補充: {result['fields_updated']['abstract']}

✅ 測試通過!
""")
```

---

## 風險管理

### 已識別風險

| 風險 | 影響 | 可能性 | 緩解策略 |
|------|------|--------|----------|
| **ID 格式不一致** | 中 | 高 | 實作 `_normalize_id()` 自動修復 |
| **論文匹配失敗** | 低 | 中 | 允許手動指定 paper_id，記錄未匹配清單 |
| **記憶體不足** | 高 | 低 | 使用生成器模式，分批處理 |
| **編碼問題** | 中 | 中 | 統一 UTF-8 編碼，強制指定 `encoding='utf-8'` |
| **FTS5 效能問題** | 中 | 低 | 建立適當索引，定期 VACUUM |
| **連結目標不存在** | 低 | 中 | 容錯處理，記錄警告但不中斷 |
| **YAML 解析錯誤** | 中 | 低 | Try-catch，跳過錯誤卡片並記錄 |

### 回滾計畫

如果出現嚴重問題，執行以下步驟：

```python
def rollback_zettel_index():
    """回滾 Zettelkasten 索引"""
    kb = KnowledgeBaseManager()
    cursor = kb.conn.cursor()

    # 1. 刪除所有 Zettelkasten 數據
    cursor.execute('DELETE FROM zettel_links')
    cursor.execute('DELETE FROM zettel_cards')
    cursor.execute('DELETE FROM zettel_cards_fts')

    # 2. 重置 paper_id（如果需要）
    # cursor.execute('UPDATE papers SET paper_id = NULL')

    kb.conn.commit()
    print("✅ Zettelkasten 數據已清除")
```

---

## 時間預估

### 詳細時間分配

| 階段 | 任務 | 預估時間 | 優先級 |
|------|------|----------|--------|
| **階段 1** | 實作 `parse_zettel_card()` | 2小時 | P0 |
|  | 實作 `parse_zettel_links()` | 1.5小時 | P0 |
|  | 撰寫 Test Suite 1-2 | 1小時 | P0 |
| **階段 2** | 實作 `index_zettelkasten()` | 2.5小時 | P0 |
|  | 實作輔助方法（insert/update/rebuild_fts） | 1小時 | P0 |
|  | 撰寫 Test Suite 3 | 1小時 | P0 |
| **階段 3** | 實作 `_link_card_to_paper()` | 1.5小時 | P1 |
|  | 實作 `enrich_paper_metadata()` | 1小時 | P1 |
|  | 撰寫 Test Suite 4 | 0.5小時 | P1 |
| **階段 4** | 實作 `search_zettel()` | 2小時 | P0 |
|  | 實作 `get_related_zettel()` (可選) | 1.5小時 | P2 |
|  | 撰寫 Test Suite 5 | 1小時 | P0 |
| **階段 5** | 擴展 `kb_manage.py` CLI | 1.5小時 | P1 |
|  | 撰寫文檔和使用範例 | 0.5小時 | P1 |
| **測試** | 執行整合測試 | 1小時 | P0 |
|  | 修復發現的問題 | 1小時 | P0 |
| **總計** | | **19-20小時** | |

### 分階段交付

**Day 1** (8小時):
- ✅ 完成階段 1（卡片解析核心）
- ✅ 完成階段 2（批次索引器）
- ✅ 執行小規模測試

**Day 2** (8小時):
- ✅ 完成階段 3（論文關聯）
- ✅ 完成階段 4（搜索功能）
- ✅ 完成階段 5（CLI 工具）
- ✅ 執行全量整合測試

**Day 3** (預留緩衝時間):
- 修復發現的問題
- 優化效能
- 完善文檔

---

## 成功驗收標準

### 必要條件（Must Have）

- ✅ 至少 95% 的卡片成功索引到數據庫
- ✅ FTS5 搜索可用且響應時間 <500ms
- ✅ 論文關聯成功率 >70%
- ✅ 單元測試覆蓋率 >80%
- ✅ 所有 CLI 命令可正常執行
- ✅ 連結網絡正確建立（可視覺化驗證）

### 期望條件（Should Have）

- ✅ 論文關聯成功率 >80%
- ✅ 搜索響應時間 <300ms
- ✅ 元數據增強功能正常運作
- ✅ 完整的錯誤處理和日誌記錄

### 可選條件（Nice to Have）

- ⭐ 概念網絡圖視覺化（`get_related_zettel()`）
- ⭐ 跨論文概念關聯分析
- ⭐ 知識圖譜導出（GraphML/Mermaid）

---

## 下一步行動

**立即開始實作** - 使用以下命令：

```bash
# 1. 開始實作 parse_zettel_card()
用戶: "開始實作 parse_zettel_card() 方法，按照實施計畫執行"

# 2. 或先執行小規模測試驗證可行性
用戶: "先測試解析單張 Zettelkasten 卡片，驗證 YAML 和 Markdown 提取邏輯"

# 3. 或直接執行完整實作
用戶: "按照實施計畫，完整實作 Task 1.3 所有功能"
```

---

**文檔狀態**: 📝 規劃完成，等待實施
**維護者**: Claude Code Agent
**最後更新**: 2025-10-30
