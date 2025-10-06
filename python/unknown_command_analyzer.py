#!/usr/bin/env python3
"""
CGM Unknown Command Analyzer

Analyzes unknown commands in cleartext CGM files and suggests implementations
based on CGM specification.
"""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# CGM Command definitions from specifications
CGM_COMMANDS = {
    # Class 0: Delimiter Elements
    0: {
        0: "NO OP",
        1: "BEGIN METAFILE",
        2: "END METAFILE", 
        3: "BEGIN PICTURE",
        4: "BEGIN PICTURE BODY",
        5: "END PICTURE",
        6: "BEGIN SEGMENT",
        7: "END SEGMENT",
        8: "BEGIN FIGURE",
        9: "END FIGURE",
        10: "BEGIN PROTECTION REGION",
        11: "END PROTECTION REGION",
        12: "BEGIN COMPOUND LINE",
        13: "END COMPOUND LINE",
        14: "BEGIN COMPOUND TEXT PATH",
        15: "END COMPOUND TEXT PATH",
        16: "BEGIN TILE ARRAY",
        17: "END TILE ARRAY",
        18: "BEGIN APPLICATION STRUCTURE",
        19: "END APPLICATION STRUCTURE",
        20: "BEGIN APPLICATION STRUCTURE BODY",
        21: "APPLICATION STRUCTURE DIRECTORY",
        22: "ESCAPE",
        23: "MESSAGE"
    },
    
    # Class 1: Metafile Descriptor Elements
    1: {
        1: "METAFILE VERSION",
        2: "METAFILE DESCRIPTION",
        3: "VDC TYPE",
        4: "INTEGER PRECISION",
        5: "REAL PRECISION",
        6: "INDEX PRECISION",
        7: "COLOUR PRECISION",
        8: "COLOUR INDEX PRECISION",
        9: "MAXIMUM COLOUR INDEX",
        10: "COLOUR VALUE EXTENT",
        11: "METAFILE ELEMENT LIST",
        12: "METAFILE DEFAULTS REPLACEMENT",
        13: "FONT LIST",
        14: "CHARACTER SET LIST",
        15: "CHARACTER CODING ANNOUNCER",
        16: "NAME PRECISION",
        17: "MAXIMUM VDC EXTENT",
        18: "SEGMENT PRIORITY EXTENT",
        19: "COLOUR MODEL",
        20: "COLOUR CALIBRATION",
        21: "FONT PROPERTIES",
        22: "GLYPH MAPPING",
        23: "SYMBOL LIBRARY LIST",
        24: "PICTURE DIRECTORY"
    },
    
    # Class 2: Picture Descriptor Elements
    2: {
        1: "SCALING MODE",
        2: "COLOUR SELECTION MODE",
        3: "LINE WIDTH SPECIFICATION MODE",
        4: "MARKER SIZE SPECIFICATION MODE",
        5: "EDGE WIDTH SPECIFICATION MODE",
        6: "VDC EXTENT",
        7: "BACKGROUND COLOUR",
        8: "DEVICE VIEWPORT",
        9: "DEVICE VIEWPORT SPECIFICATION MODE",
        10: "DEVICE VIEWPORT MAPPING",
        11: "LINE REPRESENTATION",
        12: "MARKER REPRESENTATION",
        13: "TEXT REPRESENTATION",
        14: "FILL REPRESENTATION",
        15: "EDGE REPRESENTATION",
        16: "INTERIOR STYLE SPECIFICATION MODE",
        17: "LINE AND EDGE TYPE DEFINITION",
        18: "HATCH STYLE DEFINITION",
        19: "GEOMETRIC PATTERN DEFINITION"
    },
    
    # Class 3: Control Elements
    3: {
        1: "VDC INTEGER PRECISION",
        2: "VDC REAL PRECISION",
        3: "AUXILIARY COLOUR",
        4: "TRANSPARENCY",
        5: "CLIP RECTANGLE",
        6: "CLIP INDICATOR",
        7: "LINE CLIPPING MODE",
        8: "MARKER CLIPPING MODE",
        9: "EDGE CLIPPING MODE",
        10: "NEW REGION",
        11: "SAVE PRIMITIVE CONTEXT",
        12: "RESTORE PRIMITIVE CONTEXT",
        13: "PROTECTION REGION INDICATOR",
        14: "GENERALIZED TEXT PATH MODE",
        15: "MITRE LIMIT",
        16: "TRANSPARENT CELL COLOUR",
        17: "LINE CAP",
        18: "LINE JOIN",
        19: "LINE TYPE CONTINUATION",
        20: "LINE TYPE INITIAL OFFSET"
    },
    
    # Class 4: Graphical Primitive Elements
    4: {
        1: "POLYLINE",
        2: "DISJOINT POLYLINE", 
        3: "POLYMARKER",
        4: "TEXT",
        5: "RESTRICTED TEXT",
        6: "APPEND TEXT",
        7: "POLYGON",
        8: "POLYGON SET",
        9: "CELL ARRAY",
        10: "GENERALIZED DRAWING PRIMITIVE",
        11: "RECTANGLE",
        12: "CIRCLE",
        13: "CIRCULAR ARC 3 POINT",
        14: "CIRCULAR ARC 3 POINT CLOSE",
        15: "CIRCULAR ARC CENTRE",
        16: "CIRCULAR ARC CENTRE CLOSE",
        17: "ELLIPSE",
        18: "ELLIPTICAL ARC",
        19: "ELLIPTICAL ARC CLOSE",
        20: "CIRCULAR ARC CENTRE REVERSED",
        21: "CONNECTING EDGE",
        22: "HYPERBOLIC ARC",
        23: "PARABOLIC ARC",
        24: "NON UNIFORM B-SPLINE",
        25: "NON UNIFORM RATIONAL B-SPLINE",
        26: "POLYBEZIER",
        27: "POLYSYMBOL",
        28: "BITONAL TILE",
        29: "TILE"
    },
    
    # Class 5: Attribute Elements
    5: {
        1: "LINE BUNDLE INDEX",
        2: "LINE TYPE",
        3: "LINE WIDTH",
        4: "LINE COLOUR",
        5: "MARKER BUNDLE INDEX",
        6: "MARKER TYPE",
        7: "MARKER SIZE",
        8: "MARKER COLOUR",
        9: "TEXT BUNDLE INDEX",
        10: "TEXT FONT INDEX",
        11: "TEXT PRECISION",
        12: "CHARACTER EXPANSION FACTOR",
        13: "CHARACTER SPACING",
        14: "TEXT COLOUR",
        15: "CHARACTER HEIGHT",
        16: "CHARACTER ORIENTATION",
        17: "TEXT PATH",
        18: "TEXT ALIGNMENT",
        19: "CHARACTER SET INDEX",
        20: "ALTERNATE CHARACTER SET INDEX",
        21: "FILL BUNDLE INDEX",
        22: "INTERIOR STYLE",
        23: "FILL COLOUR",
        24: "HATCH INDEX",
        25: "PATTERN INDEX",
        26: "EDGE BUNDLE INDEX",
        27: "EDGE TYPE",
        28: "EDGE WIDTH",
        29: "EDGE COLOUR",
        30: "EDGE VISIBILITY",
        31: "FILL REFERENCE POINT",
        32: "PATTERN TABLE",
        33: "PATTERN SIZE",
        34: "COLOUR TABLE",
        35: "ASPECT SOURCE FLAGS",
        36: "PICK IDENTIFIER",
        37: "LINE CAP",
        38: "LINE JOIN",
        39: "LINE TYPE CONTINUATION",
        40: "LINE TYPE INITIAL OFFSET",
        41: "RESTRICTED TEXT TYPE",
        42: "INTERPOLATED INTERIOR",
        43: "LINE AND EDGE TYPE DEFINITION",
        44: "HATCH STYLE DEFINITION",
        45: "GEOMETRIC PATTERN DEFINITION"
    },
    
    # Class 9: Application Structure Descriptor Elements  
    9: {
        1: "APPLICATION STRUCTURE ATTRIBUTE"
    }
}

