import os

# Get the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Paths for color palette processing
SAMPLE_PALETTES_DIR = os.path.join(BASE_DIR, 'script', 'svg_painter', 'palettes', 'sample')
OUTPUT_DIR = os.path.join(BASE_DIR, 'script', 'svg_painter', 'output')

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Output file path for merged colors
MERGED_COLORS_FILE = os.path.join(OUTPUT_DIR, 'merged_colors.json')
