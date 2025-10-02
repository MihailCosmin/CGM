# CGM Binary to Clear Text Converter (Python)

Python implementation for reading binary CGM (Computer Graphics Metafile) files and converting them to clear text format. This implementation is based on the ISO/IEC 8632-3:1999 (Binary encoding) and ISO/IEC 8632-4:1999 (Clear text encoding) specifications.

## Features

- **Read Binary CGM Files**: Parse binary CGM files according to ISO/IEC 8632-3:1999
- **Convert to Clear Text**: Export CGM commands in clear text format per ISO/IEC 8632-4:1999
- **Command Support**: Implements core CGM commands including:
  - Delimiter elements (BEGIN METAFILE, END METAFILE, BEGIN PICTURE, etc.)
  - Metafile descriptor elements (VERSION, DESCRIPTION, PRECISION settings, etc.)
  - Picture descriptor elements (VDC EXTENT, VDC TYPE, COLOR MODE, etc.)
  - Graphical primitives (POLYLINE, TEXT, POLYGON, etc.)
  - Attribute elements (LINE COLOUR, TEXT COLOUR, FILL COLOUR, etc.)

## Requirements

- Python 3.12 or later
- No external dependencies required (uses only Python standard library)

## Installation

No installation required. Simply ensure all Python files are in the same directory:

```
python/
├── main.py                  # Main converter script
├── cgm_file.py             # Main CGM file classes
├── binary_reader.py        # Binary format reader
├── cleartext_writer.py     # Clear text format writer
├── commands.py             # Base command classes
├── commands_extended.py    # Extended command implementations
├── command_factory.py      # Command factory
├── cgm_classes.py          # CGM data classes
└── cgm_enums.py           # CGM enumerations
```

## Usage

### Command Line

Convert a binary CGM file to clear text:

```bash
# Basic usage - output filename auto-generated
python main.py input.cgm

# Specify output filename
python main.py input.cgm output.txt
```

### Python API

```python
from cgm_file import BinaryCGMFile, ClearTextCGMFile, convert_binary_to_cleartext

# Method 1: Quick conversion
messages = convert_binary_to_cleartext('input.cgm', 'output.txt')

# Method 2: Using classes
# Read binary CGM
binary_cgm = BinaryCGMFile.read_binary('input.cgm')

# Convert to clear text
cleartext_cgm = ClearTextCGMFile(binary_cgm)

# Write to file
cleartext_cgm.write_to_file('output.txt')

# Or get as string
content = cleartext_cgm.get_content()
print(content)

# Access commands
for command in binary_cgm.commands:
    print(command)

# Check for messages/warnings
for message in binary_cgm.messages:
    print(message)
```

### Reading from Streams

```python
from cgm_file import BinaryCGMFile
from io import BytesIO

# Read from bytes
with open('input.cgm', 'rb') as f:
    data = f.read()
    stream = BytesIO(data)
    cgm = BinaryCGMFile.read_binary_stream(stream, name="my_cgm")
```

## Architecture

### Core Components

1. **cgm_enums.py**: Defines all CGM enumerations (ClassCode, Precision, VDCType, etc.)

2. **cgm_classes.py**: Defines basic CGM data structures:
   - `CGMPoint`: 2D point representation
   - `CGMColor`: Color (indexed or direct RGB)
   - `StructuredDataRecord`: SDR support
   - `Message`: Error/warning messages

3. **binary_reader.py**: Binary CGM file reader
   - Handles binary encoding per ISO/IEC 8632-3:1999
   - Reads various data types (integers, reals, points, colors, etc.)
   - Supports different precisions and formats

4. **cleartext_writer.py**: Clear text CGM file writer
   - Generates clear text output per ISO/IEC 8632-4:1999
   - Handles line wrapping (80 chars per line)
   - Formats commands properly

5. **commands.py**: Base command classes and common commands
   - Abstract `Command` base class
   - Delimiter commands (BEGIN/END METAFILE, PICTURE, etc.)
   - Basic metafile descriptor commands

6. **commands_extended.py**: Extended command implementations
   - Picture descriptor commands
   - Graphical primitives (POLYLINE, TEXT, POLYGON)
   - Attribute commands (colors, sizes, etc.)

7. **command_factory.py**: Command factory
   - Creates appropriate command instances based on class and ID
   - Extensible design for adding more commands

8. **cgm_file.py**: Main file handling classes
   - `CGMFile`: Base class with meta definitions
   - `BinaryCGMFile`: Binary CGM file reader
   - `ClearTextCGMFile`: Clear text CGM file writer
   - `convert_binary_to_cleartext()`: Convenience function

## Supported CGM Commands

### Delimiter Elements (Class 0)
- NO-OP
- BEGIN METAFILE / END METAFILE
- BEGIN PICTURE / END PICTURE
- BEGIN PICTURE BODY

### Metafile Descriptor Elements (Class 1)
- METAFILE VERSION
- METAFILE DESCRIPTION
- INTEGER PRECISION
- REAL PRECISION
- INDEX PRECISION
- COLOUR PRECISION
- COLOUR INDEX PRECISION
- METAFILE ELEMENT LIST

### Picture Descriptor Elements (Class 2)
- VDC INTEGER PRECISION
- VDC REAL PRECISION
- VDC TYPE
- COLOUR SELECTION MODE
- VDC EXTENT
- BACKGROUND COLOUR

### Graphical Primitive Elements (Class 4)
- POLYLINE
- TEXT
- POLYGON

### Attribute Elements (Class 5)
- LINE COLOUR
- TEXT COLOUR
- FILL COLOUR
- CHARACTER HEIGHT

*Note: More commands can be easily added following the existing patterns.*

## Extending the Implementation

To add support for a new CGM command:

1. Create a new command class in `commands_extended.py`:

```python
class NewCommand(Command):
    def __init__(self, container, param1=default):
        super().__init__(class_code, element_id, container)
        self.param1 = param1
    
    def read_from_binary(self, reader):
        self.param1 = reader.read_int()  # or appropriate read method
    
    def write_as_clear_text(self, writer):
        writer.write_line(f"NEWCOMM {self.write_int(self.param1)};")
```

2. Register it in `command_factory.py`:

```python
def _create_xxx_element(self, element_id: int, container):
    commands = {
        # ... existing commands ...
        element_id: lambda: NewCommand(container),
    }
```

## Limitations

- **Binary Writing**: Not yet implemented (read-only for binary format)
- **Command Coverage**: Core commands implemented; some specialized commands return as `UnknownCommand`
- **Validation**: Limited validation of CGM file structure
- **Performance**: Not optimized for very large files

## Error Handling

The implementation includes comprehensive error handling:

- **Messages**: All warnings and errors are collected in the `messages` list
- **Severity Levels**: INFO, UNSUPPORTED, UNIMPLEMENTED, FATAL
- **Graceful Degradation**: Unknown commands are handled without crashing

## ISO/IEC 8632 Compliance

This implementation follows:
- **ISO/IEC 8632-3:1999**: Binary encoding specification
- **ISO/IEC 8632-4:1999**: Clear text encoding specification

Refer to the specification documents in the `ISO 8632/` folder for detailed information.

## License

See LICENSE file in the root directory.

## References

- ISO/IEC 8632-1:1999 - Part 1: Functional specification
- ISO/IEC 8632-3:1999 - Part 3: Binary encoding
- ISO/IEC 8632-4:1999 - Part 4: Clear text encoding

## Original C# Implementation

This Python implementation is based on the C# CGM library found in the `src/` directory of this repository.
