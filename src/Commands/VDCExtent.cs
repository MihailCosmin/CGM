﻿using codessentials.CGM.Classes;

namespace codessentials.CGM.Commands
{
    /// <summary>
    /// Class=2, Element=6
    /// </summary>
    public class VdcExtent : Command
    {
        public CgmPoint LowerLeftCorner { get; set; }
        public CgmPoint UpperRightCorner { get; set; }

        public VdcExtent(CgmFile container)
            : base(new CommandConstructorArguments(ClassCode.PictureDescriptorElements, 6, container))
        {

        }

        public VdcExtent(CgmFile container, CgmPoint lowerLeft, CgmPoint upperRight)
            : this(container)
        {
            LowerLeftCorner = lowerLeft;
            UpperRightCorner = upperRight;
        }

        public override void ReadFromBinary(IBinaryReader reader)
        {
            LowerLeftCorner = reader.ReadPoint();
            UpperRightCorner = reader.ReadPoint();
        }

        public override void WriteAsBinary(IBinaryWriter writer)
        {
            writer.WritePoint(LowerLeftCorner);
            writer.WritePoint(UpperRightCorner);
        }

        public override void WriteAsClearText(IClearTextWriter writer)
        {
            writer.WriteLine($"  vdcext {WritePoint(LowerLeftCorner)} {WritePoint(UpperRightCorner)};");
        }

        public override string ToString()
        {
            return $"VDCExtent [{LowerLeftCorner.X},{LowerLeftCorner.Y}] [{UpperRightCorner.X},{UpperRightCorner.Y}]";
        }
    }
}
