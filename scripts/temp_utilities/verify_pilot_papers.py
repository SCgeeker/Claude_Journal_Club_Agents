#!/usr/bin/env python3
"""
Verify pilot papers for "Psycho Studies on crowdsourcing" Connection note.

This script:
1. Lists all 12 papers from the Connection note
2. Checks PDF existence in +/pdf/ directory
3. Verifies BibTeX entries in My Library.bib
4. Generates cite keys file for Phase 3A pilot
"""

import os
import re
from pathlib import Path

# Paths
PDF_DIR = Path(r"D:\core\research\Program_verse\+\pdf")
BIBTEX_FILE = Path(r"D:\core\research\Program_verse\+\My Library.bib")

# All 12 papers from "Psycho Studies on crowdsourcing"
PILOT_PAPERS = [
    "Adams-2020",
    "Baruch-2016",
    "Crequit-2018",
    "Hosseini-2015",
    "Leckel-2025",
    "Liao-2021",
    "Peer-2017",
    "Shapiro-2013",
    "Stewart-2017",
    "Strickland-2019",
    "Strickland-2022",
    "Woodley-2025",
]

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
    }

    result = text
    for special, normal in replacements.items():
        result = result.replace(special, normal)
    return result

def denormalize_for_filesystem(cite_key):
    """
    Generate possible filename variations with special characters.

    For cite_key "Crequit-2018", generate:
    - Crequit-2018 (normalized)
    - Créquit-2018 (common French spelling)
    """
    variations = [cite_key]

    # Common variations for specific names
    # Add more as we discover them
    special_cases = {
        'Crequit': ['Créquit'],
        # Add more mappings here as needed
    }

    for normalized, specials in special_cases.items():
        if normalized in cite_key:
            for special in specials:
                variations.append(cite_key.replace(normalized, special))

    return variations

def check_pdf_exists(cite_key, pdf_dir):
    """
    Check if PDF exists using Hybrid Path Strategy.

    Now handles special characters: BibTeX normalizes (é→e) but
    filesystem may preserve original (Créquit-2018.pdf).
    """
    # Generate cite key variations (normalized and with special chars)
    cite_key_variations = denormalize_for_filesystem(cite_key)

    candidates = []

    for key_variant in cite_key_variations:
        # Standard format
        candidates.append(pdf_dir / f"{key_variant}.pdf")
        # With version suffix
        candidates.append(pdf_dir / f"{key_variant}a.pdf")
        candidates.append(pdf_dir / f"{key_variant}b.pdf")
        # @ prefix (zotmoov format)
        candidates.append(pdf_dir / f"@{key_variant}.pdf")
        candidates.append(pdf_dir / f"@{key_variant}a.pdf")
        # -- separator (zotmoov format)
        candidates.append(pdf_dir / f"{key_variant.replace('-', '--')}.pdf")

    for candidate in candidates:
        if candidate.exists():
            return True, candidate.name
    return False, None

