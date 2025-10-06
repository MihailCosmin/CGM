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
    """VDC TYPE command (Class=1, Element=3)"""
    
    def __init__(self, container, vdc_type: VDCType = VDCType.INTEGER):
        super().__init__(1, 3, container)
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
        # Always write as 'real' instead of 'integer' for better compatibility
        # This matches the C# library behavior as many viewers have issues with integer VDC
        if self.vdc_type == VDCType.INTEGER:
            writer.info("Writing vdctype = real instead of integer (as read by the binary file) because of some problems using integer. If the CGM file could not be opened in any viewer please edit file and change vdctype.")
            writer.write_line(f" vdctype real;")
            # CRITICAL: Update the container's vdc_type so all subsequent coordinate writes format as REAL
            self.container.vdc_type = VDCType.REAL
        else:
            writer.write_line(f" vdctype {self.write_enum(self.vdc_type)};")
            self.container.vdc_type = self.vdc_type
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
        val = int(2 ** self.precision / 2)
        writer.write_line(f" integerprec -{val}, {val - 1} % {self.precision} binary bits %;")


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
        val = int(2 ** self.precision / 2)
        writer.write_line(f" indexprec -{val}, {val - 1} % {self.precision} binary bits %;")


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
        val = int(2 ** self.precision - 1)
        writer.write_line(f" colrprec {val};")


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
        # C# uses signed max values for color index precision
        if self.precision == 8:
            val = 127  # sbyte.MaxValue
        elif self.precision == 16:
            val = 32767  # short.MaxValue  
        elif self.precision == 24:
            val = 65535  # ushort.MaxValue
        else:
            val = 2147483647  # int.MaxValue
        writer.write_line(f" colrindexprec {val};")


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
            # Format: min, max, mantissa % exponent binary bits %
            writer.write_line(
                " realprec -511.0000, 511.0000, 7 % 10 binary bits %;")
        elif self.precision == Precision.FLOATING_64:
            writer.write_line(
                " realprec -1023.0000, 1023.0000, 15 % 13 binary bits %;")
        elif self.precision == Precision.FIXED_32:
            writer.write_line(
                " realprec -32768.0000, 32767.0000, 16 % 16 binary bits %;")
        elif self.precision == Precision.FIXED_64:
            writer.write_line(
                " realprec -2147483648.0000, 2147483647.0000, 32 "
                "% 32 binary bits %;")


class VdcIntegerPrecision(Command):
    """VDC INTEGER PRECISION command (Class=3, Element=1)"""
    
    def __init__(self, container, precision: int = 16):
        super().__init__(3, 1, container)
        self.precision = precision
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.precision = reader.read_int()
        self.container.vdc_integer_precision = self.precision
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        val = int(2 ** self.precision / 2)
        writer.write_line(
            f"  vdcintegerprec -{val}, {val - 1} "
            f"% {self.precision} binary bits %;")


class VdcRealPrecision(Command):
    """VDC REAL PRECISION command (Class=3, Element=2)"""
    
    def __init__(self, container, precision: Precision = Precision.FIXED_32):
        super().__init__(3, 2, container)
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
            writer.write_line(
                "  vdcrealprec -511.0000, 511.0000, 7 "
                "% 10 binary bits %;")
        elif self.precision == Precision.FLOATING_64:
            writer.write_line(
                "  vdcrealprec -1023.0000, 1023.0000, 15 "
                "% 13 binary bits %;")
        elif self.precision == Precision.FIXED_32:
            writer.write_line(
                "  vdcrealprec -32768.0000, 32767.0000, 16 "
                "% 16 binary bits %;")
        elif self.precision == Precision.FIXED_64:
            writer.write_line(
                "  vdcrealprec -2147483648.0000, 2147483647.0000, 32 "
                "% 32 binary bits %;")


# Graphical Primitive Commands (Class=4)

class Polyline(Command):
    """POLYLINE command (Class=4, Element=1)"""
    
    def __init__(self, container, points=None):
        super().__init__(4, 1, container)
        self.points = points or []
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.points = reader.read_point_list()
    
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
        self.rgb_color = (255, 255, 255)  # Default white
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        # Read direct color (RGB tuple)
        self.rgb_color = reader.read_direct_color()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        r, g, b = self.rgb_color
        writer.write_line(f"  backcolr {r} {g} {b};")


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


class LineWidth(Command):
    """LINE WIDTH command (Class=5, Element=3)"""
    
    def __init__(self, container, width: float = 1.0):
        super().__init__(5, 3, container)
        self.width = width
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.width = reader.read_size_specification(self.container.line_width_specification_mode)
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  linewidth {self.write_real(self.width)};")


class LineType(Command):
    """LINE TYPE command (Class=5, Element=2)"""
    
    def __init__(self, container, line_type: int = 1):
        super().__init__(5, 2, container)
        self.line_type = line_type
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.line_type = reader.read_index()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  linetype {self.line_type};")


class DisjointPolyline(Command):
    """DISJOINT POLYLINE command (Class=4, Element=2)"""
    
    def __init__(self, container):
        super().__init__(4, 2, container)
        self.points = []
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.points = reader.read_point_list()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        if not self.points:
            writer.write_line("  LINE;")
            return
            
        writer.write(" DISJTLINE")
        for i in range(0, len(self.points), 3):
            # Disjoint polylines have sets of (start, end, start, end, ...)
            # Every 2 points forms a line segment
            chunk = self.points[i:min(i+3, len(self.points))]
            points_str = " ".join(f"({p.x:.4f},{p.y:.4f})" for p in chunk)
            writer.write(f" {points_str}")
            if i + 3 < len(self.points):
                writer.write("\n")
        writer.write_line(";")


