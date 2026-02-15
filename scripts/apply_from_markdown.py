#!/usr/bin/env python3
"""
Apply changes from edited markdown file back to HTML files.

Usage:
    python apply_from_markdown.py

This script:
1. Reads the edited combined_content.md file
2. Extracts content for each file
3. Converts the markdown back to HTML
4. Applies changes to the original HTML files
"""

import os
import re
from pathlib import Path
from html import escape


def markdown_to_html(markdown_content):
    """Convert markdown-like content back to HTML.

    Note: This is a simplified conversion. For full markdown support,
    consider using a proper markdown-to-html library like markdown2 or mistune.
    """
    lines = markdown_content.split('\n')
    output = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        # Skip empty lines
        if not line:
            output.append('\n')
            i += 1
            continue

        # Headers
        if line.startswith('## '):
            text = line[3:].strip()
            output.append(f'\n                  <h2><p class="top-one"><center><b>{escape(text)}</b></center></p></h2>\n\n')
        elif line.startswith('### '):
            text = line[4:].strip()
            output.append(f'                  <p align="justify"><b>{escape(text)}</b></p>\n')
        # Unordered list items
        elif line.lstrip().startswith('- '):
            indent = len(line) - len(line.lstrip())
            text = line.lstrip()[2:]

            # Handle links inside list items: text (url)
            # This regex matches the last URL in parentheses
            link_match = re.search(r' \((https?://[^)]+)\)$', text)
            if link_match:
                url = link_match.group(1)
                link_text = text[:link_match.start()]
                output.append(f'<li><a href="{url}">{escape(link_text)}</a></li>\n')
            else:
                output.append(f'<li>{escape(text)}</li>\n')
        # Links in format: text (url) - standalone
        elif ' (http' in line and line.rstrip().endswith(')'):
            # Multiple links might be on one line, handle them
            parts = re.split(r' \((https?://[^)]+)\)', line)
            result = []
            for j in range(len(parts)):
                if j % 2 == 0:  # Text
                    if parts[j]:
                        result.append(escape(parts[j]))
                else:  # URL
                    url = parts[j]
                    prev_text = result[-1] if result else ''
                    if prev_text:
                        result[-1] = f'<a href="{url}">{prev_text}</a>'
                    else:
                        result.append(f'<a href="{url}">{url}</a>')
            output.append(f'                  <p align="justify">{"".join(result)}</p>\n')
        # Paragraphs
        elif line and not line.startswith('```'):
            output.append(f'                  <p align="justify">{escape(line)}</p>\n')
        # Code blocks
        elif line.startswith('```'):
            output.append(line + '\n')
        else:
            output.append(f'                  <p align="justify">{escape(line)}</p>\n')

        i += 1

    return ''.join(output)


def find_content_boundaries(html_content):
    """Find the boundaries of the main content section in HTML.

    Returns (start_pos, end_pos) for the content to be replaced.
    """
    # Find the post area first
    post_start = html_content.find('<div class="post text">')
    if post_start == -1:
        return None, None

    # Find where the post div ends
    # Look for either disqus_thread or pagination after the post
    post_end_patterns = [
        '<div id="disqus_thread">',
        '<nav id="pagination">'
    ]

    closing_div = None
    for pattern in post_end_patterns:
        match = html_content.find(pattern, post_start)
        if match != -1:
            # Find the closing </div> before disqus/pagination
            closing_div = html_content.rfind('</div>', post_start, match)
            if closing_div != -1:
                break

    if closing_div is None:
        return None, None

    post_content = html_content[post_start:closing_div + 6]

    # Remove inline style block at the start
    post_content = re.sub(r'<style>.+?</style>', '', post_content, flags=re.DOTALL).strip()

    # Find the first splitter (content starts after it)
    first_splitter = post_content.find('<div class="splitter"></div>')
    if first_splitter == -1:
        return None, None

    # Calculate the absolute position in the original HTML
    # The first_splitter is relative to post_content (which starts at post_start)
    # So the actual start is: post_start + offset to first_splitter in post_content
    # But post_content has had the style block removed, so we need to account for that

    # Better approach: work with original HTML to find the first splitter after the style block
    search_start = post_start
    style_match = re.search(r'<style>.+?</style>', html_content[search_start:], re.DOTALL)
    if style_match:
        search_start += style_match.end()

    # Find the first splitter after the style block
    first_splitter_abs = html_content.find('<div class="splitter"></div>', search_start)
    if first_splitter_abs == -1:
        return None, None

    # Content starts after this splitter
    content_start = first_splitter_abs + len('<div class="splitter"></div>')

    # Content ends at closing_div
    content_end = closing_div

    return content_start, content_end


def apply_content_to_html(html_file, new_content):
    """Apply new content to an HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Find content boundaries
    start_pos, end_pos = find_content_boundaries(html_content)
    if start_pos is None or end_pos is None:
        print(f"Warning: Could not find content boundaries in {html_file.name}")
        return False

    # Replace content
    new_html = html_content[:start_pos] + new_content + html_content[end_pos:]

    # Write back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_html)

    return True


def parse_combined_markdown(markdown_file):
    """Parse the combined markdown file and extract content for each file."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract sections between file markers
    sections = {}
    pattern = r'<!-- FILE: (.*?) -->(.+?)<!-- END: \1 -->'
    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        filename = match.group(1)
        section_content = match.group(2).strip()

        # Remove the separator lines (---) if present
        section_content = re.sub(r'^---\s*$', '', section_content, flags=re.MULTILINE).strip()

        sections[filename] = section_content

    return sections


def process_markdown_to_html(markdown_file, html_dir):
    """Process the edited markdown and apply to HTML files."""
    sections = parse_combined_markdown(markdown_file)
    html_dir = Path(html_dir)

    print(f"Processing {len(sections)} file sections...")

    success_count = 0
    for filename, content in sections.items():
        html_file = html_dir / filename
        if not html_file.exists():
            print(f"Warning: HTML file not found: {filename}")
            continue

        # Convert markdown to HTML
        new_content = markdown_to_html(content)

        # Apply to HTML file
        if apply_content_to_html(html_file, new_content):
            print(f"✓ Updated {filename}")
            success_count += 1
        else:
            print(f"✗ Failed to update {filename}")

    print(f"\nSuccessfully updated {success_count}/{len(sections)} files")
    return success_count == len(sections)


if __name__ == '__main__':
    script_dir = Path(__file__).parent
    site_dir = script_dir.parent
    markdown_file = site_dir / 'combined_content.md'

    if not markdown_file.exists():
        print(f"Error: {markdown_file} not found. Run extract_to_markdown.py first.")
        exit(1)

    print(f"Reading from: {markdown_file}")
    print(f"Applying to: {site_dir}\n")

    success = process_markdown_to_html(markdown_file, site_dir)

    if success:
        print("\nAll files updated successfully!")
    else:
        print("\nSome files had issues. Please review the warnings above.")
