"""
Command Factory for CGM
Creates appropriate command instances based on element class and ID
"""
from cgm_enums import ClassCode
from commands import (
    UnknownCommand, NoOp, BeginMetafile, EndMetafile, BeginPicture,
    BeginPictureBody, EndPicture, MetafileVersion, MetafileDescription,
    MetafileElementList
)
from commands_extended import (
    ColourSelectionMode, VdcExtent, VdcType, IntegerPrecision,
    IndexPrecision, ColourPrecision, ColourIndexPrecision, RealPrecision,
    VdcIntegerPrecision, VdcRealPrecision, Polyline, Text, PolygonElement,
    LineColour, TextColour, FillColour, BackgroundColour, CharacterHeight
)


class CommandFactory:
    """Factory for creating CGM command instances"""
    
    def create_command(self, element_id: int, element_class: int, container):
        """
        Create a command based on element class and ID
        
        Args:
            element_id: The element ID within the class
            element_class: The element class
            container: The CGM file container
            
        Returns:
            Command instance
        """
        class_code = ClassCode(element_class)
        
        if class_code == ClassCode.DELIMITER_ELEMENT:
            return self._create_delimiter_element(element_id, container)
        elif class_code == ClassCode.METAFILE_DESCRIPTOR_ELEMENTS:
            return self._create_metafile_descriptor(element_id, container)
        elif class_code == ClassCode.PICTURE_DESCRIPTOR_ELEMENTS:
            return self._create_picture_descriptor(element_id, container)
        elif class_code == ClassCode.CONTROL_ELEMENTS:
            return self._create_control_element(element_id, container)
        elif class_code == ClassCode.GRAPHICAL_PRIMITIVE_ELEMENTS:
            return self._create_graphical_primitive(element_id, container)
        elif class_code == ClassCode.ATTRIBUTE_ELEMENTS:
            return self._create_attribute_element(element_id, container)
        elif class_code == ClassCode.ESCAPE_ELEMENT:
            return UnknownCommand(element_id, element_class, container)
        elif class_code == ClassCode.EXTERNAL_ELEMENTS:
            return self._create_external_element(element_id, container)
        elif class_code == ClassCode.SEGMENT_CONTROL_AND_SEGMENT_ATTRIBUTE_ELEMENTS:
            return self._create_segment_element(element_id, container)
        elif class_code == ClassCode.APPLICATION_STRUCTURE_DESCRIPTOR_ELEMENTS:
            return self._create_application_structure(element_id, container)
        else:
            # Reserved or unknown class
            return UnknownCommand(element_id, element_class, container)
    
    def _create_delimiter_element(self, element_id: int, container):
        """Create delimiter element commands"""
        commands = {
            0: lambda: NoOp(container),
            1: lambda: BeginMetafile(container),
            2: lambda: EndMetafile(container),
            3: lambda: BeginPicture(container),
            4: lambda: BeginPictureBody(container),
            5: lambda: EndPicture(container),
            # Add more delimiter elements as needed
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 0, container)
    
    def _create_metafile_descriptor(self, element_id: int, container):
        """Create metafile descriptor commands"""
        commands = {
            1: lambda: MetafileVersion(container),
            2: lambda: MetafileDescription(container),
            4: lambda: IntegerPrecision(container),
            5: lambda: RealPrecision(container),
            6: lambda: IndexPrecision(container),
            7: lambda: ColourPrecision(container),
            8: lambda: ColourIndexPrecision(container),
            11: lambda: MetafileElementList(container),
            # Add more metafile descriptor elements as needed
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 1, container)
    
    def _create_picture_descriptor(self, element_id: int, container):
        """Create picture descriptor commands"""
        commands = {
            1: lambda: VdcIntegerPrecision(container),
            2: lambda: ColourSelectionMode(container),
            3: lambda: VdcType(container),
            6: lambda: VdcExtent(container),
            7: lambda: BackgroundColour(container),
            # VDC REAL PRECISION is element 2 but conflicts with ColorSelectionMode
            # Need to check specification for correct mapping
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 2, container)
    
    def _create_control_element(self, element_id: int, container):
        """Create control element commands"""
        # Most control elements not yet implemented
        return UnknownCommand(element_id, 3, container)
    
    def _create_graphical_primitive(self, element_id: int, container):
        """Create graphical primitive commands"""
        commands = {
            1: lambda: Polyline(container),
            4: lambda: Text(container),
            7: lambda: PolygonElement(container),
            # Add more graphical primitives as needed:
            # 2: DisjointPolyline
            # 3: Polymarker
            # 5: RestrictedText
            # 6: AppendText
            # 8: PolyBezier
            # 9: PolygonSet
            # 10: CellArray
            # 11: GeneralizedDrawingPrimitive
            # 12: Rectangle
            # 13: Circle
            # 14: CircularArc3Point
            # 15: CircularArc3PointClose
            # 16: CircularArcCentre
            # 17: CircularArcCentreClose
            # 18: Ellipse
            # 19: EllipticalArc
            # 20: EllipticalArcClose
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 4, container)
    
    def _create_attribute_element(self, element_id: int, container):
        """Create attribute element commands"""
        commands = {
            4: lambda: LineColour(container),
            14: lambda: TextColour(container),
            15: lambda: CharacterHeight(container),
            23: lambda: FillColour(container),
            # Add more attribute elements as needed:
            # 1: LineBundleIndex
            # 2: LineType
            # 3: LineWidth
            # 5: MarkerBundleIndex
            # 6: MarkerType
            # 7: MarkerSize
            # 8: MarkerColour
            # 9: TextBundleIndex
            # 10: TextFontIndex
            # 11: TextPrecision
            # 12: CharacterExpansionFactor
            # 13: CharacterSpacing
            # 16: CharacterOrientation
            # 17: TextPath
            # 18: TextAlignment
            # 19: CharacterSetIndex
            # 20: AlternateCharacterSetIndex
            # 21: FillBundleIndex
            # 22: InteriorStyle
            # 24: HatchIndex
            # 25: PatternIndex
            # 26: EdgeBundleIndex
            # 27: EdgeType
            # 28: EdgeWidth
            # 29: EdgeColour
            # 30: EdgeVisibility
            # 31: FillReferencePoint
            # 32: PatternTable
            # 33: PatternSize
            # 34: ColourTable
            # 35: AspectSourceFlags
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 5, container)
    
    def _create_external_element(self, element_id: int, container):
        """Create external element commands"""
        # Most external elements not yet implemented
        return UnknownCommand(element_id, 7, container)
    
    def _create_segment_element(self, element_id: int, container):
        """Create segment control and attribute commands"""
        # Most segment elements not yet implemented
        return UnknownCommand(element_id, 8, container)
    
    def _create_application_structure(self, element_id: int, container):
        """Create application structure descriptor commands"""
        # Most application structure elements not yet implemented
        return UnknownCommand(element_id, 9, container)
