import json
import os
import sys
from typing import List, Dict

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

from script.svg_painter.config import SAMPLE_PALETTES_DIR, MERGED_COLORS_FILE

def load_palette_file(file_path: str) -> Dict:
    """Load a single palette file and return its contents"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_palette_id_from_filename(filename: str) -> str:
    """Extract palette ID from filename"""
    base_name = os.path.splitext(filename)[0]
    
    # Handle base sample file
    if base_name == 'sample':
        return 'palette_1'
    
    # Handle sample with number in parentheses
    try:
        # Extract text between parentheses
        if '(' in base_name and ')' in base_name:
            number_part = base_name.split('(')[1].split(')')[0].strip()
            # Extract first number from the text
            number = ''.join(c for c in number_part if c.isdigit())
            if number:
                return f'palette_{int(number)}'
    except:
        pass
    
    # If we can't parse the number, use a hash of the filename
    return f'palette_{hash(base_name) % 1000 + 1000}'

def merge_palettes() -> None:
    """Merge all palette files into a single JSON file with IDs"""
    merged_data = {}
    
    # Get all JSON files in the sample directory
    json_files = [f for f in os.listdir(SAMPLE_PALETTES_DIR) if f.endswith('.json')]
    
    # Sort files to ensure consistent ordering
    def get_sort_key(filename):
        try:
            # Extract number for sorting
            base_name = os.path.splitext(filename)[0]
            if '(' in base_name and ')' in base_name:
                number_part = base_name.split('(')[1].split(')')[0].strip()
                number = ''.join(c for c in number_part if c.isdigit())
                if number:
                    return int(number)
        except:
            pass
        return float('inf')  # Put files without numbers at the end
    
    json_files.sort(key=get_sort_key)
    
    # Process each file
    for filename in json_files:
        file_path = os.path.join(SAMPLE_PALETTES_DIR, filename)
        try:
            palette_data = load_palette_file(file_path)
            
            # Generate palette ID from filename
            palette_id = get_palette_id_from_filename(filename)
            
            # Extract colors and add to merged data
            merged_data[palette_id] = {
                'name': palette_data.get('name', palette_id),
                'colors': [color['value'] for color in palette_data['colors']]
            }
            print(f"Processed {filename} -> {palette_id}")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(MERGED_COLORS_FILE), exist_ok=True)
    
    # Save merged data to output file
    with open(MERGED_COLORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSuccessfully merged {len(merged_data)} palettes into {MERGED_COLORS_FILE}")

if __name__ == '__main__':
    merge_palettes()
