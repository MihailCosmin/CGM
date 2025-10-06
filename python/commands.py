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
        """Write command as clear text"""
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
        # Use write_vdc to respect the current VDC type setting
        x_str = self.write_vdc(x)
        y_str = self.write_vdc(y)
        zero = self.write_vdc(0.0)
        
        if y_str == zero and x < 0:
            sign_char_y = "-"
        
        return f"({x_str},{sign_char_y}{y_str})"
    
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
        writer.write_line(f" BEGPIC {self.write_string(self.picture_name)};")
    
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
        writer.write_line(" BEGPICBODY;")


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
        writer.write_line(f" mfversion {self.version};")


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
        writer.write_line(f" mfdesc {self.write_string(self.description)};")


class MetafileElementList(Command):
    """METAFILE ELEMENT LIST command (Class=1, Element=11)"""
    
    def __init__(self, container):
        super().__init__(1, 11, container)
        self.elements = []
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        num_elements = reader.read_int()
        self.elements = []
        
        # Element name mappings (from C#)
        element_names = {
            -1: {
                0: "DRAWINGSET",
                1: "DRAWINGPLUS",
                2: "VERSION2",
                3: "EXTDPRIM",
                4: "VERSION2GKSM",
                5: "VERSION3",
                6: "VERSION4"
            }
        }
        
        for _ in range(num_elements):
            code1 = reader.read_index()
            code2 = reader.read_index()
            
            if code1 == -1 and code1 in element_names and code2 in element_names[code1]:
                self.elements.append(element_names[code1][code2])
            else:
                self.elements.append(f"({code1},{code2})")
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        # Format elements as comma-separated quoted strings
        elements_str = "', '".join(self.elements)
        writer.write_line(f" mfelemlist '{elements_str}';")


# GraphicalPrimitiveElement Commands (Class 4)

class CircularArcCentre(Command):
    """Circular Arc Centre command (Class=4, ID=15)"""
    
    def __init__(self, container):
        super().__init__(4, 15, container)
        self.center = None
        self.start_delta_x = 0.0
        self.start_delta_y = 0.0
        self.end_delta_x = 0.0
        self.end_delta_y = 0.0
        self.radius = 0.0
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.center = reader.read_point()
        self.start_delta_x = reader.read_vdc()
        self.start_delta_y = reader.read_vdc()
        self.end_delta_x = reader.read_vdc()
        self.end_delta_y = reader.read_vdc()
        self.radius = reader.read_vdc()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write("  ARCCTR")
        writer.write(f" ({self.center.x:.4f},{self.center.y:.4f})")
        writer.write(f" ({self.start_delta_x:.4f},{self.start_delta_y:.4f})")
        writer.write(f" ({self.end_delta_x:.4f},{self.end_delta_y:.4f})")
        writer.write(f" {self.radius:.4f}")
        writer.write_line(" ;")


class EllipticalArc(Command):
    """Elliptical Arc command (Class=4, ID=18)"""
    
    def __init__(self, container):
        super().__init__(4, 18, container)
        self.center = None
        self.first_conjugate_diameter_endpoint = None
        self.second_conjugate_diameter_endpoint = None
        self.start_vector_x = 0.0
        self.start_vector_y = 0.0
        self.end_vector_x = 0.0
        self.end_vector_y = 0.0
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.center = reader.read_point()
        self.first_conjugate_diameter_endpoint = reader.read_point()
        self.second_conjugate_diameter_endpoint = reader.read_point()
        self.start_vector_x = reader.read_vdc()
        self.start_vector_y = reader.read_vdc()
        self.end_vector_x = reader.read_vdc()
        self.end_vector_y = reader.read_vdc()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write("  elliparc")
        writer.write(f" {self.center.x:.4f} {self.center.y:.4f}")
        writer.write(f" {self.first_conjugate_diameter_endpoint.x:.4f} {self.first_conjugate_diameter_endpoint.y:.4f}")
        writer.write(f" {self.second_conjugate_diameter_endpoint.x:.4f} {self.second_conjugate_diameter_endpoint.y:.4f}")
        writer.write(f" {self.start_vector_x:.4f} {self.start_vector_y:.4f}")
        writer.write(f" {self.end_vector_x:.4f} {self.end_vector_y:.4f}")
        writer.write_line(";")


