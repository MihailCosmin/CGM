﻿using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace codessentials.CGM.Commands
{
    /// <remarks>
    /// Class=1, ElementId=4
    /// </remarks>
    public class IntegerPrecision : Command
    {
        public int Precision { get; set; }

        public IntegerPrecision(CGMFile container)
            : base(new CommandConstructorArguments(ClassCode.MetafileDescriptorElements, 4, container))
        {
            
        }

        public IntegerPrecision(CGMFile container, int precision)
            : this(container)
        {
            Precision = precision;
            AssertPrecision();
        }

        public override void ReadFromBinary(IBinaryReader reader)
        {
            Precision = reader.ReadInt();
            _container.IntegerPrecision = Precision;

            AssertPrecision();            
        }

        public override void WriteAsBinary(IBinaryWriter writer)
        {
            writer.WriteInt(Precision);
            _container.IntegerPrecision = Precision;
        }

        private void AssertPrecision()
        {
            Assert(Precision == 8 || Precision == 16 || Precision == 24 || Precision == 32, "unsupported INTEGER PRECISION");
        }

        public override void WriteAsClearText(IClearTextWriter writer)
        {
            var val = Math.Pow(2, Precision) / 2;
            writer.WriteLine($" integerprec -{val}, {val - 1} % {Precision} binary bits %;");
        }

        public override string ToString()
        {
            return "IntegerPrecision " + Precision;
        }
    }
}