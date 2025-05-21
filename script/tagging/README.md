# 🏷️ Hệ Thống Sinh Tag Tự Động

Hệ thống tự động sinh metadata cho bộ icon sử dụng CLIP Interrogator.

## 📁 Cấu Trúc Thư Mục

```
script/tagging/
├── data/               # Thư mục chứa dữ liệu và cache
│   ├── cache/         # Cache kết quả AI để tránh xử lý lại
│   └── templates/     # Mẫu prompt và cấu hình
│
├── models/            # Các model AI và xử lý
│   ├── clip_model.py    # Wrapper cho CLIP Interrogator
│   ├── tag_generator.py # Sinh tags từ mô tả
│   └── utils.py         # Các hàm tiện ích
│
├── pipeline/          # Quy trình xử lý chính
│   ├── processor.py     # Xử lý từng ảnh riêng lẻ
│   ├── batch.py        # Xử lý hàng loạt
│   └── export.py       # Xuất kết quả ra CSV
│
└── runserver.py      # Entry point chính của ứng dụng
```

## 🔄 Luồng Xử Lý

1. **Processor (`pipeline/processor.py`)**
   - Xử lý từng file PNG riêng lẻ
   - Gọi CLIP Interrogator để sinh mô tả
   - Chuyển đổi mô tả thành tags
   - Cache kết quả để tái sử dụng

2. **Batch Processing (`pipeline/batch.py`)**
   - Quét thư mục đệ quy tìm các thư mục PNG
   - Quản lý hàng đợi xử lý
   - Theo dõi tiến trình
   - Xử lý song song nếu có thể

3. **Export (`pipeline/export.py`)**
   - Tạo cấu trúc thư mục output
   - Sinh file metadata.csv
   - Copy thư mục PNG/SVG nếu cần

4. **Model AI (`models/`)**
   - `clip_model.py`: Wrapper cho CLIP Interrogator
   - `tag_generator.py`: Sinh 25 tag từ mô tả
   - `utils.py`: Các hàm hỗ trợ

## 🎯 Đặc Điểm Chính

- **Cache Thông Minh**: Lưu kết quả AI để tránh xử lý lại
- **Xử Lý Song Song**: Tận dụng GPU hiệu quả
- **Theo Dõi Tiến Trình**: Hiển thị % hoàn thành
- **Kiểm Tra Lỗi**: Báo cáo và ghi log các lỗi

## 📤 Định Dạng Output

### File metadata.csv
```csv
filename,title,keywords,Artist,description
001-virus.svg,virus,"tag1,tag2,...,tag25",,"Mô tả chi tiết..."
```

- `filename`: Tên file .svg
- `title`: Tên không có số và đuôi file
- `keywords`: 25 tag phân cách bằng dấu phẩy
- `Artist`: Để trống
- `description`: Mô tả chi tiết từ AI

## 🚀 Sử Dụng

```bash
python runserver.py <input_dir> [--output_dir] [--batch_size] [--gpu]
```

### Tham số:
- `input_dir`: Thư mục gốc chứa các thư mục icon
- `--output_dir`: Thư mục đầu ra (mặc định: E:/WORK/canva/output)
- `--batch_size`: Số ảnh xử lý mỗi lần (mặc định: 32)
- `--gpu`: Sử dụng GPU nếu có (mặc định: True)

## 🔧 Yêu Cầu Hệ Thống

- Python 3.10
- CUDA compatible GPU (khuyến nghị)
- ryzen 9 5900HX laptop
- RTX 3080 16GB laptop
- 32GB RAM
- Các thư viện:
  - clip-interrogator
  - pandas
  - Pillow
  - torch 