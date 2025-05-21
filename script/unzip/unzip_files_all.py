#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import zipfile
import shutil
import sys
from pathlib import Path


def unzip_all_files(input_dir):
    """
    Giải nén toàn bộ nội dung của tất cả các file ZIP trong thư mục.
    Tạo thư mục 'unziped_all' để lưu trữ nội dung đã giải nén.
    
    Tham số:
        input_dir (str): Đường dẫn đến thư mục chứa các file ZIP
    """
    # Chuyển đổi sang đường dẫn tuyệt đối
    input_path = Path(input_dir).resolve()
    
    # Kiểm tra thư mục có tồn tại không
    if not input_path.is_dir():
        print(f"Lỗi: '{input_dir}' không phải là thư mục hợp lệ")
        return False
    
    # Tạo thư mục đầu ra
    output_dir = input_path / "unziped_all"
    output_dir.mkdir(exist_ok=True)
    
    print(f"Thư mục đầu vào: {input_path}")
    print(f"Thư mục đầu ra: {output_dir}")
    
    # Tìm tất cả các file zip
    zip_files = list(input_path.glob("*.zip"))
    
    if not zip_files:
        print(f"Không tìm thấy file ZIP nào trong '{input_dir}'")
        return False
    
    print(f"Tìm thấy {len(zip_files)} file ZIP cần xử lý")
    
    # Xử lý từng file zip
    for zip_path in zip_files:
        process_zip_file(zip_path, output_dir)
    
    print("Tất cả các file đã được giải nén thành công!")
    return True


def process_zip_file(zip_path, output_dir):
    """
    Xử lý một file ZIP: giải nén toàn bộ nội dung.
    
    Tham số:
        zip_path (Path): Đường dẫn đến file ZIP
        output_dir (Path): Thư mục lưu kết quả giải nén
    """
    zip_name = zip_path.stem
    extract_dir = output_dir / zip_name
    
    print(f"\nĐang xử lý: {zip_path.name}")
    
    # Tạo thư mục cho file zip này
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir()
    
    # Giải nén file zip
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Hiển thị danh sách các file sẽ được giải nén
            file_list = zip_ref.namelist()
            print(f"Số lượng file/thư mục trong {zip_path.name}: {len(file_list)}")
            
            # Giải nén toàn bộ
            zip_ref.extractall(extract_dir)
            
            print(f"Đã giải nén thành công {zip_path.name} vào {extract_dir}")
    except Exception as e:
        print(f"Lỗi khi giải nén {zip_path.name}: {e}")
        return

    # Đếm số lượng file và thư mục đã giải nén
    total_files = sum(1 for _ in extract_dir.rglob('*') if _.is_file())
    total_dirs = sum(1 for _ in extract_dir.rglob('*') if _.is_dir())
    print(f"Tổng số: {total_files} file, {total_dirs} thư mục")


def main():
    """Hàm chính để xử lý tham số và chạy chương trình"""
    if len(sys.argv) != 2:
        print("Cách dùng: python unzip_files_all.py <đường_dẫn_thư_mục>")
        return 1
    
    input_dir = sys.argv[1]
    success = unzip_all_files(input_dir)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