def analyze_unknown_commands(cleartext_dir):
    """Analyze unknown commands in cleartext CGM files"""
    
    unknown_pattern = re.compile(r'% Unknown command: Class=(\d+), ID=(\d+)')
    unknown_stats = Counter()
    file_stats = defaultdict(list)
    
    cleartext_files = list(Path(cleartext_dir).glob("*cleartext.cgm"))
    
    print(f"Analyzing {len(cleartext_files)} cleartext CGM files...")
    
    for file_path in cleartext_files:
        file_unknowns = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    match = unknown_pattern.search(line)
                    if match:
                        class_id = int(match.group(1))
                        element_id = int(match.group(2))
                        unknown_stats[(class_id, element_id)] += 1
                        file_unknowns.append((class_id, element_id, line_num))
        
            if file_unknowns:
                file_stats[file_path.name] = file_unknowns
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return unknown_stats, file_stats

def suggest_implementations(unknown_stats):
    """Suggest implementations for unknown commands"""
    
    print("\n" + "="*80)
    print("UNKNOWN COMMAND ANALYSIS")
    print("="*80)
    
    print(f"\nFound {len(unknown_stats)} different unknown commands:")
    print(f"Total unknown command instances: {sum(unknown_stats.values())}")
    
    print(f"\n{'Rank':<4} {'Class':<5} {'ID':<3} {'Count':<8} {'Command Name':<40} {'Status'}")
    print("-" * 80)
    
    suggestions = []
    
    for rank, ((class_id, element_id), count) in enumerate(unknown_stats.most_common(), 1):
        command_name = CGM_COMMANDS.get(class_id, {}).get(element_id, "UNKNOWN")
        
        if command_name == "UNKNOWN":
            status = "⚠️  NOT IN SPEC"
        else:
            status = "✅ NEEDS IMPL"
            
        print(f"{rank:<4} {class_id:<5} {element_id:<3} {count:<8} {command_name:<40} {status}")
        
        if count > 100:  # Focus on high-impact commands
            suggestions.append({
                'class_id': class_id,
                'element_id': element_id, 
                'name': command_name,
                'count': count,
                'priority': 'HIGH' if count > 1000 else 'MEDIUM'
            })
    
    return suggestions

