# Critical Cleartext Format Issues

## Problem Summary

The Python binary-to-cleartext converter is producing output that is **fundamentally different** from the C# reference implementation. The differences are not just cosmetic - they represent incorrect command formatting according to ISO/IEC 8632-4:1999.

## Comparison: C# (CORRECT) vs Python (WRONG)

### Command Case
- **C# (✓)**: Uses lowercase: `mfversion`, `mfdesc`, `charsetlist`
- **Python (✗)**: Uses UPPERCASE: `MFVERSION`, `MFDESC`, `CHARSETLIST`

### MFVERSION
- **C# (✓)**: ` mfversion 4;`
- **Python (✗)**: `MFVERSION 4;`

### MFELEMLIST  
- **C# (✓)**: ` mfelemlist 'VERSION4';`
- **Python (✗)**: `MFELEMLIST 6 -1;`

### FONTPROP
- **C# (✓)**: Full parameter list
  ```
  FONTPROP 1 10 11 1 1 4 5 14 1 'ARIAL' 5 5 11 1 1 6 5 11 1 5 7 2 11 1 5 13 1 18 3 0 0 0 14 1 11 1 0;
  ```
- **Python (✗)**: Commented out stub
  ```
  % FONTPROP ;
  ```

### CHARSETLIST
- **C# (✓)**: ` charsetlist STD94 'B' STD96 'A';`
- **Python (✗)**: `  CHARSETLIST completelist 'ISO 8859-1' ;`

### Precision Commands
**COLRPREC:**
- **C# (✓)**: ` colrprec 255;`
- **Python (✗)**: `COLRPREC 8;`

**COLRINDEXPREC:**
- **C# (✓)**: ` colrindexprec 127;`
- **Python (✗)**: `COLRINDEXPREC 8;`

**COLRVALUEEXT:**
- **C# (✓)**: ` colrvalueext 0 0 0, 255 255 255;`
- **Python (✗)**: `  COLRVALUEEXT 0 255 0 255 0 255 ;`

**MAXCOLRINDEX:**
- **C# (✓)**: ` maxcolrindex 1;`
- **Python (✗)**: `  MAXCOLRINDEX 255 ;`

**INTEGERPREC:**
- **C# (✓)**: ` integerprec -32768, 32767 % 16 binary bits %;`
- **Python (✗)**: `INTEGERPREC 16;`

**REALPREC:**
- **C# (✓)**: ` realprec -511.0000, 511.0000, 7 % 10 binary bits %;`
- **Python (✗)**: `REALPREC 0 9 23;`

### SCALEMODE
- **C# (✓)**: `  scalemode metric, 1.0000;` (comma separator)
- **Python (✗)**: `  scalemode metric 1.0000;` (space separator)

### BACKCOLR
- **C# (✓)**: `  backcolr 255 255 255;` (RGB values)
- **Python (✗)**: `  backcolr 255;` (single index value)

### Application Structure
- **C# (✓)**: Uses `BEGAPS`, `APSATTR`, `BEGAPSBODY`
- **Python (✗)**: Uses commented `% APPLICATION STRUCTURE DIRECTORY ;`, `% APPLSTRUCTATTR`

## Root Cause

The issue is in **`commands.py`** and **`commands_extended.py`** where each command's `write_as_clear_text()` method is implemented incorrectly:

1. **Wrong case**: Commands use UPPERCASE instead of lowercase
2. **Wrong formats**: Many commands write parameters in binary format instead of cleartext format
3. **Missing implementations**: Many commands are stubbed out with `%` comments
4. **Wrong parameter order**: Some commands have parameters in wrong order
5. **Missing commas**: Some commands missing comma separators (e.g. scalemode)

## Files That Need Rewriting

1. **`commands.py`** - Base command implementations (all write_as_clear_text methods)
2. **`commands_extended.py`** - Extended implementations
3. Need to reference C# implementation for correct cleartext format

## Impact

The current Python cleartext output is **incompatible** with the ISO standard and cannot be properly read by cleartext CGM parsers. This explains why:
- File sizes differ (100K vs 57K)
- Line counts differ (2185 vs 2191)
- Visual rendering would be incorrect if parsed

## Next Steps

We need to systematically rewrite the `write_as_clear_text()` method for every command class to match the C# reference implementation's output format.

### Priority Commands to Fix:
1. MetafileVersion (mfversion)
2. MetafileDescription (mfdesc)
3. MetafileElementList (mfelemlist)
4. FontList (fontlist)
5. FontProperties (FONTPROP)
6. CharacterSetList (charsetlist)
7. All precision commands (colrprec, integerprec, realprec, etc.)
8. BackgroundColour (backcolr)
9. ScaleMode (scalemode)
10. Application Structure commands (BEGAPS, APSATTR, etc.)
