#!/usr/bin/env python3
"""
Sort keys inside INI sections (preserves section order by default).
Improved version with better comment handling and backup naming.

Usage:
    sort_ini.py file1.ini [file2.ini ...]
    sort_ini.py --sort-sections file1.ini
    sort_ini.py --dry-run file1.ini

Creates backup in "Backup YYYY-MM-DD HH-MM" folder next to each file.

Vibecoded with Grok because I can't code 🤷‍♂️
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import OrderedDict


def parse_ini(content: str):
    """
    Parse INI into ordered structure.
    Tries to keep comments attached to the following key when possible.
    Empty lines are treated as weak separators and are not forced inside sections.
    """
    lines = content.splitlines(keepends=True)
    sections = OrderedDict()
    current_section = None
    header = []          # everything before first section
    pending_comments = []  # comments waiting to be attached to next key

    def flush_pending_as_orphan():
        """Put pending non-empty comments as orphan items. Drop pure empty lines."""
        nonlocal pending_comments
        if current_section is not None:
            for c in pending_comments:
                if c.strip():  # keep real comments, drop blank lines
                    sections[current_section]['items'].append({
                        'type': 'comment',
                        'line': c
                    })
        else:
            # In header we keep everything (including blanks)
            header.extend(pending_comments)
        pending_comments = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Section header
        if stripped.startswith('[') and stripped.endswith(']') and len(stripped) > 2:
            flush_pending_as_orphan()

            section_name = stripped[1:-1].strip()
            current_section = section_name
            if current_section not in sections:
                sections[current_section] = {
                    'items': []
                }
            i += 1
            continue

        # Empty line or comment
        if not stripped or stripped.startswith(';') or stripped.startswith('#'):
            pending_comments.append(line)
            i += 1
            continue

        # Key = value (or just key)
        if current_section is not None:
            key = stripped.split('=', 1)[0].strip() if '=' in stripped else stripped
            sections[current_section]['items'].append({
                'type': 'key',
                'key': key,
                'line': line,
                'comments_before': pending_comments[:]
            })
            pending_comments = []
            i += 1
            continue

        # Outside any section
        header.extend(pending_comments)
        pending_comments = []
        header.append(line)
        i += 1

    # Trailing comments
    flush_pending_as_orphan()

    return header, sections


def sort_section_items(items):
    """
    Sort key items. Comments that were before a key stay with that key.
    Orphan (section-level) comments go to the top of the section.
    """
    orphans = []
    keyed = []

    for item in items:
        if item['type'] == 'comment':
            orphans.append(item)
        else:
            keyed.append(item)

    # Sort by key (case-insensitive)
    keyed.sort(key=lambda x: x['key'].lower())

    result_lines = []

    # Section-level comments first
    for item in orphans:
        result_lines.append(item['line'])

    # Then sorted keys with their attached comments
    for item in keyed:
        for c in item.get('comments_before', []):
            # Skip pure empty lines that were attached — we control spacing ourselves
            if c.strip():
                result_lines.append(c)
        result_lines.append(item['line'])

    return result_lines


def generate_sorted_content(header, sections, sort_sections=False) -> str:
    out = []

    # Header (before first section)
    if header:
        # Remove trailing blank lines from header — we will control spacing
        while header and not header[-1].strip():
            header.pop()
        out.extend(header)
        if out and not out[-1].endswith('\n'):
            out[-1] += '\n'

    section_names = list(sections.keys())
    if sort_sections:
        section_names = sorted(section_names, key=str.lower)

    for idx, section_name in enumerate(section_names):
        data = sections[section_name]

        # Blank line BEFORE section header (except before the very first section
        # when there was no header content)
        if out:
            # Ensure exactly one blank line before the section
            if out[-1].endswith('\n'):
                if not (len(out) >= 2 and out[-2].endswith('\n') and out[-1] == '\n'):
                    # previous line ends with \n, add one more blank line
                    if out[-1] != '\n':
                        out.append('\n')
            else:
                out.append('\n\n')
        elif idx > 0:
            out.append('\n')

        out.append(f'[{section_name}]\n')

        sorted_lines = sort_section_items(data['items'])
        out.extend(sorted_lines)

        # Make sure last line of section ends with newline
        if out and not out[-1].endswith('\n'):
            out[-1] += '\n'

    content = ''.join(out)

    # Ensure file ends with a single newline
    content = content.rstrip('\n') + '\n'
    return content


def process_file(filepath: Path, sort_sections=False, dry_run=False):
    if not filepath.is_file():
        print(f"Skip (not a file): {filepath}")
        return

    print(f"Processing: {filepath}")

    try:
        original = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"  ✗ Error reading: {e}")
        return

    header, sections = parse_ini(original)
    sorted_content = generate_sorted_content(header, sections, sort_sections=sort_sections)

    # Normalize for comparison (ignore pure line-ending differences)
    def normalize(s):
        return s.replace('\r\n', '\n').replace('\r', '\n')

    if normalize(original) == normalize(sorted_content):
        print("  ✓ Already sorted — nothing to do.")
        return

    if dry_run:
        print("  [dry-run] Would sort the file.")
        return

    # Create backup folder with date + time
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M")
    backup_dir = filepath.parent / f"Backup {date_str} {time_str}"
    backup_dir.mkdir(exist_ok=True)

    backup_path = backup_dir / filepath.name

    if backup_path.exists():
        backup_path = backup_dir / f"{filepath.stem}_{now.strftime('%H-%M-%S')}{filepath.suffix}"

    try:
        backup_path.write_text(original, encoding='utf-8')
        print(f"  ✓ Backup → {backup_path}")
    except Exception as e:
        print(f"  ✗ Failed to create backup: {e}")
        return

    # Write sorted version (preserve original line ending style)
    try:
        final_content = sorted_content
        if '\r\n' in original:
            final_content = sorted_content.replace('\n', '\r\n')

        filepath.write_text(final_content, encoding='utf-8')
        print(f"  ✓ Sorted and saved.")
    except Exception as e:
        print(f"  ✗ Error writing sorted file: {e}")
        try:
            filepath.write_text(original, encoding='utf-8')
            print("  ✓ Restored original.")
        except Exception:
            print("  ✗ CRITICAL: could not restore original!")


def main():
    parser = argparse.ArgumentParser(
        description="Sort keys inside INI sections. Creates dated backup."
    )
    parser.add_argument("files", nargs="+", help="INI files to process")
    parser.add_argument(
        "--sort-sections",
        action="store_true",
        help="Also sort section names alphabetically"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be done, do not write files"
    )

    args = parser.parse_args()

    for f in args.files:
        process_file(Path(f).resolve(), sort_sections=args.sort_sections, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
