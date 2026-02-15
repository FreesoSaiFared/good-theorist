# Website Content Editing System

This system allows you to extract all website content into a single markdown file for easy LLM editing, then apply the changes back to the individual HTML files.

## How It Works

### Extraction (`extract_to_markdown.py`)

1. Reads all HTML files in the website
2. Extracts the main content section (between splitter divs and before disqus/pagination)
3. Converts HTML to a markdown-like format with:
   - `## Header` for h2 tags
   - `- List item` for li tags
   - `Link text (http://url)` for links
4. Creates `combined_content.md` with file markers like `<!-- FILE: filename.html -->`

### Application (`apply_from_markdown.py`)

1. Reads the edited `combined_content.md`
2. Extracts content for each file section
3. Converts markdown back to HTML
4. Replaces the content in the original HTML files

## Usage

```bash
# Extract content to markdown
python3 scripts/extract_to_markdown.py

# Edit the combined_content.md file (manually or with an LLM)

# Apply changes back to HTML
python3 scripts/apply_from_markdown.py
```

## Important Notes

### Limitations

1. **Merged List Sections**: If a page has multiple `<ul>` lists separated by `<div class="splitter"></div>`,
   they will be merged into a single list in the markdown and HTML after applying changes.

2. **Simplified Markdown**: The conversion is simplified. Complex HTML structures may not be preserved perfectly.

3. **File Markers**: Always preserve the `<!-- FILE: filename.html -->` and `<!-- END: filename.html -->` markers.

### Git Workflow

The scripts are designed to work with a git workflow:

```bash
# Create a git branch for edits
git checkout -b edit-content

# Extract content
python3 scripts/extract_to_markdown.py

# Commit the original combined_content.md
git add combined_content.md
git commit -m "Extract original content"

# Edit combined_content.md (manually or via LLM)

# Apply changes
python3 scripts/apply_from_markdown.py

# Commit the HTML changes
git add *.html
git commit -m "Apply content edits"
```

### Worktree Usage

For parallel editing without affecting the main working directory:

```bash
# Create a worktree for content processing
git worktree add ../content-worktree -b content-edit

# Work in the worktree
cd ../content-worktree

# Extract, edit, and apply
python3 scripts/extract_to_markdown.py
# Edit combined_content.md
python3 scripts/apply_from_markdown.py

# Commit and push changes
git add .
git commit -m "Edit content"
git push origin content-edit

# Clean up worktree when done
cd ..
git worktree remove content-worktree
```

## File Structure

The `combined_content.md` file structure:

```markdown
# Combined Website Content

This file contains main content from all HTML pages.
Each section is marked with `<!-- FILE: filename.html -->` and `<!-- END: filename.html -->`.

<!-- FILE: languages.html -->

## Languages
English is a prerequisite...

<!-- END: languages.html -->

---

<!-- FILE: qmech.html -->

## Quantum Mechanics (Non-relativistic)

  - Bohr's atom
  - DeBroglie's relations (Energy-frequency, momentum-wave number)
  ...

<!-- END: qmech.html -->

---
```

## Example LLM Prompt

When using an LLM to edit the content:

```
Please edit the content in combined_content.md. Follow these rules:
1. Keep all file markers intact: <!-- FILE: filename.html --> and <!-- END: filename.html -->
2. Edit only the text content, not the markdown formatting
3. Preserve the link format: Link text (http://url)
4. Keep list items as "- List item"
5. Keep headers as "## Header title"
```

## Troubleshooting

### Warning: "HTML file not found: filename.html"

This occurs when there's an issue parsing the combined_content.md file.
Make sure the file markers are properly formatted.

### Changes not appearing

1. Check that `combined_content.md` was edited after extraction
2. Verify the file markers are still intact
3. Run `python3 scripts/extract_to_markdown.py` to re-extract

### Content structure changed

As noted in limitations, multiple lists may be merged.
If exact structure preservation is critical, edit the HTML files directly instead.