def generate_implementation_guide(suggestions):
    """Generate implementation guide for missing commands"""
    
    print("\n" + "="*80)
    print("IMPLEMENTATION PRIORITY GUIDE")
    print("="*80)
    
    high_priority = [s for s in suggestions if s['priority'] == 'HIGH']
    medium_priority = [s for s in suggestions if s['priority'] == 'MEDIUM']
    
    if high_priority:
        print(f"\n🔥 HIGH PRIORITY ({len(high_priority)} commands - implement first):")
        for cmd in high_priority:
            print(f"   • Class {cmd['class_id']}, ID {cmd['element_id']}: {cmd['name']} ({cmd['count']:,} uses)")
    
    if medium_priority:
        print(f"\n⚡ MEDIUM PRIORITY ({len(medium_priority)} commands):")
        for cmd in medium_priority:
            print(f"   • Class {cmd['class_id']}, ID {cmd['element_id']}: {cmd['name']} ({cmd['count']:,} uses)")
    
    print("\n" + "="*80)
    print("IMPLEMENTATION TEMPLATES")
    print("="*80)
    
    # Group by class for implementation templates
    by_class = defaultdict(list)
    for cmd in suggestions[:10]:  # Top 10 commands
        by_class[cmd['class_id']].append(cmd)
    
    for class_id, commands in by_class.items():
        class_names = {
            0: "DelimiterElements",
            1: "MetaFileDescriptorElements", 
            2: "PictureDescriptorElements",
            3: "ControlElements",
            4: "GraphicalPrimitiveElements",
            5: "AttributeElements",
            9: "ApplicationStructureDescriptorElements"
        }
        
        class_name = class_names.get(class_id, f"Class{class_id}Elements")
        
        print(f"\n📝 {class_name} (Class {class_id}):")
        
        for cmd in commands:
            enum_name = cmd['name'].replace(' ', '_').replace('-', '_').upper()
            class_name_pascal = ''.join(word.capitalize() for word in cmd['name'].split())
            
            print(f"""
   // Add to enum:
   {enum_name} = {cmd['element_id']},
   
   // Add to switch statement:
   {class_name}Element.{enum_name} => new {class_name_pascal}(container),
   
   // Create command class: Commands/{class_name_pascal}.cs""")

def main():
    if len(sys.argv) != 2:
        print("Usage: python unknown_command_analyzer.py <cleartext_directory>")
        sys.exit(1)
    
    cleartext_dir = sys.argv[1]
    
    if not Path(cleartext_dir).exists():
        print(f"Directory not found: {cleartext_dir}")
        sys.exit(1)
    
    unknown_stats, file_stats = analyze_unknown_commands(cleartext_dir)
    
    if not unknown_stats:
        print("No unknown commands found!")
        return
    
    suggestions = suggest_implementations(unknown_stats)
    generate_implementation_guide(suggestions)
    
    print(f"\n💡 Next steps:")
    print(f"   1. Implement high-priority commands first")
    print(f"   2. Create command classes in src/Commands/")
    print(f"   3. Add enum entries to appropriate Element files")
    print(f"   4. Update switch statements in Elements/ files")
    print(f"   5. Test with batch_tests CGM files")

if __name__ == "__main__":
    main()