#!/bin/bash

echo "=== CSS AUDIT ANALYSIS ==="
echo ""
echo "Files with NO media queries:"
for file in *.css; do
  count=$(grep -c "@media" "$file" 2>/dev/null || echo 0)
  if [ "$count" -eq 0 ]; then
    echo "  - $file"
  fi
done

echo ""
echo "Hardcoded pixel measurements (not responsive):"
cd "/home/KALPESH/Stuffs/Project Management/static/css"
for file in *.css; do
  pixels=$(grep -E "width:\s*[0-9]+px|height:\s*[0-9]+px|padding:\s*[0-9]+px|margin:\s*[0-9]+px" "$file" | wc -l)
  if [ "$pixels" -gt 20 ]; then
    echo "  - $file: $pixels instances"
  fi
done

echo ""
echo "Mobile-specific issues - max-width analysis:"
grep -l "max-width: 640px\|max-width: 768px\|max-width: 480px" *.css

echo ""
echo "Checking for rem/em usage (responsive typography):"
for file in *.css; do
  rem_count=$(grep -E "font-size:.*rem|font-size:.*em" "$file" | wc -l)
  if [ "$rem_count" -gt 0 ]; then
    echo "  - $file: $rem_count rem/em rules"
  fi
done
