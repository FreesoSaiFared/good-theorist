# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static HTML website created by Nobel laureate Gerard 't Hooft, serving as a guide for students aspiring to become theoretical physicists. The site lists study topics and resources in logical progression from basic foundations through advanced theoretical physics.

## Architecture

The site follows a simple static HTML architecture with no build process:

- **HTML pages**: All content is in standalone `.html` files (e.g., `index.html`, `qmech.html`, `languages.html`)
- **Styles**: Single `stylesheet.css` file used by all pages
- **Assets**:
  - `Images/` - Contains the author's photo (`gerardth.JPG`)
  - `files/` - Contains PDF resources (citation style guides, optics materials)

### Page Structure

Each HTML file follows the same template pattern:
- **Sidebar navigation** (25% width) - Links to all topic pages, with the current page highlighted via CSS classes (`archive`, `ask`, `submit`)
- **Main content area** (75% width) - Contains the topic description and resource links
- **Pagination** - Navigation links at the bottom for Previous/Back to Home/Next pages

### Topic Pages (Logical Progression)

The sidebar lists subjects in approximate logical order:
1. Languages → Primary Mathematics → Classical Mechanics → Optics → Statistical Mechanics & Thermodynamics → Electronics → Electromagnetism → Computational Physics
2. Quantum Mechanics (Non-relativistic) → Atoms & Molecules → Solid State Physics → Nuclear Physics → Plasma Physics → Advanced Mathematics → Special Relativity
3. Advanced Quantum Mechanics → Phenomenology → General Relativity → Cosmology → Astro-Physics & Astronomy
4. Quantum Field Theory → Supersymmetry & Supergravity → Astro Particle Physics → Super String Theory
5. Texts & Other resources → Responses & Questions → Acknowledgements

The Languages section has sub-pages (dictionaries, grammar, vocabulary, punctuation, writing, pronunciation).

### External Dependencies

- Font Awesome: Loaded from `http://static.tumblr.com/dk2dlsp/ZJlmzhwlx/font-awesome.min.css`
- Google Fonts: Gentium Book Basic (imported in stylesheet.css)
- Disqus and Google Analytics: Currently configured with placeholder variables (`{text:Disqus Shortname}`, `{text:Google Analytics ID}`)

## Common Tasks

### Running/Viewing the Site

Since this is a static site with no build process:

```bash
# Simple Python HTTP server (Python 3)
python -m http.server 8000

# Or with Python 2
python -m SimpleHTTPServer 8000

# Or using any static file server
npx serve
```

Then navigate to `http://localhost:8000` in a browser.

### Adding a New Topic Page

1. Copy an existing HTML file as a template
2. Update the page title in the `<title>` tag and `<h2>` heading
3. Add the content in the main content area
4. Update the sidebar navigation to include the new link (must be added to ALL HTML files)
5. Update pagination links appropriately

### Modifying Content

- Text content is directly in HTML `<p>`, `<ul>`, `<li>` tags
- Resource links are standard `<a>` tags
- No database or CMS - all content is static HTML

### Styling

All styles are in `stylesheet.css`. The CSS uses:
- Flexbox-like grid system with `.bit-25` (25%) and `.bit-75` (75%) classes
- Responsive breakpoints at 30em and 50em for mobile/tablet
- Font: Gentium Book Basic (serif)

### File Naming

HTML files use descriptive names (e.g., `qmech.html` for Quantum Mechanics). Note that some files contain `&` in filenames (e.g., `atoms&molecules.html`, `texts&resources.html`, `responses&questions.html`) - when creating links, ensure proper URL encoding is maintained.
