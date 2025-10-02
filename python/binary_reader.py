"""
Binary CGM Reader
Reads binary CGM files according to ISO/IEC 8632-3:1999 specification
"""
import struct
from io import BufferedReader, BytesIO
from typing import Optional, List, Tuple
from cgm_classes import CGMPoint, CGMColor, VC, ViewportPoint, StructuredDataRecord, Message
from cgm_enums import (
    Precision, ColourModelType, ColourSelectionModeType, VDCType,
    DeviceViewportSpecificationModeEnum, StructuredDataType, Severity
)


class BinaryReader:
    """Reads binary CGM data"""
    
    TWO_EX_16 = 2 ** 16
    TWO_EX_32 = 2 ** 32
    
    def __init__(self, stream: BufferedReader, cgm_file):
        self.stream = stream
        self.cgm = cgm_file
        self.arguments: Optional[bytes] = None
        self.current_arg = 0
        self.position_in_current_argument = 0
        self.messages: List[Message] = []
        self.current_command = None
    
    @property
    def argument_count(self) -> int:
        """Get the number of arguments"""
        return len(self.arguments) if self.arguments else 0
    
    def read_commands(self) -> List:
        """Read all commands from the stream"""
        commands = []
        while True:
            cmd = self._read_command()
            if cmd is None:
                break
            self.arguments = None
            commands.append(cmd)
        return commands
    
    def _read_command(self):
        """Read a single command from the stream"""
        try:
            # Read the command header (2 bytes)
            header_bytes = self.stream.read(2)
            if len(header_bytes) < 2:
                return None
            
            k = (header_bytes[0] << 8) | header_bytes[1]
            
            # Extract command information
            element_class = k >> 12
            element_id = (k >> 5) & 127
            argument_count = k & 31
            
            # Read arguments
            self.current_arg = 0
            self.arguments = None
            self._read_arguments(argument_count)
            
            # Create and read the command
            from command_factory import CommandFactory
            factory = CommandFactory()
            command = factory.create_command(element_id, element_class, self.cgm)
            
            self.current_command = command
            try:
                command.read_from_binary(self)
            except NotImplementedError as e:
                self.messages.append(Message(
                    Severity.UNIMPLEMENTED.value,
                    element_class,
                    element_id,
                    str(e),
                    str(command)
                ))
                self._read_argument_end()
            except Exception as e:
                self._read_argument_end()
                self.messages.append(Message(
                    Severity.FATAL.value,
                    element_class,
                    element_id,
                    str(e),
                    str(command)
                ))
            
            self.current_command = None
            return command
            
        except Exception:
            return None
    
    def _read_arguments(self, argument_count: int):
        """Read command arguments"""
        if argument_count != 31:
            self._read_short_form_arguments(argument_count)
        else:
            self._read_long_form_arguments()
    
    def _read_short_form_arguments(self, argument_count: int):
        """Read short form command arguments"""
        self.arguments = self.stream.read(argument_count)
        # Align on word boundary
        if argument_count % 2 == 1:
            try:
                self.stream.read(1)
            except:
                pass
    
    def _read_long_form_arguments(self):
        """Read long form command arguments"""
        done = False
        args_list = []
        
        while not done:
            count_bytes = self.stream.read(2)
            if len(count_bytes) < 2:
                break
            
            argument_count = (count_bytes[0] << 8) | count_bytes[1]
            
            # Check if data is partitioned
            if argument_count & (1 << 15):
                done = False
                argument_count &= ~(1 << 15)
            else:
                done = True
            
            # Read the arguments
            chunk = self.stream.read(argument_count)
            args_list.append(chunk)
            
            # Align on word boundary
            if argument_count % 2 == 1:
                self.stream.read(1)
        
        self.arguments = b''.join(args_list)
    
    def read_byte(self) -> int:
        """Read a single byte"""
        self._skip_bits()
        if self.current_arg >= len(self.arguments):
            raise ValueError("Read past end of arguments")
        value = self.arguments[self.current_arg]
        self.current_arg += 1
        return value
    
    def read_signed_int8(self) -> int:
        """Read signed 8-bit integer"""
        value = self.read_byte()
        return struct.unpack('b', bytes([value]))[0]
    
    def read_signed_int16(self) -> int:
        """Read signed 16-bit integer"""
        self._skip_bits()
        if self.current_arg + 1 >= len(self.arguments):
            raise ValueError("Read past end of arguments")
        value = (self.arguments[self.current_arg] << 8) | self.arguments[self.current_arg + 1]
        self.current_arg += 2
        return struct.unpack('>h', struct.pack('>H', value))[0]
    
    def read_signed_int24(self) -> int:
        """Read signed 24-bit integer"""
        self._skip_bits()
        if self.current_arg + 2 >= len(self.arguments):
            raise ValueError("Read past end of arguments")
        value = (self.arguments[self.current_arg] << 16) | \
                (self.arguments[self.current_arg + 1] << 8) | \
                self.arguments[self.current_arg + 2]
        self.current_arg += 3
        # Handle sign extension for 24-bit
        if value & 0x800000:
            value = value - 0x1000000
        return value
    
    def read_signed_int32(self) -> int:
        """Read signed 32-bit integer"""
        self._skip_bits()
        if self.current_arg + 3 >= len(self.arguments):
            raise ValueError("Read past end of arguments")
        value = (self.arguments[self.current_arg] << 24) | \
                (self.arguments[self.current_arg + 1] << 16) | \
                (self.arguments[self.current_arg + 2] << 8) | \
                self.arguments[self.current_arg + 3]
        self.current_arg += 4
        return struct.unpack('>i', struct.pack('>I', value))[0]
    
    def read_uint(self, precision: int) -> int:
        """Read unsigned integer with given precision"""
        if precision == 1:
            return self._read_uint_bit(1)
        elif precision == 2:
            return self._read_uint_bit(2)
        elif precision == 4:
            return self._read_uint_bit(4)
        elif precision == 8:
            return self.read_byte()
        elif precision == 16:
            return self._read_uint16()
        elif precision == 24:
            return self.read_signed_int24()
        elif precision == 32:
            return self.read_signed_int32()
        else:
            self.unsupported(f"Unsupported uint precision {precision}")
            return self.read_byte()
    
    def _read_uint16(self) -> int:
        """Read unsigned 16-bit integer"""
        self._skip_bits()
        if self.current_arg + 1 < len(self.arguments):
            value = (self.arguments[self.current_arg] << 8) | self.arguments[self.current_arg + 1]
            self.current_arg += 2
            return value
        elif self.current_arg < len(self.arguments):
            value = self.arguments[self.current_arg]
            self.current_arg += 1
            return value
        raise ValueError("Read past end of arguments")
    
    def _read_uint_bit(self, num_bits: int) -> int:
        """Read unsigned integer with bit precision"""
        if self.current_arg >= len(self.arguments):
            raise ValueError("Read past end of arguments")
        
        bits_position = 8 - num_bits - self.position_in_current_argument
        mask = ((1 << num_bits) - 1) << bits_position
        value = (self.arguments[self.current_arg] & mask) >> bits_position
        
        self.position_in_current_argument += num_bits
        if self.position_in_current_argument % 8 == 0:
            self.position_in_current_argument = 0
            self.current_arg += 1
        
        return value
    
    def read_int(self, precision: Optional[int] = None) -> int:
        """Read signed integer with CGM integer precision or specified precision"""
        if precision is None:
            precision = self.cgm.integer_precision
        
        if precision == 8:
            return self.read_signed_int8()
        elif precision == 16:
            return self.read_signed_int16()
        elif precision == 24:
            return self.read_signed_int24()
        elif precision == 32:
            return self.read_signed_int32()
        else:
            self.unsupported(f"Unsupported integer precision {precision}")
            return self.read_signed_int16()
    
    def read_enum(self) -> int:
        """Read enumeration value"""
        return self.read_signed_int16()
    
    def read_index(self) -> int:
        """Read index with CGM index precision"""
        return self.read_int(self.cgm.index_precision)
    
    def read_name(self) -> int:
        """Read name with CGM name precision"""
        return self.read_int(self.cgm.name_precision)
    
    def read_bool(self) -> bool:
        """Read boolean value"""
        return self.read_enum() != 0
    
    def read_string(self) -> str:
        """Read string"""
        length = self._get_string_count()
        chars = []
        for _ in range(length):
            chars.append(chr(self.read_byte()))
        return ''.join(chars)
    
    def _get_string_count(self) -> int:
        """Get the length of a string"""
        length = self.read_byte()
        if length == 255:
            length = self._read_uint16()
            if length & (1 << 16):
                length = (length << 16) | self._read_uint16()
        return length
    
    def read_vdc(self) -> float:
        """Read VDC (Virtual Device Coordinate)"""
        if self.cgm.vdc_type == VDCType.REAL:
            if self.cgm.vdc_real_precision == Precision.FIXED_32:
                return self._read_fixed_point_32()
            elif self.cgm.vdc_real_precision == Precision.FIXED_64:
                return self._read_fixed_point_64()
            elif self.cgm.vdc_real_precision == Precision.FLOATING_32:
                return self._read_floating_point_32()
            elif self.cgm.vdc_real_precision == Precision.FLOATING_64:
                return self._read_floating_point_64()
            else:
                self.unsupported(f"Unsupported VDC real precision {self.cgm.vdc_real_precision}")
                return self._read_fixed_point_32()
        else:  # INTEGER
            precision = self.cgm.vdc_integer_precision
            if precision == 16:
                return float(self.read_signed_int16())
            elif precision == 24:
                return float(self.read_signed_int24())
            elif precision == 32:
                return float(self.read_signed_int32())
            else:
                self.unsupported(f"Unsupported VDC integer precision {precision}")
                return float(self.read_signed_int16())
    
    def read_real(self) -> float:
        """Read real number"""
        precision = self.cgm.real_precision
        if precision == Precision.FIXED_32:
            return self._read_fixed_point_32()
        elif precision == Precision.FIXED_64:
            return self._read_fixed_point_64()
        elif precision == Precision.FLOATING_32:
            return self._read_floating_point_32()
        elif precision == Precision.FLOATING_64:
            return self._read_floating_point_64()
        else:
            self.unsupported(f"Unsupported real precision {precision}")
            return self._read_fixed_point_32()
    
    def _read_fixed_point_32(self) -> float:
        """Read 32-bit fixed point number"""
        whole_part = self.read_signed_int16()
        fraction_part = self._read_uint16()
        return whole_part + (fraction_part / self.TWO_EX_16)
    
    def _read_fixed_point_64(self) -> float:
        """Read 64-bit fixed point number"""
        whole_part = self.read_signed_int32()
        fraction_part = self.read_signed_int32() & 0xFFFFFFFF
        return whole_part + (fraction_part / self.TWO_EX_32)
    
    def _read_floating_point_32(self) -> float:
        """Read 32-bit floating point number"""
        self._skip_bits()
        bits = 0
        for _ in range(4):
            bits = (bits << 8) | self.read_byte()
        
        # Convert to float
        result = struct.unpack('>f', struct.pack('>I', bits))[0]
        
        # Quirks mode: handle near-zero values
        if abs(result) < 1e-10:
            result = 0.0
        
        return float(result)
    
    def _read_floating_point_64(self) -> float:
        """Read 64-bit floating point number"""
        self._skip_bits()
        bits = 0
        for _ in range(8):
            bits = (bits << 8) | self.read_byte()
        
        return struct.unpack('>d', struct.pack('>Q', bits))[0]
    
    def read_point(self) -> CGMPoint:
        """Read a 2D point"""
        return CGMPoint(self.read_vdc(), self.read_vdc())
    
    def read_color_index(self, local_color_precision: int = -1) -> int:
        """Read color index"""
        precision = self.cgm.colour_index_precision if local_color_precision == -1 else local_color_precision
        return self.read_uint(precision)
    
    def read_direct_color(self) -> Tuple[int, int, int]:
        """Read direct color (RGB)"""
        precision = self.cgm.colour_precision
        model = self.cgm.colour_model
        
        if model == ColourModelType.RGB:
            r = self.read_uint(precision)
            g = self.read_uint(precision)
            b = self.read_uint(precision)
            return self._scale_color_value_rgb(r, g, b)
        elif model == ColourModelType.CMYK:
            c = self.read_uint(precision)
            m = self.read_uint(precision)
            y = self.read_uint(precision)
            k = self.read_uint(precision)
            # Convert CMYK to RGB
            r = int(255 * (1 - c / 255) * (1 - k / 255))
            g = int(255 * (1 - m / 255) * (1 - k / 255))
            b = int(255 * (1 - y / 255) * (1 - k / 255))
            return (r, g, b)
        else:
            self.unsupported(f"Unsupported color model {model}")
            # Read and discard values
            self.read_uint(precision)
            self.read_uint(precision)
            self.read_uint(precision)
            return (0, 255, 255)  # Cyan as default
    
    def read_color(self, local_color_precision: int = -1) -> CGMColor:
        """Read color (indexed or direct)"""
        color = CGMColor()
        
        if self.cgm.colour_selection_mode == ColourSelectionModeType.DIRECT:
            r, g, b = self.read_direct_color()
            color.r = r
            color.g = g
            color.b = b
        else:  # INDEXED
            color.color_index = self.read_color_index(local_color_precision)
        
        return color
    
    def read_vc(self) -> VC:
        """Read viewport coordinate"""
        result = VC()
        
        mode = self.cgm.device_viewport_specification_mode
        if mode in (DeviceViewportSpecificationModeEnum.MM, DeviceViewportSpecificationModeEnum.PHYDEVCOORD):
            result.value_int = self.read_int()
        else:
            result.value_real = self.read_real()
        
        return result
    
    def read_viewport_point(self) -> ViewportPoint:
        """Read viewport point"""
        return ViewportPoint(self.read_vc(), self.read_vc())
    
    def read_sdr(self) -> StructuredDataRecord:
        """Read Structured Data Record"""
        sdr = StructuredDataRecord()
        sdr_length = self._get_string_count()
        start_pos = self.current_arg
        
        while self.current_arg < (start_pos + sdr_length):
            data_type = StructuredDataType(self.read_index())
            data_count = self.read_int()
            data = []
            
            for _ in range(data_count):
                if data_type == StructuredDataType.SDR:
                    data.append(self.read_sdr())
                elif data_type == StructuredDataType.CI:
                    data.append(self.read_color_index())
                elif data_type == StructuredDataType.CD:
                    data.append(self.read_direct_color())
                elif data_type == StructuredDataType.N:
                    data.append(self.read_name())
                elif data_type == StructuredDataType.E:
                    data.append(self.read_enum())
                elif data_type == StructuredDataType.I:
                    data.append(self.read_int())
                elif data_type == StructuredDataType.IF8:
                    data.append(self.read_signed_int8())
                elif data_type == StructuredDataType.IF16:
                    data.append(self.read_signed_int16())
                elif data_type == StructuredDataType.IF32:
                    data.append(self.read_signed_int32())
                elif data_type == StructuredDataType.IX:
                    data.append(self.read_index())
                elif data_type == StructuredDataType.R:
                    data.append(self.read_real())
                elif data_type == StructuredDataType.S or data_type == StructuredDataType.SF:
                    data.append(self.read_string())
                elif data_type == StructuredDataType.VC:
                    data.append(self.read_vc())
                elif data_type == StructuredDataType.VDC:
                    data.append(self.read_vdc())
                elif data_type == StructuredDataType.UI8:
                    data.append(self.read_byte())
                elif data_type == StructuredDataType.UI16:
                    data.append(self._read_uint16())
                elif data_type == StructuredDataType.UI32:
                    data.append(self.read_signed_int32())
                else:
                    raise NotImplementedError(f"SDR data type {data_type} not implemented")
            
            sdr.add(data_type, data_count, data)
        
        return sdr
    
    def read_size_specification(self, specification_mode) -> float:
        """Read size specification (absolute or scaled)"""
        from cgm_enums import SpecificationMode
        if specification_mode == SpecificationMode.ABS:
            return self.read_vdc()
        else:
            return self.read_real()
    
    def align_on_word(self):
        """Align reading position on word boundary"""
        if self.current_arg >= len(self.arguments):
            return
        
        if self.current_arg % 2 == 0 and self.position_in_current_argument > 0:
            self.position_in_current_argument = 0
            self.current_arg += 2
        elif self.current_arg % 2 == 1:
            self.position_in_current_argument = 0
            self.current_arg += 1
    
    def _skip_bits(self):
        """Skip remaining bits in current byte"""
        if self.position_in_current_argument % 8 != 0:
            self.position_in_current_argument = 0
            self.current_arg += 1
    
    def _read_argument_end(self):
        """Skip to end of arguments"""
        self.current_arg = self.argument_count
    
    def _scale_color_value_rgb(self, r: int, g: int, b: int) -> Tuple[int, int, int]:
        """Scale color values from CGM range to 0-255"""
        min_vals = self.cgm.colour_value_extent_minimum_rgb
        max_vals = self.cgm.colour_value_extent_maximum_rgb
        
        r = max(min(r, max_vals[0]), min_vals[0])
        g = max(min(g, max_vals[1]), min_vals[1])
        b = max(min(b, max_vals[2]), min_vals[2])
        
        def scale(val, min_val, max_val):
            if min_val == max_val:
                return 0
            return 255 * (val - min_val) // (max_val - min_val)
        
        return (scale(r, min_vals[0], max_vals[0]),
                scale(g, min_vals[1], max_vals[1]),
                scale(b, min_vals[2], max_vals[2]))
    
    def unsupported(self, message: str):
        """Log an unsupported feature message"""
        if self.current_command:
            self.messages.append(Message(
                Severity.UNSUPPORTED.value,
                self.current_command.element_class,
                self.current_command.element_id,
                message,
                str(self.current_command)
            ))
        else:
            self.messages.append(Message(
                Severity.UNSUPPORTED.value,
                0,
                0,
                message,
                ""
            ))
