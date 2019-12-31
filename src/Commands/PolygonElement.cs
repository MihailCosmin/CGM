﻿using codessentials.CGM.Classes;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System;

namespace codessentials.CGM.Commands
{
    /// <summary>
    /// Class=4, ElementId=7
    /// </summary>
    public class PolygonElement : Command
    {
        public CGMPoint[] Points { get; set; }

        public PolygonElement(CGMFile container) 
            : base(new CommandConstructorArguments(ClassCode.GraphicalPrimitiveElements, 7, container))
        {
            
        }

        public PolygonElement(CGMFile container, CGMPoint[] points)
            :this(container)
        {
            Points = points;
        }

        public override void ReadFromBinary(IBinaryReader reader)
        {
            Assert((reader.Arguments.Length - reader.CurrentArg) % reader.SizeOfPoint() == 0, "Invalid amount of arguments");
            int n = (reader.Arguments.Length - reader.CurrentArg) / reader.SizeOfPoint();

            Points = new CGMPoint[n];

            for (int i = 0; i < n; i++)
                Points[i] = reader.ReadPoint();            
        }

        public override void WriteAsBinary(IBinaryWriter writer)
        {
            foreach(var p in Points)
                writer.WritePoint(p);            
        }

        public override void WriteAsClearText(IClearTextWriter writer)
        {
            writer.Write("  POLYGON");

            foreach (var points in Points)
                writer.Write($" {WritePoint(points)}");

            writer.WriteLine(";");
        }

        public override string ToString()
        {
            return "PolygonElement " + string.Join<CGMPoint>(", ", Points);
        }
    }
}