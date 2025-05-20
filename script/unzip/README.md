# Công Cụ Giải Nén SVG

Bộ công cụ giải nén file ZIP với hai chức năng:
1. Chỉ giữ lại thư mục SVG
2. Giải nén toàn bộ nội dung

## Cách Sử Dụng

### 1. Giải nén và chỉ giữ SVG:
```bash
python unzip_files_svg_only.py <đường_dẫn_thư_mục>
```

### 2. Giải nén toàn bộ:
```bash
python unzip_files_all.py <đường_dẫn_thư_mục>
```

Ví dụ:
```bash
python unzip_files_svg_only.py "E:\WORK\canva\sample"
# hoặc
python unzip_files_all.py "E:\WORK\canva\sample"
```

## Đầu Vào
- Thư mục chứa các file `.zip`
- Với `unzip_files_svg_only.py`: Mỗi ZIP phải có thư mục `svg`
- Với `unzip_files_all.py`: Không có yêu cầu đặc biệt

## Đầu Ra
### 1. unzip_files_svg_only.py:
- Tạo thư mục `unziped_svg_only` trong thư mục đầu vào
- Mỗi ZIP có một thư mục con riêng chỉ chứa thư mục SVG
- Các nội dung khác bị xóa

### 2. unzip_files_all.py:
- Tạo thư mục `unziped_all` trong thư mục đầu vào
- Mỗi ZIP có một thư mục con riêng chứa toàn bộ nội dung
- Giữ nguyên cấu trúc thư mục gốc

Cấu trúc thư mục:
```
Đầu vào:
E:\WORK\canva\sample\
    ├── file1.zip
    ├── file2.zip
    └── file3.zip

Đầu ra (unzip_files_svg_only.py):
E:\WORK\canva\sample\
    ├── file1.zip
    ├── file2.zip
    ├── file3.zip
    └── unziped_svg_only\
        ├── file1\
        │   └── svg\
        ├── file2\
        │   └── svg\
        └── file3\
            └── svg\

Đầu ra (unzip_files_all.py):
E:\WORK\canva\sample\
    ├── file1.zip
    ├── file2.zip
    ├── file3.zip
    └── unziped_all\
        ├── file1\
        │   ├── svg\
        │   ├── images\
        │   └── [các thư mục khác]\
        ├── file2\
        │   └── [toàn bộ nội dung]\
        └── file3\
            └── [toàn bộ nội dung]\
```

## Lưu Ý
- Các file trong thư mục đầu ra sẽ bị ghi đè nếu đã tồn tại
- Hiển thị tiến trình và lỗi trong quá trình thực thi
- Script `unzip_files_all.py` sẽ hiển thị số lượng file/thư mục được giải nén 