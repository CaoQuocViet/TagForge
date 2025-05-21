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
    temp_dir = output_dir / f"_temp_{zip_name}"
    
    print(f"\nĐang xử lý: {zip_path.name}")
    
    # Xóa thư mục tạm nếu tồn tại từ lần chạy trước bị lỗi
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # Tạo thư mục tạm để giải nén
    temp_dir.mkdir()
    
    try:
        # Giải nén vào thư mục tạm
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            print(f"Số lượng file/thư mục trong {zip_path.name}: {len(file_list)}")
            zip_ref.extractall(temp_dir)
        
        # Kiểm tra xem có thư mục trùng tên không
        temp_contents = list(temp_dir.iterdir())
        if len(temp_contents) == 1 and temp_contents[0].is_dir() and temp_contents[0].name == zip_name:
            # Nếu có thư mục trùng tên, di chuyển nội dung của nó lên một cấp
            duplicate_dir = temp_contents[0]
            
            # Xóa thư mục đích nếu tồn tại
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            
            # Đổi tên trực tiếp từ thư mục con lên thư mục cha
            duplicate_dir.rename(extract_dir)
            temp_dir.rmdir()  # Xóa thư mục tạm rỗng
        else:
            # Nếu không có thư mục trùng tên, di chuyển toàn bộ nội dung
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            temp_dir.rename(extract_dir)
        
        # Đếm số lượng file và thư mục
        total_files = sum(1 for _ in extract_dir.rglob('*') if _.is_file())
        total_dirs = sum(1 for _ in extract_dir.rglob('*') if _.is_dir())
        print(f"Đã giải nén thành công vào {extract_dir}")
        print(f"Tổng số: {total_files} file, {total_dirs} thư mục")
        
    except Exception as e:
        print(f"Lỗi khi giải nén {zip_path.name}: {e}")
        # Dọn dẹp trong trường hợp lỗi
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


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
