#!/usr/bin/env python3
"""
Build PDF Index for Phase 3 - Zotero + Obsidian Integration

This script scans the PDF directory and builds a comprehensive index
mapping cite keys to PDF filenames. Handles various naming conventions
including special characters (é→e normalization).

Usage:
    python build_pdf_index.py --pdf-dir "D:/core/research/Program_verse/+/pdf"
    python build_pdf_index.py --pdf-dir "..." --output custom_index.json

Output:
    pdf_index.json - Complete mapping of cite_key → PDF metadata
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def normalize_for_bibtex(text):
    """
    Normalize special characters the way BibTeX does.

    Common normalizations:
    - é, è, ê, ë → e
    - á, à, â, ä → a
    - ó, ò, ô, ö → o
    - ú, ù, û, ü → u
    - ç → c
    """
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a',
        'Á': 'A', 'À': 'A', 'Â': 'A', 'Ä': 'A',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o',
        'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Ö': 'O',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'ç': 'c', 'Ç': 'C',
        'ñ': 'n', 'Ñ': 'N',
        'ø': 'o', 'Ø': 'O',
        'å': 'a', 'Å': 'A',
        'æ': 'ae', 'Æ': 'AE',
        'œ': 'oe', 'Œ': 'OE',
    }

    result = text
    for special, normal in replacements.items():
        result = result.replace(special, normal)
    return result


def extract_cite_key_from_filename(filename):
    """
    Extract possible cite key from PDF filename.

    Handles multiple formats:
    - Author-Year.pdf → Author-Year
    - @Author-Year.pdf → Author-Year
    - Author--Year_topic.pdf → Author-Year
    - Author-YearLetter.pdf → Author-YearLetter

    Returns:
        tuple: (normalized_cite_key, original_cite_key, format_type)
    """
    # Remove .pdf extension
    name = filename[:-4] if filename.endswith('.pdf') else filename

    # Initialize
    original = name
    format_type = "unknown"

    # Remove @ prefix (zotmoov format)
    if name.startswith('@'):
        name = name[1:]
        format_type = "zotmoov_at"

    # Replace -- with - (zotmoov separator)
    if '--' in name:
        name = name.replace('--', '-')
        format_type = "zotmoov_double_dash"

    # Remove _topic suffix (e.g., Author-2020_reading → Author-2020)
    if '_' in name:
        name = name.split('_')[0]
        if format_type == "unknown":
            format_type = "with_topic_suffix"

    # Remove space-separated version numbers (e.g., "Guest-2025 2" → "Guest-2025")
    name = re.sub(r'\s+\d+$', '', name)

    # Extract cite key pattern: Author-Year or Author-YearLetter
    # Match: Author-YYYY or Author-YYYYa or Author-YYYY-OptionalPart
    match = re.match(r'^([A-Z][a-zA-Z]+(?:-[A-Z][a-zA-Z]+)*)-(\d{4})([a-z]?).*$', name)

    if match:
        author = match.group(1)
        year = match.group(2)
        letter = match.group(3)
        cite_key = f"{author}-{year}{letter}"

        if format_type == "unknown":
            format_type = "standard"

        # Normalize for BibTeX (é→e, etc.)
        normalized = normalize_for_bibtex(cite_key)

        return normalized, cite_key, format_type

    # Fallback: use the whole cleaned name
    normalized = normalize_for_bibtex(name)
    return normalized, name, "non_standard"


def build_index(pdf_dir, verbose=False):
    """
    Scan PDF directory and build comprehensive index.

    Returns:
        dict: {
            'normalized_cite_key': {
                'original_cite_key': str,
                'filename': str,
                'full_path': str,
                'size_bytes': int,
                'format_type': str,
                'has_special_chars': bool,
            },
            ...
        }
    """
    pdf_dir = Path(pdf_dir)

    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

    # Scan all PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))

    if verbose:
        print(f"Scanning {len(pdf_files)} PDF files in {pdf_dir}...")

    index = {}
    format_stats = defaultdict(int)
    special_char_count = 0
    duplicates = defaultdict(list)

    for pdf_file in pdf_files:
        normalized, original, format_type = extract_cite_key_from_filename(pdf_file.name)

        # Track statistics
        format_stats[format_type] += 1
        has_special = (normalized != original)
        if has_special:
            special_char_count += 1

        # Build entry
        entry = {
            'original_cite_key': original,
            'filename': pdf_file.name,
            'full_path': str(pdf_file.absolute()),
            'size_bytes': pdf_file.stat().st_size,
            'format_type': format_type,
            'has_special_chars': has_special,
        }

        # Check for duplicates (same normalized cite key, different files)
        if normalized in index:
            duplicates[normalized].append(pdf_file.name)
            if verbose:
                print(f"⚠️  Duplicate cite key: {normalized}")
                print(f"    Existing: {index[normalized]['filename']}")
                print(f"    New: {pdf_file.name}")

        # Store (newer file overwrites if duplicate)
        index[normalized] = entry

    # Prepare statistics
    stats = {
        'total_pdfs': len(pdf_files),
        'unique_cite_keys': len(index),
        'duplicates': len(duplicates),
        'special_chars': special_char_count,
        'format_distribution': dict(format_stats),
    }

    return index, stats, duplicates


def main():
    parser = argparse.ArgumentParser(
        description="Build PDF index for Phase 3 Zotero + Obsidian integration"
    )
    parser.add_argument(
        '--pdf-dir',
        type=str,
        required=True,
        help='Path to PDF directory (e.g., D:/core/research/Program_verse/+/pdf)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='pdf_index.json',
        help='Output JSON file (default: pdf_index.json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed progress'
    )

    args = parser.parse_args()

    # Set UTF-8 output
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 80)
    print("PDF Index Builder - Phase 3A Zotero + Obsidian Integration")
    print("=" * 80)
    print()
    print(f"PDF Directory: {args.pdf_dir}")
    print(f"Output File: {args.output}")
    print()

    # Build index
    try:
        index, stats, duplicates = build_index(args.pdf_dir, verbose=args.verbose)
    except Exception as e:
        print(f"❌ Error building index: {e}")
        return 1

    # Print statistics
    print("=" * 80)
    print("Indexing Complete")
    print("=" * 80)
    print()
    print(f"Total PDFs scanned: {stats['total_pdfs']}")
    print(f"Unique cite keys: {stats['unique_cite_keys']}")
    print(f"Duplicate cite keys: {stats['duplicates']}")
    print(f"PDFs with special characters: {stats['special_chars']}")
    print()

    print("Format Distribution:")
    for format_type, count in sorted(stats['format_distribution'].items(),
                                     key=lambda x: x[1], reverse=True):
        print(f"  {format_type:<25} {count:>6} ({count/stats['total_pdfs']*100:>5.1f}%)")
    print()

    # Show duplicate details
    if duplicates:
        print("⚠️  Duplicate Cite Keys (keeping latest):")
        for cite_key, filenames in list(duplicates.items())[:10]:
            print(f"  {cite_key}:")
            for filename in filenames:
                print(f"    - {filename}")
        if len(duplicates) > 10:
            print(f"  ... and {len(duplicates) - 10} more")
        print()

    # Save to JSON
    output_data = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'pdf_directory': str(Path(args.pdf_dir).absolute()),
            'statistics': stats,
        },
        'index': index,
    }

    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("=" * 80)
    print(f"✅ PDF index saved to: {output_path.absolute()}")
    print("=" * 80)
    print()

    # Show example entries
    print("Example index entries:")
    for i, (cite_key, entry) in enumerate(list(index.items())[:5]):
        print(f"{i+1}. {cite_key}")
        print(f"   Filename: {entry['filename']}")
        print(f"   Format: {entry['format_type']}")
        if entry['has_special_chars']:
            print(f"   Original: {entry['original_cite_key']} (special chars)")
        print()

    print("Next steps:")
    print("  1. python extract_bibtex_subset.py --cite-keys pilot_cite_keys_psycho_crowdsourcing.txt")
    print("  2. python test_pdf_resolution.py --bibtex pilot_batch.bib --pdf-index pdf_index.json")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