class EllipseElement(Command):
    """Ellipse command (Class=4, ID=17)"""
    
    def __init__(self, container):
        super().__init__(4, 17, container)
        self.center = None
        self.first_conjugate_diameter_endpoint = None
        self.second_conjugate_diameter_endpoint = None
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.center = reader.read_point()
        self.first_conjugate_diameter_endpoint = reader.read_point()
        self.second_conjugate_diameter_endpoint = reader.read_point()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write("  ellipse")
        writer.write(f" {self.center.x:.4f} {self.center.y:.4f}")
        writer.write(f" {self.first_conjugate_diameter_endpoint.x:.4f} {self.first_conjugate_diameter_endpoint.y:.4f}")
        writer.write(f" {self.second_conjugate_diameter_endpoint.x:.4f} {self.second_conjugate_diameter_endpoint.y:.4f}")
        writer.write_line(";")


class CircleElement(Command):
    """Circle command (Class=4, ID=12)"""
    
    def __init__(self, container):
        super().__init__(4, 12, container)
        self.center = None
        self.radius = 0.0
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.center = reader.read_point()
        self.radius = reader.read_vdc()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write("  circle")
        writer.write(f" {self.center.x:.4f} {self.center.y:.4f}")
        writer.write(f" {self.radius:.4f}")
        writer.write_line(";")


class RestrictedText(Command):
    """Restricted Text command (Class=4, ID=5)"""
    
    def __init__(self, container):
        super().__init__(4, 5, container)
        self.delta_width = 0.0
        self.delta_height = 0.0
        self.position = None
        self.string = ""
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.delta_width = reader.read_vdc()
        self.delta_height = reader.read_vdc()
        self.position = reader.read_point()
        self.string = reader.read_string()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write("  restrtext")
        writer.write(f" {self.delta_width:.4f} {self.delta_height:.4f}")
        writer.write(f" {self.position.x:.4f} {self.position.y:.4f}")
        writer.write(f" '{self.string}'")
        writer.write_line(";")


# AttributeElement Commands (Class 5)

class EdgeVisibility(Command):
    """Edge Visibility command (Class=5, ID=30)"""
    
    def __init__(self, container):
        super().__init__(5, 30, container)
        self.visibility = True
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.visibility = reader.read_enum() == 1
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        visibility_str = "on" if self.visibility else "off"
        writer.write_line(f"  edgevis {visibility_str};")


class InteriorStyle(Command):
    """Interior Style command (Class=5, ID=22)"""
    
    def __init__(self, container):
        super().__init__(5, 22, container)
        self.style = 0  # 0=hollow, 1=solid, 2=pattern, 3=hatch, 4=empty
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.style = reader.read_enum()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        style_names = ["hollow", "solid", "pattern", "hatch", "empty"]
        style_name = style_names[self.style] if self.style < len(style_names) else str(self.style)
        writer.write_line(f"  intstyle {style_name};")


class LineCap(Command):
    """Line Cap command (Class=5, ID=37)"""
    
    def __init__(self, container):
        super().__init__(5, 37, container)
        self.cap_style = 1  # 1=unspecified, 2=butt, 3=round, 4=projecting square
        self.dash_cap_style = 1
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.cap_style = reader.read_enum()
        self.dash_cap_style = reader.read_enum()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f" LINECAP {self.cap_style} {self.dash_cap_style};")


class LineJoin(Command):
    """Line Join command (Class=5, ID=38)"""
    
    def __init__(self, container):
        super().__init__(5, 38, container)
        self.join_style = 1  # 1=unspecified, 2=miter, 3=round, 4=bevel
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.join_style = reader.read_enum()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f" LINEJOIN {self.join_style};")


