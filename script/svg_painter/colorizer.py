import os
import json
import random
import re
import shutil
from typing import List, Dict, Tuple
from xml.etree import ElementTree as ET
import colorsys
import sys
from collections import deque

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from script.svg_painter.config import (
    SVG_INPUT_DIR, SVG_OUTPUT_DIR, MERGED_COLORS_FILE,
    BLACK_COLOR_VARIANTS, BLACK_RGB_THRESHOLD, DEFAULT_BLACK_ATTRIBUTES
)

def load_color_palettes() -> Dict:
    """Load color palettes from the merged JSON file"""
    with open(MERGED_COLORS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    if not hex_color:
        return (0, 0, 0)
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c + c for c in hex_color)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def parse_rgb_string(rgb_str: str) -> Tuple[int, int, int]:
    """Parse RGB string to RGB tuple"""
    if not rgb_str:
        return (0, 0, 0)
    # Extract numbers from rgb(x,y,z) or rgba(x,y,z,a)
    numbers = re.findall(r'\d+', rgb_str)
    return tuple(int(n) for n in numbers[:3])

def is_black_or_near_black(color: str) -> bool:
    """Check if a color is black or near black"""
    if color in BLACK_COLOR_VARIANTS:
        return True
    
    try:
        # Handle hex colors
        if color and color.startswith('#'):
            r, g, b = hex_to_rgb(color)
        # Handle rgb/rgba colors
        elif color and color.startswith('rgb'):
            r, g, b = parse_rgb_string(color)
        else:
            # If no color specified and element is in DEFAULT_BLACK_ATTRIBUTES, consider it black
            return True
        
        # Check if all RGB values are below threshold
        return all(c <= BLACK_RGB_THRESHOLD for c in (r, g, b))
    except:
        # If there's any error parsing the color, consider it as default black
        return True

def find_svg_files(root_dir: str) -> List[str]:
    """Recursively find all SVG files in directory"""
    svg_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        if 'svg' in os.path.basename(dirpath).lower():
            for filename in filenames:
                if filename.lower().endswith('.svg'):
                    svg_files.append(os.path.join(dirpath, filename))
    return svg_files

def get_relative_output_path(input_path: str) -> str:
    """Get the relative output path maintaining directory structure"""
    # Get the path relative to the input directory
    rel_path = os.path.relpath(input_path, SVG_INPUT_DIR)
    
    # Replace the path to avoid nested svg_painter directory
    path_parts = rel_path.split(os.sep)
    if 'svg_painter' in path_parts:
        # Remove svg_painter from path
        path_parts.remove('svg_painter')
    
    # Join the path parts back together
    rel_path = os.sep.join(path_parts)
    
    # Return the final path in the output directory
    return os.path.join(SVG_OUTPUT_DIR, rel_path)

def copy_non_svg_dirs(src_dir: str, dest_dir: str):
    """Copy non-svg directories to output location"""
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        # Skip if it's the output directory itself
        if os.path.exists(dest_dir) and os.path.samefile(src_path, dest_dir):
            continue
            
        # Skip if it's a svg_painter directory
        if item == 'svg_painter':
            continue
            
        if os.path.isdir(src_path):
            if 'svg' not in item.lower():
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(src_path, dest_path)
                print(f"Copied directory: {item}")
            else:
                # For svg directories, we'll handle them in process_svg_file
                continue

class ColorPaletteManager:
    def __init__(self, color_palettes: Dict):
        self.all_palettes = color_palettes
        self.available_palette_ids = list(color_palettes.keys())
        random.shuffle(self.available_palette_ids)  # Shuffle initially
        self.current_index = 0
    
    def get_next_palette(self) -> Tuple[str, List[str]]:
        """Get next unused palette and select 1-2 random colors from it"""
        if self.current_index >= len(self.available_palette_ids):
            random.shuffle(self.available_palette_ids)
            self.current_index = 0
        
        palette_id = self.available_palette_ids[self.current_index]
        self.current_index += 1
        
        # Get all colors from the palette
        all_colors = self.all_palettes[palette_id]['colors'].copy()
        
        # Randomly decide to use 1 or 2 colors
        num_colors = random.randint(1, 2)
        
        # Randomly select colors
        random.shuffle(all_colors)
        selected_colors = all_colors[:num_colors]
        
        return palette_id, selected_colors

def process_svg_file(svg_path: str, palette_manager: ColorPaletteManager) -> None:
    """Process a single SVG file"""
    # Parse SVG file
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error parsing SVG file: {svg_path}")
        return

    # Get next unused palette with 1-2 colors
    palette_id, palette = palette_manager.get_next_palette()
    color_index = 0
    
    # Register SVG namespace
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    for prefix, uri in ns.items():
        ET.register_namespace(prefix, uri)

    def process_element(element):
        nonlocal color_index
        
        # Check if element is a default black element
        is_default_black = element.tag.split('}')[-1] in DEFAULT_BLACK_ATTRIBUTES
        
        # List of attributes to check for colors
        color_attrs = ['fill', 'stroke']
        has_color = False
        
        # Check if element has any color attributes
        for attr in color_attrs:
            if attr in element.attrib:
                has_color = True
                color = element.attrib[attr]
                if is_black_or_near_black(color):
                    # Replace black color with next color from limited palette
                    element.attrib[attr] = palette[color_index % len(palette)]
                    color_index = (color_index + 1) % len(palette)  # Cycle through available colors
        
        # If element is a default black element and has no color attributes, add fill color
        if is_default_black and not has_color:
            element.attrib['fill'] = palette[color_index % len(palette)]
            color_index = (color_index + 1) % len(palette)  # Cycle through available colors
        
        # Process style attribute if present
        if 'style' in element.attrib:
            style = element.attrib['style']
            style_has_color = False
            
            for attr in color_attrs:
                # Find color values in style attribute
                pattern = f"{attr}:([^;]+)"
                matches = re.finditer(pattern, style)
                for match in matches:
                    style_has_color = True
                    color = match.group(1)
                    if is_black_or_near_black(color):
                        new_color = palette[color_index % len(palette)]
                        style = style.replace(f"{attr}:{color}", f"{attr}:{new_color}")
                        color_index = (color_index + 1) % len(palette)  # Cycle through available colors
            
            # If no color in style and element is default black, add fill color
            if is_default_black and not style_has_color and not has_color:
                style += f";fill:{palette[color_index % len(palette)]}"
                color_index = (color_index + 1) % len(palette)  # Cycle through available colors
                
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
    print(f"Processed: {svg_path} -> {output_path} (using palette {palette_id} with {len(palette)} colors)")

def main():
    """Main function to process all SVG files"""
    # Load color palettes
    color_palettes = load_color_palettes()
    palette_manager = ColorPaletteManager(color_palettes)
    
    # Copy non-svg directories first
    copy_non_svg_dirs(SVG_INPUT_DIR, SVG_OUTPUT_DIR)
    
    # Find all SVG files
    svg_files = find_svg_files(SVG_INPUT_DIR)
    print(f"Found {len(svg_files)} SVG files to process")
    
    # Process each SVG file
    for svg_file in svg_files:
        try:
            process_svg_file(svg_file, palette_manager)
        except Exception as e:
            print(f"Error processing {svg_file}: {str(e)}")

if __name__ == '__main__':
    main()
