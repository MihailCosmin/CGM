﻿using System;

namespace codessentials.CGM.Commands
{
    /// <remarks>
    /// Class=1, Element=5
    /// </remarks>
    public class RealPrecision : RealPrecisionBase
    {
        public RealPrecision(CgmFile container)
            : base(new CommandConstructorArguments(ClassCode.MetafileDescriptorElements, 5, container))
        {

        }

        public RealPrecision(CgmFile container, Precision precision)
            : this(container)
        {
            SetValue(precision);
        }

        public override void ReadFromBinary(IBinaryReader reader)
        {
            base.ReadFromBinary(reader);

            _container.RealPrecision = Value;
            _container.RealPrecisionProcessed = true;
        }

        public override void WriteAsBinary(IBinaryWriter writer)
        {
            base.WriteAsBinary(writer);

            _container.RealPrecision = Value;
            _container.RealPrecisionProcessed = true;
        }

        public override string ToString()
        {
            return "RealPrecision " + Value;
        }

        public override void WriteAsClearText(IClearTextWriter writer)
        {
            if (Value == Precision.Floating_32)
                writer.WriteLine($" realprec -511.0000, 511.0000, 7 % 10 binary bits %;");
            else
                throw new NotSupportedException($"Real Precision {Value} is currently not supported.");
        }
    }
}