class EdgeWidth(Command):
    """Edge Width command (Class=5, ID=28)"""
    
    def __init__(self, container):
        super().__init__(5, 28, container)
        self.width = 1.0
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        # Edge width can be VDC or real depending on specification mode
        self.width = reader.read_vdc()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  edgewidth {self.width:.4f};")


class EdgeColour(Command):
    """Edge Colour command (Class=5, ID=29)"""
    
    def __init__(self, container):
        super().__init__(5, 29, container)
        self.colour = None
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.colour = reader.read_colour()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        if hasattr(self.colour, 'index'):
            writer.write_line(f"  edgecolr {self.colour.index};")
        else:
            writer.write_line(f"  edgecolr {self.colour};")


class EdgeType(Command):
    """Edge Type command (Class=5, ID=27)"""
    
    def __init__(self, container):
        super().__init__(5, 27, container)
        self.edge_type = 1
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.edge_type = reader.read_index()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  edgetype {self.edge_type};")


# DelimiterElement Commands (Class 0)

class BeginFigure(Command):
    """Begin Figure command (Class=0, ID=8)"""
    
    def __init__(self, container):
        super().__init__(0, 8, container)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        pass  # No parameters
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line("BEGFIG;")


class EndFigure(Command):
    """End Figure command (Class=0, ID=9)"""
    
    def __init__(self, container):
        super().__init__(0, 9, container)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        pass  # No parameters
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line("ENDFIG;")


class BeginApplicationStructure(Command):
    """Begin Application Structure command (Class=0, ID=21)"""
    
    def __init__(self, container):
        super().__init__(0, 21, container)
        self.id = ""
        self.type = ""
        self.inheritance_flag = 0  # 0=STLIST, 1=APS
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.id = reader.read_string()
        self.type = reader.read_string()
        self.inheritance_flag = reader.read_enum()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        flag_name = "stlist" if self.inheritance_flag == 0 else "aps"
        writer.write_line(f" BEGAPS {self.write_string(self.id)} {self.write_string(self.type)} {flag_name};")


class BeginApplicationStructureBody(Command):
    """Begin Application Structure Body command (Class=0, ID=22)"""
    
    def __init__(self, container):
        super().__init__(0, 22, container)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        pass  # No parameters
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(" BEGAPSBODY;")


class EndApplicationStructure(Command):
    """End Application Structure command (Class=0, ID=23)"""
    
    def __init__(self, container):
        super().__init__(0, 23, container)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        pass  # No parameters
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(" ENDAPS;")


class MessageCommand(Command):
    """Message command (Class=0, ID=23)"""
    
    def __init__(self, container):
        super().__init__(0, 23, container)
        self.action_required = False
        self.message = ""
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.action_required = reader.read_enum() == 1
        self.message = reader.read_string()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        action = "yes" if self.action_required else "no"
        writer.write_line(f" MESSAGE {action} '{self.message}';")


# ApplicationStructureDescriptorElement Commands (Class 9)

