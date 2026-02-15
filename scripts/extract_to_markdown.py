#!/usr/bin/env python3
"""
Extract content from HTML files into a combined markdown file for LLM editing.

Usage:
    python extract_to_markdown.py

This script:
1. Reads all HTML files in the site
2. Extracts the main content section (between splitter divs)
3. Creates a combined markdown file with file markers
4. Converts HTML to readable markdown-like format
"""

import os
import re
from html.parser import HTMLParser
from pathlib import Path


class ContentExtractor(HTMLParser):
    """Extract and convert HTML content to markdown-like text."""

    def __init__(self):
        super().__init__()
        self.output = []
        self.in_heading = False
        self.in_link = False
        self.link_url = None
        self.list_level = 0
        self.code_level = 0
        self.skip_tags = {'script', 'style', 'noscript', 'iframe'}
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.code_level += 1
            return

        if self.code_level > 0:
            return

        # Flush any accumulated text before opening new tag
        self._flush_text()

        if tag == 'h2':
            self.in_heading = True
        elif tag == 'h3':
            self.output.append('\n### ')
        elif tag == 'a':
            self.in_link = True
            for attr, value in attrs:
                if attr == 'href':
                    self.link_url = value
        elif tag == 'li':
            indent = '  ' * self.list_level
            self.output.append(f'\n{indent}- ')
        elif tag == 'ul':
            self.list_level += 1
        elif tag == 'div' and any(cls in attrs for cls in attrs if cls[0] == 'class' and 'box1' in cls[1]):
            self.output.append('\n```\n')

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.code_level -= 1
            return

        if self.code_level > 0:
            return

        # Flush text before closing tag
        self._flush_text()

        if tag == 'h2':
            self.in_heading = False
        elif tag == 'a' and self.in_link:
            if self.link_url:
                self.output.append(f' ({self.link_url})')
            self.in_link = False
            self.link_url = None
        elif tag == 'ul':
            self.list_level -= 1
        elif tag == 'div' and self.output and '```' in ''.join(self.output[-3:]):
            self.output.append('\n```\n')

    def handle_data(self, data):
        if self.code_level > 0:
            return
        self.current_text.append(data)

    def _flush_text(self):
        """Flush accumulated text to output."""
        data = ''.join(self.current_text).strip()
        self.current_text = []

        if not data:
            return

        if self.in_heading:
            self.output.append(f'\n## {data}\n')
        elif data:
            self.output.append(data)

    def get_content(self):
        # Flush any remaining text
        self._flush_text()
        return ''.join(self.output)


def extract_main_content(html_content):
    """Extract the main content section from HTML.

    The main content is typically between:
    - <div class="splitter"></div> after the style block in the post area
    - And before disqus_thread or pagination

    Some pages have multiple content sections separated by splitter divs.
    We extract all of them.
    """
    # Find the post area first
    post_start = html_content.find('<div class="post text">')
    if post_start == -1:
        return None

    # Find where the post div ends
    # Look for either disqus_thread or pagination after the post
    post_end_patterns = [
        '<div id="disqus_thread">',
        '<nav id="pagination">'
    ]

    post_content = None
    for pattern in post_end_patterns:
        match = html_content.find(pattern, post_start)
        if match != -1:
            # Extract content between post_start and match
            # Find the closing </div> before disqus/pagination
            closing_div = html_content.rfind('</div>', post_start, match)
            if closing_div != -1:
                post_content = html_content[post_start:closing_div + 6]
                break

    if not post_content:
        # Alternative: find closing </div> and then check for wrapper end
        # Look for typical pattern: </div>\s*</div>\s*</div> (post, posts, wrapper)
        rest = html_content[post_start:]
        # Count divs to find proper closing
        depth = 0
        pos = 0
        in_tag = False
        tag_start = 0

        while pos < len(rest):
            if rest[pos] == '<':
                in_tag = True
                tag_start = pos
            elif rest[pos] == '>':
                if in_tag:
                    tag = rest[tag_start:pos+1]
                    if '<div' in tag:
                        depth += 1
                    elif '</div>' in tag:
                        depth -= 1
                        if depth == 0:
                            post_content = rest[:pos+6]
                            break
                    in_tag = False
            pos += 1

    if not post_content:
        return None

    # Remove inline style block at the start
    post_content = re.sub(r'<style>.+?</style>', '', post_content, flags=re.DOTALL).strip()

    # Find the first splitter (content starts after it)
    first_splitter = post_content.find('<div class="splitter"></div>')
    if first_splitter != -1:
        post_content = post_content[first_splitter + len('<div class="splitter"></div>'):]

    # Remove everything from disqus_thread onwards (if any slipped through)
    post_content = re.sub(r'<div id="disqus_thread">.+', '', post_content, flags=re.DOTALL)

    # Remove pagination section (if any slipped through)
    post_content = re.sub(r'<nav id="pagination">.+?</nav>', '', post_content, flags=re.DOTALL)

    # Clean up trailing whitespace
    post_content = post_content.strip()

    return post_content if post_content else None


def html_to_markdown(html_content):
    """Convert HTML content to markdown-like format."""
    parser = ContentExtractor()
    parser.feed(html_content)
    return parser.get_content().strip()


def process_html_files(directory):
    """Process all HTML files and create combined markdown."""
    html_files = sorted(Path(directory).glob('*.html'))

    combined_md = []
    combined_md.append("# Combined Website Content\n")
    combined_md.append("\nThis file contains the main content from all HTML pages.\n")
    combined_md.append("Each section is marked with `<!-- FILE: filename.html -->` and `<!-- END: filename.html -->`.\n")
    combined_md.append("Edit the content between these markers. The HTML structure will be preserved.\n\n")

    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extract main content
        main_content = extract_main_content(html_content)
        if not main_content:
            print(f"Warning: Could not extract content from {html_file.name}")
            continue

        # Convert to markdown-like format
        markdown_content = html_to_markdown(main_content)

        # Add file markers
        combined_md.append(f"<!-- FILE: {html_file.name} -->\n")
        combined_md.append(f"\n{markdown_content}\n\n")
        combined_md.append(f"<!-- END: {html_file.name} -->\n\n")
        combined_md.append("---\n\n")

        print(f"Extracted content from {html_file.name}")

    # Write combined markdown file
    output_path = Path(directory) / 'combined_content.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(combined_md))

    print(f"\nCombined markdown file created: {output_path}")


if __name__ == '__main__':
    # Get the directory containing this script, then use parent as site root
    script_dir = Path(__file__).parent
    site_dir = script_dir.parent

    print(f"Extracting content from: {site_dir}")
    process_html_files(site_dir)
