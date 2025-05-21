#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import hashlib
from pathlib import Path
from PIL import Image
import logging

# Thiết lập logging
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
    """Tạo thư mục cache nếu chưa tồn tại"""
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def get_cache_path(image_path, prefix="desc_", cache_dir="data/cache"):
    """Tạo đường dẫn file cache dựa trên hash của đường dẫn ảnh"""
    image_hash = hashlib.md5(str(image_path).encode()).hexdigest()
    return os.path.join(cache_dir, f"{prefix}{image_hash}.json")

def save_to_cache(data, cache_path):
    """Lưu dữ liệu vào file cache"""
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Lỗi khi lưu cache: {e}")
        return False

def load_from_cache(cache_path):
    """Đọc dữ liệu từ file cache"""
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Lỗi khi đọc cache: {e}")
        return None

def clean_filename(filename):
    """Tạo tên file svg từ tên file png"""
    return os.path.splitext(filename)[0] + ".svg"

def extract_title(filename):
    """Tạo title từ filename, loại bỏ số thứ tự đầu và phần mở rộng"""
    # Loại bỏ phần mở rộng file
    name = os.path.splitext(filename)[0]
    
    # Loại bỏ số thứ tự đầu file (nếu có)
    # Pattern tìm dạng: 001-, 01-, 1-, etc.
    clean_name = re.sub(r'^\d+[-_]\s*', '', name)
    
    # Chuyển các dấu gạch ngang thành khoảng trắng và chuẩn hóa
    clean_name = clean_name.replace('-', ' ').replace('_', ' ')
    clean_name = ' '.join(clean_name.split())
    
    return clean_name

def load_image(image_path):
    """Đọc file ảnh từ đường dẫn"""
    try:
        img = Image.open(image_path).convert('RGB')
        return img
    except Exception as e:
        logger.error(f"Lỗi khi đọc ảnh {image_path}: {e}")
        return None

def find_png_dirs(root_dir):
    """Tìm tất cả thư mục png trong cấu trúc thư mục"""
    png_dirs = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.basename(dirpath) == "png" and any(f.endswith('.png') for f in filenames):
            png_dirs.append(dirpath)
    
    return png_dirs 