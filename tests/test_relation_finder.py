#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for RelationFinder (Phase 2.1)

Test coverage:
- Citation relationship extraction (Day 1)
- Co-author network analysis (Day 2)
- Concept co-occurrence analysis (Day 2)
- Timeline analysis (Day 3)
- JSON export functionality (Day 3)
- Mermaid visualization export (Days 1-3)
"""

import unittest
import json
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyzers.relation_finder import (
    RelationFinder,
    Citation,
    CoAuthorEdge,
    ConceptPair,
    Relation
)


class TestDataClasses(unittest.TestCase):
    """Test Citation, CoAuthorEdge, and ConceptPair dataclasses"""

    def test_citation_creation(self):
        """Test Citation dataclass creation"""
        citation = Citation(
            citing_paper_id=1,
            cited_paper_id=2,
            citing_title='Paper A',
            cited_title='Paper B',
            similarity_score=0.85,
            confidence='high',
            common_concepts=['AI', 'learning']
        )
        self.assertEqual(citation.citing_paper_id, 1)
        self.assertEqual(citation.cited_paper_id, 2)
        self.assertEqual(citation.citing_title, 'Paper A')
        self.assertEqual(citation.cited_title, 'Paper B')
        self.assertEqual(citation.similarity_score, 0.85)
        self.assertEqual(citation.confidence, 'high')
        self.assertEqual(len(citation.common_concepts), 2)

    def test_coauthor_edge_creation(self):
        """Test CoAuthorEdge dataclass creation"""
        edge = CoAuthorEdge(
            author1='John Doe',
            author2='Jane Smith',
            collaboration_count=5,
            shared_papers=[1, 2, 3, 4, 5]
        )
        self.assertEqual(edge.author1, 'John Doe')
        self.assertEqual(edge.author2, 'Jane Smith')
        self.assertEqual(edge.collaboration_count, 5)
        self.assertEqual(len(edge.shared_papers), 5)

    def test_concept_pair_creation(self):
        """Test ConceptPair dataclass creation"""
        pair = ConceptPair(
            concept1='machine learning',
            concept2='deep learning',
            co_occurrence_count=10,
            papers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            association_strength=0.75
        )
        self.assertEqual(pair.concept1, 'machine learning')
        self.assertEqual(pair.concept2, 'deep learning')
        self.assertEqual(pair.co_occurrence_count, 10)
        self.assertAlmostEqual(pair.association_strength, 0.75)


class TestRelationFinderInitialization(unittest.TestCase):
    """Test RelationFinder initialization and configuration"""

    def test_default_initialization(self):
        """Test RelationFinder with default configuration"""
        finder = RelationFinder()
        self.assertIsNotNone(finder.db_path)
        self.assertIsNotNone(finder.config)
        self.assertEqual(finder.config.get('citation_threshold', 0.65), 0.65)
        self.assertEqual(finder.config.get('max_citations', 50), 50)

    def test_custom_config(self):
        """Test RelationFinder with custom configuration"""
        custom_config = {
            'citation_threshold': 0.75,
            'max_citations': 100
        }
        finder = RelationFinder(config=custom_config)
        self.assertEqual(finder.config.get('citation_threshold'), 0.75)
        self.assertEqual(finder.config.get('max_citations'), 100)


class TestCitationExtraction(unittest.TestCase):
    """Test citation relationship extraction (Day 1)"""

    def setUp(self):
        """Set up test fixtures"""
        self.finder = RelationFinder()

    def test_find_citations_by_embedding_returns_citations(self):
        """Test that find_citations_by_embedding returns Citation objects"""
        citations = self.finder.find_citations_by_embedding(
            threshold=0.65,
            max_results=50
        )
        self.assertIsInstance(citations, list)
        # Citations may be empty if embedding manager is not initialized
        for citation in citations:
            self.assertIsInstance(citation, Citation)

    def test_citation_confidence_levels(self):
        """Test that citations have proper confidence levels"""
        citations = self.finder.find_citations_by_embedding()
        valid_confidences = {'high', 'medium', 'low'}
        for citation in citations:
            self.assertIn(citation.confidence, valid_confidences)

    def test_get_confidence_level(self):
        """Test confidence level calculation"""
        # High confidence
        level = self.finder._get_confidence_level(0.85)
        self.assertEqual(level, 'high')

        # Medium confidence
        level = self.finder._get_confidence_level(0.75)
        self.assertEqual(level, 'medium')

        # Low confidence
        level = self.finder._get_confidence_level(0.65)
        self.assertEqual(level, 'low')


class TestCoAuthorAnalysis(unittest.TestCase):
    """Test co-author network analysis (Day 2)"""

    def setUp(self):
        """Set up test fixtures"""
        self.finder = RelationFinder()

    def test_find_co_authors_returns_network(self):
        """Test that find_co_authors returns network structure"""
        network = self.finder.find_co_authors(min_papers=1)
        self.assertIsInstance(network, dict)
        self.assertIn('nodes', network)
        self.assertIn('edges', network)
        self.assertIn('metadata', network)

    def test_coauthor_network_metadata(self):
        """Test co-author network metadata"""
        network = self.finder.find_co_authors()
        metadata = network.get('metadata', {})
        self.assertIn('total_authors', metadata)
        self.assertIn('total_collaborations', metadata)
        self.assertIn('max_collaboration', metadata)
        self.assertIn('avg_collaboration', metadata)

    def test_coauthor_network_nodes_structure(self):
        """Test structure of co-author network nodes"""
        network = self.finder.find_co_authors()
        nodes = network.get('nodes', [])
        for node in nodes:
            self.assertIn('name', node)
            self.assertIn('paper_count', node)
            self.assertIn('paper_ids', node)

    def test_coauthor_network_edges_structure(self):
        """Test structure of co-author network edges"""
        network = self.finder.find_co_authors()
        edges = network.get('edges', [])
        for edge in edges:
            self.assertIn('author1', edge)
            self.assertIn('author2', edge)
            self.assertIn('collaboration_count', edge)
            self.assertIn('shared_papers', edge)


class TestConceptCooccurrence(unittest.TestCase):
    """Test concept co-occurrence analysis (Day 2)"""

    def setUp(self):
        """Set up test fixtures"""
        self.finder = RelationFinder()

    def test_find_co_occurrence_returns_structure(self):
        """Test that find_co_occurrence returns proper structure"""
        cooccurrence = self.finder.find_co_occurrence()
        self.assertIsInstance(cooccurrence, dict)
        self.assertIn('pairs', cooccurrence)
        self.assertIn('metadata', cooccurrence)
        self.assertIn('concept_frequency', cooccurrence)

    def test_concept_cooccurrence_metadata(self):
        """Test concept co-occurrence metadata"""
        cooccurrence = self.finder.find_co_occurrence()
        metadata = cooccurrence.get('metadata', {})
        self.assertIn('total_concepts', metadata)
        self.assertIn('total_pairs', metadata)
        self.assertIn('max_frequency', metadata)
        self.assertIn('avg_frequency', metadata)

    def test_concept_pairs_structure(self):
        """Test structure of concept pairs"""
        cooccurrence = self.finder.find_co_occurrence()
        pairs = cooccurrence.get('pairs', [])
        for pair in pairs:
            self.assertIn('concept1', pair)
            self.assertIn('concept2', pair)
            self.assertIn('co_occurrence_count', pair)
            self.assertIn('association_strength', pair)

    def test_extract_concept_pairs_handles_none(self):
        """Test that concept extraction handles None keywords gracefully"""
        pairs = self.finder._extract_concept_pairs()
        # Should return a list without raising errors
        self.assertIsInstance(pairs, list)


class TestTimelineAnalysis(unittest.TestCase):
    """Test timeline analysis (Day 3)"""

    def setUp(self):
        """Set up test fixtures"""
        self.finder = RelationFinder()

    def test_build_timeline_year_grouping(self):
        """Test timeline with year grouping"""
        timeline = self.finder.build_timeline(group_by='year')
        self.assertIsInstance(timeline, dict)
        self.assertIn('timepoints', timeline)
        self.assertIn('metadata', timeline)

    def test_build_timeline_5year_grouping(self):
        """Test timeline with 5-year grouping"""
        timeline = self.finder.build_timeline(group_by='5-year')
        self.assertIsInstance(timeline, dict)
        self.assertIn('timepoints', timeline)
        self.assertIn('metadata', timeline)

    def test_timeline_metadata(self):
        """Test timeline metadata structure"""
        timeline = self.finder.build_timeline()
        metadata = timeline.get('metadata', {})
        self.assertIn('start_year', metadata)
        self.assertIn('end_year', metadata)
        self.assertIn('total_years', metadata)
        self.assertIn('total_papers', metadata)
        self.assertIn('grouping', metadata)

    def test_timeline_timepoints_structure(self):
        """Test structure of timeline timepoints"""
        timeline = self.finder.build_timeline()
        timepoints = timeline.get('timepoints', [])
        for timepoint in timepoints:
            self.assertIn('period', timepoint)
            self.assertIn('paper_count', timepoint)
            self.assertIn('paper_ids', timepoint)
            self.assertIn('top_concepts', timepoint)

    def test_timeline_year_vs_5year(self):
        """Test that year and 5-year groupings have different structures"""
        year_timeline = self.finder.build_timeline(group_by='year')
        five_year_timeline = self.finder.build_timeline(group_by='5-year')

        year_points = year_timeline.get('timepoints', [])
        five_year_points = five_year_timeline.get('timepoints', [])

        # 5-year grouping should have fewer or equal timepoints
        self.assertLessEqual(len(five_year_points), len(year_points))

        # Year points should have 'year' field
        if year_points:
            self.assertIn('year', year_points[0])

        # 5-year points might have 'start_year' and 'end_year'
        if five_year_points and 'start_year' in five_year_points[0]:
            self.assertIn('start_year', five_year_points[0])
            self.assertIn('end_year', five_year_points[0])


class TestVisualizationExport(unittest.TestCase):
    """Test Mermaid visualization export"""

    def setUp(self):
        """Set up test fixtures"""
        self.finder = RelationFinder()

    def test_export_citations_to_mermaid_returns_code(self):
        """Test citation Mermaid export returns code"""
        citations = []
        mermaid_code = self.finder.export_citations_to_mermaid(citations)
        self.assertIsInstance(mermaid_code, str)
        self.assertIn('graph', mermaid_code)
        self.assertIn('```mermaid', mermaid_code)

    def test_export_citations_to_mermaid_to_file(self):
        """Test citation Mermaid export to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'citations.md'
            citations = []
            result = self.finder.export_citations_to_mermaid(
                citations,
                output_path=str(output_path)
            )
            self.assertEqual(result, str(output_path))
            self.assertTrue(output_path.exists())

    def test_export_coauthor_network_to_mermaid(self):
        """Test co-author network Mermaid export"""
        network = self.finder.find_co_authors()
        mermaid_code = self.finder.export_coauthor_network_to_mermaid(network)
        self.assertIsInstance(mermaid_code, str)
        self.assertIn('```mermaid', mermaid_code)

    def test_export_concepts_to_mermaid(self):
        """Test concept co-occurrence Mermaid export"""
        cooccurrence = self.finder.find_co_occurrence()
        pairs = [ConceptPair(**p) for p in cooccurrence.get('pairs', [])]
        mermaid_code = self.finder.export_concepts_to_mermaid(pairs)
        self.assertIsInstance(mermaid_code, str)
        self.assertIn('```mermaid', mermaid_code)

    def test_export_timeline_to_mermaid(self):
        """Test timeline Mermaid export"""
        timeline = self.finder.build_timeline()
        mermaid_code = self.finder.export_timeline_to_mermaid(timeline)
        self.assertIsInstance(mermaid_code, str)
        self.assertIn('gantt', mermaid_code)
        self.assertIn('```mermaid', mermaid_code)


