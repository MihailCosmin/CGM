# Quick Start Guide

## Installation

No installation required! The library uses only Python 3.12 standard library.

### Prerequisites

- Python 3.12 or later
- That's it!

### Verify Installation

```bash
cd python
python3 --version  # Should show 3.12 or later
python3 test_cgm.py  # Run tests
```

## Basic Usage

### 1. Convert Binary CGM to Clear Text

```bash
python3 main.py input.cgm output.txt
```

### 2. Use in Your Python Code

```python
from cgm_file import convert_binary_to_cleartext

# Simple conversion
convert_binary_to_cleartext('input.cgm', 'output.txt')
```

### 3. Read and Inspect CGM Files

```python
from cgm_file import BinaryCGMFile

# Read binary CGM
cgm = BinaryCGMFile.read_binary('input.cgm')

# Access commands
print(f"Total commands: {len(cgm.commands)}")
for cmd in cgm.commands[:10]:  # First 10
    print(cmd)

# Check metadata
print(f"VDC Type: {cgm.vdc_type}")
print(f"Color Mode: {cgm.colour_selection_mode}")
```

### 4. Advanced: Filter Commands

```python
from cgm_file import BinaryCGMFile, ClearTextCGMFile
from commands_extended import Text

# Read file
cgm = BinaryCGMFile.read_binary('input.cgm')

# Filter text commands
text_commands = [cmd for cmd in cgm.commands if isinstance(cmd, Text)]
print(f"Found {len(text_commands)} text commands")

for text_cmd in text_commands:
    print(f"  '{text_cmd.text}' at {text_cmd.position}")
```

## File Structure

```
python/
├── README.md              # Full documentation
├── QUICKSTART.md         # This file
├── requirements.txt      # Dependencies (none!)
├── __init__.py           # Package initialization
├── main.py              # Command-line converter
├── examples.py          # Usage examples
├── test_cgm.py          # Test suite
├── cgm_file.py          # Main CGM file classes
├── binary_reader.py     # Binary format reader
├── cleartext_writer.py  # Clear text writer
├── commands.py          # Base command classes
├── commands_extended.py # Extended commands
├── command_factory.py   # Command factory
├── cgm_classes.py       # Data classes
└── cgm_enums.py        # Enumerations
```

## Testing

Run the test suite:

```bash
python3 test_cgm.py
```

Expected output:
```
============================================================
Running CGM Library Tests
============================================================

Testing CGMPoint...
  ✓ CGMPoint tests passed
...
============================================================
Results: 7 passed, 0 failed
============================================================
```

## Examples

See `examples.py` for complete examples:

```bash
python3 examples.py
```

## Troubleshooting

### Python Version Error
```
Error: Python 3.12 or later required
```

**Solution**: Upgrade Python or use `python3.12` explicitly:
```bash
python3.12 main.py input.cgm output.txt
```

### File Not Found
```
Error: Input file 'input.cgm' not found!
```

**Solution**: Check the file path is correct. Use absolute paths if needed:
```bash
python3 main.py /full/path/to/input.cgm output.txt
```

### Import Errors
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution**: Ensure you're running from the `python/` directory:
```bash
cd /path/to/CGM/python
python3 main.py input.cgm output.txt
```

## Next Steps

- Read `README.md` for complete documentation
- Check `examples.py` for more usage patterns
- Review ISO 8632 specifications in `../ISO 8632/` folder
- Extend functionality by adding new commands (see README.md)

## Support

For issues or questions:
1. Check the README.md documentation
2. Review the ISO 8632 specifications
3. Examine the C# implementation in `../src/`

## License

See LICENSE file in repository root.
