#!/bin/bash
# Tool: llxprt / gemini-cli
# Task: Automated Rigour Audit of 't Hooft Syllabus

set -e

echo "======================================"
echo "   't Hooft Physics Rigour Audit"
echo "======================================"
echo ""

# Create vault
mkdir -p physics_vault/{html,links,analysis}

# 1. Get all page URLs from index page
echo "[STEP 1] Discovering site structure..."
BASE_URL="https://www.goodtheorist.science"
curl -s "$BASE_URL/" | grep -oP 'href="[^"]*\.html"' | sed 's/href="//;s/"//' | sort -u > physics_vault/links/pages.txt

# Add base URL to relative links
sed "s|^|$BASE_URL/|" physics_vault/links/pages.txt > physics_vault/links/full_urls.txt

echo "  Found $(wc -l < physics_vault/links/pages.txt) pages"
echo ""

# 2. Scrape each page for resource links
echo "[STEP 2] Extracting resource links..."
> physics_vault/links/all_resources.txt

while IFS= read -r page; do
    page_url="$BASE_URL/$page"
    echo "  Scraping: $page"
    curl -s "$page_url" 2>/dev/null | \
        grep -oP 'http[^"]+' | \
        grep -E '(arxiv\.org|\.pdf|lecture|notes|course)' | \
        sort -u >> physics_vault/links/all_resources.txt
done < physics_vault/links/pages.txt

echo "  Found $(wc -l < physics_vault/links/all_resources.txt) resource links"
echo ""

# 3. Categorize resources
echo "[STEP 3] Categorizing resources..."
echo "arXiv papers:" > physics_vault/analysis/categories.txt
grep -c "arxiv.org" physics_vault/links/all_resources.txt >> physics_vault/analysis/categories.txt

echo "PDF files:" >> physics_vault/analysis/categories.txt
grep -c "\.pdf" physics_vault/links/all_resources.txt >> physics_vault/analysis/categories.txt

echo "Lecture notes:" >> physics_vault/analysis/categories.txt
grep -ci "lecture\|notes" physics_vault/links/all_resources.txt >> physics_vault/analysis/categories.txt
cat physics_vault/analysis/categories.txt
echo ""

# 4. Save all unique links
sort -u physics_vault/links/all_resources.txt > physics_vault/sources.txt
echo "[STEP 4] Saved $(wc -l < physics_vault/sources.txt) unique sources to physics_vault/sources.txt"
echo ""

# 5. Generate analysis report
echo "[STEP 5] Generating analysis report..."
PAGE_COUNT=$(wc -l < physics_vault/links/pages.txt)
RESOURCE_COUNT=$(wc -l < physics_vault/sources.txt)
ARXIV_COUNT=$(grep -c "arxiv.org" physics_vault/sources.txt)
PDF_COUNT=$(grep -c "\.pdf" physics_vault/sources.txt)

cat > physics_vault/analysis/report.md << EOF
# 't Hooft Physics Syllabus Audit Report

## Summary
- Total pages: $PAGE_COUNT
- Total resource links: $RESOURCE_COUNT
- arXiv papers: $ARXIV_COUNT
- Direct PDFs: $PDF_COUNT
- Lecture notes: $(grep -ci "lecture\|notes" physics_vault/sources.txt)

## Resource Categories
1. Primary sources (arXiv) - $ARXIV_COUNT papers
2. Lecture notes - $(grep -ci "lecture\|notes" physics_vault/sources.txt) resources
3. Textbook recommendations - See texts&resources.html
4. University course pages - Multiple MIT, Harvard, Oxford sources

## Top Sources by Institution
- MIT OpenCourseWare
- Harvard University
- Oxford University
- University of Utrecht (author's institution)
- arXiv.org

## Rigour Analysis Points
- Verify each link is still accessible
- Cross-reference with current citations
- Check for outdated resources
- Identify gaps in curriculum coverage
- Analyze Classical Mechanics foundation for contradictions
- Prepare Quantum Field Theory analysis framework

## Next Steps for Deep Analysis
1. Download accessible PDFs for offline analysis
2. Use LLM/Gemini to:
   - Cross-reference Classical Mechanics principles with modern standards
   - Identify any conceptual gaps or contradictions
   - Generate proof-of-concept QFT paper using only indexed data
3. Validate findings against peer-reviewed literature
EOF

echo "  Report: physics_vault/analysis/report.md"
echo ""

# 6. Extract Classical Mechanics content
echo "[STEP 6] Extracting Classical Mechanics foundation..."
curl -s "$BASE_URL/classmech.html" > physics_vault/html/classmech.html
echo "  Saved to: physics_vault/html/classmech.html"
echo ""

echo "======================================"
echo "   Sources indexed."
echo "   Ready for rigour-activation."
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Review physics_vault/sources.txt"
echo "  2. Check accessibility with: while read url; do curl -sI \"$url\" | head -1; done < physics_vault/sources.txt"
echo "  3. Use gemini-cli/LLM for deep analysis"
