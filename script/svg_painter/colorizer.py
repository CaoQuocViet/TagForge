import os
import json
import random
import re
from typing import List, Dict, Tuple
from xml.etree import ElementTree as ET
import colorsys
import sys

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from script.svg_painter.config import (
    SVG_INPUT_DIR, SVG_OUTPUT_DIR, MERGED_COLORS_FILE,
    BLACK_COLOR_VARIANTS, BLACK_RGB_THRESHOLD
)

def load_color_palettes() -> Dict:
    """Load color palettes from the merged JSON file"""
    with open(MERGED_COLORS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c + c for c in hex_color)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def parse_rgb_string(rgb_str: str) -> Tuple[int, int, int]:
    """Parse RGB string to RGB tuple"""
    # Extract numbers from rgb(x,y,z) or rgba(x,y,z,a)
    numbers = re.findall(r'\d+', rgb_str)
    return tuple(int(n) for n in numbers[:3])

def is_black_or_near_black(color: str) -> bool:
    """Check if a color is black or near black"""
    if color in BLACK_COLOR_VARIANTS:
        return True
    
    try:
        # Handle hex colors
        if color.startswith('#'):
            r, g, b = hex_to_rgb(color)
        # Handle rgb/rgba colors
        elif color.startswith('rgb'):
            r, g, b = parse_rgb_string(color)
        else:
            return False
        
        # Check if all RGB values are below threshold
        return all(c <= BLACK_RGB_THRESHOLD for c in (r, g, b))
    except:
        return False

def find_svg_files(root_dir: str) -> List[str]:
    """Recursively find all SVG files in directory"""
    svg_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.svg'):
                svg_files.append(os.path.join(dirpath, filename))
    return svg_files

def get_relative_output_path(input_path: str) -> str:
    """Get the relative output path maintaining directory structure"""
    rel_path = os.path.relpath(input_path, SVG_INPUT_DIR)
    return os.path.join(SVG_OUTPUT_DIR, rel_path)

def process_svg_file(svg_path: str, color_palettes: Dict) -> None:
    """Process a single SVG file"""
    # Parse SVG file
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error parsing SVG file: {svg_path}")
        return

    # Choose a random color palette
    palette_id = random.choice(list(color_palettes.keys()))
    palette = color_palettes[palette_id]['colors']
    color_index = 0
    
    # Register SVG namespace
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    for prefix, uri in ns.items():
        ET.register_namespace(prefix, uri)

    def process_element(element):
        nonlocal color_index
        
        # List of attributes to check for colors
        color_attrs = ['fill', 'stroke']
        
        for attr in color_attrs:
            if attr in element.attrib:
                color = element.attrib[attr]
                if color and is_black_or_near_black(color):
                    # Replace black color with next color from palette
                    element.attrib[attr] = palette[color_index % len(palette)]
                    color_index += 1
        
        # Process style attribute if present
        if 'style' in element.attrib:
            style = element.attrib['style']
            for attr in color_attrs:
                # Find color values in style attribute
                pattern = f"{attr}:([^;]+)"
                matches = re.finditer(pattern, style)
                for match in matches:
                    color = match.group(1)
                    if is_black_or_near_black(color):
                        new_color = palette[color_index % len(palette)]
                        style = style.replace(f"{attr}:{color}", f"{attr}:{new_color}")
                        color_index += 1
            element.attrib['style'] = style
        
        # Process child elements
        for child in element:
            process_element(child)

    # Process the SVG
    process_element(root)
    
    # Create output directory if needed
    output_path = get_relative_output_path(svg_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the modified SVG
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Processed: {svg_path} -> {output_path}")

def main():
    """Main function to process all SVG files"""
    # Load color palettes
    color_palettes = load_color_palettes()
    
    # Find all SVG files
    svg_files = find_svg_files(SVG_INPUT_DIR)
    print(f"Found {len(svg_files)} SVG files to process")
    
    # Process each SVG file
    for svg_file in svg_files:
        try:
            process_svg_file(svg_file, color_palettes)
        except Exception as e:
            print(f"Error processing {svg_file}: {str(e)}")

if __name__ == '__main__':
    main()
