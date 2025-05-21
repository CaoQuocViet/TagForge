#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from pathlib import Path

# Import cấu hình
try:
    from config import PathConfig, ExecutionConfig
    from unzip_files_all import unzip_all_files
    from unzip_files_svg_only import unzip_files
except ImportError as e:
    print(f"Lỗi: Không thể import module cần thiết: {e}")
    sys.exit(1)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Giải nén file ZIP với các tùy chọn")
    
    parser.add_argument(
        "input_dir", 
        type=str, 
        nargs='?',  # Làm tham số tùy chọn
        default=PathConfig.DEFAULT_INPUT_DIR,
        help=f"Thư mục chứa file ZIP (mặc định: {PathConfig.DEFAULT_INPUT_DIR})"
    )
    
    parser.add_argument(
        "--mode", 
        type=str,
        choices=["all", "svg_only"],
        default=ExecutionConfig.DEFAULT_MODE,
        help=f"Chế độ giải nén: all=giữ nguyên cấu trúc, svg_only=chỉ giữ thư mục svg (mặc định: {ExecutionConfig.DEFAULT_MODE})"
    )
    
    parser.add_argument(
        "--overwrite", 
        action="store_true",
        default=ExecutionConfig.OVERWRITE_EXISTING,
        help="Ghi đè lên thư mục đã tồn tại"
    )
    
    return parser.parse_args()

def main():
    """Entrypoint chính của ứng dụng"""
    # Parse arguments
    args = parse_args()
    
    print("=== Giải Nén File ZIP ===")
    print(f"Thư mục đầu vào: {args.input_dir}")
    print(f"Chế độ giải nén: {args.mode}")
    print(f"Ghi đè thư mục: {args.overwrite}")
    
    # Đặt biến môi trường tạm thời
    # Lưu ý: điều này không thực sự thay đổi biến môi trường hệ thống
    # nhưng tác động đến các lớp cấu hình của chúng ta
    ExecutionConfig.OVERWRITE_EXISTING = args.overwrite
    
    # Chạy chế độ giải nén tương ứng
    if args.mode == "all":
        print("\n=== Chế độ ALL: Giữ nguyên cấu trúc ===")
        success = unzip_all_files(args.input_dir)
    else:  # svg_only
        print("\n=== Chế độ SVG_ONLY: Chỉ giữ thư mục SVG ===")
        success = unzip_files(args.input_dir)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 