"""
Base Command Classes for CGM
Based on ISO/IEC 8632-3:1999 and ISO/IEC 8632-4:1999 specifications
"""
from abc import ABC, abstractmethod
from typing import Tuple
from cgm_classes import CGMPoint, CGMColor, VC, ViewportPoint
from cgm_enums import ColourModelType, ColourSelectionModeType, VDCType, DeviceViewportSpecificationModeEnum


class Command(ABC):
    """Base class for all CGM commands"""
    
    def __init__(self, element_class: int, element_id: int, container):
        self.element_class = element_class
        self.element_id = element_id
        self.container = container
    
    @abstractmethod
    def read_from_binary(self, reader):
        """Read command data from binary format"""
        pass
    
    @abstractmethod
    def write_as_clear_text(self, writer):
        """Write command in clear text format"""
        pass
    
    def __str__(self):
        return self.__class__.__name__
    
    # Helper methods for writing clear text
    @staticmethod
    def write_double(value: float) -> str:
        """Format double value with 4 decimal places"""
        return f"{value:.4f}"
    
    def write_real(self, value: float) -> str:
        """Write real value"""
        return self.write_double(value)
    
    def write_vdc(self, value: float) -> str:
        """Write VDC value"""
        if self.container.vdc_type == VDCType.REAL:
            return self.write_double(value)
        else:
            return self.write_int(int(value))
    
    def write_vc(self, value: VC) -> str:
        """Write viewport coordinate"""
        mode = self.container.device_viewport_specification_mode
        if mode in (DeviceViewportSpecificationModeEnum.MM, DeviceViewportSpecificationModeEnum.PHYDEVCOORD):
            return self.write_int(value.value_int)
        else:
            return self.write_real(value.value_real)
    
    def write_viewport_point(self, value: ViewportPoint) -> str:
        """Write viewport point"""
        return f"{self.write_vc(value.first_point)} {self.write_vc(value.second_point)}"
    
    def write_point(self, point: CGMPoint) -> str:
        """Write a 2D point"""
        return self._write_point_xy(point.x, point.y)
    
    def _write_point_xy(self, x: float, y: float) -> str:
        """Write point from x, y coordinates"""
        sign_char_y = ""
        zero = self.write_double(0.0)
        
        if self.write_double(y) == zero and x < 0:
            sign_char_y = "-"
        
        return f"({self.write_double(x)},{sign_char_y}{self.write_double(y)})"
    
    @staticmethod
    def write_bool(value: bool) -> str:
        """Write boolean as on/off"""
        return "on" if value else "off"
    
    @staticmethod
    def write_bool_yes_no(value: bool) -> str:
        """Write boolean as yes/no"""
        return "yes" if value else "no"
    
    @staticmethod
    def write_string(value: str) -> str:
        """Write string with quotes, removing control characters"""
        # Remove non-printable characters except CR, LF, TAB
        filtered = ''.join(c for c in value if not c.isspace() or c in '\r\n\t' or c == ' ')
        filtered = ''.join(c for c in filtered if ord(c) >= 32 or c in '\r\n\t')
        return f"'{filtered}'"
    
    @staticmethod
    def write_enum(value) -> str:
        """Write enumeration value"""
        if hasattr(value, 'value'):
            return str(value.value).lower()
        return str(value).lower()
    
    @staticmethod
    def write_name(value: int) -> str:
        """Write name value"""
        return str(value)
    
    @staticmethod
    def write_index(value: int) -> str:
        """Write index value"""
        return str(value)
    
    @staticmethod
    def write_int(value: int) -> str:
        """Write integer value"""
        return str(value)
    
    def write_color_rgb(self, r: int, g: int, b: int, model: ColourModelType) -> str:
        """Write RGB color"""
        if model == ColourModelType.RGB:
            return f"{r} {g} {b}"
        else:
            raise NotImplementedError(f"Writing color for {model} is not implemented")
    
    def write_color(self, color: CGMColor) -> str:
        """Write color (indexed or direct)"""
        if self.container.colour_selection_mode == ColourSelectionModeType.INDEXED:
            return self.write_index(color.color_index)
        else:
            return self.write_color_rgb(color.r, color.g, color.b, self.container.colour_model)


# Delimiter Commands

class BeginMetafile(Command):
    """BEGIN METAFILE command (Class=0, Element=1)"""
    
    def __init__(self, container, filename: str = ""):
        super().__init__(0, 1, container)
        self.filename = filename
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        if reader.argument_count > 0:
            self.filename = reader.read_string()
        else:
            self.filename = ""
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"BEGMF {self.write_string(self.filename)};")
    
    def __str__(self):
        return f"BeginMetafile {self.filename}"


class EndMetafile(Command):
    """END METAFILE command (Class=0, Element=2)"""
    
    def __init__(self, container):
        super().__init__(0, 2, container)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        pass  # No parameters
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line("ENDMF;")


class BeginPicture(Command):
    """BEGIN PICTURE command (Class=0, Element=3)"""
    
    def __init__(self, container, picture_name: str = ""):
        super().__init__(0, 3, container)
        self.picture_name = picture_name
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        if reader.argument_count > 0:
            self.picture_name = reader.read_string()
        else:
            self.picture_name = ""
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"BEGPIC {self.write_string(self.picture_name)};")
    
    def __str__(self):
        return f"BeginPicture {self.picture_name}"


class BeginPictureBody(Command):
    """BEGIN PICTURE BODY command (Class=0, Element=4)"""
    
    def __init__(self, container):
        super().__init__(0, 4, container)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        pass  # No parameters
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line("BEGPICBODY;")


class EndPicture(Command):
    """END PICTURE command (Class=0, Element=5)"""
    
    def __init__(self, container):
        super().__init__(0, 5, container)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        pass  # No parameters
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line("ENDPIC;")


class NoOp(Command):
    """NO-OP command (Class=0, Element=0)"""
    
    def __init__(self, container):
        super().__init__(0, 0, container)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        pass  # No parameters
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        pass  # No output for NO-OP


# Metafile Descriptor Commands

class MetafileVersion(Command):
    """METAFILE VERSION command (Class=1, Element=1)"""
    
    def __init__(self, container, version: int = 1):
        super().__init__(1, 1, container)
        self.version = version
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.version = reader.read_int()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"MFVERSION {self.version};")


class MetafileDescription(Command):
    """METAFILE DESCRIPTION command (Class=1, Element=2)"""
    
    def __init__(self, container, description: str = ""):
        super().__init__(1, 2, container)
        self.description = description
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        if reader.argument_count > 0:
            self.description = reader.read_string()
        else:
            self.description = ""
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"MFDESC {self.write_string(self.description)};")


class MetafileElementList(Command):
    """METAFILE ELEMENT LIST command (Class=1, Element=11)"""
    
    def __init__(self, container):
        super().__init__(1, 11, container)
        self.elements = []
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        num_elements = reader.read_int()
        self.elements = []
        for _ in range(num_elements):
            index = reader.read_index()
            element_class = reader.read_int()
            self.elements.append((index, element_class))
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write("MFELEMLIST")
        for index, element_class in self.elements:
            writer.write(f" {element_class} {index}")
        writer.write_line(";")


# UnknownCommand for unsupported commands

class UnknownCommand(Command):
    """Placeholder for unknown/unsupported commands"""
    
    def __init__(self, element_id: int, element_class: int, container):
        super().__init__(element_class, element_id, container)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        # Skip all arguments
        reader._read_argument_end()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"% Unknown command: Class={self.element_class}, ID={self.element_id}")
    
    def __str__(self):
        return f"UnknownCommand(Class={self.element_class}, ID={self.element_id})"
