"""
CGM Basic Classes
Based on ISO/IEC 8632-3:1999 and ISO/IEC 8632-4:1999 specifications
"""
from dataclasses import dataclass
from typing import Optional, Tuple, List, Any
from cgm_enums import StructuredDataType


@dataclass
class CGMPoint:
    """Represents a 2D point in CGM"""
    x: float
    y: float
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"
    
    def __eq__(self, other):
        if not isinstance(other, CGMPoint):
            return False
        return self._is_same(self.x, other.x) and self._is_same(self.y, other.y)
    
    @staticmethod
    def _is_same(x: float, y: float) -> bool:
        """Check if two floating point values are approximately equal"""
        x = round(x, 4)
        y = round(y, 4)
        return abs(x - y) < 0.0004


@dataclass
class CGMColor:
    """Represents a color in CGM (either direct RGB or indexed)"""
    color_index: int = -1
    r: int = 0
    g: int = 0
    b: int = 0
    
    @property
    def is_indexed(self) -> bool:
        return self.color_index >= 0
    
    def __str__(self):
        if self.is_indexed:
            return f"ColorIndex {self.color_index}"
        return f"Color RGB({self.r}, {self.g}, {self.b})"


@dataclass
class VC:
    """Viewport Coordinate"""
    value_int: int = 0
    value_real: float = 0.0


@dataclass
class ViewportPoint:
    """Viewport Point with two VC values"""
    first_point: VC = None
    second_point: VC = None
    
    def __post_init__(self):
        if self.first_point is None:
            self.first_point = VC()
        if self.second_point is None:
            self.second_point = VC()


@dataclass
class StructuredDataMember:
    """Member of a Structured Data Record"""
    data_type: StructuredDataType
    count: int
    data: List[Any]


class StructuredDataRecord:
    """Structured Data Record (SDR)"""
    
    def __init__(self):
        self.members: List[StructuredDataMember] = []
    
    def add(self, data_type: StructuredDataType, count: int, data: List[Any]):
        """Add a member to the SDR"""
        self.members.append(StructuredDataMember(data_type, count, data))
    
    def __str__(self):
        return f"SDR with {len(self.members)} members"


@dataclass
class Message:
    """Message from reading/writing CGM files"""
    severity: str
    element_class: int
    element_id: int
    message: str
    command_info: str = ""
    
    def __str__(self):
        return f"[{self.severity.upper()}] Class={self.element_class}, ID={self.element_id}: {self.message}"
