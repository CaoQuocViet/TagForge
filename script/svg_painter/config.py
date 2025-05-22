import os

# Get the absolute path of the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Paths for color palette processing
SAMPLE_PALETTES_DIR = os.path.join(BASE_DIR, 'script', 'svg_painter', 'palettes', 'sample')
OUTPUT_DIR = os.path.join(BASE_DIR, 'script', 'svg_painter', 'output')

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Output file path for merged colors
MERGED_COLORS_FILE = os.path.join(OUTPUT_DIR, 'merged_colors.json')

# SVG processing paths
SVG_INPUT_DIR = os.path.join(BASE_DIR, 'sample', 'unziped_all')
SVG_OUTPUT_DIR = os.path.join(BASE_DIR, 'sample', 'unziped_all', 'svg_painter')

# Create SVG output directory
os.makedirs(SVG_OUTPUT_DIR, exist_ok=True)

# Color detection settings
BLACK_COLOR_VARIANTS = [
    '#000000', '#000', 'black', 'rgb(0,0,0)', 'rgb(0, 0, 0)',
    '#010002', '#010101', '#020202'
]
BLACK_RGB_THRESHOLD = 20  # Max RGB value to consider as "near black"
