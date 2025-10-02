"""
Example: Reading and Converting CGM Files

This example demonstrates various ways to work with binary CGM files
and convert them to clear text format.
"""

from cgm_file import BinaryCGMFile, ClearTextCGMFile, convert_binary_to_cleartext


def example_1_simple_conversion():
    """Example 1: Simple conversion using convenience function"""
    print("Example 1: Simple Conversion")
    print("-" * 50)
    
    # Quick conversion
    messages = convert_binary_to_cleartext('input.cgm', 'output.txt')
    
    print(f"Conversion complete. {len(messages)} messages.")
    for msg in messages:
        print(f"  {msg}")
    print()


def example_2_read_and_inspect():
    """Example 2: Read binary CGM and inspect contents"""
    print("Example 2: Read and Inspect")
    print("-" * 50)
    
    # Read binary file
    cgm = BinaryCGMFile.read_binary('input.cgm')
    
    print(f"File: {cgm.name}")
    print(f"Total commands: {len(cgm.commands)}")
    print(f"VDC Type: {cgm.vdc_type}")
    print(f"Colour Selection Mode: {cgm.colour_selection_mode}")
    print()
    
    # Show all commands
    print("Commands:")
    for i, cmd in enumerate(cgm.commands, 1):
        print(f"  {i:3d}. {cmd}")
    print()
    
    # Show any messages
    if cgm.messages:
        print("Messages:")
        for msg in cgm.messages:
            print(f"  {msg}")
    print()


def example_3_convert_to_string():
    """Example 3: Convert to clear text string"""
    print("Example 3: Convert to String")
    print("-" * 50)
    
    # Read binary
    binary_cgm = BinaryCGMFile.read_binary('input.cgm')
    
    # Convert to clear text
    cleartext_cgm = ClearTextCGMFile(binary_cgm)
    
    # Get as string
    content = cleartext_cgm.get_content()
    
    print("Clear Text Content:")
    print(content[:500])  # Show first 500 characters
    print("...")
    print()


def example_4_process_commands():
    """Example 4: Process specific command types"""
    print("Example 4: Process Commands")
    print("-" * 50)
    
    # Read binary file
    cgm = BinaryCGMFile.read_binary('input.cgm')
    
    # Count command types
    from collections import Counter
    command_types = Counter(type(cmd).__name__ for cmd in cgm.commands)
    
    print("Command Type Statistics:")
    for cmd_type, count in command_types.most_common():
        print(f"  {cmd_type:30s}: {count:4d}")
    print()
    
    # Find all text commands
    from commands import Text
    text_commands = [cmd for cmd in cgm.commands if isinstance(cmd, Text)]
    
    print(f"Found {len(text_commands)} text commands:")
    for i, text_cmd in enumerate(text_commands[:5], 1):  # Show first 5
        print(f"  {i}. Position: {text_cmd.position}, Text: '{text_cmd.text}'")
    print()


def example_5_filter_and_export():
    """Example 5: Filter commands and export"""
    print("Example 5: Filter and Export")
    print("-" * 50)
    
    # Read binary file
    binary_cgm = BinaryCGMFile.read_binary('input.cgm')
    
    # Create a new CGM with filtered commands
    from commands_extended import Polyline
    cleartext_cgm = ClearTextCGMFile()
    cleartext_cgm.name = "filtered"
    
    # Copy only polyline commands
    cleartext_cgm.commands = [
        cmd for cmd in binary_cgm.commands 
        if isinstance(cmd, Polyline)
    ]
    
    print(f"Original commands: {len(binary_cgm.commands)}")
    print(f"Filtered commands: {len(cleartext_cgm.commands)}")
    
    # Save filtered version
    cleartext_cgm.write_to_file('filtered_output.txt')
    print("Filtered output written to: filtered_output.txt")
    print()


def example_6_read_from_bytes():
    """Example 6: Read from bytes/stream"""
    print("Example 6: Read from Bytes")
    print("-" * 50)
    
    from io import BytesIO
    
    # Read file into bytes
    with open('input.cgm', 'rb') as f:
        data = f.read()
    
    print(f"Read {len(data)} bytes from file")
    
    # Create stream and read
    stream = BytesIO(data)
    cgm = BinaryCGMFile.read_binary_stream(stream, name="from_bytes")
    
    print(f"Parsed {len(cgm.commands)} commands")
    print(f"File name: {cgm.name}")
    print()


def main():
    """Run all examples"""
    examples = [
        example_2_read_and_inspect,
        example_3_convert_to_string,
        example_4_process_commands,
        example_5_filter_and_export,
        example_6_read_from_bytes,
        # example_1_simple_conversion,  # Requires actual file
    ]
    
    print("=" * 60)
    print("CGM Binary to Clear Text - Examples")
    print("=" * 60)
    print()
    
    for example in examples:
        try:
            example()
        except FileNotFoundError:
            print(f"Skipping {example.__name__}: input file not found")
            print()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            print()


if __name__ == "__main__":
    main()