class ApplicationStructureAttribute(Command):
    """Application Structure Attribute command (Class=9, ID=1)"""
    
    def __init__(self, container):
        super().__init__(9, 1, container)
        self.attribute_type = ""
        self.sdr = None
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.attribute_type = reader.read_string()
        self.sdr = reader.read_sdr()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write(f" APSATTR {self.write_string(self.attribute_type)} ")
        # Write SDR members
        if self.sdr:
            for member in self.sdr.members:
                writer.write(f" {member.data_type.value} {member.count}")
                for value in member.data:
                    if isinstance(value, str):
                        writer.write(f" {self.write_string(value)}")
                    else:
                        writer.write(f" {value}")
        writer.write_line(";")
    
    def _sanitize_string(self, text):
        """Sanitize string for cleartext output removing non-printable chars"""
        if not text:
            return ""
        
        # Convert to bytes if needed and handle encoding properly
        if isinstance(text, bytes):
            # Try to decode as UTF-8 first, then fallback to latin-1
            try:
                text = text.decode('utf-8', errors='ignore')
            except Exception:
                text = text.decode('latin-1', errors='ignore')
        
        # Convert to string if it's not already
        text = str(text)
        
        # More aggressive sanitization - only keep ASCII printable chars
        sanitized_chars = []
        for c in text:
            # Only keep standard ASCII printable characters (32-126)
            if 32 <= ord(c) <= 126:
                sanitized_chars.append(c)
            elif c in ' \t\n':  # Allow basic whitespace
                sanitized_chars.append(c)
            # Skip all other characters (binary/control/high-bit chars)
        
        sanitized = ''.join(sanitized_chars)
        
        # Remove null terminators and clean up
        sanitized = sanitized.replace('\x00', '').strip()
        
        # If the result is empty or just whitespace, return a placeholder
        if not sanitized or sanitized.isspace():
            return 'BINARY_DATA'
        
        return sanitized




# MetaFileDescriptorElement Commands (Class 1)

class FontProperties(Command):
    """Font Properties command (Class=1, ID=21)"""
    
    def __init__(self, container):
        super().__init__(1, 21, container)
        self.font_infos = []  # List of (property_indicator, priority, sdr)
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        # Read multiple font property entries
        while reader.current_arg < len(reader.arguments):
            property_indicator = reader.read_index()
            priority = reader.read_int()
            sdr = reader.read_sdr()
            self.font_infos.append((property_indicator, priority, sdr))
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write(" FONTPROP")
        for prop_ind, priority, sdr in self.font_infos:
            writer.write(f" {prop_ind} {priority}")
            # Write SDR members
            for member in sdr.members:
                writer.write(f" {member.data_type.value} {member.count}")
                for value in member.data:
                    if isinstance(value, str):
                        writer.write(f" '{value}'")
                    else:
                        writer.write(f" {value}")
        writer.write_line(";")


# ControlElement Commands (Class 3)

class Transparency(Command):
    """Transparency command (Class=3, ID=4)"""
    
    def __init__(self, container):
        super().__init__(3, 4, container)
        self.flag = False
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.flag = reader.read_bool()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  transparency {self.write_bool(self.flag)};")


class RestrictedTextType(Command):
    """Restricted Text Type command (Class=5, ID=42)"""
    
    def __init__(self, container):
        super().__init__(5, 42, container)
        self.text_type = 1  # 1=BASIC, 2=BOXED_CAP, etc.
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.text_type = reader.read_index()
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f" RESTRTEXTTYPE {self.text_type};")


class ClipIndicator(Command):
    """Clip Indicator command (Class=3, ID=6)"""
    
    def __init__(self, container):
        super().__init__(3, 6, container)
        self.clipping = True
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.clipping = reader.read_enum() == 1
    
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        clip_str = "on" if self.clipping else "off"
        writer.write_line(f"  clip {clip_str};")


# Additional MetaFileDescriptorElements (Class 1)
class VDCTypeCommand(Command):
    """VDC Type command (Class=1, ID=3)"""
    
    def __init__(self, container):
        super().__init__(1, 3, container)
        
    def read_from_binary(self, reader):
        # Skip all data for now
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  VDCTYPE integer ;")

