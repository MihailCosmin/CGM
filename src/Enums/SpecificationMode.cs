﻿namespace codessentials.CGM
{
    public enum SpecificationMode
    {
        ABS,   // type: VDC
        SCALED,     // type: R        
        FRACTIONAL, // type: R
        MM			// type: R        
    }

    public static class SpecificationModeTools
    {
        public static SpecificationMode GetMode(int mode)
        {
            if (mode > 3)
                return SpecificationMode.SCALED;
            else
                return (SpecificationMode)mode;
        }
    }
}
