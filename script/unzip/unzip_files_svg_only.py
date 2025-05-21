#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import zipfile
import shutil
import sys
from pathlib import Path

# Import configuration
try:
    from config import PathConfig, ExecutionConfig
except ImportError:
    print("Error: Could not import configuration file. Ensure config.py exists.")
    sys.exit(1)

def unzip_files(input_dir=None):
    """
    Extract all ZIP files in a directory and keep only the 'svg' folders.
    Creates an 'unziped_svg_only' directory to store the extracted content.
    
    Args:
        input_dir (str): Path to directory containing ZIP files
    """
    # Use default path if not provided
    if input_dir is None:
        input_dir = PathConfig.DEFAULT_INPUT_DIR
    
    # Convert to absolute path
    input_path = Path(input_dir).resolve()
    
    # Check if directory exists
    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a valid directory")
        return False
    
    # Create output directory
    output_dir = Path(PathConfig.DEFAULT_SVG_OUTPUT_DIR) if input_dir == PathConfig.DEFAULT_INPUT_DIR else input_path / "unziped_svg_only"
    output_dir.mkdir(exist_ok=True)
    
    print(f"Input directory: {input_path}")
    print(f"Output directory: {output_dir}")
    
    # Find all zip files
    zip_files = list(input_path.glob("*.zip"))
    
    if not zip_files:
        print(f"No ZIP files found in '{input_dir}'")
        return False
    
    print(f"Found {len(zip_files)} ZIP files to process")
    
    # Process each zip file
    for zip_path in zip_files:
        process_zip_file(zip_path, output_dir)
    
    print("All files processed successfully!")
    return True


def process_zip_file(zip_path, output_dir):
    """
    Process a ZIP file: extract and keep only the svg directory.
    
    Args:
        zip_path (Path): Path to the ZIP file
        output_dir (Path): Directory to store the extraction results
    """
    zip_name = zip_path.stem
    extract_dir = output_dir / zip_name
    
    print(f"\nProcessing: {zip_path.name}")
    
    # Create directory for this zip file
    if extract_dir.exists():
        if ExecutionConfig.OVERWRITE_EXISTING:
            shutil.rmtree(extract_dir)
        else:
            print(f"Directory {extract_dir} already exists and overwriting is not allowed")
            return
    extract_dir.mkdir(exist_ok=True)
    
    # Extract zip file
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except Exception as e:
        print(f"Error extracting {zip_path.name}: {e}")
        return
    
    # Find svg directories
    svg_dirs = list(extract_dir.rglob("svg"))
    
    if not svg_dirs:
        print(f"Warning: No 'svg' directory found in {zip_path.name}")
        return
    
    # Keep only the first svg directory found
    svg_dir = svg_dirs[0]
    print(f"Found SVG directory: {svg_dir.relative_to(extract_dir)}")
    
    # Create temporary location for svg directory
    temp_dir = extract_dir / "_temp_svg"
    temp_dir.mkdir()
    
    # Move svg directory to temporary location
    shutil.move(str(svg_dir), str(temp_dir))
    
    # Delete all other content
    for item in extract_dir.iterdir():
        if item != temp_dir:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    
    # Move svg back to extraction directory
    shutil.move(str(temp_dir / "svg"), str(extract_dir))
    temp_dir.rmdir()
    
    print(f"Successfully processed {zip_path.name}")


def main():
    """Main function to handle parameters and run the program"""
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = None  # Use default value
    
    success = unzip_files(input_dir)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 