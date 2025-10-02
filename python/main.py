#!/usr/bin/env python3
"""
CGM Binary to Clear Text Converter
Main script for converting binary CGM files to clear text format

Usage:
    python main.py input.cgm output.txt
    python main.py input.cgm  # outputs to input.txt
"""
import sys
import os
from cgm_file import convert_binary_to_cleartext, BinaryCGMFile, ClearTextCGMFile


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_binary_cgm> [output_cleartext_cgm]")
        print("\nExample:")
        print("  python main.py sample.cgm sample.txt")
        print("  python main.py sample.cgm  # creates sample.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        sys.exit(1)
    
    # Determine output filename
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Replace extension with .txt
        base_name = os.path.splitext(input_file)[0]
        output_file = base_name + ".txt"
    
    print(f"Converting CGM file:")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")
    print()
    
    try:
        # Perform conversion
        messages = convert_binary_to_cleartext(input_file, output_file)
        
        print(f"Conversion completed successfully!")
        print(f"Output written to: {output_file}")
        
        # Report any messages
        if messages:
            print(f"\n{len(messages)} message(s) during conversion:")
            for msg in messages:
                print(f"  {msg}")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_read_binary():
    """Test reading a binary CGM file"""
    if len(sys.argv) < 2:
        print("Please provide a CGM file to test")
        return
    
    input_file = sys.argv[1]
    
    print(f"Reading binary CGM file: {input_file}")
    
    try:
        # Read the binary file
        cgm = BinaryCGMFile.read_binary(input_file)
        
        print(f"\nFile: {cgm.name}")
        print(f"Commands read: {len(cgm.commands)}")
        print(f"Messages: {len(cgm.messages)}")
        
        # Show first few commands
        print("\nFirst 10 commands:")
        for i, cmd in enumerate(cgm.commands[:10]):
            print(f"  {i+1}. {cmd}")
        
        # Show messages
        if cgm.messages:
            print(f"\nMessages:")
            for msg in cgm.messages:
                print(f"  {msg}")
        
    except Exception as e:
        print(f"Error reading file: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
