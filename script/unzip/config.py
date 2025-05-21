#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# Thư mục gốc của dự án
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Cấu hình đường dẫn
class PathConfig:
    # Thư mục đầu vào mặc định - nơi chứa các file ZIP
    DEFAULT_INPUT_DIR = os.environ.get('CANVA_ZIP_INPUT_DIR', str(PROJECT_ROOT / "sample"))
    
    # Thư mục đầu ra cho SVG only
    DEFAULT_SVG_OUTPUT_DIR = os.environ.get('CANVA_SVG_OUTPUT_DIR', 
                                         lambda: os.path.join(str(PathConfig.DEFAULT_INPUT_DIR), "unziped_svg_only"))()
    
    # Thư mục đầu ra cho ALL files
    DEFAULT_ALL_OUTPUT_DIR = os.environ.get('CANVA_ALL_OUTPUT_DIR', 
                                         lambda: os.path.join(str(PathConfig.DEFAULT_INPUT_DIR), "unziped_all"))()

# Cấu hình thực thi
class ExecutionConfig:
    # Mặc định giữ lại SVG hay giữ tất cả
    DEFAULT_MODE = os.environ.get('CANVA_UNZIP_MODE', "all")  # "svg_only" hoặc "all"
    
    # Có ghi đè thư mục đã tồn tại không
    OVERWRITE_EXISTING = os.environ.get('CANVA_UNZIP_OVERWRITE', "True").lower() in ('true', '1', 'yes')

# In ra thông tin cấu hình khi import module
if __name__ == "__main__":
    print("=== Cấu hình Unzip ===")
    print(f"Thư mục đầu vào: {PathConfig.DEFAULT_INPUT_DIR}")
    print(f"Thư mục đầu ra SVG: {PathConfig.DEFAULT_SVG_OUTPUT_DIR}")
    print(f"Thư mục đầu ra ALL: {PathConfig.DEFAULT_ALL_OUTPUT_DIR}")
    print(f"Chế độ mặc định: {ExecutionConfig.DEFAULT_MODE}")
    print(f"Ghi đè thư mục hiện có: {ExecutionConfig.OVERWRITE_EXISTING}") 