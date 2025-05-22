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

def unzip_all_files(input_dir=None):
    """
    Extract all contents of ZIP files in a directory.
    Creates an 'unziped_all' directory to store the extracted content.
    
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
    output_dir = Path(PathConfig.DEFAULT_ALL_OUTPUT_DIR) if input_dir == PathConfig.DEFAULT_INPUT_DIR else input_path / "unziped_all"
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
    
    print("All files have been extracted successfully!")
    return True


def process_zip_file(zip_path, output_dir):
    """
    Process a ZIP file: extract all contents.
    
    Args:
        zip_path (Path): Path to the ZIP file
        output_dir (Path): Directory to store the extraction results
    """
    zip_name = zip_path.stem
    extract_dir = output_dir / zip_name
    temp_dir = output_dir / f"_temp_{zip_name}"
    
    print(f"\nProcessing: {zip_path.name}")
    
    # Remove temporary directory if it exists from a previous failed run
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # Check if destination directory already exists
    if extract_dir.exists() and not ExecutionConfig.OVERWRITE_EXISTING:
        print(f"Directory {extract_dir} already exists and overwriting is not allowed")
        return
    
    # Create temporary directory for extraction
    temp_dir.mkdir()
    
    try:
        # Extract to temporary directory
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            print(f"Number of files/directories in {zip_path.name}: {len(file_list)}")
            zip_ref.extractall(temp_dir)
        
        # Check for duplicate named directory
        temp_contents = list(temp_dir.iterdir())
        if len(temp_contents) == 1 and temp_contents[0].is_dir() and temp_contents[0].name == zip_name:
            # If there's a directory with the same name, move its contents up one level
            duplicate_dir = temp_contents[0]
            
            # Remove destination directory if it exists
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            
            # Use shutil.move instead of rename
            shutil.move(str(duplicate_dir), str(extract_dir))
            temp_dir.rmdir()  # Remove empty temp directory
        else:
            # If no duplicate directory, move all contents
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            # Use shutil.move instead of rename
            shutil.move(str(temp_dir), str(extract_dir))
        
        # Count files and directories
        total_files = sum(1 for _ in extract_dir.rglob('*') if _.is_file())
        total_dirs = sum(1 for _ in extract_dir.rglob('*') if _.is_dir())
        print(f"Successfully extracted to {extract_dir}")
        print(f"Total: {total_files} files, {total_dirs} directories")
        
    except Exception as e:
        print(f"Error extracting {zip_path.name}: {e}")
        # Clean up in case of error
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        if extract_dir.exists() and str(e).find("Access is denied") >= 0:
            # If access denied, try to clean up the target directory
            try:
                shutil.rmtree(extract_dir)
            except:
                pass


def main():
    """Main function to handle parameters and run the program"""
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = None  # Use default value
    
    success = unzip_all_files(input_dir)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
