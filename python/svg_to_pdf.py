#!/usr/bin/env python3
"""
SVG to PDF Converter

Converts SVG (Scalable Vector Graphics) files to PDF format.
This completes the CGM processing pipeline: Binary CGM → Clear Text CGM → SVG → PDF

Features:
- High-quality SVG to PDF conversion
- Preserves vector graphics quality
- Maintains original dimensions and scaling
- Supports text, paths, and graphics elements
- Command-line interface with progress reporting

Dependencies:
- reportlab: pip install reportlab
- svglib: pip install svglib

Author: GitHub Copilot
Date: October 2025
"""

import sys
import os
from pathlib import Path
import argparse
import time
from typing import Optional, Tuple

try:
    from reportlab.graphics import renderPDF
    from reportlab.lib.pagesizes import letter, A4, legal
    from reportlab.lib.units import inch
    from svglib.svglib import svg2rlg
except ImportError as e:
    print("Error: Missing required dependencies. Please install:")
    print("pip install reportlab svglib")
    print(f"Import error: {e}")
    sys.exit(1)


class SVGToPDFConverter:
    """
    Converts SVG files to PDF format while preserving vector graphics quality.
    """
    
    def __init__(self):
        """Initialize the converter."""
        self.supported_page_sizes = {
            'letter': letter,
            'a4': A4,
            'legal': legal
        }
    
    def get_svg_dimensions(self, svg_path: str) -> Optional[Tuple[float, float]]:
        """
        Extract dimensions from SVG file.
        
        Args:
            svg_path: Path to the SVG file
            
        Returns:
            Tuple of (width, height) in points, or None if dimensions cannot be determined
        """
        try:
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for width and height attributes in the SVG tag
            import re
            
            # Try to find width and height attributes
            width_match = re.search(r'width\s*=\s*["\']([^"\']+)["\']', content)
            height_match = re.search(r'height\s*=\s*["\']([^"\']+)["\']', content)
            
            if width_match and height_match:
                width_str = width_match.group(1)
                height_str = height_match.group(1)
                
                # Remove units and convert to float
                width = float(re.sub(r'[^\d.]', '', width_str))
                height = float(re.sub(r'[^\d.]', '', height_str))
                
                return (width, height)
            
            # Try to find viewBox attribute as fallback
            viewbox_match = re.search(r'viewBox\s*=\s*["\']([^"\']+)["\']', content)
            if viewbox_match:
                viewbox = viewbox_match.group(1).split()
                if len(viewbox) >= 4:
                    width = float(viewbox[2]) - float(viewbox[0])
                    height = float(viewbox[3]) - float(viewbox[1])
                    return (width, height)
            
            return None
            
        except Exception as e:
            print(f"Warning: Could not extract SVG dimensions: {e}")
            return None
    
    def get_content_bounds(self, svg_path: str) -> Optional[Tuple[float, float, float, float]]:
        """
        Calculate the actual content bounds of the SVG by analyzing all drawing elements.
        
        Args:
            svg_path: Path to the SVG file
            
        Returns:
            Tuple of (min_x, min_y, max_x, max_y) in points, or None if bounds cannot be determined
        """
        try:
            import xml.etree.ElementTree as ET
            import re
            
            tree = ET.parse(svg_path)
            root = tree.getroot()
            
            # SVG namespace
            ns = {'svg': 'http://www.w3.org/2000/svg'}
            
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')
            
            def parse_path_data(path_data):
                """Extract coordinates from SVG path data"""
                coords = []
                # Find all numeric values in the path data
                numbers = re.findall(r'-?\d*\.?\d+', path_data)
                for i in range(0, len(numbers), 2):
                    if i + 1 < len(numbers):
                        coords.append((float(numbers[i]), float(numbers[i + 1])))
                return coords
            
            def is_visible_element(elem):
                """Check if element has visible content"""
                # Check for stroke or fill
                style = elem.attrib.get('style', '')
                fill = elem.attrib.get('fill', 'black')
                stroke = elem.attrib.get('stroke', 'none')
                
                # Element is visible if it has fill or stroke
                if 'fill:none' in style and 'stroke:none' in style:
                    return False
                if fill == 'none' and stroke == 'none':
                    return False
                if 'visibility:hidden' in style or 'display:none' in style:
                    return False
                
                return True
            
            def update_bounds(x, y):
                nonlocal min_x, min_y, max_x, max_y
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
            
            # Process all drawing elements
            for elem in root.iter():
                # Skip invisible elements
                if not is_visible_element(elem):
                    continue
                    
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                
                if tag == 'path' and 'd' in elem.attrib:
                    # Process path elements
                    path_coords = parse_path_data(elem.attrib['d'])
                    for x, y in path_coords:
                        update_bounds(x, y)
                
                elif tag == 'text' and 'x' in elem.attrib and 'y' in elem.attrib:
                    # Process text elements
                    x = float(elem.attrib['x'])
                    y = float(elem.attrib['y'])
                    update_bounds(x, y)
                
                elif tag == 'line':
                    # Process line elements
                    x1 = float(elem.attrib.get('x1', 0))
                    y1 = float(elem.attrib.get('y1', 0))
                    x2 = float(elem.attrib.get('x2', 0))
                    y2 = float(elem.attrib.get('y2', 0))
                    update_bounds(x1, y1)
                    update_bounds(x2, y2)
                
                elif tag == 'rect':
                    # Process rectangle elements
                    x = float(elem.attrib.get('x', 0))
                    y = float(elem.attrib.get('y', 0))
                    width = float(elem.attrib.get('width', 0))
                    height = float(elem.attrib.get('height', 0))
                    update_bounds(x, y)
                    update_bounds(x + width, y + height)
                
                elif tag == 'circle':
                    # Process circle elements
                    cx = float(elem.attrib.get('cx', 0))
                    cy = float(elem.attrib.get('cy', 0))
                    r = float(elem.attrib.get('r', 0))
                    update_bounds(cx - r, cy - r)
                    update_bounds(cx + r, cy + r)
            
            # Check if we found any content
            if min_x == float('inf'):
                return None
            
            # Collect all coordinates for statistical analysis
            all_coords = []
            
            # Re-process elements to collect all coordinates
            for elem in root.iter():
                if not is_visible_element(elem):
                    continue
                    
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                
                if tag == 'path' and 'd' in elem.attrib:
                    path_coords = parse_path_data(elem.attrib['d'])
                    all_coords.extend(path_coords)
                elif tag == 'text' and 'x' in elem.attrib and 'y' in elem.attrib:
                    x = float(elem.attrib['x'])
                    y = float(elem.attrib['y'])
                    all_coords.append((x, y))
                elif tag == 'line':
                    x1 = float(elem.attrib.get('x1', 0))
                    y1 = float(elem.attrib.get('y1', 0))
                    x2 = float(elem.attrib.get('x2', 0))
                    y2 = float(elem.attrib.get('y2', 0))
                    all_coords.extend([(x1, y1), (x2, y2)])
                elif tag == 'rect':
                    x = float(elem.attrib.get('x', 0))
                    y = float(elem.attrib.get('y', 0))
                    width = float(elem.attrib.get('width', 0))
                    height = float(elem.attrib.get('height', 0))
                    all_coords.extend([(x, y), (x + width, y + height)])
                elif tag == 'circle':
                    cx = float(elem.attrib.get('cx', 0))
                    cy = float(elem.attrib.get('cy', 0))
                    r = float(elem.attrib.get('r', 0))
                    all_coords.extend([(cx - r, cy - r), (cx + r, cy + r)])
            
            if all_coords:
                # Use statistical analysis to filter outliers
                x_coords = sorted([coord[0] for coord in all_coords])
                y_coords = sorted([coord[1] for coord in all_coords])
                
                # Use 5th and 95th percentiles to exclude outliers
                x_count = len(x_coords)
                y_count = len(y_coords)
                
                min_x = x_coords[int(x_count * 0.05)]
                max_x = x_coords[int(x_count * 0.95)]
                min_y = y_coords[int(y_count * 0.05)]
                max_y = y_coords[int(y_count * 0.95)]
            
            # Add reasonable padding 
            padding = 15
            min_x -= padding
            min_y -= padding
            max_x += padding
            max_y += padding
            
            return (min_x, min_y, max_x, max_y)
            
        except Exception as e:
            print(f"Warning: Could not calculate content bounds: {e}")
            return None
    
    def convert_svg_to_pdf(self, 
                          svg_path: str, 
                          pdf_path: str, 
                          page_size: str = 'a4',
                          fit_to_page: bool = True,
                          margin: float = 0.5,
                          crop_to_content: bool = True) -> bool:
        """
        Convert SVG file to PDF.
        
        Args:
            svg_path: Path to input SVG file
            pdf_path: Path to output PDF file
            page_size: Page size ('a4', 'letter', 'legal', or 'auto')
            fit_to_page: Whether to scale SVG to fit page
            margin: Margin in inches
            crop_to_content: Whether to crop to actual content bounds
            
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            print(f"Converting SVG to PDF:")
            print(f"  Input:  {svg_path}")
            print(f"  Output: {pdf_path}")
            
            # Render SVG to ReportLab drawing
            drawing = svg2rlg(svg_path)
            
            if drawing is None:
                print("Error: Failed to render SVG")
                return False
            
            # Get SVG dimensions
            svg_dimensions = self.get_svg_dimensions(svg_path)
            original_width = drawing.width
            original_height = drawing.height
            
            print(f"  Original SVG dimensions: {original_width:.1f} x {original_height:.1f} points")
            
            # Apply content cropping if requested
            if crop_to_content:
                content_bounds = self.get_content_bounds(svg_path)
                if content_bounds:
                    min_x, min_y, max_x, max_y = content_bounds
                    content_width = max_x - min_x
                    content_height = max_y - min_y
                    
                    print(f"  Content bounds: ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f})")
                    print(f"  Content dimensions: {content_width:.1f} x {content_height:.1f} points")
                    
                    # Create a new drawing with cropped content
                    from reportlab.graphics.shapes import Group
                    cropped_drawing = Group()
                    
                    # Copy all elements from original drawing but translate them
                    for element in drawing.contents:
                        cropped_drawing.add(element)
                    
                    # Translate to remove the minimum bounds (crop to content)
                    cropped_drawing.translate(-min_x, -min_y)
                    
                    # Create new drawing with content dimensions
                    from reportlab.graphics.shapes import Drawing as RLDrawing
                    drawing = RLDrawing(content_width, content_height)
                    drawing.add(cropped_drawing)
                    
                    print(f"  Cropped to content: {content_width:.1f} x {content_height:.1f} points")
                else:
                    print("  Warning: Could not determine content bounds, using full SVG")
            
            drawing_width = drawing.width
            drawing_height = drawing.height
            
            # Determine page size
            if page_size == 'auto' and svg_dimensions:
                # Use SVG dimensions with margin
                margin_points = margin * inch
                page_width = drawing_width + 2 * margin_points
                page_height = drawing_height + 2 * margin_points
                page_size_tuple = (page_width, page_height)
                print(f"  Auto page size: {page_width:.1f} x {page_height:.1f} points")
            else:
                page_size_tuple = self.supported_page_sizes.get(page_size, A4)
                print(f"  Page size: {page_size}")
            
            # Calculate scaling if fit_to_page is enabled
            margin_points = margin * inch
            available_width = page_size_tuple[0] - 2 * margin_points
            available_height = page_size_tuple[1] - 2 * margin_points
            
            if fit_to_page and page_size != 'auto':
                scale_x = available_width / drawing_width
                scale_y = available_height / drawing_height
                scale = min(scale_x, scale_y)
                
                # Apply scaling
                drawing.scale(scale, scale)
                scaled_width = drawing_width * scale
                scaled_height = drawing_height * scale
                
                print(f"  Scaling: {scale:.3f}")
                print(f"  Scaled dimensions: {scaled_width:.1f} x {scaled_height:.1f} points")
                
                # Center the drawing on the page
                x_offset = margin_points + (available_width - scaled_width) / 2
                y_offset = margin_points + (available_height - scaled_height) / 2
            else:
                # No scaling, just apply margin
                x_offset = margin_points
                y_offset = margin_points
            
            # Create PDF canvas
            from reportlab.pdfgen import canvas
            from reportlab.graphics import renderPDF
            
            # Create a temporary canvas to get the drawing rendered
            c = canvas.Canvas(pdf_path, pagesize=page_size_tuple)
            
            # Render the drawing to PDF
            renderPDF.draw(drawing, c, x_offset, y_offset)
            
            # Save the PDF
            c.save()
            
            print(f"  Conversion completed successfully!")
            
            # Get file sizes for reporting
            svg_size = os.path.getsize(svg_path)
            pdf_size = os.path.getsize(pdf_path)
            
            print(f"  SVG size: {svg_size:,} bytes ({svg_size/1024:.1f} KB)")
            print(f"  PDF size: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")
            
            return True
            
        except Exception as e:
            print(f"Error converting SVG to PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def batch_convert(self, input_dir: str, output_dir: str, 
                     page_size: str = 'a4', fit_to_page: bool = True, 
                     margin: float = 0.5, crop_to_content: bool = True) -> int:
        """
        Convert all SVG files in a directory to PDF.
        
        Args:
            input_dir: Directory containing SVG files
            output_dir: Directory for output PDF files
            page_size: Page size for PDFs
            fit_to_page: Whether to scale SVG to fit page
            margin: Page margin in inches
            crop_to_content: Whether to crop to content bounds
            
        Returns:
            Number of files successfully converted
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all SVG files
        svg_files = list(input_path.glob("*.svg"))
        
        if not svg_files:
            print(f"No SVG files found in {input_dir}")
            return 0
        
        print(f"Found {len(svg_files)} SVG files to convert")
        
        successful = 0
        total_start_time = time.time()
        
        for i, svg_file in enumerate(svg_files, 1):
            print(f"\n[{i}/{len(svg_files)}] Processing: {svg_file.name}")
            
            # Generate output filename
            pdf_file = output_path / f"{svg_file.stem}.pdf"
            
            start_time = time.time()
            
            if self.convert_svg_to_pdf(str(svg_file), str(pdf_file),
                                     page_size=page_size,
                                     fit_to_page=fit_to_page,
                                     margin=margin,
                                     crop_to_content=crop_to_content):
                successful += 1
                elapsed = time.time() - start_time
                print(f"  Completed in {elapsed:.2f} seconds")
            else:
                print(f"  Failed to convert {svg_file.name}")
        
        total_elapsed = time.time() - total_start_time
        
        print(f"\nBatch conversion completed:")
        print(f"  Successfully converted: {successful}/{len(svg_files)} files")
        print(f"  Total time: {total_elapsed:.2f} seconds")
        print(f"  Average time per file: {total_elapsed/len(svg_files):.2f} seconds")
        
        return successful