class TestJSONExport(unittest.TestCase):
    """Test JSON export functionality (Day 3)"""

    def setUp(self):
        """Set up test fixtures"""
        self.finder = RelationFinder()

    def test_export_to_json_returns_structure(self):
        """Test export_to_json returns correct structure"""
        result = self.finder.export_to_json()
        self.assertIsInstance(result, dict)
        self.assertIn('version', result)
        self.assertIn('generated_at', result)
        self.assertIn('data', result)
        self.assertIn('metadata', result)

    def test_export_to_json_with_all_components(self):
        """Test export with all component types"""
        result = self.finder.export_to_json(
            include_citations=True,
            include_coauthors=True,
            include_concepts=True,
            include_timeline=True
        )
        data = result.get('data', {})
        self.assertIn('citations', data)
        self.assertIn('coauthors', data)
        self.assertIn('concepts', data)
        self.assertIn('timeline', data)

    def test_export_to_json_selective(self):
        """Test selective export (exclude some components)"""
        result = self.finder.export_to_json(
            include_citations=False,
            include_coauthors=True,
            include_concepts=False,
            include_timeline=True
        )
        data = result.get('data', {})
        self.assertNotIn('citations', data)
        self.assertIn('coauthors', data)
        self.assertNotIn('concepts', data)
        self.assertIn('timeline', data)

    def test_export_to_json_metadata(self):
        """Test JSON export metadata"""
        result = self.finder.export_to_json()
        metadata = result.get('metadata', {})
        self.assertIn('author_count', metadata)
        self.assertIn('concept_count', metadata)
        self.assertIn('total_papers', metadata)
        self.assertIn('year_range', metadata)

    def test_export_to_json_to_file(self):
        """Test JSON export to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'relations.json'
            result = self.finder.export_to_json(
                output_path=str(output_path)
            )
            self.assertTrue(output_path.exists())
            # Verify file contents
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.assertIn('version', data)
            self.assertIn('metadata', data)


class TestLegacyRelationMethods(unittest.TestCase):
    """Test legacy Relation class compatibility (backward compatibility)"""

    def setUp(self):
        """Set up test fixtures"""
        self.finder = RelationFinder()

    def test_find_all_relations(self):
        """Test legacy find_all_relations method"""
        paper_id = 2
        relations = self.finder.find_all_relations(paper_id)
        self.assertIsInstance(relations, dict)
        # Should return dict with relation types as keys
        for rel_type, rel_list in relations.items():
            self.assertIsInstance(rel_list, list)

    def test_relation_object_structure(self):
        """Test Relation class structure"""
        relation = Relation(
            source_id=1,
            target_id=2,
            relation_type='citation',
            strength=0.8,
            metadata={'comment': 'test relation'}
        )
        self.assertEqual(relation.source_id, 1)
        self.assertEqual(relation.target_id, 2)
        self.assertEqual(relation.relation_type, 'citation')
        self.assertEqual(relation.strength, 0.8)
        self.assertIsInstance(relation.metadata, dict)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.finder = RelationFinder()

    def test_handle_missing_keywords(self):
        """Test handling of papers without keywords"""
        # This is tested implicitly in concept extraction
        cooccurrence = self.finder.find_co_occurrence()
        self.assertIsInstance(cooccurrence, dict)
        # Should not raise error even if some papers have no keywords

    def test_handle_missing_authors(self):
        """Test handling of papers without authors"""
        network = self.finder.find_co_authors()
        self.assertIsInstance(network, dict)
        # Should not raise error even if some papers have no authors

    def test_handle_missing_years(self):
        """Test handling of papers without years"""
        timeline = self.finder.build_timeline()
        self.assertIsInstance(timeline, dict)
        # Should not raise error even if some papers have no year

    def test_timeline_handles_none_keywords(self):
        """Test that timeline extraction handles None keywords"""
        timeline = self.finder.build_timeline(group_by='year')
        # Should not raise TypeError even with None keywords
        self.assertIsInstance(timeline, dict)
        self.assertIn('timepoints', timeline)

    def test_timeline_handles_none_keywords_5year(self):
        """Test that 5-year timeline extraction handles None keywords"""
        timeline = self.finder.build_timeline(group_by='5-year')
        # Should not raise TypeError even with None keywords
        self.assertIsInstance(timeline, dict)
        self.assertIn('timepoints', timeline)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""

    def setUp(self):
        """Set up test fixtures"""
        self.finder = RelationFinder()

    def test_complete_workflow(self):
        """Test complete relation-finder workflow"""
        # Step 1: Get co-authors
        coauthors = self.finder.find_co_authors()
        self.assertGreater(len(coauthors.get('nodes', [])), 0)

        # Step 2: Get concept co-occurrence
        concepts = self.finder.find_co_occurrence()
        self.assertGreater(len(concepts.get('pairs', [])), 0)

        # Step 3: Build timeline
        timeline = self.finder.build_timeline()
        self.assertGreater(len(timeline.get('timepoints', [])), 0)

        # Step 4: Export all to JSON
        result = self.finder.export_to_json()
        self.assertIn('data', result)
        self.assertIn('metadata', result)

    def test_multiple_export_formats(self):
        """Test exporting in multiple formats"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Export co-author network
            coauthors = self.finder.find_co_authors()
            mermaid_path = tmpdir / 'coauthors.md'
            self.finder.export_coauthor_network_to_mermaid(
                network_data=coauthors,
                output_path=str(mermaid_path)
            )
            self.assertTrue(mermaid_path.exists())

            # Export concepts
            concepts = self.finder.find_co_occurrence()
            pairs = [ConceptPair(**p) for p in concepts.get('pairs', [])]
            mermaid_path = tmpdir / 'concepts.md'
            self.finder.export_concepts_to_mermaid(
                concept_pairs=pairs,
                output_path=str(mermaid_path)
            )
            self.assertTrue(mermaid_path.exists())

            # Export timeline
            timeline = self.finder.build_timeline()
            mermaid_path = tmpdir / 'timeline.md'
            self.finder.export_timeline_to_mermaid(
                timeline_data=timeline,
                output_path=str(mermaid_path)
            )
            self.assertTrue(mermaid_path.exists())

            # Export JSON
            json_path = tmpdir / 'relations.json'
            self.finder.export_to_json(output_path=str(json_path))
            self.assertTrue(json_path.exists())


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
