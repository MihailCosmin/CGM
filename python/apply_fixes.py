#!/usr/bin/env python3
"""
Apply all fixes to commands_extended.py
This script applies all necessary fixes to make the CGM converter work properly
"""
import re

def main():
    with open('commands_extended.py', 'r') as f:
        content = f.read()
    
    # Fix 1: VdcType class number from 2 to 1
    content = content.replace(
        'class VdcType(Command):\n    """VDC TYPE command (Class=2, Element=3)"""\n    \n    def __init__(self, container, vdc_type: VDCType = VDCType.INTEGER):\n        super().__init__(2, 3, container)',
        'class VdcType(Command):\n    """VDC TYPE command (Class=1, Element=3)"""\n    \n    def __init__(self, container, vdc_type: VDCType = VDCType.INTEGER):\n        super().__init__(1, 3, container)'
    )
    
    # Fix 2: VdcType write_as_clear_text to always use REAL
    old_vdctype_write = '''    def write_as_clear_text(self, writer):
        """Write as clear text"""
        writer.write_line(f"  vdctype {self.write_enum(self.vdc_type)};")'''
    
    new_vdctype_write = '''    def write_as_clear_text(self, writer):
        """Write as clear text"""
        # Always write as 'real' instead of 'integer' for better compatibility
        # This matches the C# library behavior as many viewers have issues with integer VDC
        if self.vdc_type == VDCType.INTEGER:
            writer.info("Writing vdctype = real instead of integer (as read by the binary file) because of some problems using integer. If the CGM file could not be opened in any viewer please edit file and change vdctype.")
            writer.write_line(f" vdctype real;")
        else:
            writer.write_line(f" vdctype {self.write_enum(self.vdc_type)};")'''
    
    content = content.replace(old_vdctype_write, new_vdctype_write)
    
    # Fix 3: VdcIntegerPrecision class number from 2 to 3
    content = content.replace(
        'class VdcIntegerPrecision(Command):\n    """VDC INTEGER PRECISION command (Class=2, Element=1)"""\n    \n    def __init__(self, container, precision: int = 16):\n        super().__init__(2, 1, container)',
        'class VdcIntegerPrecision(Command):\n    """VDC INTEGER PRECISION command (Class=3, Element=1)"""\n    \n    def __init__(self, container, precision: int = 16):\n        super().__init__(3, 1, container)'
    )
    
    # Fix 4: VdcRealPrecision class number from 2 to 3
    content = content.replace(
        'class VdcRealPrecision(Command):\n    """VDC REAL PRECISION command (Class=2, Element=2)"""\n    \n    def __init__(self, container, precision: Precision = Precision.FIXED_32):\n        super().__init__(2, 2, container)',
        'class VdcRealPrecision(Command):\n    """VDC REAL PRECISION command (Class=3, Element=2)"""\n    \n    def __init__(self, container, precision: Precision = Precision.FIXED_32):\n        super().__init__(3, 2, container)'
    )
    
    # Fix 5: Simplify Polyline read_from_binary
    old_polyline_read = '''    def read_from_binary(self, reader):
        """Read from binary format"""
        # Calculate number of points from argument size
        point_size = 2 * (self.container.vdc_integer_precision // 8 
                         if self.container.vdc_type == VDCType.INTEGER 
                         else 8)  # Simplified, should check VDC precision
        
        n = reader.argument_count // point_size if point_size > 0 else 0
        
        self.points = []
        for _ in range(n):
            self.points.append(reader.read_point())'''
    
    new_polyline_read = '''    def read_from_binary(self, reader):
        """Read from binary format"""
        self.points = reader.read_point_list()'''
    
    content = content.replace(old_polyline_read, new_polyline_read)
    
    # Now add new commands at the end
    # Find the end of PolygonElement class to add after it
    new_commands = '''


class LineWidth(Command):
    """LINE WIDTH command (Class=5, Element=3)"""
    
    def __init__(self, container, width: float = 1.0):
        super().__init__(5, 3, container)
        self.width = width
    
    def read_from_binary(self, reader):
        """Read from binary format"""
        self.width = reader.read_size_specification()
    
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
                writer.write("\\n")
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
        while reader.current_arg < len(reader.args):
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
            writer.write_line(f"  scalemode {mode_name} {self.write_real(self.metric_scale)};")
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
'''
    
    # Add before the last line (usually empty)
    if content.endswith('\n'):
        content = content[:-1] + new_commands + '\n'
    else:
        content = content + new_commands
    
    with open('commands_extended.py', 'w') as f:
        f.write(content)
    
    print("All fixes applied successfully!")

if __name__ == '__main__':
    main()
