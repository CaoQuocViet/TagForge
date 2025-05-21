# TagForge
Auto-generate tags and descriptions for icon sets from SVG/PNG using vision-language models. Export metadata in CSV format

# 📄 Tự Động Sinh Metadata Cho Icon PNG

## 🎯 Mục đích

Tự động tạo file `metadata.csv` từ một thư mục chứa nhiều icon định dạng `.png`, phục vụ cho việc đăng bán trên nền tảng như Canva.

---

## ⚙️ Công nghệ & Yêu cầu hệ thống

- **Mô hình AI sử dụng**: CLIP Interrogator (kết hợp giữa BLIP + CLIP).
- **Ngôn ngữ**: Python 3.8+
- **Thư viện**:
  - `clip-interrogator`
  - `pandas`
  - `Pillow`
- **Hệ thống đề xuất**:
  - GPU: NVIDIA RTX 3080 (Laptop) hoặc tương đương
  - RAM: 32GB
  - CPU: AMD Ryzen 5900HX hoặc tương đương

---

## 🗂️ Cấu trúc thư mục đầu vào

- **Thư mục gốc** được truyền vào (ví dụ: `E:\WORK\canva\sample\unziped_all`) chứa **nhiều thư mục chủ đề** (ví dụ: `110790-speeches`, `110791-sweet-home`, ...).
- Mỗi thư mục chủ đề lại chứa nhiều thư mục con như `png/`, `svg/`, `eps/`, `license/`...

👉 **Chỉ làm việc với ảnh trong thư mục con `png/`**.

### Ví dụ cấu trúc:

E:\WORK\canva\sample\unziped_all
│
├── 110790-speeches
│ ├── png
│ │ ├── 001-mic.png
│ │ ├── 002-speech-bubble.png
│ ├── svg
│ ├── eps
│ └── ...
├── 110791-sweet-home
│ └── png
│ ├── 001-house.png
│ ├── 002-door.png

---

## 📤 Đầu ra

- Thư mục output sẽ nằm tại: `E:\WORK\canva\output\`
- Với mỗi thư mục chủ đề đầu vào, tạo một thư mục tương ứng bên trong output.
- Trong mỗi thư mục output:
  - **Giữ nguyên thư mục `png/` và `svg/` từ input (nếu cần copy lại)**
  - Tạo file `metadata.csv` chứa mô tả cho toàn bộ ảnh trong `png/`.

### Ví dụ:

E:\WORK\canva\output
├── 110790-speeches
│ ├── png
│ ├── svg
│ └── metadata.csv

### Các cột cần có của file csv:

| Cột        | Ý nghĩa |
|------------|--------|
| `filename` | Tên file ảnh, giữ nguyên tên nhưng đổi đuôi thành `.svg` |
| `title`    | Tên rút gọn từ file, bỏ chỉ số đầu và phần `.png` |
| `keywords` | Danh sách **25 tag** liên quan đến hình ảnh, phân cách bằng dấu phẩy |
| `Artist`   | Để trống (`,,` trong CSV) |
| `description` | Mô tả chi tiết nội dung ảnh do AI sinh ra |

---

## ⚙️ Công nghệ sử dụng

- **Mô hình AI chính**: CLIP Interrogator (sử dụng BLIP + CLIP)
- **Ngôn ngữ**: Python >= 3.8
- **Thư viện chính**:
  - `clip-interrogator`
  - `Pillow`
  - `pandas`
- **Chạy cục bộ** (offline), tận dụng GPU nếu có.

---

## 🧠 Quy trình xử lý

1. **Duyệt đệ quy** tất cả thư mục con trong thư mục gốc.
2. Với mỗi thư mục có `png/`:
   - Đọc toàn bộ file `.png`.
   - Với mỗi ảnh:
     - Sinh mô tả chi tiết bằng AI (`description`).
     - Từ mô tả → sinh 25 tag liên quan (`keywords`).
     - Lấy tên file, **chuyển đuôi thành `.svg`** → `filename`
     - Tên rút gọn không số thứ tự → `title`
3. Ghi ra file `metadata.csv` với cấu trúc chuẩn.

---

## 📝 Ví dụ nội dung CSV đầu ra

```csv
filename,title,keywords,Artist,description
001-virus.svg,virus,"virus,petri dish,pandemic,no virus,no plane,no meat,statistics,talking,thermometer,headache,medical mask,cough,vomit,temperature sensor,fever,medicine,hands,no touch,washing hand,rubber gloves,long distance,warning sign,spreader,avoid crowds,quarantine",,"A stylized illustration of a virus with surrounding health and safety icons representing symptoms and pandemic precautions."
002-petri dish.svg,petri dish,"petri dish,pandemic,no virus,no plane,no meat,statistics,talking,thermometer,medical mask,virus,headache,cough,vomit,fever,medicine,temperature sensor,hands,no touch,washing hand,rubber gloves,long distance,warning sign,spreader,avoid crowds,quarantine",,"An icon showing a scientific petri dish with bacteria growth, used to represent microbiology, infection control, or lab testing during pandemics."