def check_bibtex_entry(cite_key, bibtex_file):
    """Check if BibTeX entry exists."""
    try:
        with open(bibtex_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Match @article{Cite-Key, or @inproceedings{Cite-Key,
        pattern = rf'@\w+\{{{re.escape(cite_key)},'
        if re.search(pattern, content, re.MULTILINE):
            return True
    except Exception as e:
        print(f"Error reading BibTeX: {e}")
    return False

def main():
    # Set UTF-8 output
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 80)
    print("Phase 3A Pilot Papers Verification")
    print("Connection Note: 🔗Psycho Studies on crowdsourcing")
    print("=" * 80)
    print()

    # Verify each paper
    results = []
    print(f"{'Cite Key':<20} {'PDF':<8} {'BibTeX':<8} {'PDF Filename':<30}")
    print("-" * 80)

    for cite_key in PILOT_PAPERS:
        pdf_exists, pdf_filename = check_pdf_exists(cite_key, PDF_DIR)
        bibtex_exists = check_bibtex_entry(cite_key, BIBTEX_FILE)

        pdf_status = "✅" if pdf_exists else "❌"
        bibtex_status = "✅" if bibtex_exists else "❌"
        pdf_display = pdf_filename if pdf_filename else "NOT FOUND"

        print(f"{cite_key:<20} {pdf_status:<8} {bibtex_status:<8} {pdf_display:<30}")

        results.append({
            'cite_key': cite_key,
            'pdf_exists': pdf_exists,
            'pdf_filename': pdf_filename,
            'bibtex_exists': bibtex_exists,
        })

    print("-" * 80)
    print()

    # Summary
    total = len(results)
    pdf_ok = sum(1 for r in results if r['pdf_exists'])
    bibtex_ok = sum(1 for r in results if r['bibtex_exists'])
    both_ok = sum(1 for r in results if r['pdf_exists'] and r['bibtex_exists'])

    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total papers: {total}")
    print(f"PDFs found: {pdf_ok}/{total} ({pdf_ok/total*100:.1f}%)")
    print(f"BibTeX entries found: {bibtex_ok}/{total} ({bibtex_ok/total*100:.1f}%)")
    print(f"Both PDF + BibTeX: {both_ok}/{total} ({both_ok/total*100:.1f}%)")
    print()

    # Missing items
    missing_pdf = [r['cite_key'] for r in results if not r['pdf_exists']]
    missing_bibtex = [r['cite_key'] for r in results if not r['bibtex_exists']]

    if missing_pdf:
        print("⚠️ Missing PDFs:")
        for cite_key in missing_pdf:
            print(f"  - {cite_key}")
        print()

    if missing_bibtex:
        print("⚠️ Missing BibTeX entries:")
        for cite_key in missing_bibtex:
            print(f"  - {cite_key}")
        print()

    # Decision
    print("=" * 80)
    print("Phase 3A Pilot Feasibility Assessment")
    print("=" * 80)
    print()

    if both_ok >= 10:
        print(f"✅ PROCEED - {both_ok}/{total} papers have both PDF and BibTeX")
        print(f"   Resolution rate: {both_ok/total*100:.1f}%")
        print()
        print("Recommendation:")
        print("  1. Use these papers for Phase 3A pilot")
        if missing_pdf or missing_bibtex:
            print(f"  2. Skip {len(missing_pdf) + len(missing_bibtex)} missing papers")
        print("  3. Proceed with build_pdf_index.py and test_pdf_resolution.py")
    else:
        print(f"⚠️ CAUTION - Only {both_ok}/{total} papers ready")
        print(f"   Resolution rate: {both_ok/total*100:.1f}% (below 90% threshold)")
        print()
        print("Options:")
        print("  1. Proceed with available papers only")
        print("  2. Find missing PDFs/BibTeX entries first")
        print("  3. Select a different Connection note")

    print()

    # Generate cite keys file (for papers with both PDF and BibTeX)
    ready_papers = [r['cite_key'] for r in results if r['pdf_exists'] and r['bibtex_exists']]

    if ready_papers:
        output_file = Path("pilot_cite_keys_psycho_crowdsourcing.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            for cite_key in ready_papers:
                f.write(f"{cite_key}\n")

        print("=" * 80)
        print(f"✅ Cite keys file generated: {output_file}")
        print("=" * 80)
        print()
        print(f"Contains {len(ready_papers)} papers ready for Phase 3A pilot:")
        for cite_key in ready_papers:
            print(f"  - {cite_key}")
        print()
        print("Next steps:")
        print("  1. python build_pdf_index.py --pdf-dir 'D:/core/research/Program_verse/+/pdf'")
        print("  2. python extract_bibtex_subset.py --cite-keys pilot_cite_keys_psycho_crowdsourcing.txt")
        print("  3. python test_pdf_resolution.py --bibtex pilot_batch.bib")

if __name__ == "__main__":
    main()
