#!/usr/bin/env python3
"""
Test Script for CGM Library

Tests various components of the CGM binary to clear text converter.
"""

import sys
import io
from cgm_file import BinaryCGMFile, ClearTextCGMFile
from cgm_classes import CGMPoint, CGMColor
from binary_reader import BinaryReader
from cleartext_writer import ClearTextWriter
from commands import BeginMetafile, BeginPicture, EndPicture, EndMetafile
from commands_extended import VdcExtent, Polyline, Text
from cgm_enums import VDCType, ColourSelectionModeType


def test_cgm_point():
    """Test CGMPoint class"""
    print("Testing CGMPoint...")
    
    p1 = CGMPoint(10.5, 20.3)
    p2 = CGMPoint(10.5, 20.3)
    p3 = CGMPoint(15.0, 25.0)
    
    assert p1 == p2, "Equal points should be equal"
    assert p1 != p3, "Different points should not be equal"
    assert str(p1) == "Point(10.5, 20.3)", "String representation should be correct"
    
    print("  ✓ CGMPoint tests passed")


def test_cgm_color():
    """Test CGMColor class"""
    print("Testing CGMColor...")
    
    # Indexed color
    c1 = CGMColor(color_index=5)
    assert c1.is_indexed, "Should be indexed"
    assert c1.color_index == 5, "Index should be 5"
    
    # Direct color
    c2 = CGMColor(r=255, g=128, b=0)
    assert not c2.is_indexed, "Should not be indexed"
    assert c2.r == 255 and c2.g == 128 and c2.b == 0, "RGB values should match"
    
    print("  ✓ CGMColor tests passed")


def test_command_creation():
    """Test command creation"""
    print("Testing command creation...")
    
    # Create a mock CGM file
    cgm = BinaryCGMFile()
    
    # Test BeginMetafile
    cmd1 = BeginMetafile(cgm, "test_file")
    assert cmd1.filename == "test_file", "Filename should be set"
    assert cmd1.element_class == 0, "Element class should be 0"
    assert cmd1.element_id == 1, "Element ID should be 1"
    
    # Test VdcExtent
    p1 = CGMPoint(0, 0)
    p2 = CGMPoint(100, 100)
    cmd2 = VdcExtent(cgm, p1, p2)
    assert cmd2.lower_left_corner == p1, "Lower left should match"
    assert cmd2.upper_right_corner == p2, "Upper right should match"
    
    print("  ✓ Command creation tests passed")


def test_clear_text_writer():
    """Test clear text writer"""
    print("Testing clear text writer...")
    
    # Create a string stream
    stream = io.StringIO()
    writer = ClearTextWriter(stream)
    
    # Write some test commands
    cgm = BinaryCGMFile()
    
    cmd1 = BeginMetafile(cgm, "test")
    cmd1.write_as_clear_text(writer)
    
    cmd2 = BeginPicture(cgm, "picture1")
    cmd2.write_as_clear_text(writer)
    
    cmd3 = EndPicture(cgm)
    cmd3.write_as_clear_text(writer)
    
    cmd4 = EndMetafile(cgm)
    cmd4.write_as_clear_text(writer)
    
    # Get the output
    output = stream.getvalue()
    
    # Check output contains expected commands
    assert "BEGMF 'test';" in output, "Should contain BEGMF command"
    assert "BEGPIC 'picture1';" in output, "Should contain BEGPIC command"
    assert "ENDPIC;" in output, "Should contain ENDPIC command"
    assert "ENDMF;" in output, "Should contain ENDMF command"
    
    print("  ✓ Clear text writer tests passed")


def test_binary_reader_primitives():
    """Test binary reader primitive operations"""
    print("Testing binary reader primitives...")
    
    # Create a mock CGM file
    cgm = BinaryCGMFile()
    cgm.integer_precision = 16
    cgm.vdc_type = VDCType.INTEGER
    cgm.vdc_integer_precision = 16
    
    # Test reading integers
    data = bytes([0x00, 0x0A])  # 16-bit int: 10
    stream = io.BytesIO(data)
    reader = BinaryReader(stream, cgm)
    reader.arguments = data
    reader.current_arg = 0
    
    value = reader.read_signed_int16()
    assert value == 10, f"Should read 10, got {value}"
    
    # Test reading unsigned integers
    data = bytes([0xFF])  # 8-bit uint: 255
    reader.arguments = data
    reader.current_arg = 0
    
    value = reader.read_byte()
    assert value == 255, f"Should read 255, got {value}"
    
    print("  ✓ Binary reader primitive tests passed")


def test_command_factory():
    """Test command factory"""
    print("Testing command factory...")
    
    from command_factory import CommandFactory
    
    cgm = BinaryCGMFile()
    factory = CommandFactory()
    
    # Test creating delimiter commands
    cmd1 = factory.create_command(1, 0, cgm)  # BeginMetafile
    assert isinstance(cmd1, BeginMetafile), "Should create BeginMetafile"
    
    cmd2 = factory.create_command(2, 0, cgm)  # EndMetafile
    assert isinstance(cmd2, EndMetafile), "Should create EndMetafile"
    
    # Test creating picture descriptor commands
    cmd3 = factory.create_command(6, 2, cgm)  # VdcExtent
    assert isinstance(cmd3, VdcExtent), "Should create VdcExtent"
    
    # Test creating graphical primitives
    cmd4 = factory.create_command(1, 4, cgm)  # Polyline
    assert isinstance(cmd4, Polyline), "Should create Polyline"
    
    cmd5 = factory.create_command(4, 4, cgm)  # Text
    assert isinstance(cmd5, Text), "Should create Text"
    
    print("  ✓ Command factory tests passed")


def test_end_to_end():
    """Test end-to-end conversion (mock)"""
    print("Testing end-to-end conversion...")
    
    # Create a minimal CGM file programmatically
    cgm = BinaryCGMFile()
    
    # Add some commands
    cgm.commands.append(BeginMetafile(cgm, "test_file"))
    cgm.commands.append(BeginPicture(cgm, "picture1"))
    
    # Add a polyline
    points = [CGMPoint(0, 0), CGMPoint(10, 10), CGMPoint(20, 0)]
    cgm.commands.append(Polyline(cgm, points))
    
    # Add text
    cgm.commands.append(Text(cgm, "Hello CGM", CGMPoint(5, 5), True))
    
    cgm.commands.append(EndPicture(cgm))
    cgm.commands.append(EndMetafile(cgm))
    
    # Convert to clear text
    cleartext = ClearTextCGMFile(cgm)
    content = cleartext.get_content()
    
    # Verify output
    assert "BEGMF 'test_file';" in content, "Should contain begin metafile"
    assert "BEGPIC 'picture1';" in content, "Should contain begin picture"
    assert "LINE" in content, "Should contain polyline"
    assert "TEXT" in content, "Should contain text"
    assert "Hello CGM" in content, "Should contain text content"
    assert "ENDPIC;" in content, "Should contain end picture"
    assert "ENDMF;" in content, "Should contain end metafile"
    
    print("  ✓ End-to-end tests passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running CGM Library Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_cgm_point,
        test_cgm_color,
        test_command_creation,
        test_clear_text_writer,
        test_binary_reader_primitives,
        test_command_factory,
        test_end_to_end,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
