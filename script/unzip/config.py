#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Path configuration
class PathConfig:
    # Default input directory - contains ZIP files
    DEFAULT_INPUT_DIR = os.environ.get('CANVA_ZIP_INPUT_DIR', str(PROJECT_ROOT / "sample"))
    
    # Output directory for SVG only
    DEFAULT_SVG_OUTPUT_DIR = os.environ.get(
        'CANVA_SVG_OUTPUT_DIR', 
        os.path.join(os.environ.get('CANVA_ZIP_INPUT_DIR', str(PROJECT_ROOT / "sample")), "unziped_svg_only")
    )
    
    # Output directory for ALL files
    DEFAULT_ALL_OUTPUT_DIR = os.environ.get(
        'CANVA_ALL_OUTPUT_DIR', 
        os.path.join(os.environ.get('CANVA_ZIP_INPUT_DIR', str(PROJECT_ROOT / "sample")), "unziped_all")
    )

# Execution configuration
class ExecutionConfig:
    # Default mode - keep SVG only or keep all
    DEFAULT_MODE = os.environ.get('CANVA_UNZIP_MODE', "all")  # "svg_only" or "all"
    
    # Whether to overwrite existing directories
    OVERWRITE_EXISTING = os.environ.get('CANVA_UNZIP_OVERWRITE', "True").lower() in ('true', '1', 'yes')

# Print configuration information when module is imported
if __name__ == "__main__":
    print("=== Unzip Configuration ===")
    print(f"Input directory: {PathConfig.DEFAULT_INPUT_DIR}")
    print(f"SVG output directory: {PathConfig.DEFAULT_SVG_OUTPUT_DIR}")
    print(f"ALL output directory: {PathConfig.DEFAULT_ALL_OUTPUT_DIR}")
    print(f"Default mode: {ExecutionConfig.DEFAULT_MODE}")
    print(f"Overwrite existing directories: {ExecutionConfig.OVERWRITE_EXISTING}") 