# Virtual Environment (venv) Activation

Tạo venv (dùng chung):
python -m venv venv

## PowerShell (Windows)
Activate:   venv\Scripts\Activate.ps1
Nếu lỗi:    Set-ExecutionPolicy RemoteSigned
Deactivate: deactivate

## CMD (Windows)
Activate:   venv\Scripts\activate.bat
Deactivate: deactivate

## Git Bash (Windows)
Activate:   source venv/Scripts/activate
Deactivate: deactivate

## Linux / macOS
Activate:   source venv/bin/activate
Deactivate: deactivate


# Cài package
python.exe -m pip install --upgrade pip
pip install -r script/tagging/requirements.txt

# Với tagging

## Không cần tham số, sử dụng giá trị mặc định
python script/tagging/runserver.py

## Hoặc với tham số tùy chọn
python script/tagging/runserver.py "E:\WORK\canva\sample\unziped_all"

# Với unzip
## Không cần tham số, sử dụng giá trị mặc định
python script/unzip/main.py

## Chọn chế độ unzip
python script/unzip/main.py --mode all
python script/unzip/main.py --mode svg_only

## Với đường dẫn tùy chỉnh
python script/unzip/main.py "E:\WORK\canva\mysamples"

.\venv\Scripts\Activate.ps1; 

# Xử lý svg

## Gộp các file json color
python .\script\svg_painter\palettes\merge_color.py

## Tô màu svg
python script/svg_painter/colorizer.py