def main():
    """Main entry point for the SVG to PDF converter."""
    parser = argparse.ArgumentParser(
        description="Convert SVG files to PDF format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single SVG to PDF with content cropping (default)
  python svg_to_pdf.py input.svg output.pdf
  
  # Convert with A4 page size and fit to page with cropping
  python svg_to_pdf.py input.svg output.pdf --page-size a4 --fit-to-page
  
  # Convert with auto page size (uses actual content dimensions)
  python svg_to_pdf.py input.svg output.pdf --page-size auto
  
  # Convert without content cropping (use full SVG dimensions)
  python svg_to_pdf.py input.svg output.pdf --no-crop
  
  # Batch convert all SVG files in a directory
  python svg_to_pdf.py input_dir/ output_dir/ --batch
  
  # Convert with custom margin
  python svg_to_pdf.py input.svg output.pdf --margin 1.0

Page sizes: a4, letter, legal, auto
Content cropping: Enabled by default, removes whitespace around actual content
        """
    )
    
    parser.add_argument('input', help='Input SVG file or directory')
    parser.add_argument('output', help='Output PDF file or directory')
    
    parser.add_argument('--page-size', 
                       choices=['a4', 'letter', 'legal', 'auto'],
                       default='a4',
                       help='PDF page size (default: a4)')
    
    parser.add_argument('--fit-to-page', 
                       action='store_true',
                       help='Scale SVG to fit page (ignored with --page-size auto)')
    
    parser.add_argument('--margin', 
                       type=float, 
                       default=0.5,
                       help='Page margin in inches (default: 0.5)')
    
    parser.add_argument('--crop-to-content', 
                       action='store_true',
                       default=True,
                       help='Crop PDF to actual content bounds (default: enabled)')
    
    parser.add_argument('--no-crop', 
                       action='store_true',
                       help='Disable content cropping, use full SVG dimensions')
    
    parser.add_argument('--batch', 
                       action='store_true',
                       help='Batch convert all SVG files in input directory')
    
    parser.add_argument('--version', 
                       action='version', 
                       version='SVG to PDF Converter 1.0')
    
    args = parser.parse_args()
    
    # Validate inputs
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input path '{args.input}' does not exist")
        return 1
    
    if args.batch:
        if not input_path.is_dir():
            print("Error: Input must be a directory when using --batch")
            return 1
    else:
        if not input_path.is_file():
            print("Error: Input must be a file when not using --batch")
            return 1
        
        if not input_path.suffix.lower() == '.svg':
            print("Error: Input file must have .svg extension")
            return 1
    
    # Create converter
    converter = SVGToPDFConverter()
    
    # Determine crop setting
    crop_to_content = args.crop_to_content and not args.no_crop
    
    try:
        if args.batch:
            # Batch conversion
            successful = converter.batch_convert(
                args.input,
                args.output,
                page_size=args.page_size,
                fit_to_page=args.fit_to_page,
                margin=args.margin,
                crop_to_content=crop_to_content
            )
            
            if successful == 0:
                return 1
                
        else:
            # Single file conversion
            success = converter.convert_svg_to_pdf(
                args.input,
                args.output,
                page_size=args.page_size,
                fit_to_page=args.fit_to_page,
                margin=args.margin,
                crop_to_content=crop_to_content
            )
            
            if not success:
                return 1
    
    except KeyboardInterrupt:
        print("\nConversion interrupted by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())