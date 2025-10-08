### CRITICAL REMAINING FIXES NEEDED

Based on latest comparison, we need to fix:

1. **ColourIndexPrecision** - Outputting 255, should output 127
   - C#: ` colrindexprec 127;`
   - Python: ` colrindexprec 255;`
   - Issue: precision=8, so 2^8-1=255, but C# shows 127. Need to check C# logic!

2. **FontProperties** - Currently commented out, needs full SDR implementation
   - C#: ` FONTPROP 1 10 11 1 1 4 5 14 1 'ARIAL' 5 5 11 1 1 6 5 11 1 5 7 2 11 1 5 13 1 18 3 0 0 0 14 1 11 1 0;`
   - Python: `% FONTPROP ;`
   - Complex: Requires reading/writing Structured Data Records

3. **CharacterSetList** - Wrong format
   - C#: ` charsetlist STD94 'B' STD96 'A';`
   - Python: `  CHARSETLIST completelist 'ISO 8859-1' ;`
   - Fix: Proper charset format, case

4. **ColourValueExtent** - Wrong format
   - C#: ` colrvalueext 0 0 0, 255 255 255;` (comma between RGB triplets)
   - Python: `  COLRVALUEEXT 0 255 0 255 0 255 ;` (wrong format, case, spacing)

5. **MaximumColourIndex** - Wrong value
   - C#: ` maxcolrindex 1;`
   - Python: `  MAXCOLRINDEX 255 ;`
   - Need to read actual value from binary

6. **ScaleMode** - Missing comma
   - C#: `  scalemode metric, 1.0000;` (comma separator!)
   - Python: `  scalemode metric 1.0000;`
   - Simple fix: add comma

7. **EdgeWidthMode** - Case and spacing
   - C#: `  edgewidthmode abs;` (lowercase)
   - Python: `  EDGEWIDTHMODE abs ;`

8. **BackgroundColour** - Format check
   - C#: `  backcolr 255 255 255;` (RGB)
   - Python: `  backcolr 255;` (indexed?)
   - Need to verify color mode

### PRIORITY ORDER:
1. ScaleMode - EASY FIX
2. ColourIndexPrecision - Check C# source
3. MaximumColourIndex - Read from binary
4. ColourValueExtent - Format fix
5. CharacterSetList - Read from binary properly
6. EdgeWidthMode - Case fix
7. FontProperties - COMPLEX, may skip if time constrained
