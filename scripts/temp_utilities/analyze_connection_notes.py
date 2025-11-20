#!/usr/bin/env python3
"""
Analyze Connection notes in ACT directory to find suitable pilot papers for Phase 3.

This script:
1. Scans annotation notes (@*.md) to extract their connection tags
2. Counts papers per connection note
3. Extracts cite keys from annotation filenames
4. Recommends suitable connection notes for pilot (10-20 papers)
"""

import os
import re
from collections import defaultdict
from pathlib import Path

# Paths
ACT_DIR = Path(r"D:\core\research\Program_verse\ACT")
ANNOTATION_DIR = ACT_DIR / "0️⃣Annotation"
CONN_DIR = ACT_DIR / "1️⃣Conn"

def extract_conn_tag(md_file):
    """Extract connection tag from annotation note frontmatter."""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Match: conn: "[[🔗Connection Name]]" or conn: [[🔗Connection Name]]
        match = re.search(r'conn:\s*"?\[\[([^\]]+)\]\]"?', content)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error reading {md_file.name}: {e}")
    return None

def extract_cite_key(filename):
    """Extract cite key from @Author-Year.md format."""
    # Remove @, .md suffix
    if filename.startswith('@') and filename.endswith('.md'):
        return filename[1:-3]  # Remove @ prefix and .md suffix
    return None

def main():
    # Set UTF-8 output encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 80)
    print("Connection Notes Analysis for Phase 3 Pilot Selection")
    print("=" * 80)
    print()

    # Scan annotation notes
    conn_papers = defaultdict(list)  # {connection_name: [(cite_key, filename), ...]}

    annotation_files = list(ANNOTATION_DIR.glob("@*.md"))
    print(f"Scanning {len(annotation_files)} annotation notes...")
    print()

    for md_file in annotation_files:
        conn_tag = extract_conn_tag(md_file)
        cite_key = extract_cite_key(md_file.name)

        if conn_tag and cite_key:
            conn_papers[conn_tag].append((cite_key, md_file.name))

    # Sort by paper count
    sorted_conns = sorted(conn_papers.items(), key=lambda x: len(x[1]), reverse=True)

    # Print statistics
    print(f"Found {len(sorted_conns)} connection notes with papers")
    print()
    print("-" * 80)
    print(f"{'Connection Note':<60} {'Papers':>8}")
    print("-" * 80)

    for conn_name, papers in sorted_conns:
        print(f"{conn_name:<60} {len(papers):>8}")

    print("-" * 80)
    print()

    # Recommend pilot candidates (10-20 papers)
    print("=" * 80)
    print("Recommended Pilot Candidates (10-20 papers)")
    print("=" * 80)
    print()

    pilot_candidates = [
        (conn_name, papers)
        for conn_name, papers in sorted_conns
        if 10 <= len(papers) <= 20
    ]

    if pilot_candidates:
        for i, (conn_name, papers) in enumerate(pilot_candidates, 1):
            print(f"{i}. {conn_name} ({len(papers)} papers)")
            print(f"   Connection file: 1️⃣Conn/{conn_name}.md")
            print(f"   Sample papers:")
            for cite_key, filename in papers[:5]:
                print(f"     - {cite_key} ({filename})")
            if len(papers) > 5:
                print(f"     ... and {len(papers) - 5} more")
            print()
    else:
        print("No connection notes with exactly 10-20 papers found.")
        print()
        print("Alternatives:")

        # Show connections with 6-10 papers (can combine)
        small_conns = [(c, p) for c, p in sorted_conns if 6 <= len(p) < 10]
        if small_conns:
            print()
            print("Connections with 6-9 papers (can combine 2-3 for pilot):")
            for conn_name, papers in small_conns:
                print(f"  - {conn_name} ({len(papers)} papers)")

        # Show connections with 21-30 papers (can subset)
        large_conns = [(c, p) for c, p in sorted_conns if 21 <= len(p) <= 30]
        if large_conns:
            print()
            print("Connections with 21-30 papers (can select subset for pilot):")
            for conn_name, papers in large_conns:
                print(f"  - {conn_name} ({len(papers)} papers)")

    print()
    print("=" * 80)
    print("Cite Key Extraction for Selected Connection")
    print("=" * 80)
    print()

    # Ask user to select (for future use)
    if pilot_candidates:
        selected_conn = pilot_candidates[0][0]  # Default: first candidate
        selected_papers = pilot_candidates[0][1]

        print(f"Example: Cite keys for '{selected_conn}':")
        print()
        for cite_key, filename in selected_papers:
            print(cite_key)

        print()
        print(f"To use these papers, save cite keys to a file:")
        print(f"  1. Copy cite keys above")
        print(f"  2. Save to 'pilot_cite_keys_{selected_conn.replace('🔗', '').replace(' ', '_')}.txt'")
        print(f"  3. Run: python extract_bibtex_subset.py --cite-keys <file>")

    print()
    print("Analysis complete!")

if __name__ == "__main__":
    main()
