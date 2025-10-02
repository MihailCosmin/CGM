"""
CGM (Computer Graphics Metafile) Library for Python

A Python implementation for reading binary CGM files and converting them
to clear text format, based on ISO/IEC 8632-3:1999 and ISO/IEC 8632-4:1999.

Quick Start:
    from cgm_file import convert_binary_to_cleartext
    
    # Convert binary CGM to clear text
    convert_binary_to_cleartext('input.cgm', 'output.txt')

Classes:
    - BinaryCGMFile: Read binary CGM files
    - ClearTextCGMFile: Write clear text CGM files
    - CGMPoint: 2D point representation
    - CGMColor: Color representation (indexed or RGB)

Example:
    from cgm_file import BinaryCGMFile, ClearTextCGMFile
    
    # Read binary CGM
    binary_cgm = BinaryCGMFile.read_binary('input.cgm')
    
    # Convert to clear text
    cleartext_cgm = ClearTextCGMFile(binary_cgm)
    cleartext_cgm.write_to_file('output.txt')
    
    # Or get as string
    content = cleartext_cgm.get_content()
"""

__version__ = "1.0.0"
__author__ = "CGM Library Contributors"

from cgm_file import (
    BinaryCGMFile,
    ClearTextCGMFile,
    CGMFile,
    convert_binary_to_cleartext
)

from cgm_classes import (
    CGMPoint,
    CGMColor,
    VC,
    ViewportPoint,
    StructuredDataRecord,
    Message
)

from cgm_enums import (
    ClassCode,
    Precision,
    SpecificationMode,
    ColourModelType,
    ColourSelectionModeType,
    VDCType,
    Severity
)

__all__ = [
    # Main classes
    'BinaryCGMFile',
    'ClearTextCGMFile',
    'CGMFile',
    'convert_binary_to_cleartext',
    
    # Data classes
    'CGMPoint',
    'CGMColor',
    'VC',
    'ViewportPoint',
    'StructuredDataRecord',
    'Message',
    
    # Enumerations
    'ClassCode',
    'Precision',
    'SpecificationMode',
    'ColourModelType',
    'ColourSelectionModeType',
    'VDCType',
    'Severity',
]
