#!/usr/bin/env python3
"""
Extract BibTeX Subset for Phase 3A Pilot

This script extracts a subset of BibTeX entries from My Library.bib
based on a list of cite keys. Used for Phase 3A pilot testing with
"Psycho Studies on crowdsourcing" connection note.

Usage:
    python extract_bibtex_subset.py --cite-keys pilot_cite_keys_psycho_crowdsourcing.txt
    python extract_bibtex_subset.py --input custom.bib --cite-keys keys.txt --output subset.bib
"""

import re
import argparse
from pathlib import Path
from datetime import datetime


def parse_bibtex_entries(bibtex_content):
    """
    Parse BibTeX file into individual entries.

    Returns:
        dict: {cite_key: full_entry_text, ...}
    """
    entries = {}

    # Match @type{CiteKey, ... } with nested braces support
    # This regex captures the full entry including nested braces
    pattern = r'(@\w+\{[^@]+)'

    matches = re.finditer(pattern, bibtex_content, re.MULTILINE | re.DOTALL)

    for match in matches:
        entry_text = match.group(1)

        # Extract cite key from first line: @article{CiteKey,
        cite_key_match = re.match(r'@\w+\{([^,]+),', entry_text)
        if cite_key_match:
            cite_key = cite_key_match.group(1).strip()
            entries[cite_key] = entry_text

    return entries


def load_cite_keys(cite_keys_file):
    """Load cite keys from text file (one per line)."""
    cite_keys = []

    with open(cite_keys_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                cite_keys.append(line)

    return cite_keys


def main():
    parser = argparse.ArgumentParser(
        description="Extract BibTeX subset for Phase 3A pilot"
    )
    parser.add_argument(
        '--input',
        type=str,
        default='D:/core/research/Program_verse/+/My Library.bib',
        help='Input BibTeX file (default: My Library.bib)'
    )
    parser.add_argument(
        '--cite-keys',
        type=str,
        required=True,
        help='Text file containing cite keys (one per line)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='pilot_batch.bib',
        help='Output BibTeX file (default: pilot_batch.bib)'
    )

    args = parser.parse_args()

    # Set UTF-8 output
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 80)
    print("BibTeX Subset Extractor - Phase 3A Pilot")
    print("=" * 80)
    print()
    print(f"Input BibTeX: {args.input}")
    print(f"Cite Keys: {args.cite_keys}")
    print(f"Output BibTeX: {args.output}")
    print()

    # Load cite keys
    try:
        cite_keys = load_cite_keys(args.cite_keys)
        print(f"Loaded {len(cite_keys)} cite keys from {args.cite_keys}")
        print()
    except Exception as e:
        print(f"❌ Error loading cite keys: {e}")
        return 1

    # Load and parse BibTeX
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ BibTeX file not found: {input_path}")
        return 1

    print(f"Parsing BibTeX file ({input_path.stat().st_size / 1024 / 1024:.1f} MB)...")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            bibtex_content = f.read()

        entries = parse_bibtex_entries(bibtex_content)
        print(f"Found {len(entries)} entries in BibTeX file")
        print()
    except Exception as e:
        print(f"❌ Error parsing BibTeX: {e}")
        return 1

    # Extract subset
    print("=" * 80)
    print("Extracting Entries")
    print("=" * 80)
    print()

    extracted = []
    missing = []

    for cite_key in cite_keys:
        if cite_key in entries:
            extracted.append(entries[cite_key])
            print(f"✅ {cite_key}")
        else:
            missing.append(cite_key)
            print(f"❌ {cite_key} - NOT FOUND")

    print()
    print("-" * 80)
    print(f"Extracted: {len(extracted)}/{len(cite_keys)} entries")
    if missing:
        print(f"Missing: {len(missing)} entries")
    print("-" * 80)
    print()

    # Write output
    if extracted:
        output_path = Path(args.output)

        # Build output content
        output_lines = [
            f"% BibTeX Subset for Phase 3A Pilot",
            f"% Generated: {datetime.now().isoformat()}",
            f"% Source: {input_path.name}",
            f"% Entries: {len(extracted)}/{len(cite_keys)}",
            "",
        ]

        for entry in extracted:
            output_lines.append(entry)
            output_lines.append("")  # Blank line between entries

        output_content = "\n".join(output_lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)

        print("=" * 80)
        print(f"✅ BibTeX subset saved to: {output_path.absolute()}")
        print("=" * 80)
        print()
        print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")
        print()

    # Summary
    if missing:
        print("⚠️  Missing Entries:")
        for cite_key in missing:
            print(f"  - {cite_key}")
        print()
        print("Possible reasons:")
        print("  1. Cite key not in BibTeX file")
        print("  2. Special character mismatch (é→e)")
        print("  3. Cite key format different from expected")
        print()

    # Next steps
    print("Next steps:")
    if len(extracted) >= len(cite_keys) * 0.9:  # >= 90% success
        print("  ✅ Ready to proceed with Phase 3A pilot")
        print(f"  1. python test_pdf_resolution.py --bibtex {args.output} --pdf-index pdf_index.json")
        print(f"  2. python batch_process.py --from-bibtex {args.output} ...")
    else:
        print("  ⚠️  Less than 90% of entries found")
        print("  1. Review missing entries above")
        print("  2. Check cite key format in BibTeX file")
        print("  3. Consider manual addition or cite key correction")

    print()

    return 0


if __name__ == "__main__":
    exit(main())
