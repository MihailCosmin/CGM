#!/bin/bash
# Quick Command Coverage Analysis
# Analyzes all CGM files and generates Excel report

cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════╗"
echo "║    CGM Command Coverage Analyzer                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Run analysis
/home/cosmin/Develop/CGM/.venv/bin/python analyze_command_coverage.py

# Check if report was generated
if [ -f "command_coverage_report.xlsx" ]; then
    echo ""
    echo "📊 Opening Excel report..."
    xdg-open command_coverage_report.xlsx 2>/dev/null &
    
    echo ""
    echo "✅ Analysis complete!"
    echo ""
    echo "Files generated:"
    echo "  - command_coverage_report.xlsx"
    echo ""
    echo "Documentation:"
    echo "  - README_COMMAND_COVERAGE.md"
    echo "  - COMMAND_COVERAGE_SUMMARY.md"
else
    echo ""
    echo "❌ Error: Report file not generated"
    exit 1
fi
