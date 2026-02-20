using System;
using System.Linq;
using codessentials.CGM;

namespace CgmConverter
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length < 2)
            {
                Console.WriteLine("Usage: ConvertCgmToCleartext <input.cgm> <output_cleartext.cgm>");
                Console.WriteLine("Example: ConvertCgmToCleartext test_edgevis.cgm test_edgevis_cleartext.cgm");
                return;
            }

            string inputFile = args[0];
            string outputFile = args[1];

            try
            {
                Console.WriteLine($"Reading binary CGM file: {inputFile}");
                var binaryCgm = CgmFile.ReadBinary(inputFile);
                
                Console.WriteLine($"Converting to cleartext...");
                var clearTextCgm = new ClearTextCgmFile(binaryCgm);
                
                Console.WriteLine($"Writing cleartext CGM to: {outputFile}");
                clearTextCgm.WriteFile(outputFile);
                
                Console.WriteLine("✓ Conversion complete!");
                Console.WriteLine($"Messages: {binaryCgm.Messages.Count()}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine(ex.StackTrace);
            }
        }
    }
}