class FontList(Command):
    """FONT LIST command (Class=1, Element=13)"""
    
    def __init__(self, container, fonts=None):
        super().__init__(1, 13, container)
        self.fonts = fonts or []
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        # Read fonts as fixed strings until all arguments are consumed
        self.fonts = []
        while reader.current_arg < len(reader.arguments):
            try:
                font_name = reader.read_fixed_string()
                self.fonts.append(font_name)
            except:
                break
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        if not self.fonts:
            writer.write_line(" fontlist;")
            return
        font_list = ", ".join(f"'{font}'" for font in self.fonts)
        writer.write_line(f" fontlist {font_list};")


class CharacterCodingAnnouncer(Command):
    """CHARACTER CODING ANNOUNCER command (Class=1, Element=15)"""
    
    def __init__(self, container, coding_type: int = 0):
        super().__init__(1, 15, container)
        self.coding_type = coding_type
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.coding_type = reader.read_enum()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        coding_names = {0: "BASIC7BIT", 1: "BASIC8BIT", 2: "EXTD7BIT", 3: "EXTD8BIT"}
        coding_name = coding_names.get(self.coding_type, f"UNKNOWN({self.coding_type})")
        writer.write_line(f" charcoding {coding_name};")


class MetafileDefaultsReplacement(Command):
    """METAFILE DEFAULTS REPLACEMENT command (Class=1, Element=12)"""
    
    def __init__(self, container):
        super().__init__(1, 12, container)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        # This command has no parameters - just marks the start of defaults replacement
        pass
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line("  BEGMFDEFAULTS;")


class ScalingMode(Command):
    """SCALING MODE command (Class=2, Element=1)"""
    
    def __init__(self, container, mode: int = 0, metric_scale: float = 1.0):
        super().__init__(2, 1, container)
        self.mode = mode
        self.metric_scale = metric_scale
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.mode = reader.read_enum()
        if self.mode == 1:  # metric
            self.metric_scale = reader.read_real()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        mode_names = {0: "abstract", 1: "metric"}
        mode_name = mode_names.get(self.mode, f"unknown({self.mode})")
        if self.mode == 1:
            # Note: C# uses comma separator for metric scale
            writer.write_line(
                f"  scalemode {mode_name}, {self.write_real(self.metric_scale)};")
        else:
            writer.write_line(f"  scalemode {mode_name};")


class LineWidthSpecificationMode(Command):
    """LINE WIDTH SPECIFICATION MODE command (Class=2, Element=3)"""
    
    def __init__(self, container, mode: int = 0):
        super().__init__(2, 3, container)
        self.mode = mode
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.mode = reader.read_enum()
        # Update container's line width specification mode
        from cgm_enums import SpecificationMode
        self.container.line_width_specification_mode = SpecificationMode.ABS if self.mode == 0 else SpecificationMode.SCALED
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        mode_names = {0: "abs", 1: "scaled"}
        mode_name = mode_names.get(self.mode, f"unknown({self.mode})")
        writer.write_line(f"  linewidthmode {mode_name};")


class CharacterOrientation(Command):
    """CHARACTER ORIENTATION command (Class=5, Element=16)"""
    
    def __init__(self, container):
        super().__init__(5, 16, container)
        self.x_up = 0
        self.y_up = 1
        self.x_base = 1
        self.y_base = 0
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.x_up = reader.read_vdc()
        self.y_up = reader.read_vdc()
        self.x_base = reader.read_vdc()
        self.y_base = reader.read_vdc()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  charori {self.write_vdc(self.x_up)},{self.write_vdc(self.y_up)} {self.write_vdc(self.x_base)},{self.write_vdc(self.y_base)};")


class TextFontIndex(Command):
    """TEXT FONT INDEX command (Class=5, Element=10)"""
    
    def __init__(self, container, index: int = 1):
        super().__init__(5, 10, container)
        self.index = index
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.index = reader.read_index()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  textfontindex {self.index};")



class MaximumVdcExtent(Command):
    """MAXIMUM VDC EXTENT command (Class=1, Element=17)"""
    
    def __init__(self, container, first_corner: CGMPoint = None, second_corner: CGMPoint = None):
        super().__init__(1, 17, container)
        self.first_corner = first_corner or CGMPoint(0, 0)
        self.second_corner = second_corner or CGMPoint(0, 0)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.first_corner = reader.read_point()
        self.second_corner = reader.read_point()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f" MAXVDCEXT {self.write_point(self.first_corner)} {self.write_point(self.second_corner)};")
        writer.write_line("")  # Blank line after MAXVDCEXT


class FontList(Command):
    """FONT LIST command (Class=1, Element=13)"""
    
    def __init__(self, container, font_names: list = None):
        super().__init__(1, 13, container)
        self.font_names = font_names or []
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.font_names = []
        # Read fonts until end of arguments
        while reader.current_arg < len(reader.arguments):
            try:
                font_name = reader.read_string()
                if font_name:
                    self.font_names.append(font_name)
            except:
                break
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        if self.font_names:
            fonts_str = ', '.join([f"'{name}'" for name in self.font_names])
            writer.write_line(f" fontlist {fonts_str};")
        else:
            writer.write_line(" fontlist;")
