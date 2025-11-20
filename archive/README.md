# Archive Directory

This directory contains session-specific tools and scripts that have been moved from the root directory to improve project structure clarity.

## Directory Structure

### zettel_tools/
**Purpose**: Specialized tools for Zettelkasten card management

- `import_existing_zettel.py` (214 lines)
  - Manual import tool for Zettelkasten cards to knowledge base
  - **Status**: Superseded by batch_processor.py auto-import feature
  - **Use case**: Legacy imports or troubleshooting

- `regenerate_zettel_with_openrouter.py` (300+ lines)
  - Generate Zettelkasten cards using OpenRouter API
  - **Status**: Active for custom LLM testing
  - **Use case**: Testing new LLM models, regenerating specific papers

- `analyze_card_links.py`
  - Analyze link structure in Zettelkasten cards
  - **Status**: Useful for debugging link extraction
  - **Use case**: Phase 2.4 RelationFinder improvements

### zotero_integration/
**Purpose**: Tools for Zotero library integration (Phase 1)

- `import_zotero_batch.py`
  - Batch import papers from Zotero BibTeX
  - **Status**: Phase 1 implementation
  - **Use case**: Phase 3 Zotero + Obsidian integration

- `auto_match_pdfs.py`
  - Automatically match BibTeX entries to PDF files
  - **Status**: Active for Phase 3
  - **Use case**: Zotero library scanning

- `enhanced_fuzzy_match.py`
  - Fuzzy matching for citation keys and file names
  - **Status**: Active for Phase 3
  - **Use case**: Handling inconsistent naming

- `import_unrecorded.py`
  - Import papers not yet in knowledge base
  - **Status**: Specialized tool
  - **Use case**: Incremental imports

### metadata_tools/
**Purpose**: Tools for fixing metadata issues (Phase 1.6)

- `fix_metadata.py`
  - Batch fix metadata issues in knowledge base
  - **Status**: Phase 1.6 cleanup tool
  - **Use case**: Data quality maintenance

- `fix_single_paper.py`
  - Interactive tool for fixing individual paper metadata
  - **Status**: Troubleshooting tool
  - **Use case**: Manual corrections

- `interactive_pdf_reimport.py`
  - Interactive PDF re-import with validation
  - **Status**: Recovery tool
  - **Use case**: Fixing corrupted imports

- `interactive_repair.py`
  - Interactive metadata repair wizard
  - **Status**: Legacy tool
  - **Use case**: Historical reference

- `llm_metadata_generator.py`
  - Use LLM to generate missing metadata
  - **Status**: Experimental
  - **Use case**: Papers with missing DOI/BibTeX

### testing/
**Purpose**: Development and testing scripts

- `test_full_network.py`
  - Test complete concept network generation
  - **Status**: Development tool
  - **Use case**: Phase 2.2 testing

- `test_openrouter.py`
  - Test OpenRouter API integration
  - **Status**: Development tool
  - **Use case**: LLM provider testing

- `test_relation_finder_improvements.py`
  - Test RelationFinder algorithm improvements
  - **Status**: Phase 2.4 development
  - **Use case**: Algorithm validation

- `test_single_model.py`
  - Test individual LLM model performance
  - **Status**: Development tool
  - **Use case**: Model comparison

- `test_three_models.py`
  - Compare three LLM models (Gemini, DeepSeek, Llama)
  - **Status**: Phase 2.3 validation
  - **Use case**: Quality assessment

- `check_free_models.py`
  - Check available free models on OpenRouter
  - **Status**: Utility tool
  - **Use case**: Model discovery

### visualization/
**Purpose**: Visualization and analysis tools

- `generate_improved_visualization.py`
  - Generate improved concept network visualizations
  - **Status**: Superseded by generate_concept_network.py
  - **Use case**: Legacy visualization

### deprecated/
**Purpose**: Obsolete or superseded files

- `cleanup_session.py`
  - Session cleanup tool
  - **Status**: Superseded by src/utils/session_organizer.py
  - **Reason**: Functionality moved to utils module

- `final_import_list.json`
  - Phase 1 import list
  - **Status**: Obsolete (Phase 1 completed)
  - **Reason**: Historical artifact

- `regenerate_remaining_result_20251104_163445.json`
  - Phase 2.3 regeneration results
  - **Status**: Obsolete (Phase 2.3 completed)
  - **Reason**: Historical artifact

## When to Use Archived Tools

### Active Use Cases

**Phase 3 (Zotero + Obsidian Integration)**:
- `zotero_integration/import_zotero_batch.py`
- `zotero_integration/auto_match_pdfs.py`
- `zotero_integration/enhanced_fuzzy_match.py`

**Custom Zettelkasten Generation**:
- `zettel_tools/regenerate_zettel_with_openrouter.py`

**Metadata Maintenance**:
- `metadata_tools/fix_metadata.py`
- `metadata_tools/fix_single_paper.py`

**Algorithm Development**:
- `testing/test_relation_finder_improvements.py`

### Legacy Reference

**Phase 1-2 Completion**:
- All tools in `deprecated/`
- Some tools in `metadata_tools/` (Phase 1.6)

## Core CLI Tools (Root Directory)

The following 12 tools remain in the root directory as core CLI utilities:

**Essential**:
- `analyze_paper.py` - Analyze single paper
- `batch_process.py` - Batch processing
- `kb_manage.py` - Knowledge base management
- `make_slides.py` - Slide generation
- `check_db.py` - Database status check
- `generate_embeddings.py` - Vector embeddings

**Embargo System** (Phase 2.3):
- `add_public_column.py` - Mark papers as public/embargo
- `export_public_db.py` - Export public database
- `test_embargo_workflow.py` - Embargo system tests

**Development** (Phase 2.3):
- `generate_concept_network.py` - UTF-8 safe network visualization
- `test_auto_import.py` - Test auto-import functionality
- `test_batch_import.py` - Test batch import

## Migration Notes

**Date**: 2025-11-20
**Commit**: chore: Archive session-specific tools and cleanup root directory
**Files Moved**: 21
**Root Directory**: 32 → 12 files (-63%)

**Breaking Changes**: None (all tools still accessible in archive/)

**Path Updates Required**: If any scripts reference these tools, update import paths:
```python
# Before
from import_existing_zettel import import_cards

# After
from archive.zettel_tools.import_existing_zettel import import_cards
```

## Restoration

To restore a tool to root directory:
```bash
git mv archive/[category]/[tool].py .
```

Example:
```bash
# Restore Zotero import tool for Phase 3
git mv archive/zotero_integration/import_zotero_batch.py .
```

---

**Last Updated**: 2025-11-20
**Maintainer**: Claude Code
**Status**: Active
