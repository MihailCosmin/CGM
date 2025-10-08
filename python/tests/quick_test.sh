#!/bin/bash
# Quick test script - runs regression test and opens report

cd "$(dirname "$0")"

echo "Running regression test..."
python regression_test.py --test --report

if [ $? -eq 0 ]; then
    echo ""
    echo "Opening report..."
    
    # Find most recent report
    REPORT=$(ls -t regression_reports/report_*.html 2>/dev/null | head -1)
    
    if [ -n "$REPORT" ]; then
        xdg-open "$REPORT" 2>/dev/null || firefox "$REPORT" 2>/dev/null || echo "Please open: $REPORT"
    fi
fi
