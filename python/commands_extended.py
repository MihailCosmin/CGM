"""
Extended CGM Commands
Additional command implementations for various CGM element classes
"""
from commands import Command
from cgm_classes import CGMPoint, CGMColor
from cgm_enums import (
    Precision, ColourModelType, ColourSelectionModeType, VDCType,
    SpecificationMode, RestrictedTextTypeEnum
)


# Picture Descriptor Commands (Class=2)

class ColourSelectionMode(Command):
    """COLOUR SELECTION MODE command (Class=2, Element=2)"""
    
    def __init__(self, container, mode: ColourSelectionModeType = ColourSelectionModeType.INDEXED):
        super().__init__(2, 2, container)
        self.mode = mode
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        e = reader.read_enum()
        if e == 0:
            self.mode = ColourSelectionModeType.INDEXED
        elif e == 1:
            self.mode = ColourSelectionModeType.DIRECT
        else:
            self.mode = ColourSelectionModeType.INDEXED
            reader.unsupported(f"color selection mode {e}")
        
        self.container.colour_selection_mode = self.mode
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  colrmode {self.write_enum(self.mode)};")


class VdcExtent(Command):
    """VDC EXTENT command (Class=2, Element=6)"""
    
    def __init__(self, container, lower_left: CGMPoint = None, upper_right: CGMPoint = None):
        super().__init__(2, 6, container)
        self.lower_left_corner = lower_left or CGMPoint(0, 0)
        self.upper_right_corner = upper_right or CGMPoint(0, 0)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.lower_left_corner = reader.read_point()
        self.upper_right_corner = reader.read_point()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  vdcext {self.write_point(self.lower_left_corner)} "
                         f"{self.write_point(self.upper_right_corner)};")


class VdcType(Command):
    """VDC TYPE command (Class=2, Element=3)"""
    
    def __init__(self, container, vdc_type: VDCType = VDCType.INTEGER):
        super().__init__(2, 3, container)
        self.vdc_type = vdc_type
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        e = reader.read_enum()
        if e == 0:
            self.vdc_type = VDCType.INTEGER
        elif e == 1:
            self.vdc_type = VDCType.REAL
        else:
            self.vdc_type = VDCType.INTEGER
            reader.unsupported(f"VDC type {e}")
        
        self.container.vdc_type = self.vdc_type
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  vdctype {self.write_enum(self.vdc_type)};")


class IntegerPrecision(Command):
    """INTEGER PRECISION command (Class=1, Element=4)"""
    
    def __init__(self, container, precision: int = 16):
        super().__init__(1, 4, container)
        self.precision = precision
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.precision = reader.read_int()
        self.container.integer_precision = self.precision
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"INTEGERPREC {self.precision};")


class IndexPrecision(Command):
    """INDEX PRECISION command (Class=1, Element=6)"""
    
    def __init__(self, container, precision: int = 16):
        super().__init__(1, 6, container)
        self.precision = precision
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.precision = reader.read_int()
        self.container.index_precision = self.precision
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"INDEXPREC {self.precision};")


class ColourPrecision(Command):
    """COLOUR PRECISION command (Class=1, Element=7)"""
    
    def __init__(self, container, precision: int = 8):
        super().__init__(1, 7, container)
        self.precision = precision
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.precision = reader.read_int()
        self.container.colour_precision = self.precision
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"COLRPREC {self.precision};")


class ColourIndexPrecision(Command):
    """COLOUR INDEX PRECISION command (Class=1, Element=8)"""
    
    def __init__(self, container, precision: int = 8):
        super().__init__(1, 8, container)
        self.precision = precision
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.precision = reader.read_int()
        self.container.colour_index_precision = self.precision
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"COLRINDEXPREC {self.precision};")


class RealPrecision(Command):
    """REAL PRECISION command (Class=1, Element=5)"""
    
    def __init__(self, container, precision: Precision = Precision.FIXED_32):
        super().__init__(1, 5, container)
        self.precision = precision
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        p1 = reader.read_enum()
        p2 = reader.read_int()
        p3 = reader.read_int()
        
        if p1 == 0:  # Floating point
            if p2 == 9 and p3 == 23:
                self.precision = Precision.FLOATING_32
            elif p2 == 12 and p3 == 52:
                self.precision = Precision.FLOATING_64
            else:
                reader.unsupported("unsupported real precision")
                self.precision = Precision.FIXED_32
        elif p1 == 1:  # Fixed point
            if p2 == 16 and p3 == 16:
                self.precision = Precision.FIXED_32
            elif p2 == 32 and p3 == 32:
                self.precision = Precision.FIXED_64
            else:
                reader.unsupported("unsupported real precision")
                self.precision = Precision.FIXED_32
        
        self.container.real_precision = self.precision
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        if self.precision == Precision.FLOATING_32:
            writer.write_line("REALPREC 0 9 23;")
        elif self.precision == Precision.FLOATING_64:
            writer.write_line("REALPREC 0 12 52;")
        elif self.precision == Precision.FIXED_32:
            writer.write_line("REALPREC 1 16 16;")
        elif self.precision == Precision.FIXED_64:
            writer.write_line("REALPREC 1 32 32;")


