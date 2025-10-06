"""
Command Factory for CGM
Creates appropriate command instances based on element class and ID
"""
from cgm_enums import ClassCode
from commands import (
    UnknownCommand, NoOp, BeginMetafile, EndMetafile, BeginPicture,
    BeginPictureBody, EndPicture, MetafileVersion, MetafileDescription,
    MetafileElementList, CircularArcCentre, EllipticalArc, EllipseElement,
    CircleElement, RestrictedText, EdgeVisibility, InteriorStyle, LineCap,
    LineJoin, EdgeWidth, EdgeCap, EdgeJoin, EdgeColour, EdgeType, 
    BeginFigure, EndFigure,
    BeginApplicationStructure, BeginApplicationStructureBody,
    EndApplicationStructure, MessageCommand, ApplicationStructureAttribute,
    FontProperties, Transparency, ClipIndicator, CharacterSetList,
    MaximumColourIndex, ColourValueExtent, RestrictedTextType,
    MarkerSizeSpecificationMode, EdgeWidthSpecificationMode,
    LineAndEdgeTypeDefinition, LineTypeContinuation, Polybezier,
    CharacterExpansionFactor, TextAlignment, CharacterSetIndex,
    AlternateCharacterSetIndex, ColourTable, InterpolatedInterior,
    HatchStyleDefinition, GeometricPatternDefinition
)
from commands_extended import (
    ColourSelectionMode, VdcExtent, VdcType, IntegerPrecision,
    IndexPrecision, ColourPrecision, ColourIndexPrecision, RealPrecision,
    VdcIntegerPrecision, VdcRealPrecision, Polyline, Text, PolygonElement,
    LineColour, TextColour, FillColour, BackgroundColour, CharacterHeight,
    LineWidth, LineType, DisjointPolyline, FontList, CharacterCodingAnnouncer,
    MetafileDefaultsReplacement, ScalingMode, LineWidthSpecificationMode,
    CharacterOrientation, TextFontIndex, MaximumVdcExtent
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
            8: lambda: BeginFigure(container),
            9: lambda: EndFigure(container),
            21: lambda: BeginApplicationStructure(container),
            22: lambda: BeginApplicationStructureBody(container),
            23: lambda: EndApplicationStructure(container),
            # Add more delimiter elements as needed:
            # 6: BeginSegment
            # 7: EndSegment
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
            3: lambda: VdcType(container),  # Use proper VdcType from commands_extended
            4: lambda: IntegerPrecision(container),
            5: lambda: RealPrecision(container),
            6: lambda: IndexPrecision(container),
            7: lambda: ColourPrecision(container),
            8: lambda: ColourIndexPrecision(container),
            9: lambda: MaximumColourIndex(container),
            10: lambda: ColourValueExtent(container),
            11: lambda: MetafileElementList(container),
            13: lambda: FontList(container),
            14: lambda: CharacterSetList(container),
            15: lambda: CharacterCodingAnnouncer(container),
            17: lambda: MaximumVdcExtent(container),  # Proper implementation
            21: lambda: FontProperties(container),
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 1, container)
    
    def _create_picture_descriptor(self, element_id: int, container):
        """Create picture descriptor commands"""
        commands = {
            1: lambda: ScalingMode(container),
            2: lambda: ColourSelectionMode(container),
            3: lambda: LineWidthSpecificationMode(container),
            4: lambda: MarkerSizeSpecificationMode(container),
            5: lambda: EdgeWidthSpecificationMode(container),
            6: lambda: VdcExtent(container),
            7: lambda: BackgroundColour(container),
            17: lambda: LineAndEdgeTypeDefinition(container),
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 2, container)
    
    def _create_control_element(self, element_id: int, container):
        """Create control element commands"""
        commands = {
            1: lambda: VdcIntegerPrecision(container),
            2: lambda: VdcRealPrecision(container),
            4: lambda: Transparency(container),
            6: lambda: ClipIndicator(container),
            19: lambda: LineTypeContinuation(container),
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 3, container)
    
    def _create_graphical_primitive(self, element_id: int, container):
        """Create graphical primitive commands"""
        commands = {
            1: lambda: Polyline(container),
            2: lambda: DisjointPolyline(container),
            4: lambda: Text(container),
            5: lambda: RestrictedText(container),
            7: lambda: PolygonElement(container),
            12: lambda: CircleElement(container),
            15: lambda: CircularArcCentre(container),
            17: lambda: EllipseElement(container),
            18: lambda: EllipticalArc(container),
            26: lambda: Polybezier(container),
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 4, container)
    
    def _create_attribute_element(self, element_id: int, container):
        """Create attribute element commands"""
        commands = {
            2: lambda: LineType(container),
            3: lambda: LineWidth(container),
            4: lambda: LineColour(container),
            10: lambda: TextFontIndex(container),
            12: lambda: CharacterExpansionFactor(container),
            14: lambda: TextColour(container),
            15: lambda: CharacterHeight(container),
            16: lambda: CharacterOrientation(container),
            18: lambda: TextAlignment(container),
            19: lambda: CharacterSetIndex(container),
            20: lambda: AlternateCharacterSetIndex(container),
            22: lambda: InteriorStyle(container),
            23: lambda: FillColour(container),
            27: lambda: EdgeType(container),
            28: lambda: EdgeWidth(container),
            29: lambda: EdgeColour(container),
            30: lambda: EdgeVisibility(container),
            34: lambda: ColourTable(container),
            37: lambda: LineCap(container),
            38: lambda: LineJoin(container),
            42: lambda: RestrictedTextType(container),
            44: lambda: EdgeCap(container),
            45: lambda: EdgeJoin(container),
            46: lambda: GeometricPatternDefinition(container),
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 5, container)
    
    def _create_external_element(self, element_id: int, container):
        """Create external element commands"""
        commands = {
            1: lambda: MessageCommand(container),
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 7, container)
    
    def _create_segment_element(self, element_id: int, container):
        """Create segment control and attribute commands"""
        # Most segment elements not yet implemented
        return UnknownCommand(element_id, 8, container)
    
    def _create_application_structure(self, element_id: int, container):
        """Create application structure descriptor commands"""
        commands = {
            1: lambda: ApplicationStructureAttribute(container),
        }
        
        creator = commands.get(element_id)
        if creator:
            return creator()
        return UnknownCommand(element_id, 9, container)
