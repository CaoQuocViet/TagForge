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

## 📥 Đầu vào

- Thư mục chứa nhiều ảnh `.png`, mỗi ảnh là một icon theo chủ đề.
- Tên file có định dạng: `001-name.png`, `002-anothername.png`, v.v.

---

## 📤 Đầu ra

Một file `metadata.csv` chứa thông tin metadata cho từng ảnh PNG.

### Các cột cần có:

| Cột        | Ý nghĩa |
|------------|--------|
| `filename` | Tên file ảnh, giữ nguyên tên nhưng đổi đuôi thành `.svg` |
| `title`    | Tên rút gọn từ file, bỏ chỉ số đầu và phần `.png` |
| `keywords` | Danh sách **25 tag** liên quan đến hình ảnh, phân cách bằng dấu phẩy |
| `Artist`   | Để trống (`,,` trong CSV) |
| `description` | Mô tả chi tiết nội dung ảnh do AI sinh ra |

---

## 🧠 Quy trình xử lý

1. Đọc từng ảnh `.png` trong thư mục.
2. Sinh mô tả (`description`) cho ảnh bằng AI.
3. Từ mô tả, sinh danh sách **25 từ khóa** (keywords).
4. Tạo dòng metadata tương ứng trong CSV.

---

## 📝 Ví dụ nội dung CSV đầu ra

```csv
filename,title,keywords,Artist,description
001-virus.svg,virus,"virus,petri dish,pandemic,no virus,no plane,no meat,statistics,talking,thermometer,headache,medical mask,cough,vomit,temperature sensor,fever,medicine,hands,no touch,washing hand,rubber gloves,long distance,warning sign,spreader,avoid crowds,quarantine",,"A stylized illustration of a virus with surrounding health and safety icons representing symptoms and pandemic precautions."
002-petri dish.svg,petri dish,"petri dish,pandemic,no virus,no plane,no meat,statistics,talking,thermometer,medical mask,virus,headache,cough,vomit,fever,medicine,temperature sensor,hands,no touch,washing hand,rubber gloves,long distance,warning sign,spreader,avoid crowds,quarantine",,"An icon showing a scientific petri dish with bacteria growth, used to represent microbiology, infection control, or lab testing during pandemics."
