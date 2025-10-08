# Cleartext Format Progress Report

## STATUS: IN PROGRESS

### ✅ COMPLETED FIXES

**Precision Commands:**
- IntegerPrecision: ` integerprec -{val}, {val-1} % {bits} binary bits %;`
- IndexPrecision: ` indexprec -{val}, {val-1} % {bits} binary bits %;`
- ColourPrecision: ` colrprec {2^precision-1};`
- ColourIndexPrecision: ` colrindexprec {2^precision-1};`
- RealPrecision: ` realprec {min}, {max}, {mantissa} % {bits} binary bits %;`
- VdcIntegerPrecision: `  vdcintegerprec -{val}, {val-1} % {bits} binary bits %;`
- VdcRealPrecision: `  vdcrealprec {min}, {max}, {mantissa} % {bits} binary bits %;`

**Metafile Descriptor Commands:**
- MetafileVersion: ` mfversion {version};`
- MetafileDescription: ` mfdesc {description};`
- MetafileElementList: ` mfelemlist '{elements}';`
- VdcType: ` vdctype {type};` (lowercase!)

**Delimiter Commands:**
- BeginMetafile: `BEGMF {name};` (UPPERCASE - correct!)
- BeginPicture: `BEGPIC {name};` (UPPERCASE - correct!)
- BeginPictureBody: `BEGPICBODY;` (UPPERCASE - correct!)
- EndPicture: `ENDPIC;` (UPPERCASE - correct!)
- EndMetafile: `ENDMF;` (UPPERCASE - correct!)

### ⚠️ NEEDS FIXING

**Critical Missing:**
1. **FontList** - Currently writes but need to verify format
2. **FontProperties** - Currently commented out `% FONTPROP ;` - CRITICAL!
3. **CharacterSetList** - Wrong format
4. **ColourValueExtent** - Wrong format
5. **MaximumColourIndex** - Wrong format
6. **BackgroundColour** - Wrong RGB format  
7. **ScaleMode** - Missing comma separator
8. **RestrictedTextType** - Unknown format
9. **Application Structure commands** - BEGAPS, APSATTR, etc.

### 🔍 FORMAT PATTERNS IDENTIFIED

**Case Rules:**
- Delimiter commands (Class 0): UPPERCASE (BEGMF, ENDMF, BEGPIC, etc.)
- Metafile descriptor (Class 1 - space prefix): lowercase (` mfversion`, ` colrprec`)
- Picture descriptor (Class 2 - 2 spaces): lowercase (`  backcolr`, `  vdcext`)
- Control (Class 3 - 2 spaces): lowercase (`  vdcrealprec`)
- Primitives (Class 4 - 2 spaces): Some UPPERCASE (ARCCTR, LINE)

**String Quoting:**
- Use single quotes: `'text'`
- Multiple strings: comma-space separated: `'A', 'B', 'C'`

**Color Format:**
- RGB mode: space-separated `R G B`
- Indexed mode: single value

**Separator Rules:**
- Most: space-separated
- ScaleMode: comma-separated `metric, 1.0000`
- ColourValueExtent: comma-separated RGB triplets

## NEXT STEPS

1. Fix FontProperties (read and write properly)
2. Fix CharacterSetList format
3. Fix ColourValueExtent format  
4. Fix MaximumColourIndex
5. Fix BackgroundColour RGB output
6. Fix ScaleMode comma
7. Test full conversion with ICN-C0419-S1000D0394-001-01.CGM
8. Compare output line-by-line with C# reference
