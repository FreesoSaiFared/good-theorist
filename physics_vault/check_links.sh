#!/bin/bash
echo "Checking accessibility of sources..."
echo ""

SUCCESS=0
FAILED=0
TIMEOUT=0

while IFS= read -r url; do
    [ -z "$url" ] && continue
    
    status=$(curl -sI -m 5 "$url" 2>/dev/null | head -1)
    
    if echo "$status" | grep -q "200"; then
        echo "✓ $url"
        ((SUCCESS++))
    elif echo "$status" | grep -q "404"; then
        echo "✗ 404: $url"
        ((FAILED++))
    elif echo "$status" | grep -q "301\|302"; then
        final_url=$(curl -sI -m 5 "$url" 2>/dev/null | grep -i "location:" | sed 's/.*: //' | tr -d '\r')
        echo "→ $url -> $final_url"
        ((SUCCESS++))
    else
        echo "? $status: $url"
        ((TIMEOUT++))
    fi
done < physics_vault/sources.txt

echo ""
echo "Summary:"
echo "  ✓ Accessible: $SUCCESS"
echo "  ✗ Failed (404): $FAILED"
echo "  ? Unknown/Timeout: $TIMEOUT"
