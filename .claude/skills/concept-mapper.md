# Concept Mapper Skill

**功能**: Zettelkasten 概念網絡分析與 Obsidian 整合

**使用時機**:
- 需要了解知識庫的概念結構和關聯
- 想要生成 Obsidian 友好的概念地圖
- 需要識別核心概念和知識社群
- 希望獲得智能連結建議

## 快速使用

```bash
# 執行完整分析 + 生成 Obsidian 格式
python kb_manage.py visualize-network --obsidian

# 查看結果
cd output/concept_analysis/obsidian/
# 在 Obsidian 中打開這個目錄
```

## Python API

```python
from src.analyzers.concept_mapper import ConceptMapper

mapper = ConceptMapper()
results = mapper.analyze_all(
    output_dir="output/concept_analysis",
    visualize=True,
    obsidian_mode=True
)
```

## 輸出文件

- `suggested_links.md` - 智能連結建議（信度評分）
- `key_concepts_moc.md` - 核心概念地圖（PageRank Top 20）
- `community_summaries/` - 概念社群摘要
- `concept_network.html` - D3.js 互動視覺化

## 參數調整

**降低建議閾值**（獲得更多建議）:
```bash
python kb_manage.py visualize-network --obsidian --min-confidence 0.3
```

**增加顯示數量**:
```bash
python kb_manage.py visualize-network --obsidian --top-n 100 --moc-top 30
```

## Wiki Links 格式

自動生成錨點格式連結:
```markdown
[[zettel_Abbas-2022_20251104/zettel_index#1. [目標設定理論](zettel_cards/Abbas-2022-001.md)|目標設定理論]]
```

## 詳細文檔

參見: `OBSIDIAN_INTEGRATION_GUIDE.md`
