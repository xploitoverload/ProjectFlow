#!/bin/bash

# Real-time monitoring of facial verification logs
# Run this in a separate terminal while you test

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║ FACIAL VERIFICATION LIVE DEBUG MONITOR                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Monitoring logs with color highlighting..."
echo "🔴 Errors in RED"
echo "🟡 Warnings in YELLOW"  
echo "🟢 Success in GREEN"
echo "🔵 Info in BLUE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

tail -f /tmp/flask_app.log | grep --line-buffered -E "facial|VERIFY|Face|face|encoding|distance|confidence|match" | while IFS= read -r line; do
    if echo "$line" | grep -q "❌\|ERROR\|Error\|FAILED"; then
        echo -e "\033[91m$line\033[0m"  # Red for errors
    elif echo "$line" | grep -q "⚠️\|WARNING\|warning"; then
        echo -e "\033[93m$line\033[0m"  # Yellow for warnings
    elif echo "$line" | grep -q "✅\|SUCCESS\|success\|MATCH"; then
        echo -e "\033[92m$line\033[0m"  # Green for success
    elif echo "$line" | grep -q "VERIFY-START\|VERIFY-PROCESS"; then
        echo -e "\033[94m$line\033[0m"  # Blue for process steps
    else
        echo "$line"
    fi
done
