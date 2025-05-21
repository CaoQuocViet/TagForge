#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import hashlib
from pathlib import Path
from PIL import Image
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("tagging.log")
    ]
)
logger = logging.getLogger("tag_utils")

def setup_cache_dir(cache_dir="data/cache"):
    """Create cache directory if it doesn't exist"""
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def get_cache_path(image_path, prefix="desc_", cache_dir="data/cache"):
    """Create cache file path based on image path hash"""
    image_hash = hashlib.md5(str(image_path).encode()).hexdigest()
    return os.path.join(cache_dir, f"{prefix}{image_hash}.json")

def save_to_cache(data, cache_path):
    """Save data to cache file"""
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving to cache: {e}")
        return False

def load_from_cache(cache_path):
    """Read data from cache file"""
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading from cache: {e}")
        return None

def clean_filename(filename):
    """Create svg filename from png filename"""
    return os.path.splitext(filename)[0] + ".svg"

def extract_title(filename):
    """Create title from filename, removing leading index number and extension"""
    # Remove file extension
    name = os.path.splitext(filename)[0]
    
    # Remove leading index number (if any)
    # Pattern matches: 001-, 01-, 1-, etc.
    clean_name = re.sub(r'^\d+[-_]\s*', '', name)
    
    # Convert hyphens to spaces and normalize
    clean_name = clean_name.replace('-', ' ').replace('_', ' ')
    clean_name = ' '.join(clean_name.split())
    
    return clean_name

def load_image(image_path):
    """Read image file from path"""
    try:
        img = Image.open(image_path).convert('RGB')
        return img
    except Exception as e:
        logger.error(f"Error reading image {image_path}: {e}")
        return None

def find_png_dirs(root_dir):
    """Find all png directories in the directory structure"""
    png_dirs = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.basename(dirpath) == "png" and any(f.endswith('.png') for f in filenames):
            png_dirs.append(dirpath)
    
    return png_dirs 