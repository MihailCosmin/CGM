#!/usr/bin/env python3
"""
Debug CGM Command Creation
Test what commands are actually being created by our factory
"""
import sys
import os
sys.path.append('/home/cosmin/Develop/CGM/python')

from command_factory import CommandFactory
from commands import CircularArcCentre, EllipticalArc, UnknownCommand

def test_command_creation():
    """Test command creation for the problematic IDs"""
    print("🔍 Testing Command Factory")
    print("=" * 40)
    
    factory = CommandFactory()
    
    # Test Class=4 (GraphicalPrimitiveElements) commands
    test_cases = [
        (4, 15, "CIRCULAR_ARC_CENTRE"),
        (4, 18, "ELLIPTICAL_ARC"),
        (4, 17, "ELLIPSE"),
        (4, 12, "CIRCLE"),
        (4, 5, "RESTRICTED_TEXT"),
        (1, 21, "Unknown Class 1"),
        (5, 30, "Unknown Class 5")
    ]
    
    for element_class, element_id, expected_name in test_cases:
        try:
            command = factory.create_command(element_id, element_class, None)
            command_type = type(command).__name__
            
            if isinstance(command, UnknownCommand):
                print(f"❌ Class={element_class}, ID={element_id}: {command_type} (Expected: {expected_name})")
            else:
                print(f"✅ Class={element_class}, ID={element_id}: {command_type}")
                
        except Exception as e:
            print(f"💥 Class={element_class}, ID={element_id}: ERROR - {e}")

if __name__ == "__main__":
    test_command_creation()