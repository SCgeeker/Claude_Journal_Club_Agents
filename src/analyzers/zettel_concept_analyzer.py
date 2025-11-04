#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zettelkasten 概念分析模組
用於從 Zettelkasten 原子筆記提取概念，建立概念層級網絡
"""

import json
import sqlite3
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class ZettelConcept:
    """Zettel 中的概念"""
    concept: str
    zettel_id: str
    zettel_title: str
    concept_type: str  # 'core_concept' or 'tag'
    card_type: str  # 'concept', 'method', 'finding', 'question'
    domain: str
    paper_id: Optional[int] = None


@dataclass
class ConceptRelation:
    """概念關聯"""
    concept1: str
    concept2: str
    co_occurrence_count: int
    shared_zettel: List[str]
    association_strength: float


class ZettelConceptAnalyzer:
    """Zettelkasten 概念分析主類"""

    def __init__(self, kb_path: str = "knowledge_base"):
        self.kb_path = kb_path
        self.db_path = Path(kb_path) / "index.db"

    # ========== 1. 概念提取 ==========

    def extract_all_concepts(self) -> Dict[str, List[ZettelConcept]]:
        """
        從所有 Zettelkasten 卡片提取概念

        Returns:
            {concept: [ZettelConcept, ...], ...}
        """
        concepts_dict = defaultdict(list)

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                SELECT card_id, zettel_id, title, core_concept, tags, card_type, domain, paper_id
                FROM zettel_cards
                ORDER BY zettel_id
            """)

            for row in cursor.fetchall():
                card_id, zettel_id, title, core_concept, tags, card_type, domain, paper_id = row

                # 提取 core_concept
                if core_concept and core_concept.strip():
                    # 簡單化：取第一句話作為核心概念
                    concept_text = core_concept.split('.')[0].strip()
                    if len(concept_text) > 5:  # 過濾太短的概念
                        concept = ZettelConcept(
                            concept=concept_text[:100],  # 限制長度
                            zettel_id=zettel_id,
                            zettel_title=title or '',
                            concept_type='core_concept',
                            card_type=card_type or 'concept',
                            domain=domain or 'Unknown',
                            paper_id=paper_id
                        )
                        concepts_dict[concept_text[:100]].append(concept)

                # 提取 tags
                if tags:
                    try:
                        if isinstance(tags, str):
                            tag_list = json.loads(tags) if tags.startswith('[') else [tags]
                        else:
                            tag_list = tags if isinstance(tags, list) else [str(tags)]

                        for tag in tag_list:
                            if isinstance(tag, str) and tag.strip() and len(tag) > 2:
                                concept = ZettelConcept(
                                    concept=tag.strip(),
                                    zettel_id=zettel_id,
                                    zettel_title=title or '',
                                    concept_type='tag',
                                    card_type=card_type or 'concept',
                                    domain=domain or 'Unknown',
                                    paper_id=paper_id
                                )
                                concepts_dict[tag.strip()].append(concept)
                    except (json.JSONDecodeError, TypeError):
                        pass

            conn.close()
        except Exception as e:
            print(f"Warning: Error extracting concepts: {e}")

        return dict(concepts_dict)

    # ========== 2. 概念共現分析 ==========

    def find_concept_relations(self, concepts_dict: Dict[str, List[ZettelConcept]],
                               min_co_occurrence: int = 2) -> List[ConceptRelation]:
        """
        分析概念之間的共現關係

        Args:
            concepts_dict: 概念字典
            min_co_occurrence: 最小共現次數

        Returns:
            概念關聯列表
        """
        relations = []
        concept_list = list(concepts_dict.keys())

        for i, concept1 in enumerate(concept_list):
            for concept2 in concept_list[i+1:]:
                # 找出同時出現在哪些 zettel 中
                zettel1 = {z.zettel_id for z in concepts_dict[concept1]}
                zettel2 = {z.zettel_id for z in concepts_dict[concept2]}
                shared_zettel = zettel1 & zettel2

                if len(shared_zettel) >= min_co_occurrence:
                    max_count = max(len(zettel1), len(zettel2))
                    relation = ConceptRelation(
                        concept1=concept1,
                        concept2=concept2,
                        co_occurrence_count=len(shared_zettel),
                        shared_zettel=sorted(list(shared_zettel)),
                        association_strength=len(shared_zettel) / max_count
                    )
                    relations.append(relation)

        # 按共現次數排序
        return sorted(relations, key=lambda x: x.co_occurrence_count, reverse=True)

    # ========== 3. 概念層級構建 ==========

    def build_concept_hierarchy(self, concepts_dict: Dict[str, List[ZettelConcept]]) -> Dict:
        """
        按領域和類型構建概念層級

        Returns:
            {domain: {card_type: [concepts], ...}, ...}
        """
        hierarchy = defaultdict(lambda: defaultdict(list))

        for concept, zettel_concepts in concepts_dict.items():
            for zc in zettel_concepts:
                hierarchy[zc.domain][zc.card_type].append(concept)

        # 去重並計數
        result = {}
        for domain, card_types in hierarchy.items():
            result[domain] = {}
            for card_type, concepts in card_types.items():
                result[domain][card_type] = sorted(list(set(concepts)))

        return result

    # ========== 4. Mermaid 圖表導出 ==========

    def export_concepts_to_mermaid(self, relations: List[ConceptRelation],
                                   max_pairs: int = 50) -> str:
        """導出概念關聯為 Mermaid 圖表"""
        lines = ["```mermaid", "graph TD"]
        seen_concepts = set()

        for relation in relations[:max_pairs]:
            c1_id = f'C{hash(relation.concept1) % 10000}'
            c2_id = f'C{hash(relation.concept2) % 10000}'

            if relation.concept1 not in seen_concepts:
                concept_name = relation.concept1[:35] if len(relation.concept1) > 35 else relation.concept1
                lines.append(f'    {c1_id}["{concept_name}"]')
                seen_concepts.add(relation.concept1)

            if relation.concept2 not in seen_concepts:
                concept_name = relation.concept2[:35] if len(relation.concept2) > 35 else relation.concept2
                lines.append(f'    {c2_id}["{concept_name}"]')
                seen_concepts.add(relation.concept2)

            # 根據共現強度決定邊型
            if relation.association_strength >= 0.5:
                lines.append(f'    {c1_id} -->|{relation.co_occurrence_count}| {c2_id}')
            else:
                lines.append(f'    {c1_id} -.->|{relation.co_occurrence_count}| {c2_id}')

        lines.append("```")
        return "\n".join(lines)

    def export_hierarchy_to_mermaid(self, hierarchy: Dict) -> str:
        """導出概念層級為 Mermaid 圖表"""
        lines = ["```mermaid", "graph TD"]

        for domain, card_types in hierarchy.items():
            domain_id = f'D_{domain.replace(" ", "_")}'
            lines.append(f'    subgraph {domain_id}["{domain}"]')

            for card_type, concepts in card_types.items():
                if concepts:
                    ct_id = f'{domain_id}_{card_type}'
                    lines.append(f'        {ct_id}["{card_type}: {len(concepts)} concepts"]')

            lines.append('    end')

        lines.append("```")
        return "\n".join(lines)

    # ========== 5. 統計報告 ==========

    def generate_report(self, output_dir: str = "output/relations") -> Dict:
        """生成 Zettelkasten 概念分析報告"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*70}")
        print(f"Zettelkasten Concept Analysis")
        print(f"{'='*70}")

        # 1. 提取概念
        print(f"\n[1] Extracting concepts from zettel cards...")
        concepts_dict = self.extract_all_concepts()
        total_concepts = len(concepts_dict)
        total_concept_mentions = sum(len(v) for v in concepts_dict.values())
        print(f"    Found {total_concepts} unique concepts, {total_concept_mentions} total mentions")

        # 保存概念字典
        concepts_data = {
            concept: [asdict(zc) for zc in zettel_concepts]
            for concept, zettel_concepts in concepts_dict.items()
        }
        with open(output_path / "zettel_concepts.json", 'w', encoding='utf-8') as f:
            json.dump(concepts_data, f, ensure_ascii=False, indent=2)

        # 2. 分析概念關係
        print(f"\n[2] Analyzing concept relations...")
        relations = self.find_concept_relations(concepts_dict, min_co_occurrence=1)
        print(f"    Found {len(relations)} concept relations")

        # 導出 Mermaid 圖表
        concept_mermaid = self.export_concepts_to_mermaid(relations)
        with open(output_path / "zettel_concept_network.md", 'w', encoding='utf-8') as f:
            f.write("# Zettelkasten Concept Network\n\n")
            f.write(concept_mermaid)

        # 保存關係數據
        relations_data = [asdict(r) for r in relations]
        with open(output_path / "zettel_concept_relations.json", 'w', encoding='utf-8') as f:
            json.dump(relations_data, f, ensure_ascii=False, indent=2)

        # 3. 構建層級
        print(f"\n[3] Building concept hierarchy...")
        hierarchy = self.build_concept_hierarchy(concepts_dict)
        print(f"    Hierarchy by domain:")
        for domain, card_types in hierarchy.items():
            total_in_domain = sum(len(c) for c in card_types.values())
            print(f"      {domain}: {total_in_domain} concepts")

        # 導出層級圖表
        hierarchy_mermaid = self.export_hierarchy_to_mermaid(hierarchy)
        with open(output_path / "zettel_concept_hierarchy.md", 'w', encoding='utf-8') as f:
            f.write("# Concept Hierarchy by Domain\n\n")
            f.write(hierarchy_mermaid)

        # 保存層級數據
        with open(output_path / "zettel_hierarchy.json", 'w', encoding='utf-8') as f:
            json.dump(hierarchy, f, ensure_ascii=False, indent=2)

        # 4. 統計摘要
        summary = {
            'total_unique_concepts': total_concepts,
            'total_concept_mentions': total_concept_mentions,
            'concept_relations': len(relations),
            'domains': len(hierarchy),
            'domain_distribution': {d: {ct: len(c) for ct, c in card_types.items()}
                                   for d, card_types in hierarchy.items()}
        }

        print(f"\n{'='*70}")
        print(f"Zettel Concept Analysis Summary")
        print(f"{'='*70}")
        print(f"Unique concepts: {summary['total_unique_concepts']}")
        print(f"Total mentions: {summary['total_concept_mentions']}")
        print(f"Concept relations: {summary['concept_relations']}")
        print(f"Domains: {summary['domains']}")
        print(f"\nAll reports saved to: {output_path}")
        print(f"{'='*70}\n")

        return summary


if __name__ == "__main__":
    analyzer = ZettelConceptAnalyzer(kb_path="knowledge_base")
    summary = analyzer.generate_report(output_dir="output/relations")
