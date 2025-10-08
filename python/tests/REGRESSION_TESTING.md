# CGM Regression Test Suite

This directory contains the regression test system for the CGM to SVG converter.

## Directory Structure

```
tests/
├── batch_tests/          # Current working directory with test CGM files
├── baseline/             # Baseline files for regression testing (created by test)
├── regression_output/    # Output from regression test runs
│   └── run_YYYYMMDD_HHMMSS/
│       ├── *_cleartext.cgm
│       ├── *.svg
│       └── test_results.json
└── regression_reports/   # HTML and text reports
    ├── report_YYYYMMDD_HHMMSS.html
    └── summary_YYYYMMDD_HHMMSS.txt
```

## Quick Start

### 1. Create Baseline (First Time)

This captures the current state as the "known good" baseline:

```bash
cd /home/cosmin/Develop/CGM/python/tests
python regression_test.py --create-baseline
```

This will:
- Back up any existing baseline
- Copy all `*_cleartext.cgm` files from `batch_tests/` to `baseline/`
- Copy all `*.svg` files from `batch_tests/` to `baseline/`
- Create metadata file

### 2. Run Regression Test

After making changes to the converter, test for regressions:

```bash
python regression_test.py --test
```

This will:
- Convert all binary `.CGM` files to cleartext
- Convert all cleartext files to SVG
- Compare generated files with baseline
- Report differences

### 3. Generate Report

Create a detailed HTML report:

```bash
python regression_test.py --report
```

Or combine test + report:

```bash
python regression_test.py --test --report
```

## Workflow

### Initial Setup
```bash
# 1. Make sure your current output is correct
cd /home/cosmin/Develop/CGM/python
python batch_tests.py  # or manually verify outputs

# 2. Create baseline
cd tests
python regression_test.py --create-baseline
```

### After Code Changes
```bash
# Run test and generate report
python regression_test.py --test --report

# View the report
firefox regression_reports/report_*.html
# or
cat regression_reports/summary_*.txt
```

### Understanding Results

#### Identical Files ✓
Files match the baseline exactly - no regressions detected.

#### Different Files ⚠
Files differ from baseline. Review the differences:
- **Expected**: If you intentionally improved the output
- **Regression**: If output quality degraded

#### Missing Files ⚠
New files not in baseline (usually not an issue).

### Updating Baseline

When you've verified that changes are improvements:

```bash
# Create new baseline (old one is automatically backed up)
python regression_test.py --create-baseline
```

## Report Details

### HTML Report
- Full summary with statistics
- Conversion success/failure for each file
- Detailed comparison results
- Line-by-line difference counts

### Text Summary
- Quick overview of test results
- List of files with differences
- Easy to review in terminal

## Example Output

```
================================================================================
RUNNING REGRESSION TEST
================================================================================

Output directory: tests/regression_output/run_20251008_104531

Found 25 binary CGM files to process

[1/25] Processing ICN-07GB6-BIKECI0001-001-01.CGM...
  Converting to cleartext...
  ✓ Created ICN-07GB6-BIKECI0001-001-01_cleartext.cgm
  Converting to SVG...
  ✓ Created ICN-07GB6-BIKECI0001-001-01.svg

...

================================================================================
COMPARING WITH BASELINE
================================================================================

Comparing cleartext CGM files...
  ✓ ICN-07GB6-BIKECI0001-001-01_cleartext.cgm: Identical
  ✓ ICN-C0419-S1000D0361-001-01_cleartext.cgm: Identical
  ...

Comparing SVG files...
  ✓ ICN-07GB6-BIKECI0001-001-01.svg: Identical
  ⚠ ICN-C0419-S1000D0361-001-01.svg: Different (+5/-3 lines)
  ...

================================================================================
COMPARISON SUMMARY
================================================================================

Cleartext CGM files:
  Total: 25
  ✓ Identical: 25

SVG files:
  Total: 25
  ✓ Identical: 24
  ⚠ Different: 1
```

## Prerequisites

- Python 3.6+
- `cgmcli` tool compiled and available at:
  - `/home/cosmin/Develop/CGM/bin/Release/net8.0/linux-x64/publish/cgmcli`
  - OR `/home/cosmin/Develop/CGM/bin/Debug/net8.0/cgmcli`
- `cleartextcgm_to_svg.py` in the python directory

## Tips

1. **Run tests frequently** - Catch regressions early
2. **Review differences** - Not all changes are bad
3. **Update baseline** - When improvements are verified
4. **Keep old baselines** - Automatically backed up with timestamp
5. **Check reports** - HTML report shows detailed information

## Troubleshooting

### "cgmcli tool not found"
Make sure the C# tool is compiled:
```bash
cd /home/cosmin/Develop/CGM
dotnet publish -c Release
```

### "No baseline found"
Run `--create-baseline` first before running tests.

### "Permission denied"
Make sure the script is executable:
```bash
chmod +x regression_test.py
```
