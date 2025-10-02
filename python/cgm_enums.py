"""
CGM Enumerations
Based on ISO/IEC 8632-3:1999 and ISO/IEC 8632-4:1999 specifications
"""
from enum import Enum, IntEnum


class ClassCode(IntEnum):
    """CGM Element Classes"""
    DELIMITER_ELEMENT = 0
    METAFILE_DESCRIPTOR_ELEMENTS = 1
    PICTURE_DESCRIPTOR_ELEMENTS = 2
    CONTROL_ELEMENTS = 3
    GRAPHICAL_PRIMITIVE_ELEMENTS = 4
    ATTRIBUTE_ELEMENTS = 5
    ESCAPE_ELEMENT = 6
    EXTERNAL_ELEMENTS = 7
    SEGMENT_CONTROL_AND_SEGMENT_ATTRIBUTE_ELEMENTS = 8
    APPLICATION_STRUCTURE_DESCRIPTOR_ELEMENTS = 9
    RESERVED_FOR_FUTURE_USE_1 = 10
    RESERVED_FOR_FUTURE_USE_2 = 11
    RESERVED_FOR_FUTURE_USE_3 = 12
    RESERVED_FOR_FUTURE_USE_4 = 13
    RESERVED_FOR_FUTURE_USE_5 = 14
    RESERVED_FOR_FUTURE_USE_6 = 15


class Precision(Enum):
    """Real Number Precision"""
    FLOATING_32 = "floating_32"
    FLOATING_64 = "floating_64"
    FIXED_32 = "fixed_32"
    FIXED_64 = "fixed_64"


class SpecificationMode(Enum):
    """Specification Mode for width/size parameters"""
    ABS = "abs"  # Absolute
    SCALED = "scaled"  # Scaled


class ColourModelType(Enum):
    """Colour Model Types"""
    RGB = "rgb"
    CIELAB = "cielab"
    CIELUV = "cieluv"
    CMYK = "cmyk"
    RGB_RELATED = "rgb_related"


class ColourSelectionModeType(Enum):
    """Colour Selection Mode"""
    INDEXED = "indexed"
    DIRECT = "direct"


class VDCType(Enum):
    """VDC Type"""
    INTEGER = "integer"
    REAL = "real"


class RestrictedTextTypeEnum(Enum):
    """Restricted Text Type"""
    BASIC = "basic"
    BOXED_CAP = "boxed_cap"
    BOXED_ALL = "boxed_all"
    ISOTROPIC_CAP = "isotropic_cap"
    ISOTROPIC_ALL = "isotropic_all"
    JUSTIFIED = "justified"


class DeviceViewportSpecificationModeEnum(Enum):
    """Device Viewport Specification Mode"""
    FRACTION = "fraction"
    MM = "mm"
    PHYDEVCOORD = "phydevcoord"


class StructuredDataType(IntEnum):
    """Structured Data Record Types"""
    SDR = 0
    CI = 1
    CD = 2
    N = 3
    E = 4
    I = 5
    RESERVED = 6
    IF8 = 7
    IF16 = 8
    IF32 = 9
    IX = 10
    R = 11
    S = 12
    SF = 13
    VC = 14
    VDC = 15
    CCO = 16
    UI8 = 17
    UI32 = 18
    BS = 19
    CL = 20
    UI16 = 21


class DelimiterElement(IntEnum):
    """Delimiter Element IDs"""
    NO_OP = 0
    BEGIN_METAFILE = 1
    END_METAFILE = 2
    BEGIN_PICTURE = 3
    BEGIN_PICTURE_BODY = 4
    END_PICTURE = 5
    BEGIN_SEGMENT = 6
    END_SEGMENT = 7
    BEGIN_FIGURE = 8
    END_FIGURE = 9
    BEGIN_PROTECTION_REGION = 10
    END_PROTECTION_REGION = 11
    BEGIN_COMPOUND_LINE = 12
    END_COMPOUND_LINE = 13
    BEGIN_COMPOUND_TEXT_PATH = 14
    END_COMPOUND_TEXT_PATH = 15
    BEGIN_TILE_ARRAY = 16
    END_TILE_ARRAY = 17
    BEGIN_APPLICATION_STRUCTURE = 18
    BEGIN_APPLICATION_STRUCTURE_BODY = 19
    END_APPLICATION_STRUCTURE = 20


class Severity(Enum):
    """Message Severity Levels"""
    INFO = "info"
    UNSUPPORTED = "unsupported"
    UNIMPLEMENTED = "unimplemented"
    FATAL = "fatal"
