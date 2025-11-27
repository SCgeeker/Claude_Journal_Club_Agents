# templates/ - 模板庫

## 結構

```
templates/
├── prompts/    # LLM Prompt 模板
└── styles/     # 學術風格定義
```

## Prompt 模板

### prompts/zettelkasten_template.jinja2
Zettelkasten 卡片生成 Prompt

**變數**:
- `topic` - 論文主題
- `card_count` - 卡片數量
- `detail_level` - 詳細程度
- `paper_content` - 論文內容
- `cite_key` - 引用鍵
- `language` - 語言

### prompts/journal_club_template.jinja2
投影片生成 Prompt

## 學術風格

### styles/academic_styles.yaml

8 種風格：
- `classic_academic` - 經典學術
- `modern_academic` - 現代學術（預設）
- `clinical` - 臨床導向
- `research_methods` - 研究方法
- `literature_review` - 文獻回顧
- `case_analysis` - 案例分析
- `teaching` - 教學導向
- `zettelkasten` - 原子化筆記

5 種詳細程度：
- `minimal` / `brief` / `standard` / `detailed` / `comprehensive`

3 種語言：
- `chinese` / `english` / `bilingual`
