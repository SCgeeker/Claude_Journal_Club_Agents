#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relation-Finder 關係分析模組
用於發現論文間的語義關係、共同作者網絡和概念共現
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

from src.knowledge_base.kb_manager import KnowledgeBaseManager

# 嘗試相對導入，失敗則使用絕對導入
try:
    from .zettel_concept_analyzer import ZettelConceptAnalyzer
except ImportError:
    from src.analyzers.zettel_concept_analyzer import ZettelConceptAnalyzer


@dataclass
class Citation:
    """論文引用關係"""
    citing_paper_id: int
    cited_paper_id: int
    citing_title: str
    cited_title: str
    similarity_score: float
    confidence: str
    common_concepts: List[str]

    def __repr__(self) -> str:
        return f"Citation({self.citing_paper_id} → {self.cited_paper_id}, {self.similarity_score:.2f})"


@dataclass
class CoAuthorEdge:
    """共同作者邊"""
    author1: str
    author2: str
    collaboration_count: int
    shared_papers: List[int]


@dataclass
class ConceptPair:
    """概念對"""
    concept1: str
    concept2: str
    co_occurrence_count: int
    papers: List[int]
    association_strength: float


class RelationFinder:
    """關係發現主類"""

    def __init__(self, kb_path: str = "knowledge_base", config: Optional[Dict] = None):
        self.kb = KnowledgeBaseManager(kb_root=kb_path)
        self.config = config or self._default_config()
        self.db_path = Path(kb_path) / "index.db"
        self.zettel_analyzer = ZettelConceptAnalyzer(kb_path=kb_path)

    def _default_config(self) -> Dict:
        return {
            'title_similarity_threshold': 0.65,
            'co_author_min_papers': 2,
            'concept_min_frequency': 2,
            'year_range': 5,
        }

    # ========== 0. 安全獲取論文數據 ==========

    def _get_papers_safe(self) -> List[Dict]:
        """從數據庫直接安全地獲取所有論文"""
        papers = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, authors, year, keywords FROM papers ORDER BY id")

            for row in cursor.fetchall():
                paper_id, title, authors, year, keywords = row
                paper = {
                    'id': paper_id,
                    'title': title or '',
                    'authors': authors or '[]',
                    'year': year,
                    'keywords': keywords or '[]',
                }
                papers.append(paper)

            conn.close()
        except Exception as e:
            print(f"Warning: Error reading papers: {e}")
            # 回退到 kb_manager
            try:
                papers = self.kb.list_papers(limit=1000)
            except:
                papers = []

        return papers

    # ========== 1. 標題相似度引用關係 ==========

    def find_citations_by_title_similarity(self, threshold: Optional[float] = None) -> List[Citation]:
        """基於標題相似度推測引用關係"""
        threshold = threshold or self.config['title_similarity_threshold']
        papers = self._get_papers_safe()
        citations = []

        for i, paper1 in enumerate(papers):
            for j, paper2 in enumerate(papers):
                if i >= j:
                    continue

                title1 = paper1.get('title', '').lower()
                title2 = paper2.get('title', '').lower()

                words1 = set(title1.split())
                words2 = set(title2.split())

                if not words1 or not words2:
                    continue

                intersection = len(words1 & words2)
                union = len(words1 | words2)
                similarity = intersection / union if union > 0 else 0

                if similarity >= threshold:
                    citation = Citation(
                        citing_paper_id=paper1['id'],
                        cited_paper_id=paper2['id'],
                        citing_title=paper1.get('title', ''),
                        cited_title=paper2.get('title', ''),
                        similarity_score=similarity,
                        confidence=self._get_confidence_level(similarity),
                        common_concepts=self._extract_common_concepts(paper1, paper2),
                    )
                    citations.append(citation)

        return sorted(citations, key=lambda x: x.similarity_score, reverse=True)

    # ========== 2. 共同作者網絡 ==========

    def find_co_authors(self, min_papers: Optional[int] = None) -> Tuple[Dict, List[CoAuthorEdge]]:
        """構建共同作者網絡"""
        min_papers = min_papers or self.config['co_author_min_papers']
        papers = self._get_papers_safe()

        author_papers = defaultdict(list)
        for paper in papers:
            authors = self._parse_authors(paper)
            for author in authors:
                if author:
                    author_papers[author].append(paper['id'])

        co_author_edges = []
        author_list = list(author_papers.keys())

        for i, author1 in enumerate(author_list):
            for author2 in author_list[i+1:]:
                shared_papers = set(author_papers[author1]) & set(author_papers[author2])
                if len(shared_papers) >= min_papers:
                    edge = CoAuthorEdge(
                        author1=author1,
                        author2=author2,
                        collaboration_count=len(shared_papers),
                        shared_papers=sorted(list(shared_papers)),
                    )
                    co_author_edges.append(edge)

        return dict(author_papers), sorted(co_author_edges,
                                          key=lambda x: x.collaboration_count, reverse=True)

    # ========== 3. 概念共現分析 ==========

    def find_co_occurrence(self, min_frequency: Optional[int] = None,
                          top_k: Optional[int] = None) -> List[ConceptPair]:
        """分析概念共現模式"""
        min_frequency = min_frequency or self.config['concept_min_frequency']
        papers = self._get_papers_safe()

        concept_papers = defaultdict(list)
        for paper in papers:
            concepts = self._extract_concepts(paper)
            for concept in concepts:
                if concept:
                    concept_papers[concept].append(paper['id'])

        concept_list = list(concept_papers.keys())
        concept_pairs = []

        for i, concept1 in enumerate(concept_list):
            for concept2 in concept_list[i+1:]:
                shared_papers = set(concept_papers[concept1]) & set(concept_papers[concept2])
                if len(shared_papers) >= min_frequency:
                    max_count = max(len(concept_papers[concept1]), len(concept_papers[concept2]))
                    pair = ConceptPair(
                        concept1=concept1,
                        concept2=concept2,
                        co_occurrence_count=len(shared_papers),
                        papers=sorted(list(shared_papers)),
                        association_strength=len(shared_papers) / max_count,
                    )
                    concept_pairs.append(pair)

        concept_pairs = sorted(concept_pairs,
                              key=lambda x: x.co_occurrence_count, reverse=True)

        if top_k:
            concept_pairs = concept_pairs[:top_k]

        return concept_pairs

    # ========== 4. Mermaid 導出 ==========

    def export_citations_to_mermaid(self, citations: List[Citation],
                                   max_edges: int = 50) -> str:
        """導出引用關係為 Mermaid 圖表"""
        lines = ["```mermaid", "graph TD"]
        seen_nodes = set()

        for citation in citations[:max_edges]:
            node1_id = f'P{citation.citing_paper_id}'
            node2_id = f'P{citation.cited_paper_id}'

            if node1_id not in seen_nodes:
                title = citation.citing_title[:40] + "..." if len(citation.citing_title) > 40 else citation.citing_title
                lines.append(f'    {node1_id}["{title}"]')
                seen_nodes.add(node1_id)

            if node2_id not in seen_nodes:
                title = citation.cited_title[:40] + "..." if len(citation.cited_title) > 40 else citation.cited_title
                lines.append(f'    {node2_id}["{title}"]')
                seen_nodes.add(node2_id)

            if citation.confidence == 'high':
                lines.append(f'    {node1_id} --> {node2_id}')
            else:
                lines.append(f'    {node1_id} -.-> {node2_id}')

        lines.append("```")
        return "\n".join(lines)

    def export_coauthors_to_mermaid(self, author_papers: Dict, edges: List[CoAuthorEdge],
                                   max_edges: int = 30) -> str:
        """導出共同作者網絡為 Mermaid 圖表"""
        lines = ["```mermaid", "graph TD"]

        author_counts = [(a, len(p)) for a, p in author_papers.items()]
        author_counts = sorted(author_counts, key=lambda x: x[1], reverse=True)[:15]
        author_set = {a[0] for a in author_counts}

        lines.append('    subgraph Authors["共同作者網絡"]')
        for author, count in author_counts:
            author_id = f'A{hash(author) % 10000}'
            lines.append(f'        {author_id}["{author} ({count}篇)"]')
        lines.append('    end')

        for edge in edges[:max_edges]:
            if edge.author1 in author_set and edge.author2 in author_set:
                author1_id = f'A{hash(edge.author1) % 10000}'
                author2_id = f'A{hash(edge.author2) % 10000}'
                lines.append(f'    {author1_id} -->|{edge.collaboration_count}| {author2_id}')

        lines.append("```")
        return "\n".join(lines)

    def export_concepts_to_mermaid(self, concepts: List[ConceptPair],
                                  max_pairs: int = 30) -> str:
        """導出概念共現為 Mermaid 圖表"""
        lines = ["```mermaid", "graph TD"]
        seen_concepts = set()

        for pair in concepts[:max_pairs]:
            c1_id = f'C{hash(pair.concept1) % 10000}'
            c2_id = f'C{hash(pair.concept2) % 10000}'

            if pair.concept1 not in seen_concepts:
                concept_name = pair.concept1[:30] + "..." if len(pair.concept1) > 30 else pair.concept1
                lines.append(f'    {c1_id}["{concept_name}"]')
                seen_concepts.add(pair.concept1)

            if pair.concept2 not in seen_concepts:
                concept_name = pair.concept2[:30] + "..." if len(pair.concept2) > 30 else pair.concept2
                lines.append(f'    {c2_id}["{concept_name}"]')
                seen_concepts.add(pair.concept2)

            if pair.association_strength >= 0.5:
                lines.append(f'    {c1_id} --> {c2_id}')
            else:
                lines.append(f'    {c1_id} -.-> {c2_id}')

        lines.append("```")
        return "\n".join(lines)

    # ========== 5. 輔助方法 ==========

    def _get_confidence_level(self, similarity_score: float) -> str:
        if similarity_score >= 0.80:
            return 'high'
        elif similarity_score >= 0.70:
            return 'medium'
        else:
            return 'low'

    def _extract_common_concepts(self, paper1: Dict, paper2: Dict) -> List[str]:
        concepts1 = set(self._extract_concepts(paper1))
        concepts2 = set(self._extract_concepts(paper2))
        return sorted(list(concepts1 & concepts2))

    def _extract_concepts(self, paper: Dict) -> List[str]:
        keywords = paper.get('keywords', '')

        try:
            if isinstance(keywords, str):
                if not keywords or keywords == '[]':
                    return []
                if keywords.startswith('['):
                    try:
                        kw_list = json.loads(keywords)
                        return [k.strip() for k in kw_list if isinstance(k, str) and k.strip()]
                    except (json.JSONDecodeError, ValueError):
                        pass
                return [k.strip() for k in keywords.split(',') if k.strip()]
            elif isinstance(keywords, list):
                return [k.strip() for k in keywords if isinstance(k, str) and k.strip()]
        except Exception:
            pass

        return []

    def _parse_authors(self, paper: Dict) -> List[str]:
        authors_data = paper.get('authors', '')

        try:
            if isinstance(authors_data, str):
                if not authors_data or authors_data == '[]':
                    return []
                if authors_data.startswith('['):
                    try:
                        author_list = json.loads(authors_data)
                        return [a.strip() for a in author_list if isinstance(a, str) and a.strip()]
                    except (json.JSONDecodeError, ValueError):
                        pass
                authors = authors_data.replace(' and ', ',').split(',')
                return [a.strip() for a in authors if a.strip()]
            elif isinstance(authors_data, list):
                return [a.strip() for a in authors_data if isinstance(a, str) and a.strip()]
        except Exception:
            pass

        return []

    # ========== 6. 統計和報告 ==========

    def generate_report(self, output_dir: str = "output/relations") -> Dict:
        """生成完整的關係分析報告"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        papers = self._get_papers_safe()
        total_papers = len(papers)

        print(f"\n{'='*70}")
        print(f"Relation-Finder - Relationship Analysis")
        print(f"{'='*70}")
        print(f"Total Papers: {total_papers}")

        # 1. Citation Relationship Analysis
        print(f"\n[1] Analyzing title similarity citations...")
        citations = self.find_citations_by_title_similarity()
        print(f"    Found {len(citations)} similar citations")

        citations_mermaid = self.export_citations_to_mermaid(citations)
        with open(output_path / "citations_network.md", 'w', encoding='utf-8') as f:
            f.write("# Paper Citation Network\n\n")
            f.write(citations_mermaid)

        citations_json = [asdict(c) for c in citations]
        with open(output_path / "citations.json", 'w', encoding='utf-8') as f:
            json.dump(citations_json, f, ensure_ascii=False, indent=2)

        # 2. Co-Author Network Analysis
        print(f"\n[2] Analyzing co-author network...")
        author_papers, coauthor_edges = self.find_co_authors()
        total_authors = len(author_papers)
        print(f"    Found {total_authors} authors, {len(coauthor_edges)} co-author pairs")

        coauthor_mermaid = self.export_coauthors_to_mermaid(author_papers, coauthor_edges)
        with open(output_path / "coauthor_network.md", 'w', encoding='utf-8') as f:
            f.write("# Co-Author Network\n\n")
            f.write(coauthor_mermaid)

        coauthor_json = [asdict(e) for e in coauthor_edges]
        with open(output_path / "coauthors.json", 'w', encoding='utf-8') as f:
            json.dump(coauthor_json, f, ensure_ascii=False, indent=2)

        # 3. Paper Concept Co-Occurrence Analysis
        print(f"\n[3] Analyzing paper concept co-occurrence...")
        concept_pairs = self.find_co_occurrence(top_k=30)
        all_concepts = set()
        for pair in concept_pairs:
            all_concepts.add(pair.concept1)
            all_concepts.add(pair.concept2)
        print(f"    Found {len(all_concepts)} concepts, {len(concept_pairs)} co-occurrences")

        concept_mermaid = self.export_concepts_to_mermaid(concept_pairs)
        with open(output_path / "paper_concept_network.md", 'w', encoding='utf-8') as f:
            f.write("# Paper Concept Co-Occurrence Network\n\n")
            f.write(concept_mermaid)

        concept_json = [asdict(p) for p in concept_pairs]
        with open(output_path / "paper_concepts.json", 'w', encoding='utf-8') as f:
            json.dump(concept_json, f, ensure_ascii=False, indent=2)

        # 4. Zettelkasten Concept Analysis (NEW!)
        print(f"\n[4] Analyzing zettelkasten concepts...")
        zettel_summary = self.zettel_analyzer.generate_report(output_dir=output_dir)
        zettel_concepts_total = zettel_summary['total_unique_concepts']
        zettel_relations = zettel_summary['concept_relations']
        print(f"    Found {zettel_concepts_total} zettel concepts, {zettel_relations} relations")

        # 5. Generate Summary Report
        summary = {
            'total_papers': total_papers,
            'total_authors': total_authors,
            'paper_concepts': len(all_concepts),
            'paper_concept_pairs': len(concept_pairs),
            'zettel_concepts': zettel_concepts_total,
            'zettel_concept_relations': zettel_relations,
            'citations': len(citations),
            'coauthors': len(coauthor_edges),
        }

        print(f"\n{'='*70}")
        print(f"Complete Analysis Summary")
        print(f"{'='*70}")
        print(f"Papers: {summary['total_papers']}")
        print(f"Authors: {summary['total_authors']}")
        print(f"Paper concepts: {summary['paper_concepts']}")
        print(f"Zettel concepts: {summary['zettel_concepts']} (UNIQUE)")
        print(f"Zettel concept relations: {summary['zettel_concept_relations']}")
        print(f"Co-author pairs: {summary['coauthors']}")
        print(f"Citations: {summary['citations']}")
        print(f"\nAll reports saved to: {output_path}")
        print(f"{'='*70}\n")

        return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Relation-Finder 關係分析工具")
    parser.add_argument("--kb-path", default="knowledge_base", help="知識庫路徑")
    parser.add_argument("--output", default="output/relations", help="輸出目錄")
    args = parser.parse_args()
    finder = RelationFinder(kb_path=args.kb_path)
    summary = finder.generate_report(output_dir=args.output)
