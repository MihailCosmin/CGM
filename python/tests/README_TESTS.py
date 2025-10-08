#!/usr/bin/env python3
"""
Quick example of using the regression test system
"""

import subprocess
import sys
from pathlib import Path

def main():
    tests_dir = Path(__file__).parent
    
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     CGM Regression Test System                           ║
║                           Quick Reference                                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

COMMON TASKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Run quick test (recommended):
   $ ./quick_test.sh
   
   This will:
   - Run full regression test
   - Generate HTML report
   - Open report in browser

2. Create/update baseline:
   $ ./update_baseline.sh
   
   Use this when you've verified that output improvements are correct.

3. Manual operations:
   $ python regression_test.py --create-baseline    # Create baseline
   $ python regression_test.py --test               # Run test only
   $ python regression_test.py --report             # Generate report only
   $ python regression_test.py --test --report      # Both

WORKFLOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Initial Setup:
  1. Verify current output is correct
  2. Run: ./update_baseline.sh

After Making Changes:
  1. Run: ./quick_test.sh
  2. Review report in browser
  3. If changes are improvements: ./update_baseline.sh

FILES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  regression_test.py      - Main test script
  quick_test.sh          - Quick test + report
  update_baseline.sh     - Update baseline (with confirmation)
  REGRESSION_TESTING.md  - Full documentation
  
  baseline/              - Known good outputs
  regression_output/     - Test run outputs
  regression_reports/    - HTML and text reports

EXAMPLE SESSION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # After fixing a bug in cleartextcgm_to_svg.py
  $ ./quick_test.sh
  
  # Review report in browser - all tests pass!
  # Update baseline to reflect the improvements
  $ ./update_baseline.sh
  yes
  
  ✓ Done! Future tests will compare against this new baseline.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For detailed information, see: REGRESSION_TESTING.md
""")

if __name__ == "__main__":
    main()
