#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
關係發現器 (Relation Finder) - Phase 2.1

自動發現論文之間的複雜關係網絡：
- 引用關係 (向量相似度 + 內容分析)
- 主題關聯 (關鍵詞比對 + 向量相似度)
- 作者合作 (作者重疊)
- 相似度關係 (標題/摘要相似度 + 向量相似度)

升級後支持Phase 1.5的向量嵌入系統，提供向量基礎的關係發現。
可視化輸出遵循Zettelkasten的Mermaid格式標準。
"""

import sys
import io
import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import json
from datetime import datetime

# Windows UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


@dataclass
class Citation:
    """引用關係（向量基礎）"""
    citing_paper_id: int
    cited_paper_id: int
    citing_title: str
    cited_title: str
    similarity_score: float  # 向量相似度
    confidence: str  # 'high'/'medium'/'low'
    common_concepts: List[str]
    strength: float = None  # 兼容性

    def __post_init__(self):
        if self.strength is None:
            self.strength = self.similarity_score

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
    """概念共現對"""
    concept1: str
    concept2: str
    co_occurrence_count: int
    papers: List[int]
    association_strength: float


@dataclass
class Relation:
    """論文關係數據結構（舊格式，保持向後兼容）"""
    source_id: int
    target_id: int
    relation_type: str  # 'citation', 'shared_topic', 'author_collaboration', 'similarity'
    strength: float  # 0-1, 關係強度
    metadata: dict  # 額外信息


class RelationFinder:
    """
    關係發現器 (Phase 2.1)

    使用多種策略發現論文間的複雜關係網絡：
    1. 引用分析：基於向量相似度 + 內容分析（作者-年份模式）
    2. 主題關聯：計算關鍵詞交集 + 向量相似度
    3. 作者合作：檢查共同作者
    4. 相似度：計算標題/摘要文本相似度 + 向量相似度
    5. 可視化：Mermaid格式（遵循Zettelkasten標準）

    支持向量嵌入系統進行更精確的相似度計算。
    """

    def __init__(self,
                 db_path: str = "knowledge_base/index.db",
                 embedding_manager = None,
                 config: Dict = None):
        """
        初始化關係發現器

        Args:
            db_path: 知識庫數據庫路徑
            embedding_manager: EmbeddingManager實例（可選，用於向量基礎的分析）
            config: 配置參數字典
        """
        self.db_path = db_path
        self.embedding_manager = embedding_manager
        self.config = config or self._default_config()
        self.papers_cache = None  # 緩存論文數據

    def _default_config(self) -> Dict:
        """默認配置"""
        return {
            'citation_threshold': 0.65,       # 引用關係相似度閾值
            'co_author_min_papers': 2,        # 共同作者最少合作論文數
            'concept_min_frequency': 2,       # 概念最少出現次數
            'use_embeddings': True,           # 使用向量嵌入
            'mermaid_format': 'graph TD',     # Mermaid圖表格式
            'max_nodes_in_graph': 50,         # 圖表最大節點數
            'max_edges_in_graph': 100,        # 圖表最大邊數
        }

    def _get_connection(self) -> sqlite3.Connection:
        """獲取數據庫連接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _load_papers(self, force_reload: bool = False) -> List[Dict]:
        """
        載入所有論文數據（帶緩存）

        Args:
            force_reload: 強制重新載入

        Returns:
            論文列表
        """
        if self.papers_cache is not None and not force_reload:
            return self.papers_cache

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, authors, year, keywords, abstract, cite_key, file_path
            FROM papers
            ORDER BY id
        ''')

        papers = []
        for row in cursor.fetchall():
            paper = dict(row)

            # 解析JSON字段
            if paper['authors'] and isinstance(paper['authors'], str):
                try:
                    paper['authors'] = json.loads(paper['authors'])
                except:
                    paper['authors'] = []

            if paper['keywords'] and isinstance(paper['keywords'], str):
                try:
                    paper['keywords'] = json.loads(paper['keywords'])
                except:
                    paper['keywords'] = []

            papers.append(paper)

        conn.close()
        self.papers_cache = papers
        return papers

    def find_citation_relations(self, paper_id: int, confidence_threshold: float = 0.6) -> List[Relation]:
        """
        通過內容分析發現引用關係

        策略：
        1. 讀取論文 Markdown 內容
        2. 搜索引用模式：(Author, Year) 或 Author (Year)
        3. 匹配知識庫中的論文

        Args:
            paper_id: 源論文ID
            confidence_threshold: 置信度閾值

        Returns:
            引用關係列表
        """
        papers = self._load_papers()
        source_paper = next((p for p in papers if p['id'] == paper_id), None)

        if not source_paper or not source_paper['file_path']:
            return []

        # 讀取論文內容
        try:
            with open(source_paper['file_path'], 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️  無法讀取論文內容: {e}")
            return []

        relations = []

        # 引用模式匹配
        # 模式1: (Author, Year) 或 (Author et al., Year)
        # 模式2: Author (Year) 或 Author et al. (Year)
        citation_patterns = [
            r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?),?\s+(\d{4})\)',  # (Smith, 2020)
            r'([A-Z][a-z]+(?:\s+et\s+al\.)?)\s+\((\d{4})\)',    # Smith (2020)
        ]

        cited_papers = set()

        for pattern in citation_patterns:
            matches = re.finditer(pattern, content)

            for match in matches:
                author_part = match.group(1)
                year_part = int(match.group(2))

                # 提取姓氏（處理 "et al." 情況）
                if 'et al' in author_part:
                    author_surname = author_part.split()[0]
                else:
                    author_surname = author_part

                # 在知識庫中尋找匹配的論文
                for target_paper in papers:
                    if target_paper['id'] == paper_id:
                        continue  # 跳過自己

                    # 匹配年份
                    if target_paper['year'] != year_part:
                        continue

                    # 匹配作者姓氏
                    if not target_paper['authors']:
                        continue

                    author_match = False
                    for author in target_paper['authors']:
                        if isinstance(author, str):
                            # 提取姓氏（通常是最後一個詞）
                            surname = author.split()[-1].strip('.,')
                            if author_surname.lower() in surname.lower():
                                author_match = True
                                break

                    if author_match:
                        cited_papers.add(target_paper['id'])

        # 創建引用關係
        for target_id in cited_papers:
            relations.append(Relation(
                source_id=paper_id,
                target_id=target_id,
                relation_type='citation',
                strength=0.8,  # 高置信度（直接匹配作者-年份）
                metadata={
                    'method': 'content_analysis',
                    'pattern_matched': True
                }
            ))

        return relations

    def find_citations_by_embedding(self,
                                   threshold: float = None,
                                   source_papers: List[int] = None,
                                   max_results: int = None) -> List[Citation]:
        """
        基於向量相似度推測引用關係（Phase 1.5整合版本）

        使用embedding系統計算論文相似度，效果優於傳統方法。

        Args:
            threshold: 相似度閾值 (0-1)，默認使用config中的值
            source_papers: 僅分析這些論文的引用（整數ID列表，None表示全部）
            max_results: 限制返回結果數量

        Returns:
            List[Citation]: 按相似度排序的引用關係列表
        """
        if not self.embedding_manager:
            print("⚠️  EmbeddingManager未初始化，使用內容分析版本")
            return []

        threshold = threshold or self.config['citation_threshold']
        papers = self._load_papers()

        try:
            # 步驟1: 加載論文向量
            paper_ids = [p['id'] for p in papers]
            embeddings = self.embedding_manager.get_paper_embeddings(paper_ids)

            if embeddings is None:
                print("⚠️  無法獲取向量嵌入，使用內容分析版本")
                return []

            # 步驟2: 計算相似度矩陣
            from sklearn.metrics.pairwise import cosine_similarity
            similarity_matrix = cosine_similarity(embeddings)

            # 步驟3: 提取引用關係
            citations = []

            for i, source_paper in enumerate(papers):
                if source_papers and source_paper['id'] not in source_papers:
                    continue

                for j, target_paper in enumerate(papers):
                    if i == j:
                        continue  # 跳過自己

                    sim_score = float(similarity_matrix[i][j])

                    # 過濾極高相似度（認為是重複論文）
                    if sim_score > 0.95:
                        continue

                    # 應用相似度閾值
                    if sim_score < threshold:
                        continue

                    # 提取共同概念
                    common_concepts = self._extract_common_concepts(source_paper, target_paper)

                    # 確定置信度
                    confidence = self._get_confidence_level(sim_score)

                    citation = Citation(
                        citing_paper_id=source_paper['id'],
                        cited_paper_id=target_paper['id'],
                        citing_title=source_paper.get('title', f"Paper {source_paper['id']}")[:60],
                        cited_title=target_paper.get('title', f"Paper {target_paper['id']}")[:60],
                        similarity_score=sim_score,
                        confidence=confidence,
                        common_concepts=common_concepts,
                    )
                    citations.append(citation)

            # 步驟4: 排序
            citations = sorted(citations, key=lambda x: x.similarity_score, reverse=True)

            # 步驟5: 限制結果
            if max_results:
                citations = citations[:max_results]

            return citations

        except Exception as e:
            print(f"❌ 向量基礎引用發現失敗: {e}")
            return []

    def _get_confidence_level(self, similarity_score: float) -> str:
        """根據相似度確定置信度"""
        if similarity_score >= 0.80:
            return 'high'
        elif similarity_score >= 0.70:
            return 'medium'
        else:
            return 'low'

    def _extract_common_concepts(self, paper1: Dict, paper2: Dict) -> List[str]:
        """提取兩篇論文的共同概念"""
        keywords1 = set(paper1.get('keywords', []))
        keywords2 = set(paper2.get('keywords', []))

        if isinstance(keywords1, str):
            keywords1 = set(k.strip() for k in keywords1.split(',') if k.strip())
        if isinstance(keywords2, str):
            keywords2 = set(k.strip() for k in keywords2.split(',') if k.strip())

        common = keywords1 & keywords2
        return list(common)[:5]  # 返回最多5個共同概念

    def find_co_authors(self,
                       min_papers: int = None,
                       include_metadata: bool = True) -> Dict:
        """
        構建完整的共同作者網絡

        Args:
            min_papers: 最少共同論文數（默認使用config）
            include_metadata: 是否包含詳細元數據

        Returns:
            Dict: 包含作者節點、邊和統計信息的網絡
        """
        min_papers = min_papers or self.config.get('co_author_min_papers', 2)
        papers = self._load_papers()
        author_papers = {}
        author_metadata = {}

        # 步驟1: 提取所有作者及其論文
        for paper in papers:
            authors = paper.get('authors', [])
            if isinstance(authors, str):
                authors = json.loads(authors) if authors else []
            if not authors:
                authors = []

            for author in authors:
                author_lower = author.lower() if isinstance(author, str) else str(author).lower()

                if author_lower not in author_papers:
                    author_papers[author_lower] = []
                    author_metadata[author_lower] = {
                        'name': author,
                        'papers': [],
                        'paper_ids': []
                    }

                author_papers[author_lower].append(paper['id'])
                author_metadata[author_lower]['papers'].append(paper)
                author_metadata[author_lower]['paper_ids'].append(paper['id'])

        # 步驟2: 計算共同作者和協作邊
        edges = []
        edge_set = set()
        author_list = sorted(author_papers.keys())

        for i, author1_key in enumerate(author_list):
            for author2_key in author_list[i+1:]:
                shared_papers = set(author_papers[author1_key]) & set(author_papers[author2_key])

                if len(shared_papers) >= min_papers:
                    edge_key = tuple(sorted([author1_key, author2_key]))

                    if edge_key not in edge_set:
                        edge = CoAuthorEdge(
                            author1=author_metadata[author1_key]['name'],
                            author2=author_metadata[author2_key]['name'],
                            collaboration_count=len(shared_papers),
                            shared_papers=sorted(list(shared_papers))
                        )
                        edges.append(edge)
                        edge_set.add(edge_key)

        # 步驟3: 構建節點數據
        nodes = []
        for author_key in author_list:
            node = {
                'name': author_metadata[author_key]['name'],
                'paper_count': len(author_papers[author_key]),
                'paper_ids': author_metadata[author_key]['paper_ids']
            }

            if include_metadata:
                node['years'] = sorted(set(p.get('year') for p in author_metadata[author_key]['papers'] if p.get('year')))
                node['keywords'] = []
                for paper in author_metadata[author_key]['papers']:
                    keywords = paper.get('keywords', [])
                    if isinstance(keywords, str):
                        keywords = [k.strip() for k in keywords.split(',')]
                    node['keywords'].extend(keywords)
                node['keywords'] = sorted(list(set(node['keywords'])))[:10]  # Top 10

            nodes.append(node)

        # 步驟4: 計算網絡統計
        return {
            'nodes': nodes,
            'edges': [asdict(e) for e in sorted(edges, key=lambda x: x.collaboration_count, reverse=True)],
            'metadata': {
                'total_authors': len(nodes),
                'total_collaborations': len(edges),
                'max_collaboration': max([e.collaboration_count for e in edges], default=0),
                'avg_collaboration': sum(e.collaboration_count for e in edges) / len(edges) if edges else 0,
            }
        }

    def find_shared_topic_relations(self, paper_id: int, min_shared_keywords: int = 2) -> List[Relation]:
        """
        通過關鍵詞重疊發現主題關聯

        Args:
            paper_id: 論文ID
            min_shared_keywords: 最少共享關鍵詞數

        Returns:
            主題關聯列表
        """
        papers = self._load_papers()
        source_paper = next((p for p in papers if p['id'] == paper_id), None)

        if not source_paper or not source_paper['keywords']:
            return []

        source_keywords = set(kw.lower() for kw in source_paper['keywords'])
        relations = []

        for target_paper in papers:
            if target_paper['id'] == paper_id:
                continue

            if not target_paper['keywords']:
                continue

            target_keywords = set(kw.lower() for kw in target_paper['keywords'])
            shared = source_keywords & target_keywords

            if len(shared) >= min_shared_keywords:
                # 計算Jaccard相似度
                union = source_keywords | target_keywords
                jaccard = len(shared) / len(union)

                relations.append(Relation(
                    source_id=paper_id,
                    target_id=target_paper['id'],
                    relation_type='shared_topic',
                    strength=jaccard,
                    metadata={
                        'shared_keywords': list(shared),
                        'keyword_count': len(shared)
                    }
                ))

        return sorted(relations, key=lambda r: r.strength, reverse=True)

    def find_co_occurrence(self,
                          min_frequency: int = None,
                          top_k: int = None) -> Dict:
        """
        完整的概念共現分析

        Args:
            min_frequency: 最少共現次數（默認使用config）
            top_k: 返回最常見的概念對數

        Returns:
            Dict: 包含概念對、統計和網絡信息
        """
        min_frequency = min_frequency or self.config.get('concept_min_frequency', 2)
        papers = self._load_papers()
        concept_papers = {}
        concept_freq = {}

        # 步驟1: 提取所有概念及其論文
        for paper in papers:
            concepts = paper.get('keywords', [])

            if isinstance(concepts, str):
                concepts = [c.strip() for c in concepts.split(',') if c.strip()]
            elif concepts is None:
                concepts = []

            for concept in concepts:
                concept_lower = concept.lower()

                if concept_lower not in concept_papers:
                    concept_papers[concept_lower] = []
                    concept_freq[concept_lower] = 0

                concept_papers[concept_lower].append(paper['id'])
                concept_freq[concept_lower] += 1

        # 步驟2: 計算概念共現和關聯強度
        pairs = []
        concept_list = sorted(concept_papers.keys())

        for i, concept1_key in enumerate(concept_list):
            for concept2_key in concept_list[i+1:]:
                shared_papers = set(concept_papers[concept1_key]) & set(concept_papers[concept2_key])

                if len(shared_papers) >= min_frequency:
                    # 計算關聯強度（Jaccard相似度）
                    union = set(concept_papers[concept1_key]) | set(concept_papers[concept2_key])
                    jaccard = len(shared_papers) / len(union) if union else 0

                    pair = ConceptPair(
                        concept1=concept1_key,
                        concept2=concept2_key,
                        co_occurrence_count=len(shared_papers),
                        papers=sorted(list(shared_papers)),
                        association_strength=jaccard
                    )
                    pairs.append(pair)

        # 步驟3: 排序和限制
        pairs = sorted(pairs, key=lambda x: x.co_occurrence_count, reverse=True)
        if top_k:
            pairs = pairs[:top_k]

        # 步驟4: 計算統計信息
        return {
            'pairs': [asdict(p) for p in pairs],
            'concept_frequency': sorted(
                [(c, freq) for c, freq in concept_freq.items()],
                key=lambda x: x[1],
                reverse=True
            ),
            'metadata': {
                'total_concepts': len(concept_freq),
                'total_pairs': len(pairs),
                'max_frequency': max(concept_freq.values()) if concept_freq else 0,
                'avg_frequency': sum(concept_freq.values()) / len(concept_freq) if concept_freq else 0,
            }
        }

    def find_author_collaboration_relations(self, paper_id: int) -> List[Relation]:
        """
        通過共同作者發現合作關係

        Args:
            paper_id: 論文ID

        Returns:
            作者合作關係列表
        """
        papers = self._load_papers()
        source_paper = next((p for p in papers if p['id'] == paper_id), None)

        if not source_paper or not source_paper['authors']:
            return []

        source_authors = set(a.lower() for a in source_paper['authors'])
        relations = []

        for target_paper in papers:
            if target_paper['id'] == paper_id:
                continue

            if not target_paper['authors']:
                continue

            target_authors = set(a.lower() for a in target_paper['authors'])
            shared_authors = source_authors & target_authors

            if shared_authors:
                # 計算作者重疊率
                overlap_ratio = len(shared_authors) / max(len(source_authors), len(target_authors))

                relations.append(Relation(
                    source_id=paper_id,
                    target_id=target_paper['id'],
                    relation_type='author_collaboration',
                    strength=overlap_ratio,
                    metadata={
                        'shared_authors': list(shared_authors),
                        'author_count': len(shared_authors)
                    }
                ))

        return sorted(relations, key=lambda r: r.strength, reverse=True)

    def find_similarity_relations(self, paper_id: int, similarity_threshold: float = 0.3) -> List[Relation]:
        """
        通過標題相似度發現相關論文

        使用簡單的詞彙重疊計算相似度（未來可升級為向量相似度）

        Args:
            paper_id: 論文ID
            similarity_threshold: 相似度閾值

        Returns:
            相似關係列表
        """
        papers = self._load_papers()
        source_paper = next((p for p in papers if p['id'] == paper_id), None)

        if not source_paper or not source_paper['title']:
            return []

        # 標題分詞（簡單空格分割，轉小寫）
        source_words = set(source_paper['title'].lower().split())
        # 移除常見停用詞
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        source_words = source_words - stop_words

        relations = []

        for target_paper in papers:
            if target_paper['id'] == paper_id:
                continue

            if not target_paper['title']:
                continue

            target_words = set(target_paper['title'].lower().split())
            target_words = target_words - stop_words

            # 計算Jaccard相似度
            shared = source_words & target_words
            union = source_words | target_words

            if len(union) == 0:
                continue

            jaccard = len(shared) / len(union)

            if jaccard >= similarity_threshold:
                relations.append(Relation(
                    source_id=paper_id,
                    target_id=target_paper['id'],
                    relation_type='similarity',
                    strength=jaccard,
                    metadata={
                        'shared_words': list(shared),
                        'word_count': len(shared),
                        'method': 'title_jaccard'
                    }
                ))

        return sorted(relations, key=lambda r: r.strength, reverse=True)

    def find_all_relations(self, paper_id: int) -> Dict[str, List[Relation]]:
        """
        發現所有類型的關係

        Args:
            paper_id: 論文ID

        Returns:
            關係字典：{relation_type: [relations]}
        """
        return {
            'citation': self.find_citation_relations(paper_id),
            'shared_topic': self.find_shared_topic_relations(paper_id),
            'author_collaboration': self.find_author_collaboration_relations(paper_id),
            'similarity': self.find_similarity_relations(paper_id),
        }

    def build_citation_network(self, paper_ids: Optional[List[int]] = None) -> Dict:
        """
        構建引用網絡

        Args:
            paper_ids: 論文ID列表（None表示所有論文）

        Returns:
            網絡數據：{nodes: [], edges: []}
        """
        papers = self._load_papers()

        if paper_ids is None:
            paper_ids = [p['id'] for p in papers]

        nodes = []
        edges = []
        edge_set = set()  # 去重

        # 構建節點
        for paper in papers:
            if paper['id'] in paper_ids:
                nodes.append({
                    'id': paper['id'],
                    'label': paper['title'][:50] if paper['title'] else f"Paper {paper['id']}",
                    'title': paper['title'],
                    'year': paper['year'],
                    'cite_key': paper['cite_key'],
                })

        # 構建邊（引用關係）
        for paper_id in paper_ids:
            relations = self.find_citation_relations(paper_id)

            for rel in relations:
                if rel.target_id in paper_ids:
                    edge_key = (rel.source_id, rel.target_id)
                    if edge_key not in edge_set:
                        edges.append({
                            'source': rel.source_id,
                            'target': rel.target_id,
                            'type': rel.relation_type,
                            'strength': rel.strength
                        })
                        edge_set.add(edge_key)

        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'paper_ids': paper_ids
            }
        }

    def export_to_networkx(self, network_data: Dict):
        """
        轉換為NetworkX圖對象

        Args:
            network_data: build_citation_network()的輸出

        Returns:
            NetworkX DiGraph對象
        """
        try:
            import networkx as nx
        except ImportError:
            raise ImportError("需要安裝 networkx: pip install networkx")

        G = nx.DiGraph()

        # 添加節點
        for node in network_data['nodes']:
            G.add_node(node['id'], **node)

        # 添加邊
        for edge in network_data['edges']:
            G.add_edge(edge['source'], edge['target'],
                      type=edge['type'],
                      strength=edge['strength'])

        return G

    def export_to_json(self, network_data: Dict, output_path: str):
        """
        導出為JSON格式

        Args:
            network_data: 網絡數據
            output_path: 輸出路徑
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(network_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 網絡數據已導出到: {output_path}")

    def export_to_graphml(self, G, output_path: str):
        """
        導出為GraphML格式（可用於Gephi等工具）

        Args:
            G: NetworkX圖對象
            output_path: 輸出路徑
        """
        try:
            import networkx as nx
            nx.write_graphml(G, output_path)
            print(f"✅ GraphML已導出到: {output_path}")
        except ImportError:
            raise ImportError("需要安裝 networkx: pip install networkx")

    # ============== Mermaid 可視化（ Phase 2.1新增）==============

    def export_citations_to_mermaid(self,
                                    citations: List[Citation],
                                    output_path: str = None,
                                    max_edges: int = None) -> str:
        """
        將引用關係導出為Mermaid格式（Zettelkasten標準）

        格式參考：output/zettelkasten_notes/zettel_index.md

        Args:
            citations: Citation物件列表
            output_path: 輸出檔案路徑（如果None，返回Mermaid代碼）
            max_edges: 最大邊數（避免圖表過於複雜）

        Returns:
            str: Mermaid代碼或檔案路徑
        """
        max_edges = max_edges or self.config.get('max_edges_in_graph', 100)

        # 限制邊數
        citations = sorted(citations, key=lambda x: x.similarity_score, reverse=True)[:max_edges]

        # 構建Mermaid代碼
        lines = []
        lines.append("```mermaid")
        lines.append("graph TD")
        lines.append("")

        # 添加節點（去重）
        node_ids = set()
        for citation in citations:
            node_ids.add(citation.citing_paper_id)
            node_ids.add(citation.cited_paper_id)

        papers = {p['id']: p for p in self._load_papers()}

        for paper_id in sorted(node_ids):
            if paper_id in papers:
                title = papers[paper_id].get('title', f"Paper {paper_id}")
                # 標題長度限制
                title = title[:50] if len(title) > 50 else title
                lines.append(f'    P{paper_id}["{title}"]')

        lines.append("")

        # 添加邊（根據confidence決定線型）
        for citation in citations:
            if citation.confidence == 'high':
                # 實線：高置信度
                lines.append(f'    P{citation.citing_paper_id} --> P{citation.cited_paper_id}')
            else:
                # 虛線：中/低置信度
                lines.append(f'    P{citation.citing_paper_id} -.-> P{citation.cited_paper_id}')

        lines.append("")
        lines.append("```")

        mermaid_code = '\n'.join(lines)

        # 輸出檔案或返回代碼
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)
            print(f"✅ Mermaid圖表已導出到: {output_path}")
            return output_path
        else:
            return mermaid_code

    def export_coauthor_network_to_mermaid(self,
                                          network_data: Dict = None,
                                          output_path: str = None,
                                          max_nodes: int = None) -> str:
        """
        將共同作者網絡導出為Mermaid格式

        Args:
            network_data: 共同作者網絡數據（如果None，自動生成）
            output_path: 輸出檔案路徑
            max_nodes: 最大節點數

        Returns:
            str: Mermaid代碼或檔案路徑
        """
        max_nodes = max_nodes or self.config.get('max_nodes_in_graph', 50)

        # 生成共同作者網絡
        if network_data is None:
            network_data = self._build_coauthor_network()

        lines = []
        lines.append("```mermaid")
        lines.append("graph TD")
        lines.append('    subgraph Authors["共同作者網絡"]')

        # 添加作者節點（限制數量）
        author_edges = network_data.get('edges', [])
        author_nodes = set()

        for edge in author_edges[:max_nodes]:
            author_nodes.add(edge['author1'])
            author_nodes.add(edge['author2'])

        for i, author in enumerate(list(author_nodes)[:max_nodes]):
            # 計算該作者的論文數
            author_papers = []
            for edge in author_edges:
                if edge['author1'] == author:
                    author_papers.extend(edge['shared_papers'])
                elif edge['author2'] == author:
                    author_papers.extend(edge['shared_papers'])

            paper_count = len(set(author_papers))
            # 簡化作者名稱
            short_name = author.split(',')[0][:20] if ',' in author else author[:20]
            node_id = f"A{i}"

            lines.append(f'        {node_id}["{short_name} ({paper_count}篇)"]')

        lines.append('    end')
        lines.append("")

        # 添加邊（作者協作）
        for i, edge in enumerate(author_edges[:max_nodes]):
            if i > 0:  # 限制邊數
                break

            author_idx1 = list(author_nodes).index(edge['author1']) if edge['author1'] in author_nodes else None
            author_idx2 = list(author_nodes).index(edge['author2']) if edge['author2'] in author_nodes else None

            if author_idx1 is not None and author_idx2 is not None:
                lines.append(f'    A{author_idx1} --> A{author_idx2}')

        lines.append("")
        lines.append("```")

        mermaid_code = '\n'.join(lines)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)
            print(f"✅ 共同作者Mermaid圖表已導出到: {output_path}")
            return output_path
        else:
            return mermaid_code

    def _build_coauthor_network(self) -> Dict:
        """構建共同作者網絡數據"""
        papers = self._load_papers()
        author_papers = {}

        # 提取所有作者及其論文
        for paper in papers:
            authors = paper.get('authors', [])
            if not authors:
                continue

            for author in authors:
                if author not in author_papers:
                    author_papers[author] = []
                author_papers[author].append(paper['id'])

        # 計算共同作者
        edges = []
        author_list = list(author_papers.keys())

        for i, author1 in enumerate(author_list):
            for author2 in author_list[i+1:]:
                shared_papers = set(author_papers[author1]) & set(author_papers[author2])
                if len(shared_papers) >= self.config.get('co_author_min_papers', 1):
                    edges.append({
                        'author1': author1,
                        'author2': author2,
                        'collaboration_count': len(shared_papers),
                        'shared_papers': list(shared_papers)
                    })

        return {
            'authors': author_list,
            'edges': edges,
            'total_authors': len(author_list),
            'total_collaborations': len(edges)
        }

    def export_concepts_to_mermaid(self,
                                  concept_pairs: List[ConceptPair] = None,
                                  output_path: str = None,
                                  max_pairs: int = None) -> str:
        """
        將概念共現導出為Mermaid格式

        Args:
            concept_pairs: ConceptPair物件列表（如果None，自動生成）
            output_path: 輸出檔案路徑
            max_pairs: 最大概念對數

        Returns:
            str: Mermaid代碼或檔案路徑
        """
        max_pairs = max_pairs or self.config.get('max_edges_in_graph', 50)

        # 生成概念對（如果未提供）
        if concept_pairs is None:
            concept_pairs = self._extract_concept_pairs()

        # 限制對數
        concept_pairs = sorted(concept_pairs,
                             key=lambda x: x.co_occurrence_count,
                             reverse=True)[:max_pairs]

        lines = []
        lines.append("```mermaid")
        lines.append("graph TD")
        lines.append("")

        # 添加節點（去重）
        concepts = set()
        for pair in concept_pairs:
            concepts.add(pair.concept1)
            concepts.add(pair.concept2)

        # 節點命名（使用哈希）
        concept_to_node = {}
        for concept in sorted(concepts):
            node_id = f"C{hash(concept) % 10000}"
            concept_to_node[concept] = node_id
            lines.append(f'    {node_id}["{concept}"]')

        lines.append("")

        # 添加邊（概念共現）
        for pair in concept_pairs:
            node1 = concept_to_node[pair.concept1]
            node2 = concept_to_node[pair.concept2]

            # 根據關聯強度決定線型
            if pair.association_strength >= 0.5:
                lines.append(f'    {node1} --> {node2}')
            else:
                lines.append(f'    {node1} -.-> {node2}')

        lines.append("")
        lines.append("```")

        mermaid_code = '\n'.join(lines)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)
            print(f"✅ 概念共現Mermaid圖表已導出到: {output_path}")
            return output_path
        else:
            return mermaid_code

    def _extract_concept_pairs(self) -> List[ConceptPair]:
        """提取概念共現對"""
        papers = self._load_papers()
        concept_papers = {}

        # 提取所有概念及其論文
        for paper in papers:
            concepts = paper.get('keywords', [])
            if isinstance(concepts, str):
                concepts = [c.strip() for c in concepts.split(',') if c.strip()]
            elif concepts is None:
                concepts = []

            for concept in concepts:
                if concept not in concept_papers:
                    concept_papers[concept] = []
                concept_papers[concept].append(paper['id'])

        # 計算概念共現
        pairs = []
        concept_list = list(concept_papers.keys())

        for i, concept1 in enumerate(concept_list):
            for concept2 in concept_list[i+1:]:
                shared_papers = set(concept_papers[concept1]) & set(concept_papers[concept2])

                if len(shared_papers) >= self.config.get('concept_min_frequency', 1):
                    # 計算關聯強度
                    max_count = max(len(concept_papers[concept1]), len(concept_papers[concept2]))
                    strength = len(shared_papers) / max_count if max_count > 0 else 0

                    pair = ConceptPair(
                        concept1=concept1,
                        concept2=concept2,
                        co_occurrence_count=len(shared_papers),
                        papers=list(shared_papers),
                        association_strength=strength
                    )
                    pairs.append(pair)

        return sorted(pairs, key=lambda x: x.co_occurrence_count, reverse=True)


# CLI測試代碼
if __name__ == "__main__":
    print("🔍 relation-finder Phase 2.1 Day 2 測試\n")

    finder = RelationFinder()
    output_dir = Path("output/relations")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ===== 測試 1: 共同作者完整分析 =====
    print("=" * 70)
    print("測試 1: 共同作者網絡完整分析（Day 2新增）")
    print("=" * 70)

    coauthor_network = finder.find_co_authors(min_papers=1)

    print(f"\n👥 共同作者網絡統計:")
    print(f"   📊 總作者數: {coauthor_network['metadata']['total_authors']}")
    print(f"   🤝 協作對數: {coauthor_network['metadata']['total_collaborations']}")
    print(f"   📈 最大協作: {coauthor_network['metadata']['max_collaboration']}篇論文")
    print(f"   📉 平均協作: {coauthor_network['metadata']['avg_collaboration']:.2f}篇論文")

    # 顯示top協作對
    if coauthor_network['edges']:
        print(f"\n🏆 Top 5 協作對:")
        for i, edge in enumerate(coauthor_network['edges'][:5], 1):
            print(f"   {i}. {edge['author1']} ↔ {edge['author2']}")
            print(f"      共同論文: {edge['collaboration_count']}篇 (ID: {edge['shared_papers'][:2]}...)")

    # 導出為JSON
    with open(output_dir / "coauthor_network.json", 'w', encoding='utf-8') as f:
        json.dump(coauthor_network, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 共同作者網絡已導出到: {output_dir}/coauthor_network.json")

    # ===== 測試 2: 概念共現完整分析 =====
    print("\n" + "=" * 70)
    print("測試 2: 概念共現完整分析（Day 2新增）")
    print("=" * 70)

    cooccurrence = finder.find_co_occurrence(min_frequency=1, top_k=30)

    print(f"\n📚 概念共現統計:")
    print(f"   📊 總概念數: {cooccurrence['metadata']['total_concepts']}")
    print(f"   🔗 概念對數: {cooccurrence['metadata']['total_pairs']}")
    print(f"   📈 最高頻率: {cooccurrence['metadata']['max_frequency']}")
    print(f"   📉 平均頻率: {cooccurrence['metadata']['avg_frequency']:.2f}")

    # 顯示top概念
    if cooccurrence['concept_frequency']:
        print(f"\n⭐ Top 10 高頻概念:")
        for i, (concept, freq) in enumerate(cooccurrence['concept_frequency'][:10], 1):
            print(f"   {i}. {concept}: {freq}篇論文")

    # 顯示top概念對
    if cooccurrence['pairs']:
        print(f"\n🔗 Top 5 概念對:")
        for i, pair in enumerate(cooccurrence['pairs'][:5], 1):
            print(f"   {i}. '{pair['concept1']}' ↔ '{pair['concept2']}'")
            print(f"      共現: {pair['co_occurrence_count']}次, 強度: {pair['association_strength']:.2f}")

    # 導出為JSON
    with open(output_dir / "concept_cooccurrence.json", 'w', encoding='utf-8') as f:
        json.dump(cooccurrence, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 概念共現已導出到: {output_dir}/concept_cooccurrence.json")

    # ===== 測試 3: 更新Mermaid可視化 =====
    print("\n" + "=" * 70)
    print("測試 3: 使用新數據更新Mermaid可視化")
    print("=" * 70)

    # 共同作者Mermaid
    print("\n👥 生成共同作者Mermaid...")
    finder.export_coauthor_network_to_mermaid(
        network_data=coauthor_network,
        output_path=output_dir / "coauthor_network.md"
    )

    # 概念共現Mermaid
    print("📚 生成概念共現Mermaid...")
    concept_pairs = [ConceptPair(**p) for p in cooccurrence['pairs']]
    finder.export_concepts_to_mermaid(
        concept_pairs=concept_pairs,
        output_path=output_dir / "concept_cooccurrence.md"
    )

    # ===== 測試 4: 傳統關係分析 =====
    print("\n" + "=" * 70)
    print("測試 4: 傳統引用關係分析（Day 1功能驗證）")
    print("=" * 70)

    paper_id = 2
    print(f"\n📄 論文 ID {paper_id} 的關係:")

    all_relations = finder.find_all_relations(paper_id)

    for rel_type, relations in all_relations.items():
        if relations:
            print(f"\n🔗 {rel_type.upper()} ({len(relations)}個)")
            for rel in relations[:3]:
                print(f"   → Paper {rel.target_id} (強度: {rel.strength:.2f})")

    print("\n" + "=" * 70)
    print("✅ Phase 2.1 Day 2 測試完成！")
    print("=" * 70)
    print(f"\n📁 輸出檔案:")
    print(f"   ✅ {output_dir}/coauthor_network.json")
    print(f"   ✅ {output_dir}/coauthor_network.md (Mermaid)")
    print(f"   ✅ {output_dir}/concept_cooccurrence.json")
    print(f"   ✅ {output_dir}/concept_cooccurrence.md (Mermaid)")
    print(f"\n📊 新增功能:")
    print(f"   ✨ find_co_authors() - 共同作者網絡（含統計）")
    print(f"   ✨ find_co_occurrence() - 概念共現分析（含統計）")
