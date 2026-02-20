# CGM Command Coverage Analyzer

## Overview
This tool analyzes all cleartext CGM files in the `batch_tests` folder and generates a comprehensive Excel report showing:
- Which CGM commands are present in the files
- How each command is converted to SVG (or if it's not handled)
- Command frequency and distribution across files

## Usage

```bash
cd /home/cosmin/Develop/CGM/python/tests
/home/cosmin/Develop/CGM/.venv/bin/python analyze_command_coverage.py
```

Or use the shortcut:
```bash
./analyze_command_coverage.py
```

## Output

The tool generates `command_coverage_report.xlsx` with 4 sheets:

### 1. Summary
- Overall statistics (total files, commands, coverage percentage)
- Top 10 most common commands
- Quick overview of analysis results

### 2. Command List
- Complete list of all unique commands found
- Total count for each command across all files
- SVG conversion mapping for each command
- Status indicator (Handled/Not Handled)
- Color-coded: Green = handled, Red = not handled

### 3. File-by-File Analysis
- Detailed breakdown per CGM file
- Shows which commands appear in each file
- Command frequency within each file
- SVG conversion for each command
- Grouped by file with visual separators

### 4. Unhandled Commands
- Lists all commands that are NOT currently converted to SVG
- Shows total count for each unhandled command
- Indicates how many files contain each unhandled command
- Priority indicator for implementation

## Current Coverage

**Latest Results** (as of October 8, 2025):
- **Total Files Analyzed**: 41 cleartext CGM files
- **Total Unique Commands**: 77
- **Handled Commands**: 63
- **Unhandled Commands**: 14
- **Coverage**: 81.8%

### Unhandled Commands
Most unhandled commands are metadata/setup commands or advanced styling:
- `indexprec`, `vdcintegerprec` - Precision setup (no visual impact)
- `CHAREXPAN` - Character expansion factor
- `EDGECAP`, `EDGEJOIN` - Edge styling
- `FONTPROP` - Font properties
- `LINETYPECONT`, `LINETYPEDEF` - Custom line types
- `MARKERSIZEMODE` - Marker sizing
- `IsoDraw` - Application-specific metadata
- Numbers (0, 1, 3, 29) - Likely parsing artifacts

## Command Mapping Examples

### Graphical Primitives
- `LINE` → `SVG: <line> or <polyline>`
- `POLYGON` → `SVG: <polygon>`
- `CIRCLE` → `SVG: <circle>`
- `POLYBEZIER` → `SVG: <path> (bezier curves)`
- `TEXT` → `SVG: <text> with transform`

### Attributes
- `linewidth` → `State: line_width`
- `linecolr` → `State: line_color`
- `fillcolr` → `State: fill_color`
- `textfontindex` → `State: text_font_index`

### Structural
- `BEGMF` → `XML Comment (Metafile)`
- `BEGPIC` → `XML Comment (Picture)`
- `vdcext` → `State: vdc_extent (viewport)`

## Dependencies

```bash
pip install openpyxl
```

Or in virtual environment:
```bash
/home/cosmin/Develop/CGM/.venv/bin/python -m pip install openpyxl
```

## Implementation Details

The analyzer:
1. Scans all `*_cleartext.cgm` files in `batch_tests/`
2. Extracts command names using regex pattern matching
3. Maps commands to their SVG conversions based on `cleartextcgm_to_svg.py`
4. Generates multi-sheet Excel report with formatting and color coding
5. Provides statistics and prioritization for unhandled commands

## Use Cases

1. **Quality Assurance**: Verify all CGM commands are properly handled
2. **Development**: Identify which commands need implementation
3. **Documentation**: Understand command distribution in real-world files
4. **Testing**: Ensure no regressions when modifying the converter
5. **Prioritization**: Focus on most frequently used unhandled commands

## Notes

- Commands are case-insensitive in matching
- Setup/metadata commands that don't affect rendering are marked as "No output (setup)"
- State-changing commands are marked as "State: <variable_name>"
- Visual elements are marked as "SVG: <element_type>"

## Related Files

- `cleartextcgm_to_svg.py` - Main converter implementation
- `batch_tests/` - Test CGM files
- `command_coverage_report.xlsx` - Generated report
