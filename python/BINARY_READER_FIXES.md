# Binary Reader Fixes Required

## Critical Issues Found

1. **VdcType** - FIXED ✓
   - Was using stub `VDCTypeCommand` that always wrote "integer"
   - Now uses proper `VdcType` from commands_extended that:
     - Reads actual value from binary
     - Writes "real" when value is integer (for compatibility)
     - **Updates container.vdc_type to REAL** so coordinates format correctly

2. **write_point()** - FIXED ✓
   - Was calling `write_double()` directly
   - Now calls `write_vdc()` to respect VDC type

3. **MaximumVDCExtent** - NEEDS FIX
   - Currently hardcodes `0 32767 0 32767`
   - Should read actual coordinates from binary

4. **FontList** - NEEDS FIX
   - Currently writes empty `fontlist;`
   - Should read font names from binary

5. **FontProperties** - NEEDS FIX
   - Currently commented out
   - Should read and write full font property data

6. **IntegerPrecision** - NEEDS FIX
   - Currently hardcodes `16`
   - Should read actual value

7. **RealPrecision** - NEEDS FIX
   - Currently hardcodes values
   - Should read from binary

8. **Many other stub commands** that don't read from binary

## Next Steps
1. Implement proper MaximumVDCExtent
2. Fix FontList and FontProperties
3. Fix precision commands
4. Test full conversion

