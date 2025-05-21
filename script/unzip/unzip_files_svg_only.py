#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import zipfile
import shutil
import sys
from pathlib import Path


def unzip_files(input_dir):
    """
    Giải nén tất cả các file ZIP trong thư mục và chỉ giữ lại thư mục 'svg'.
    Tạo thư mục 'unziped_svg_only' để lưu trữ nội dung đã giải nén.
    
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
    output_dir = input_path / "unziped_svg_only"
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
    
    print("Tất cả các file đã được xử lý thành công!")
    return True


def process_zip_file(zip_path, output_dir):
    """
    Xử lý một file ZIP: giải nén và chỉ giữ lại thư mục svg.
    
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
            zip_ref.extractall(extract_dir)
    except Exception as e:
        print(f"Lỗi khi giải nén {zip_path.name}: {e}")
        return
    
    # Tìm các thư mục svg
    svg_dirs = list(extract_dir.rglob("svg"))
    
    if not svg_dirs:
        print(f"Cảnh báo: Không tìm thấy thư mục 'svg' trong {zip_path.name}")
        return
    
    # Chỉ giữ lại thư mục svg đầu tiên tìm thấy
    svg_dir = svg_dirs[0]
    print(f"Đã tìm thấy thư mục SVG: {svg_dir.relative_to(extract_dir)}")
    
    # Tạo vị trí tạm thời cho thư mục svg
    temp_dir = extract_dir / "_temp_svg"
    temp_dir.mkdir()
    
    # Di chuyển thư mục svg vào vị trí tạm thời
    shutil.move(str(svg_dir), str(temp_dir))
    
    # Xóa tất cả nội dung khác
    for item in extract_dir.iterdir():
        if item != temp_dir:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    
    # Di chuyển svg trở lại thư mục giải nén
    shutil.move(str(temp_dir / "svg"), str(extract_dir))
    temp_dir.rmdir()
    
    print(f"Đã xử lý thành công {zip_path.name}")


def main():
    """Hàm chính để xử lý tham số và chạy chương trình"""
    if len(sys.argv) != 2:
        print("Cách dùng: python unzip_files.py <đường_dẫn_thư_mục>")
        return 1
    
    input_dir = sys.argv[1]
    success = unzip_files(input_dir)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 