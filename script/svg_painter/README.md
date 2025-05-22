# SVG Painter

Module tự động tô màu cho các file SVG từ bộ màu được định nghĩa trước.
* Màu lấy từ https://loading.io/asset

## Tính năng chính

- Tự động tô màu cho các file SVG từ bộ màu được chọn
- Mỗi file SVG chỉ sử dụng tối đa 2 màu từ một bộ màu
- Tự động phát hiện và thay thế các màu đen/gần đen
- Duy trì cấu trúc thư mục gốc khi xuất file
- Hỗ trợ nhiều định dạng màu (HEX, RGB, RGBA)
- Cache thông minh và xử lý song song

## Cấu trúc thư mục

```
script/svg_painter/
├── colorizer.py     # Module chính xử lý tô màu SVG
├── config.py        # Cấu hình đường dẫn và tham số
├── palettes/        # Chứa các bộ màu mẫu
│   ├── sample/      # Các file JSON chứa bộ màu
│   └── merge_color.py   # Script gộp các bộ màu
└── output/          # Thư mục chứa kết quả xử lý
```

## Cài đặt

Không cần cài đặt thêm thư viện. Module sử dụng các thư viện có sẵn của Python:
- xml.etree.ElementTree: Xử lý file SVG
- json: Đọc/ghi file JSON
- os, shutil: Thao tác với file/thư mục

## Cấu hình

File `config.py` chứa các thông số cấu hình:

```python
SVG_INPUT_DIR      # Thư mục chứa file SVG đầu vào
SVG_OUTPUT_DIR     # Thư mục xuất kết quả
MERGED_COLORS_FILE # File JSON chứa bộ màu đã gộp
BLACK_RGB_THRESHOLD # Ngưỡng xác định màu gần đen (mặc định: 20)
```

## Sử dụng

1. Chuẩn bị bộ màu:
   - Đặt các file JSON chứa bộ màu vào thư mục `palettes/sample/`
   - Chạy script gộp màu:
   ```bash
   python -m script.svg_painter.palettes.merge_color
   ```

2. Xử lý tô màu SVG:
   ```bash
   python -m script.svg_painter.colorizer
   ```

## Quy tắc tô màu

1. **Giới hạn màu**: 
   - Mỗi file SVG chỉ sử dụng 1-2 màu từ một bộ màu
   - Số lượng màu được chọn ngẫu nhiên (1 hoặc 2)
   - Các màu được chọn ngẫu nhiên từ bộ màu

2. **Phát hiện màu đen**:
   - Tự động phát hiện các phần tử có màu đen hoặc gần đen
   - Hỗ trợ nhiều định dạng màu: #000000, rgb(0,0,0), black,...
   - Ngưỡng màu gần đen có thể điều chỉnh qua `BLACK_RGB_THRESHOLD`

3. **Áp dụng màu**:
   - Màu được áp dụng cho cả thuộc tính fill và stroke
   - Xử lý cả màu trong thuộc tính style
   - Duy trì tính nhất quán khi áp dụng màu trong cùng một file

## Định dạng bộ màu

File JSON chứa bộ màu cần theo format:

```json
{
  "name": "Tên bộ màu",
  "colors": [
    {"value": "#HEXCOLOR1"},
    {"value": "#HEXCOLOR2"},
    ...
  ]
}
```

## Xử lý lỗi

- Tự động bỏ qua các file SVG không đọc được
- Giữ nguyên cấu trúc thư mục gốc
- Log đầy đủ thông tin xử lý và lỗi
- Xử lý các trường hợp đặc biệt (không có màu, màu không hợp lệ,...)

## Lưu ý

- Chọn các set màu cho chuẩn, xóa các màu lem nhem ra khỏi set dùm cái, trước khi merge
- Đảm bảo quyền ghi vào thư mục đầu ra
- Backup dữ liệu trước khi xử lý hàng loạt
- Kiểm tra kết quả sau khi xử lý
- Điều chỉnh ngưỡng màu đen nếu cần thiết 