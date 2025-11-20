#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian Exporter - 將 Concept Mapper 分析結果導出為 Obsidian 友好格式

提供以下功能：
- 建議連結列表 (suggested_links.md)
- 關鍵概念地圖 MOC (key_concepts_moc.md)
- 社群摘要筆記 (community_summaries/)
- 路徑分析筆記 (path_analysis.md)

使用範例:
    from src.analyzers.obsidian_exporter import ObsidianExporter

    exporter = ObsidianExporter(vault_path="path/to/vault")
    exporter.export_all(
        analysis_results={...},
        output_dir="path/to/output"
    )
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

# 導入概念映射器的數據類型
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.analyzers.concept_mapper import (
    Community,
    ConceptPath,
    CentralityScores
)


class ObsidianExporter:
    """Obsidian 導出器

    將 Concept Mapper 的分析結果轉換為 Obsidian 可直接使用的格式
    """

    def __init__(self, kb_path: str = "knowledge_base"):
        """初始化導出器

        參數:
            kb_path: 知識庫路徑（包含 Zettelkasten 卡片）
        """
        self.kb_path = Path(kb_path)
        self.zettel_dir = self.kb_path / "zettelkasten"

        # 建立卡片 ID 到標題的映射
        self.card_map = self._build_card_map()

    def _build_card_map(self) -> Dict[str, Dict[str, str]]:
        """建立卡片 ID 到元數據的映射（包含 zettel_index.md 錨點信息）

        返回:
            Dict[card_id, {
                'title': str,
                'path': str,
                'core_concept': str,
                'zettel_folder': str,
                'index_entry': str,
                'index_number': str
            }]
        """
        card_map = {}

        # 檢查是否使用 output/zettelkasten_notes/ 路徑
        possible_zettel_dirs = [
            self.zettel_dir,
            Path("output/zettelkasten_notes")
        ]

        zettel_dir = None
        for dir_path in possible_zettel_dirs:
            if dir_path.exists():
                zettel_dir = dir_path
                break

        if not zettel_dir:
            print(f"⚠️ Zettelkasten 目錄不存在")
            print(f"   嘗試過的路徑: {', '.join(str(p) for p in possible_zettel_dirs)}")
            return card_map

        print(f"✅ 使用 Zettelkasten 目錄: {zettel_dir}")

        # 掃描所有 Zettelkasten 資料夾
        for zettel_folder in zettel_dir.iterdir():
            if not zettel_folder.is_dir():
                continue

            index_file = zettel_folder / "zettel_index.md"
            if not index_file.exists():
                continue

            # 讀取 index 文件，解析條目
            try:
                index_content = index_file.read_text(encoding='utf-8')
                # 提取每個卡片條目（格式: ### 1. [標題](zettel_cards/ID.md)）
                entry_pattern = r'###\s+(\d+)\.\s+\[([^\]]+)\]\(zettel_cards/([^)]+)\.md\)'
                entries = re.findall(entry_pattern, index_content)

                for entry_num, entry_title, card_id in entries:
                    # 讀取卡片文件獲取完整元數據
                    card_file = zettel_folder / "zettel_cards" / f"{card_id}.md"
                    if card_file.exists():
                        try:
                            card_content = card_file.read_text(encoding='utf-8')

                            # 提取 YAML frontmatter 中的標題
                            title_match = re.search(r'^title:\s*"?([^"\n]+)"?', card_content, re.MULTILINE)
                            title = title_match.group(1).strip() if title_match else entry_title

                            # 提取核心概念
                            core_match = re.search(r'^core_concept:\s*"?([^"\n]+)"?', card_content, re.MULTILINE)
                            core_concept = core_match.group(1).strip() if core_match else ""

                            # 構建相對路徑（從 zettel 資料夾名稱開始，不包含 output/zettelkasten_notes/）
                            # 例如: zettel_Abbas-2022_20251104/zettel_index
                            zettel_folder_name = zettel_folder.name  # 只取資料夾名稱
                            index_path_rel = f"{zettel_folder_name}/zettel_index"
                            card_path_rel = f"{zettel_folder_name}/zettel_cards/{card_id}.md"

                            # 構建 index 條目字符串（用於錨點）
                            index_entry = f"{entry_num}. [{entry_title}](zettel_cards/{card_id}.md)"

                            card_map[card_id] = {
                                'title': title,
                                'path': card_path_rel,
                                'core_concept': core_concept,
                                'zettel_folder': zettel_folder_name,
                                'index_path': index_path_rel,  # 格式: zettel_xxx/zettel_index
                                'index_entry': index_entry,
                                'index_number': entry_num
                            }
                        except Exception as e:
                            print(f"⚠️ 無法讀取卡片 {card_file}: {e}")
            except Exception as e:
                print(f"⚠️ 無法讀取索引 {index_file}: {e}")

        print(f"✅ 建立卡片映射: {len(card_map)} 張卡片")
        return card_map

    def _get_note_title(self, card_id: str) -> str:
        """獲取卡片標題（用於 Wiki Link）

        參數:
            card_id: 卡片 ID

        返回:
            標題字符串（如果找不到則返回 card_id）
        """
        if card_id in self.card_map:
            return self.card_map[card_id]['title']
        return card_id

    def _get_note_path(self, card_id: str) -> str:
        """獲取卡片相對路徑

        參數:
            card_id: 卡片 ID

        返回:
            相對路徑（如果找不到則返回 card_id）
        """
        if card_id in self.card_map:
            return self.card_map[card_id]['path']
        return card_id

    def _format_wiki_link(self, card_id: str, use_alias: bool = True, use_index_anchor: bool = False) -> str:
        """格式化 Wiki Link（使用直接卡片路徑）

        參數:
            card_id: 卡片 ID
            use_alias: 是否使用別名（|title），在表格中應設為 False 避免管道符號問題
            use_index_anchor: 已棄用，保留參數以向後相容

        返回:
            格式化的 Wiki Link 字符串

        範例:
            完整格式（use_alias=True）: [[zettel_Abbas-2022_20251104/zettel_cards/Abbas-2022-001|目標設定理論]]
            簡單格式（use_alias=False）: [[zettel_Abbas-2022_20251104/zettel_cards/Abbas-2022-001]]
            找不到時: [[card_id]]
        """
        if card_id not in self.card_map:
            # 找不到卡片信息，使用簡單格式
            return f"[[{card_id}]]"

        card_info = self.card_map[card_id]
        title = card_info['title']
        card_path = card_info['path']

        # 移除 .md 副檔名（Obsidian Wiki Link 不需要副檔名）
        if card_path.endswith('.md'):
            card_path = card_path[:-3]

        if use_alias:
            # 完整格式：帶別名的連結（適用於正文）
            return f"[[{card_path}|{title}]]"
        else:
            # 簡單格式：不帶別名（適用於表格，避免管道符號衝突）
            return f"[[{card_path}]]"

    def _get_timestamp(self) -> str:
        """獲取當前時間戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def export_suggested_links(
        self,
        relations: List[Dict],
        top_n: int = 50,
        min_confidence: float = 0.4
    ) -> str:
        """生成建議連結的 Markdown 文件

        參數:
            relations: 關係列表
            top_n: 返回 top-n 建議
            min_confidence: 最小信度閾值（默認 0.4，推薦範圍 0.3-0.5）

        返回:
            Markdown 格式的建議連結文檔
        """
        lines = ["# 🔗 建議新增的概念連結\n"]
        lines.append(f"**生成時間**: {self._get_timestamp()}\n")
        lines.append(f"**分析來源**: Concept Mapper (Phase 2.2)\n")
        lines.append(f"**信度閾值**: {min_confidence}\n")
        lines.append("---\n")
        lines.append("基於語義相似度分析，以下連結可能有助於知識整合。\n")
        lines.append("**使用方法**: 複製 Wiki Link 格式 `[[概念名稱]]` 並貼到相應筆記中。\n")

        # 過濾和排序關係
        filtered_relations = [
            rel for rel in relations
            if rel.get('confidence', 0) >= min_confidence  # 修復：使用正確的字段名 'confidence'
        ]

        filtered_relations.sort(
            key=lambda r: r.get('confidence', 0),  # 修復：使用正確的字段名 'confidence'
            reverse=True
        )

        # 保存高信度關係總數（在截取前）
        high_confidence_count = len(filtered_relations)

        # 只取 top-n
        filtered_relations = filtered_relations[:top_n]

        lines.append(f"\n## 📊 統計\n")
        lines.append(f"- 總關係數: {len(relations)}")
        lines.append(f"- 高信度關係 (≥ {min_confidence}): {high_confidence_count}")  # 修復：顯示真實總數
        lines.append(f"- 本文檔顯示: Top {min(top_n, len(filtered_relations))} 建議\n")

        # 按關係類型分組
        relation_types = {}
        for rel in filtered_relations:
            rel_type = rel.get('relation_type', 'unknown')
            if rel_type not in relation_types:
                relation_types[rel_type] = []
            relation_types[rel_type].append(rel)

        # 生成建議
        for rel_type, rels in relation_types.items():
            # 關係類型標題
            type_name = {
                'leads_to': '導向關係 (Leads To)',
                'based_on': '基於關係 (Based On)',
                'related_to': '相關關係 (Related To)',
                'contrasts_with': '對比關係 (Contrasts With)',
                'superclass_of': '上位關係 (Superclass Of)',
                'subclass_of': '下位關係 (Subclass Of)'
            }.get(rel_type, rel_type)

            lines.append(f"\n## {type_name}\n")

            for i, rel in enumerate(rels[:20], 1):  # 每類最多 20 個
                source_id = rel['source']
                target_id = rel['target']
                confidence = rel.get('confidence', 0)
                similarity = rel.get('similarity', 0)

                source_title = self._get_note_title(source_id)
                target_title = self._get_note_title(target_id)
                # 代碼區塊中使用完整格式（帶別名）
                source_link = self._format_wiki_link(source_id, use_alias=True)
                target_link = self._format_wiki_link(target_id, use_alias=True)

                lines.append(f"### {i}. {source_title} → {target_title}\n")
                lines.append(f"- **信度**: {confidence:.2f} (相似度: {similarity:.2f})")
                lines.append(f"- **關係類型**: `{rel_type}`")
                lines.append(f"- **建議操作**:")
                lines.append(f"  ```markdown")
                lines.append(f"  在 {source_link} 中新增: {target_link}")
                lines.append(f"  ```")

                # 如果有核心概念，顯示
                if source_id in self.card_map and self.card_map[source_id]['core_concept']:
                    lines.append(f"- **來源概念**: {self.card_map[source_id]['core_concept'][:80]}")
                if target_id in self.card_map and self.card_map[target_id]['core_concept']:
                    lines.append(f"- **目標概念**: {self.card_map[target_id]['core_concept'][:80]}")

                lines.append("")

        lines.append("\n---\n")
        lines.append("**提示**: 這些建議基於 AI 分析，請根據實際情況判斷是否採納。\n")

        return "\n".join(lines)

    def export_key_concepts_moc(
        self,
        centralities: List[CentralityScores],
        top_n: int = 20
    ) -> str:
        """生成關鍵概念 MOC (Map of Content)

        參數:
            centralities: 中心性分數列表
            top_n: 顯示 top-n 概念

        返回:
            Markdown 格式的 MOC 文檔
        """
        lines = ["# 🗺️ 關鍵概念地圖 (MOC)\n"]
        lines.append(f"**生成時間**: {self._get_timestamp()}\n")
        lines.append(f"**分析來源**: Concept Mapper - PageRank 分析\n")
        lines.append("---\n")
        lines.append("本地圖列出知識庫中最具影響力的核心概念，基於 PageRank 算法識別。\n")

        # 排序
        sorted_centralities = sorted(
            centralities,
            key=lambda c: c.pagerank,
            reverse=True
        )[:top_n]

        lines.append(f"\n## 📊 Top {top_n} 核心概念\n")
        lines.append("| 排名 | 概念 | PageRank | 度中心性 | 介數中心性 |")
        lines.append("|------|------|----------|----------|-----------|")

        for i, cent in enumerate(sorted_centralities, 1):
            card_id = cent.node_id
            # 表格中使用簡單格式（無別名）避免管道符號問題
            wiki_link = self._format_wiki_link(card_id, use_alias=False)

            lines.append(
                f"| {i} | {wiki_link} | {cent.pagerank:.4f} | "
                f"{cent.degree_centrality:.3f} | {cent.betweenness_centrality:.3f} |"
            )

        # 添加說明
        lines.append("\n## 📖 指標說明\n")
        lines.append("- **PageRank**: 概念的整體影響力（值越高越重要）")
        lines.append("- **度中心性**: 與其他概念的連接數（值越高連接越多）")
        lines.append("- **介數中心性**: 作為橋接概念的重要性（值越高越關鍵）\n")

        # 按度中心性分類
        lines.append("\n## 🌟 不同類型的核心概念\n")

        # Hub 節點（高度中心性）
        hubs = sorted(sorted_centralities, key=lambda c: c.degree_centrality, reverse=True)[:5]
        lines.append("### Hub 節點（高度連接）\n")
        lines.append("這些概念與許多其他概念相連，是知識網絡的中心。\n")
        for hub in hubs:
            # 列表項目使用完整格式（帶別名）
            wiki_link = self._format_wiki_link(hub.node_id, use_alias=True)
            lines.append(f"- {wiki_link} (度: {hub.degree_centrality:.3f})")

        # Bridge 節點（高介數中心性）
        bridges = sorted(sorted_centralities, key=lambda c: c.betweenness_centrality, reverse=True)[:5]
        lines.append("\n### Bridge 節點（橋接概念）\n")
        lines.append("這些概念連接不同的知識領域，是跨領域整合的關鍵。\n")
        for bridge in bridges:
            # 列表項目使用完整格式（帶別名）
            wiki_link = self._format_wiki_link(bridge.node_id, use_alias=True)
            lines.append(f"- {wiki_link} (介數: {bridge.betweenness_centrality:.3f})")

        lines.append("\n---\n")
        lines.append("**使用建議**: 將這些核心概念作為學習和整理的起點，優先完善它們的內容。\n")

        return "\n".join(lines)

    def export_community_notes(
        self,
        communities: List[Community],
        max_communities: int = 10
    ) -> Dict[str, str]:
        """為每個社群生成摘要筆記

        參數:
            communities: 社群列表
            max_communities: 最多生成多少個社群筆記

        返回:
            Dict[filename, content]: 文件名到內容的映射
        """
        notes = {}

        # 按社群大小排序
        sorted_communities = sorted(
            communities,
            key=lambda c: c.size,
            reverse=True
        )[:max_communities]

        for comm in sorted_communities:
            # 生成文件名（使用第一個核心概念）
            main_concept = comm.top_concepts[0] if comm.top_concepts else f"社群{comm.community_id}"
            # 清理文件名（移除特殊字符）
            safe_name = re.sub(r'[^\w\s-]', '', main_concept)
            safe_name = re.sub(r'[\s]+', '_', safe_name)
            filename = f"Community_{comm.community_id}_{safe_name}.md"

            # 生成內容
            lines = [f"# 📦 社群 {comm.community_id}: {main_concept}\n"]
            lines.append(f"**生成時間**: {self._get_timestamp()}\n")
            lines.append(f"**分析來源**: Concept Mapper - 社群檢測 (Louvain 算法)\n")
            lines.append("---\n")

            # 社群統計
            lines.append("## 📊 社群統計\n")
            lines.append(f"- **節點數**: {comm.size}")
            lines.append(f"- **密度**: {comm.density:.3f}")
            # 列表項目使用完整格式（帶別名）
            hub_link = self._format_wiki_link(comm.hub_node, use_alias=True)
            lines.append(f"- **中心節點**: {hub_link}\n")

            # 核心概念
            lines.append("## 🔑 核心概念\n")
            for concept in comm.top_concepts[:10]:
                lines.append(f"- {concept}")

            # 所有節點
            lines.append(f"\n## 📝 所有概念 ({comm.size} 個)\n")

            # 按字母順序排列
            sorted_nodes = sorted(comm.nodes, key=lambda nid: self._get_note_title(nid))

            for node_id in sorted_nodes:
                # 列表項目使用完整格式（帶別名）
                wiki_link = self._format_wiki_link(node_id, use_alias=True)
                lines.append(f"- {wiki_link}")

            lines.append("\n---\n")
            lines.append("**說明**: 這個社群中的概念通常討論相同或相關的主題，可以一起學習和整理。\n")

            notes[filename] = "\n".join(lines)

        return notes

    def export_path_analysis(
        self,
        paths: List[ConceptPath],
        top_n: int = 10
    ) -> str:
        """生成路徑分析文檔

        參數:
            paths: 概念路徑列表
            top_n: 顯示 top-n 路徑

        返回:
            Markdown 格式的路徑分析文檔
        """
        lines = ["# 🛤️ 概念推導路徑分析\n"]
        lines.append(f"**生成時間**: {self._get_timestamp()}\n")
        lines.append(f"**分析來源**: Concept Mapper - 路徑分析\n")
        lines.append("---\n")
        lines.append("以下路徑展示概念之間的推導和演化關係。\n")

        if not paths:
            lines.append("\n⚠️ 未找到有影響力的路徑。\n")
            lines.append("這可能是因為：\n")
            lines.append("- 知識庫是一個高度連接的單一社群\n")
            lines.append("- Hub 節點之間直接連接，無需中間路徑\n")
            return "\n".join(lines)

        # 排序路徑（按信度）
        sorted_paths = sorted(
            paths,
            key=lambda p: p.confidence,
            reverse=True
        )[:top_n]

        lines.append(f"\n## 📊 Top {len(sorted_paths)} 有影響力的路徑\n")

        for i, path in enumerate(sorted_paths, 1):
            start_title = self._get_note_title(path.start_node)
            end_title = self._get_note_title(path.end_node)

            lines.append(f"### {i}. {start_title} ➔ {end_title}\n")
            lines.append(f"- **路徑長度**: {path.length}")
            lines.append(f"- **平均信度**: {path.confidence:.2f}\n")
            lines.append("**推導路徑**:\n")
            lines.append("```")

            # 生成路徑可視化
            path_titles = [self._get_note_title(nid) for nid in path.path]
            lines.append(" → ".join(path_titles))
            lines.append("```\n")

            # 詳細節點列表
            lines.append("**節點詳情**:\n")
            for j, node_id in enumerate(path.path, 1):
                # 列表項目使用完整格式（帶別名）
                wiki_link = self._format_wiki_link(node_id, use_alias=True)
                lines.append(f"{j}. {wiki_link}")

            lines.append("")

        lines.append("\n---\n")
        lines.append("**使用建議**: 這些路徑可以幫助理解概念之間的邏輯連接和演化關係。\n")

        return "\n".join(lines)

    def export_all(
        self,
        analysis_results: Dict,
        output_dir: str,
        options: Optional[Dict] = None
    ):
        """導出所有 Obsidian 友好的分析結果

        參數:
            analysis_results: 分析結果字典，包含:
                - relations: List[Dict]
                - centralities: List[CentralityScores]
                - communities: List[Community]
                - paths: List[ConceptPath]
            output_dir: 輸出目錄
            options: 可選配置，包含:
                - suggested_links_top_n: int (默認 50)
                - suggested_links_min_confidence: float (默認 0.4，推薦 0.3-0.5)
                - moc_top_n: int (默認 20)
                - max_communities: int (默認 10)
                - path_top_n: int (默認 10)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 默認選項
        if options is None:
            options = {}

        print("\n" + "="*70)
        print("📤 導出 Obsidian 友好格式")
        print("="*70)

        # 1. 建議連結
        print("\n[1] 生成建議連結...")
        suggested_links = self.export_suggested_links(
            relations=analysis_results.get('relations', []),
            top_n=options.get('suggested_links_top_n', 50),
            min_confidence=options.get('suggested_links_min_confidence', 0.4)
        )
        links_path = output_path / "suggested_links.md"
        links_path.write_text(suggested_links, encoding='utf-8')
        print(f"   ✅ {links_path}")

        # 2. 關鍵概念 MOC
        print("\n[2] 生成關鍵概念地圖...")
        moc = self.export_key_concepts_moc(
            centralities=analysis_results.get('centralities', []),
            top_n=options.get('moc_top_n', 20)
        )
        moc_path = output_path / "key_concepts_moc.md"
        moc_path.write_text(moc, encoding='utf-8')
        print(f"   ✅ {moc_path}")

        # 3. 社群摘要
        print("\n[3] 生成社群摘要筆記...")
        comm_dir = output_path / "community_summaries"
        comm_dir.mkdir(exist_ok=True)

        community_notes = self.export_community_notes(
            communities=analysis_results.get('communities', []),
            max_communities=options.get('max_communities', 10)
        )

        for filename, content in community_notes.items():
            note_path = comm_dir / filename
            note_path.write_text(content, encoding='utf-8')
            print(f"   ✅ {note_path}")

        # 4. 路徑分析
        print("\n[4] 生成路徑分析...")
        path_analysis = self.export_path_analysis(
            paths=analysis_results.get('paths', []),
            top_n=options.get('path_top_n', 10)
        )
        path_path = output_path / "path_analysis.md"
        path_path.write_text(path_analysis, encoding='utf-8')
        print(f"   ✅ {path_path}")

        # 5. 生成索引文件
        print("\n[5] 生成索引文件...")
        index_content = self._generate_index(output_path, analysis_results)
        index_path = output_path / "README.md"
        index_path.write_text(index_content, encoding='utf-8')
        print(f"   ✅ {index_path}")

        print("\n" + "="*70)
        print(f"✅ Obsidian 輸出完成！")
        print(f"   輸出目錄: {output_path}")
        print("="*70 + "\n")

    def _generate_index(self, output_path: Path, analysis_results: Dict) -> str:
        """生成索引文件

        參數:
            output_path: 輸出目錄
            analysis_results: 分析結果

        返回:
            索引文件的 Markdown 內容
        """
        lines = ["# 📊 Concept Mapper 分析結果索引\n"]
        lines.append(f"**生成時間**: {self._get_timestamp()}\n")
        lines.append(f"**知識庫**: {self.kb_path}\n")
        lines.append("---\n")

        lines.append("## 📁 文件列表\n")
        lines.append("### 核心文件\n")
        lines.append("1. **[[suggested_links]]** - 建議新增的概念連結")
        lines.append("   - 基於語義相似度的智能推薦")
        lines.append("   - 包含關係類型和信度評分\n")

        lines.append("2. **[[key_concepts_moc]]** - 關鍵概念地圖")
        lines.append("   - Top 20 核心概念 (基於 PageRank)")
        lines.append("   - Hub 節點和 Bridge 節點分析\n")

        lines.append("3. **[[path_analysis]]** - 概念推導路徑")
        lines.append("   - 有影響力的概念演化路徑")
        lines.append("   - 幫助理解概念間的邏輯關係\n")

        lines.append("### 社群摘要\n")
        lines.append("- 📂 [[community_summaries/]] - 社群檢測結果")

        comm_count = len(analysis_results.get('communities', []))
        lines.append(f"  - 檢測到 {comm_count} 個概念社群")
        lines.append(f"  - 每個社群對應一個摘要筆記\n")

        # 統計信息
        lines.append("## 📊 統計摘要\n")

        network_stats = analysis_results.get('network_statistics', {})
        lines.append(f"- **節點數**: {network_stats.get('node_count', 0)}")
        lines.append(f"- **邊數**: {network_stats.get('edge_count', 0)}")
        lines.append(f"- **平均度**: {network_stats.get('avg_degree', 0):.2f}")
        lines.append(f"- **網絡密度**: {network_stats.get('density', 0):.4f}")
        lines.append(f"- **社群數**: {comm_count}\n")

        # 關係類型分布
        if 'relation_type_counts' in network_stats:
            lines.append("### 關係類型分布\n")
            for rel_type, count in network_stats['relation_type_counts'].items():
                lines.append(f"- `{rel_type}`: {count}")

        lines.append("\n## 🚀 使用指南\n")
        lines.append("1. 從 **key_concepts_moc** 開始，了解核心概念")
        lines.append("2. 查看 **suggested_links**，補充連結到你的筆記")
        lines.append("3. 瀏覽 **community_summaries**，理解知識結構")
        lines.append("4. 探索 **path_analysis**，發現概念演化路徑\n")

        lines.append("---\n")
        lines.append("**工具**: [Concept Mapper](https://github.com/your-repo) Phase 2.2\n")

        return "\n".join(lines)


# 測試代碼
if __name__ == "__main__":
    # 簡單測試
    exporter = ObsidianExporter()
    print(f"✅ ObsidianExporter 初始化完成")
    print(f"   卡片數: {len(exporter.card_map)}")
