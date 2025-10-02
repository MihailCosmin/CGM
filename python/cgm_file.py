"""
CGM File Classes
Main classes for reading and writing CGM files in binary and clear text formats
"""
from typing import List, BinaryIO, TextIO
from io import BytesIO, StringIO
from cgm_classes import Message
from cgm_enums import (
    Precision, ColourModelType, ColourSelectionModeType, VDCType,
    SpecificationMode, RestrictedTextTypeEnum, DeviceViewportSpecificationModeEnum
)
from binary_reader import BinaryReader
from cleartext_writer import ClearTextWriter


class CGMFile:
    """Base class for CGM files"""
    
    def __init__(self):
        self.name = "new"
        self.commands: List = []
        self.messages: List[Message] = []
        
        # Initialize meta definitions
        self.reset_meta_definitions()
    
    def reset_meta_definitions(self):
        """Reset CGM metadata settings to defaults"""
        self.colour_index_precision = 8
        self.colour_precision = 8
        self.colour_model = ColourModelType.RGB
        self.colour_selection_mode = ColourSelectionModeType.INDEXED
        self.colour_value_extent_minimum_rgb = [0, 0, 0]
        self.colour_value_extent_maximum_rgb = [255, 255, 255]
        self.device_viewport_specification_mode = DeviceViewportSpecificationModeEnum.FRACTION
        self.edge_width_specification_mode = SpecificationMode.ABS
        self.index_precision = 16
        self.integer_precision = 16
        self.name_precision = 16
        self.line_width_specification_mode = SpecificationMode.ABS
        self.marker_size_specification_mode = SpecificationMode.ABS
        self.interior_style_specification_mode = SpecificationMode.ABS
        self.real_precision = Precision.FIXED_32
        self.real_precision_processed = False
        self.restricted_text_type = RestrictedTextTypeEnum.BASIC
        self.vdc_integer_precision = 16
        self.vdc_real_precision = Precision.FIXED_32
        self.vdc_type = VDCType.INTEGER
    
    def apply_values(self, other_file: 'CGMFile'):
        """Copy values from another CGM file"""
        self.name = other_file.name
        self.commands.extend(other_file.commands)
        self.reset_meta_definitions()


class BinaryCGMFile(CGMFile):
    """Represents a CGM file in binary format"""
    
    def __init__(self, filename: str = None, stream: BinaryIO = None, name: str = "stream"):
        super().__init__()
        
        if filename:
            self.filename = filename
            self.name = filename.split('/')[-1].split('\\')[-1]  # Get filename from path
            self._read_from_file(filename)
        elif stream:
            self.filename = None
            self.name = name
            self._read_from_stream(stream)
        else:
            self.filename = None
            self.name = "new"
    
    def _read_from_file(self, filename: str):
        """Read CGM data from a file"""
        with open(filename, 'rb') as f:
            self._read_from_stream(f)
    
    def _read_from_stream(self, stream: BinaryIO):
        """Read CGM data from a stream"""
        self.reset_meta_definitions()
        reader = BinaryReader(stream, self)
        self.commands = reader.read_commands()
        self.messages.extend(reader.messages)
    
    def write_to_file(self, filename: str):
        """Write CGM data to a binary file"""
        # Binary writing not implemented yet
        raise NotImplementedError("Binary writing not yet implemented")
    
    def get_content(self) -> bytes:
        """Get the CGM content as bytes"""
        # Binary writing not implemented yet
        raise NotImplementedError("Binary writing not yet implemented")
    
    @staticmethod
    def read_binary(filename: str) -> 'BinaryCGMFile':
        """Read a binary CGM file from disk"""
        return BinaryCGMFile(filename=filename)
    
    @staticmethod
    def read_binary_stream(stream: BinaryIO, name: str = "stream") -> 'BinaryCGMFile':
        """Read a binary CGM file from a stream"""
        return BinaryCGMFile(stream=stream, name=name)


class ClearTextCGMFile(CGMFile):
    """Represents a CGM file in clear text format"""
    
    def __init__(self, binary_file: BinaryCGMFile = None):
        super().__init__()
        
        if binary_file:
            self.filename = binary_file.filename
            self.apply_values(binary_file)
        else:
            self.filename = None
    
    def write_to_file(self, filename: str):
        """Write CGM commands to a clear text file"""
        with open(filename, 'w', encoding='cp1252') as f:
            self._write_to_stream(f)
    
    def _write_to_stream(self, stream: TextIO):
        """Write CGM commands to a stream"""
        self.reset_meta_definitions()
        writer = ClearTextWriter(stream)
        
        for command in self.commands:
            writer.write_command(command)
        
        self.messages.extend(writer.messages)
    
    def get_content(self) -> str:
        """Get the CGM content as clear text string"""
        stream = StringIO()
        self._write_to_stream(stream)
        return stream.getvalue()


def convert_binary_to_cleartext(binary_filename: str, cleartext_filename: str):
    """
    Convert a binary CGM file to clear text format
    
    Args:
        binary_filename: Path to the binary CGM file
        cleartext_filename: Path where the clear text CGM file will be written
    """
    # Read binary file
    binary_cgm = BinaryCGMFile.read_binary(binary_filename)
    
    # Convert to clear text
    cleartext_cgm = ClearTextCGMFile(binary_cgm)
    
    # Write clear text file
    cleartext_cgm.write_to_file(cleartext_filename)
    
    # Return messages for reporting
    return binary_cgm.messages + cleartext_cgm.messages
