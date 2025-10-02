# codessentials.CGM

[![NuGet](https://img.shields.io/nuget/v/codessentials.CGM.svg)](https://nuget.org/packages/codessentials.CGM/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build Status](https://github.com/twenzel/CGM/workflows/Build/badge.svg?branch=master)](https://github.com/twenzel/CGM/actions)

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=twenzel_CGM&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=twenzel_CGM)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=twenzel_CGM&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=twenzel_CGM)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=twenzel_CGM&metric=security_rating)](https://sonarcloud.io/dashboard?id=twenzel_CGM)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=twenzel_CGM&metric=bugs)](https://sonarcloud.io/dashboard?id=twenzel_CGM)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=twenzel_CGM&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=twenzel_CGM)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=twenzel_CGM&metric=coverage)](https://sonarcloud.io/dashboard?id=twenzel_CGM)

This library reads CGM (Computer Graphics Metafile) in binary and clear text format. Read graphics can be modified, analyzed and exported. Creating new graphics is also supported.
It implements the `ISO/IEC 8632-3:1999` and `ISO/IEC 8632-4:1999` specification.

Some additional functions for reading technical documentation items (Figures, Names) etc are also implemented.

## Implementations

This repository contains **two implementations**:

### C# / .NET Implementation
The original implementation for .NET Standard 2.0+, available as a NuGet package. See below for C# usage.

### Python 3.12 Implementation
A complete Python implementation for reading binary CGM files and converting to clear text format. Located in the [`python/`](python/) directory.

**Quick Start (Python)**:
```bash
cd python
python3 main.py input.cgm output.txt
```

See the [Python README](python/README.md) for complete documentation.

## Install
Add the NuGet package [codessentials.CGM](https://nuget.org/packages/codessentials.CGM/) to any project supporting .NET Standard 2.0 or higher.

> &gt; dotnet add package codessentials.CGM

## Usage

### Write new CGM files
```CSharp
var writer = new CgmWriter(FileFormat.Binary);
writer.SetDescription("Created By UnitTest");
writer.SetElementList("DRAWINGPLUS");
writer.SetFontList(new[] { "Arial", "Arial Bold" });
writer.SetCharacterSetList(new[] { new KeyValuePair<CharacterSetList.Type, string>(CharacterSetList.Type._94_CHAR_G_SET, "B"), new KeyValuePair<CharacterSetList.Type, string>(CharacterSetList.Type._96_CHAR_G_SET, "A"), new KeyValuePair<CharacterSetList.Type, string>(CharacterSetList.Type.COMPLETE_CODE, "I"), new KeyValuePair<CharacterSetList.Type, string>(CharacterSetList.Type.COMPLETE_CODE, "L") });
writer.SetVDCType(VDCType.Type.Real);
// add several "drawing" commands
writer.AddCommand(...)

//
writer.Finish();

var data = writer.GetContent();
```

### Read & write binary CGM
```CSharp
var cgm = new BinaryCgmFile("corvette.cgm");

// modify graphic

cgm.WriteFile();
```

### Convert binary to clear text format
```CSharp
var binaryFile = new BinaryCgmFile("corvette.cgm");

var cleanTextFile = new ClearTextCgmFile(binaryFile);
var content = cleanTextFile.GetContent();
```

### `CGMFile` Helper functions
Name|Description
-|-
ContainsTextElement|Determines whether any text element equals the specified text.
GetMetaTitle|Gets the meta data title.
GetGraphicName|Gets the title of the illustration.
GetFigureItemTexts|Gets all texts of the figure items.
ContainsFigureItemText|Determines whether CGM contains a specific figure item text.
GetRectangles|Gets all found rectangles.

### Geometry Recognition Engine
The class `GeometryRecognitionEngine` provides several functions to find rectangles.

Name|Description
-|-
GetRectangles | Gets all rectangles of the given file.
IsNearBy | Determines whether point A is near point b.

## Python Implementation

The [`python/`](python/) directory contains a complete Python 3.12 implementation for reading binary CGM files and converting them to clear text format.

### Features
- Read binary CGM files per ISO/IEC 8632-3:1999
- Convert to clear text format per ISO/IEC 8632-4:1999
- No external dependencies (uses Python standard library only)
- Comprehensive test suite
- Full documentation and examples

### Quick Start
```bash
cd python

# Run tests
python3 test_cgm.py

# Convert a file
python3 main.py input.cgm output.txt
```

### Python API
```python
from cgm_file import convert_binary_to_cleartext

# Quick conversion
convert_binary_to_cleartext('input.cgm', 'output.txt')

# Or use classes for more control
from cgm_file import BinaryCGMFile, ClearTextCGMFile

binary_cgm = BinaryCGMFile.read_binary('input.cgm')
cleartext_cgm = ClearTextCGMFile(binary_cgm)
cleartext_cgm.write_to_file('output.txt')
```

### Documentation
- [Python README](python/README.md) - Complete documentation
- [Quick Start Guide](python/QUICKSTART.md) - Get started quickly
- [Examples](python/examples.py) - Usage examples
- [Project Summary](python/PROJECT_SUMMARY.md) - Implementation details