class VdcIntegerPrecision(Command):
    """VDC INTEGER PRECISION command (Class=2, Element=1)"""
    
    def __init__(self, container, precision: int = 16):
        super().__init__(2, 1, container)
        self.precision = precision
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.precision = reader.read_int()
        self.container.vdc_integer_precision = self.precision
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  vdcintegerprec {self.precision};")


class VdcRealPrecision(Command):
    """VDC REAL PRECISION command (Class=2, Element=2)"""
    
    def __init__(self, container, precision: Precision = Precision.FIXED_32):
        super().__init__(2, 2, container)
        self.precision = precision
    
    def read_from_binary(self, reader):
        """Read from binary format - same as RealPrecision"""
        p1 = reader.read_enum()
        p2 = reader.read_int()
        p3 = reader.read_int()
        
        if p1 == 0:  # Floating point
            if p2 == 9 and p3 == 23:
                self.precision = Precision.FLOATING_32
            elif p2 == 12 and p3 == 52:
                self.precision = Precision.FLOATING_64
            else:
                reader.unsupported("unsupported VDC real precision")
                self.precision = Precision.FIXED_32
        elif p1 == 1:  # Fixed point
            if p2 == 16 and p3 == 16:
                self.precision = Precision.FIXED_32
            elif p2 == 32 and p3 == 32:
                self.precision = Precision.FIXED_64
            else:
                reader.unsupported("unsupported VDC real precision")
                self.precision = Precision.FIXED_32
        
        self.container.vdc_real_precision = self.precision
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        if self.precision == Precision.FLOATING_32:
            writer.write_line("  vdcrealprec 0 9 23;")
        elif self.precision == Precision.FLOATING_64:
            writer.write_line("  vdcrealprec 0 12 52;")
        elif self.precision == Precision.FIXED_32:
            writer.write_line("  vdcrealprec 1 16 16;")
        elif self.precision == Precision.FIXED_64:
            writer.write_line("  vdcrealprec 1 32 32;")


# Graphical Primitive Commands (Class=4)

class Polyline(Command):
    """POLYLINE command (Class=4, Element=1)"""
    
    def __init__(self, container, points=None):
        super().__init__(4, 1, container)
        self.points = points or []
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        # Calculate number of points from argument size
        point_size = 2 * (self.container.vdc_integer_precision // 8 
                         if self.container.vdc_type == VDCType.INTEGER 
                         else 8)  # Simplified, should check VDC precision
        
        n = reader.argument_count // point_size if point_size > 0 else 0
        
        self.points = []
        for _ in range(n):
            self.points.append(reader.read_point())
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write("  LINE")
        for point in self.points:
            writer.write(f" {self.write_point(point)}")
        writer.write_line(";")


class Text(Command):
    """TEXT command (Class=4, Element=4)"""
    
    def __init__(self, container, text: str = "", position: CGMPoint = None, final: bool = True):
        super().__init__(4, 4, container)
        self.text = text
        self.position = position or CGMPoint(0, 0)
        self.final = final
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.position = reader.read_point()
        self.final = reader.read_enum() != 0
        self.text = reader.read_string()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write(f" TEXT {self.write_point(self.position)}")
        
        if self.final:
            writer.write(" final")
        else:
            writer.write(" notfinal")
        
        writer.write(f" {self.write_string(self.text)}")
        writer.write_line(";")


class PolygonElement(Command):
    """POLYGON command (Class=4, Element=7)"""
    
    def __init__(self, container, points=None):
        super().__init__(4, 7, container)
        self.points = points or []
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        point_size = 2 * (self.container.vdc_integer_precision // 8 
                         if self.container.vdc_type == VDCType.INTEGER 
                         else 8)
        
        n = reader.argument_count // point_size if point_size > 0 else 0
        
        self.points = []
        for _ in range(n):
            self.points.append(reader.read_point())
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write("  POLYGON")
        for point in self.points:
            writer.write(f" {self.write_point(point)}")
        writer.write_line(";")


# Attribute Commands (Class=5)

class LineColour(Command):
    """LINE COLOUR command (Class=5, Element=4)"""
    
    def __init__(self, container, color: CGMColor = None):
        super().__init__(5, 4, container)
        self.color = color or CGMColor()
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.color = reader.read_color()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  linecolr {self.write_color(self.color)};")


class TextColour(Command):
    """TEXT COLOUR command (Class=5, Element=14)"""
    
    def __init__(self, container, color: CGMColor = None):
        super().__init__(5, 14, container)
        self.color = color or CGMColor()
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.color = reader.read_color()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  textcolr {self.write_color(self.color)};")


class FillColour(Command):
    """FILL COLOUR command (Class=5, Element=23)"""
    
    def __init__(self, container, color: CGMColor = None):
        super().__init__(5, 23, container)
        self.color = color or CGMColor()
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.color = reader.read_color()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  fillcolr {self.write_color(self.color)};")


class BackgroundColour(Command):
    """BACKGROUND COLOUR command (Class=2, Element=7)"""
    
    def __init__(self, container, color: CGMColor = None):
        super().__init__(2, 7, container)
        self.color = color or CGMColor()
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.color = reader.read_color()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  backcolr {self.write_color(self.color)};")


class CharacterHeight(Command):
    """CHARACTER HEIGHT command (Class=5, Element=15)"""
    
    def __init__(self, container, height: float = 1.0):
        super().__init__(5, 15, container)
        self.height = height
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.height = reader.read_vdc()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  charheight {self.write_vdc(self.height)};")
