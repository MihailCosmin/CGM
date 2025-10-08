# Cleartext Writer Fix Plan

## C# Patterns Identified

### Command Name Format
- **ALWAYS lowercase** (e.g., `mfversion`, `fontlist`, `colrprec`)
- **Leading space** for metafile descriptor elements (` mfversion`)
- **Two spaces** for picture descriptor elements (`  backcolr`)

### Precision Commands Format
**ColourPrecision:**
```csharp
writer.WriteLine($" colrprec {Math.Pow(2, precision) - 1};");
// Example: precision=8 → " colrprec 255;"
```

**IntegerPrecision:**
```csharp
var val = Math.Pow(2, Precision) / 2;
writer.WriteLine($" integerprec -{val}, {val - 1} % {Precision} binary bits %;");
// Example: precision=16 → " integerprec -32768, 32767 % 16 binary bits %;"
```

**RealPrecision:**
Similar pattern with min/max values and bits comment

### Color Format
```csharp
// RGB mode:
return $"{color.R} {color.G} {color.B}";
// Space-separated RGB values

// Indexed mode:
return WriteIndex(value.ColorIndex);
// Single index value
```

### String Format
- Single-quoted strings: `'VERSION4'`
- Multiple strings comma-separated: `'ARIAL', 'ARIAL-BOLD'`

## Commands to Fix (Priority Order)

### HIGH PRIORITY (Metafile Descriptor - Class 1)
1. ✅ MetafileVersion - ` mfversion {Version};`
2. ✅ MetafileDescription - ` mfdesc {description};`
3. ⚠️ MetafileElementList - ` mfelemlist '{join(Elements)}';`
4. ⚠️ FontList - ` fontlist '{join(FontNames)}';`
5. ❌ FontProperties - `FONTPROP {params};` (complex)
6. ⚠️ CharacterSetList - ` charsetlist {format};`
7. ❌ ColourPrecision - ` colrprec {2^precision-1};`
8. ❌ ColourIndexPrecision - ` colrindexprec {2^precision-1};`
9. ❌ ColourValueExtent - ` colrvalueext {format};`
10. ❌ IntegerPrecision - ` integerprec -{val}, {val-1} % {bits} binary bits %;`
11. ❌ RealPrecision - ` realprec {min}, {max}, {mantissa} % {bits} binary bits %;`
12. ❌ VdcType - ` vdctype {type};` (lowercase!)
13. ❌ MaximumColourIndex - ` maxcolrindex {value};`

### MEDIUM PRIORITY (Picture Descriptor - Class 2)
14. BackgroundColour - `  backcolr {R G B};` (note: two spaces)
15. ScaleMode - `  scalemode metric, {scale};` (comma separator!)

### Application Structure Commands
16. BeginApplicationStructure - ` BEGAPS {params};`
17. ApplicationStructureAttribute - ` APSATTR {params};`
18. BeginApplicationStructureBody - ` BEGAPSBODY;`

## Implementation Strategy

1. **Phase 1**: Fix base Command class helper methods
   - Ensure write_real(), write_int(), write_index() match C# format
   - Add write_color() helper with RGB vs indexed logic
   
2. **Phase 2**: Fix high-priority commands (metafile descriptors)
   - Change case to lowercase
   - Fix precision calculations
   - Fix string quoting
   
3. **Phase 3**: Fix picture descriptor commands
   - Adjust spacing (two spaces)
   - Fix color format
   - Fix comma separators

4. **Phase 4**: Test and validate
   - Compare output with C# reference
   - Verify file can be read by cleartext parser
