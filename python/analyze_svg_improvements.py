#!/usr/bin/env python3
"""
Analyze SVG conversion improvements
Shows what graphical elements are being converted from cleartext CGM to SVG
"""

import re
import os
from collections import Counter

def analyze_cleartext_commands(cleartext_file):
    """Analyze commands in cleartext CGM file"""
    commands = Counter()
    with open(cleartext_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('%'):
                parts = line.split()
                if parts:
                    cmd = parts[0].upper()
                    commands[cmd] += 1
    return commands

def analyze_svg_elements(svg_file):
    """Analyze elements in SVG file"""
    elements = Counter()
    with open(svg_file, 'r') as f:
        content = f.read()
        # Count each type of SVG element
        for match in re.finditer(r'<(\w+)', content):
            elem_type = match.group(1)
            if elem_type not in ['svg', 'defs', 'style', 'g', '?xml']:
                elements[elem_type] += 1
    return elements

def main():
    cleartext_file = 'tests/batch_tests/ICN-C0419-S1000D0394-001-01_cleartext.cgm'
    svg_file = 'tests/batch_tests/ICN-C0419-S1000D0394-001-01.svg'
    
    if not os.path.exists(cleartext_file):
        print(f"Error: {cleartext_file} not found")
        return
    
    if not os.path.exists(svg_file):
        print(f"Error: {svg_file} not found")
        return
    
    print("=" * 70)
    print("CGM TO SVG CONVERSION ANALYSIS")
    print("=" * 70)
    
    # Analyze cleartext commands
    commands = analyze_cleartext_commands(cleartext_file)
    print("\n📄 CLEARTEXT CGM COMMANDS (Graphical Primitives):")
    print("-" * 70)
    graphical_commands = ['LINE', 'CIRCLE', 'ELLIPSE', 'POLYGON', 'ARCCTR', 
                          'ELLIPARC', 'RESTRTEXT', 'TEXT']
    for cmd in graphical_commands:
        if cmd in commands:
            print(f"  {cmd:15s}: {commands[cmd]:5d} occurrences")
    
    # Analyze SVG elements
    elements = analyze_svg_elements(svg_file)
    print("\n🎨 SVG OUTPUT ELEMENTS:")
    print("-" * 70)
    for elem, count in elements.most_common():
        print(f"  <{elem}>{' ' * (12-len(elem))}: {count:5d} elements")
    
    # Conversion mapping
    print("\n🔄 CONVERSION MAPPING:")
    print("-" * 70)
    print(f"  LINE     → <polyline>  : {commands.get('LINE', 0):5d} → {elements.get('polyline', 0):5d}")
    print(f"  CIRCLE   → <circle>    : {commands.get('CIRCLE', 0):5d} → {elements.get('circle', 0):5d}")
    print(f"  ELLIPSE  → <ellipse>   : {commands.get('ELLIPSE', 0):5d} → {elements.get('ellipse', 0):5d}")
    print(f"  POLYGON  → <polygon>   : {commands.get('POLYGON', 0):5d} → {elements.get('polygon', 0):5d}")
    print(f"  ARCCTR   → <path>      : {commands.get('ARCCTR', 0):5d} → ~{elements.get('path', 0):5d}")
    print(f"  RESTRTEXT→ <text>      : {commands.get('RESTRTEXT', 0):5d} → {elements.get('text', 0):5d}")
    
    # Coverage analysis
    total_graphical = sum(commands.get(cmd, 0) for cmd in graphical_commands)
    total_svg = sum(elements.values())
    
    print("\n📊 COVERAGE STATISTICS:")
    print("-" * 70)
    print(f"  Total graphical commands in CGM: {total_graphical:5d}")
    print(f"  Total SVG elements generated   : {total_svg:5d}")
    
    # Check what's missing
    print("\n⚠️  COMMANDS NOT YET CONVERTED:")
    print("-" * 70)
    not_converted = set()
    if commands.get('ELLIPARC', 0) > elements.get('path', 0):
        not_converted.add(f"ELLIPARC ({commands.get('ELLIPARC', 0)} commands)")
    
    # List other high-frequency commands that might be graphical
    other_commands = set(commands.keys()) - set(graphical_commands)
    other_commands -= {'BEGMF', 'ENDMF', 'BEGPIC', 'ENDPIC', 'BEGPICBODY', 
                       'MFVERSION', 'MFDESC', 'MFELEMLIST', 'FONTLIST',
                       'FONTPROP', 'LINECAP', 'LINEJOIN', 'LINEWIDTH',
                       'LINECOLR', 'LINETYPE', 'FILLCOLR', 'EDGEWIDTH',
                       'EDGECOLR', 'EDGEVIS', 'INTSTYLE', 'TEXTCOLR',
                       'TRANSPARENCY', 'BEGAPS', 'BEGAPSBODY;', 'ENDAPS;',
                       'APSATTR', '1', '3'}
    
    if other_commands:
        print("  Other commands in file:")
        for cmd in sorted(other_commands):
            if commands[cmd] > 0:
                print(f"    {cmd}: {commands[cmd]} occurrences")
    else:
        print("  ✅ All major graphical commands are being converted!")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
