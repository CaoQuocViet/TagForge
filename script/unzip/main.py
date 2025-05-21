#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from pathlib import Path

# Import configuration
try:
    from config import PathConfig, ExecutionConfig
    from unzip_files_all import unzip_all_files
    from unzip_files_svg_only import unzip_files
except ImportError as e:
    print(f"Error: Cannot import required module: {e}")
    sys.exit(1)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Extract ZIP files with options")
    
    parser.add_argument(
        "input_dir", 
        type=str, 
        nargs='?',  # Make parameter optional
        default=PathConfig.DEFAULT_INPUT_DIR,
        help=f"Directory containing ZIP files (default: {PathConfig.DEFAULT_INPUT_DIR})"
    )
    
    parser.add_argument(
        "--mode", 
        type=str,
        choices=["all", "svg_only"],
        default=ExecutionConfig.DEFAULT_MODE,
        help=f"Extraction mode: all=keep all structure, svg_only=keep only svg directory (default: {ExecutionConfig.DEFAULT_MODE})"
    )
    
    parser.add_argument(
        "--overwrite", 
        action="store_true",
        default=ExecutionConfig.OVERWRITE_EXISTING,
        help="Overwrite existing directories"
    )
    
    return parser.parse_args()

def main():
    """Main entry point of the application"""
    # Parse arguments
    args = parse_args()
    
    print("=== ZIP File Extraction ===")
    print(f"Input directory: {args.input_dir}")
    print(f"Extraction mode: {args.mode}")
    print(f"Overwrite directories: {args.overwrite}")
    
    # Set temporary environment variable
    # Note: this doesn't actually change the system environment variables
    # but affects our configuration classes
    ExecutionConfig.OVERWRITE_EXISTING = args.overwrite
    
    # Run the corresponding extraction mode
    if args.mode == "all":
        print("\n=== ALL Mode: Keep entire structure ===")
        success = unzip_all_files(args.input_dir)
    else:  # svg_only
        print("\n=== SVG_ONLY Mode: Keep only SVG directory ===")
        success = unzip_files(args.input_dir)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 