class IntegerPrecision(Command):
    """Integer Precision command (Class=1, ID=4)"""
    
    def __init__(self, container):
        super().__init__(1, 4, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  INTEGERPREC 16 ;")

class RealPrecision(Command):
    """Real Precision command (Class=1, ID=5)"""
    
    def __init__(self, container):
        super().__init__(1, 5, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  REALPREC 1 16 16 ;")

class IndexPrecision(Command):
    """Index Precision command (Class=1, ID=6)"""
    
    def __init__(self, container):
        super().__init__(1, 6, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  INDEXPREC 16 ;")

class ColourPrecision(Command):
    """Colour Precision command (Class=1, ID=7)"""
    
    def __init__(self, container):
        super().__init__(1, 7, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  COLRPREC 8 ;")

class ColourIndexPrecision(Command):
    """Colour Index Precision command (Class=1, ID=8)"""
    
    def __init__(self, container):
        super().__init__(1, 8, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  COLRINDEXPREC 8 ;")

class MaximumColourIndex(Command):
    """Maximum Colour Index command (Class=1, ID=9)"""
    
    def __init__(self, container, value: int = 255):
        super().__init__(1, 9, container)
        self.value = value
        
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.value = reader.read_color_index()
        
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f" maxcolrindex {self.value};")


class ColourValueExtent(Command):
    """Colour Value Extent command (Class=1, ID=10)"""
    
    def __init__(self, container):
        super().__init__(1, 10, container)
        self.min_rgb = [0, 0, 0]
        self.max_rgb = [255, 255, 255]
        
    def read_from_binary(self, reader):
        """Read from binary format"""
        if self.container.colour_model == ColourModelType.RGB:
            precision = self.container.colour_precision
            self.min_rgb = [
                reader.read_uint(precision),
                reader.read_uint(precision),
                reader.read_uint(precision)
            ]
            self.max_rgb = [
                reader.read_uint(precision),
                reader.read_uint(precision),
                reader.read_uint(precision)
            ]
        
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        # RGB triplets with comma between min and max
        writer.write_line(
            f" colrvalueext {self.min_rgb[0]} {self.min_rgb[1]} "
            f"{self.min_rgb[2]}, {self.max_rgb[0]} {self.max_rgb[1]} "
            f"{self.max_rgb[2]};")


class CharacterSetList(Command):
    """Character Set List command (Class=1, ID=14)"""
    
    CHARSET_TYPE_94_CHAR = 0
    CHARSET_TYPE_96_CHAR = 1
    CHARSET_TYPE_94_MBYTE = 2
    CHARSET_TYPE_96_MBYTE = 3
    CHARSET_TYPE_COMPLETE = 4
    
    def __init__(self, container):
        super().__init__(1, 14, container)
        self.character_sets = []  # List of (type, designation) tuples
        
    def read_from_binary(self, reader):
        """Read from binary format"""
        while reader.current_arg < len(reader.arguments):
            charset_type = reader.read_enum()
            designation = reader.read_string()
            self.character_sets.append((charset_type, designation))
        
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write(" charsetlist")
        
        for charset_type, designation in self.character_sets:
            if charset_type == self.CHARSET_TYPE_94_CHAR:
                writer.write(" STD94 ")
            elif charset_type == self.CHARSET_TYPE_96_CHAR:
                writer.write(" STD96 ")
            elif charset_type == self.CHARSET_TYPE_94_MBYTE:
                writer.write(" STD94MULTIBYTE ")
            elif charset_type == self.CHARSET_TYPE_96_MBYTE:
                writer.write(" STD96MULTIBYTE ")
            elif charset_type == self.CHARSET_TYPE_COMPLETE:
                writer.write(" COMPLETECODE ")
            
            writer.write(f"'{designation}'")
        
        writer.write_line(";")

class CharacterCodingAnnouncer(Command):
    """Character Coding Announcer command (Class=1, ID=15)"""
    
    def __init__(self, container):
        super().__init__(1, 15, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  CHARCODING basic8bit ;")

class MaximumVDCExtent(Command):
    """Maximum VDC Extent command (Class=1, ID=17)"""
    
    def __init__(self, container):
        super().__init__(1, 17, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  MAXVDCEXT 0 32767 0 32767 ;")

# PictureDescriptorElements (Class 2)
class MarkerSizeSpecificationMode(Command):
    """Marker Size Specification Mode command (Class=2, ID=4)"""
    
    def __init__(self, container):
        super().__init__(2, 4, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  MARKERSIZEMODE abs ;")

class EdgeWidthSpecificationMode(Command):
    """Edge Width Specification Mode command (Class=2, ID=5)"""
    
    def __init__(self, container):
        super().__init__(2, 5, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  edgewidthmode abs;")

class LineAndEdgeTypeDefinition(Command):
    """Line and Edge Type Definition command (Class=2, ID=17)"""
    
    def __init__(self, container):
        super().__init__(2, 17, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  LINETYPEDEF 1 1 1 ;")

# ControlElements (Class 3)
class VDCIntegerPrecision(Command):
    """VDC Integer Precision command (Class=3, ID=1)"""
    
    def __init__(self, container):
        super().__init__(3, 1, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  VDCINTEGERPREC 16 ;")

class VDCRealPrecision(Command):
    """VDC Real Precision command (Class=3, ID=2)"""
    
    def __init__(self, container):
        super().__init__(3, 2, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  VDCREALPREC 1 16 16 ;")

class LineTypeContinuation(Command):
    """Line Type Continuation command (Class=3, ID=19)"""
    
    def __init__(self, container):
        super().__init__(3, 19, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  LINETYPECONT unbroken ;")

# GraphicalPrimitiveElements (Class 4)
class Polybezier(Command):
    """Polybezier command (Class=4, ID=26)"""
    
    def __init__(self, container):
        super().__init__(4, 26, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  POLYBEZIER unbroken 0 0 ;")

# Additional AttributeElements (Class 5)
class CharacterExpansionFactor(Command):
    """Character Expansion Factor command (Class=5, ID=12)"""
    
    def __init__(self, container):
        super().__init__(5, 12, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  CHAREXPAN 1.0 ;")

class TextAlignment(Command):
    """Text Alignment command (Class=5, ID=18)"""
    
    def __init__(self, container):
        super().__init__(5, 18, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  textalign normhoriz normvert 0.0 0.0;")

class CharacterSetIndex(Command):
    """Character Set Index command (Class=5, ID=19)"""
    
    def __init__(self, container):
        super().__init__(5, 19, container)
        self.index = 1
        
    def read_from_binary(self, reader):
        self.index = reader.read_index()
        
    def write_as_clear_text(self, writer):
        writer.write_line(f" charsetindex {self.index};")

class AlternateCharacterSetIndex(Command):
    """Alternate Character Set Index command (Class=5, ID=20)"""
    
    def __init__(self, container):
        super().__init__(5, 20, container)
        self.index = 1
        
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.index = reader.read_index()
        
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f" altcharsetindex {self.index};")

class ColourTable(Command):
    """Colour Table command (Class=5, ID=34)"""
    
    def __init__(self, container):
        super().__init__(5, 34, container)
        self.start_index = 0
        self.colors = []
        
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.start_index = reader.read_color_index()
        
        # Read all remaining colors
        self.colors = []
        while reader.current_arg < len(reader.arguments):
            self.colors.append(reader.read_direct_color())
        
    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write(f"  colrtable {self.start_index} ")
        
        first = True
        for color in self.colors:
            if not first:
                writer.write(",\n              ")
            if first:
                first = False
            # color is a tuple (r, g, b)
            writer.write(f" {color[0]} {color[1]} {color[2]}")
        
        writer.write_line(";")

class InterpolatedInterior(Command):
    """Interpolated Interior command (Class=5, ID=42)"""
    
    def __init__(self, container):
        super().__init__(5, 42, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  interpint 0 0 0 0 255 255 255;")

class HatchStyleDefinition(Command):
    """Hatch Style Definition command (Class=5, ID=44)"""
    
    def __init__(self, container):
        super().__init__(5, 44, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  hatchstyledef 1 parallel 0 0 0 0;")

class GeometricPatternDefinition(Command):
    """Geometric Pattern Definition command (Class=5, ID=45)"""
    
    def __init__(self, container):
        super().__init__(5, 45, container)
        
    def read_from_binary(self, reader):
        pass
        
    def write_as_clear_text(self, writer):
        writer.write_line("  patterndefn 1 0 0 0 0;")

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
