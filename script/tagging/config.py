#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# Thư mục gốc của dự án
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Cấu hình đường dẫn
class PathConfig:
    # Thư mục đầu vào mặc định - thư mục chứa các thư mục con với PNG
    DEFAULT_INPUT_DIR = os.environ.get('CANVA_INPUT_DIR', str(PROJECT_ROOT / "sample" / "unziped_all"))
    
    # Thư mục đầu ra mặc định - nơi lưu kết quả metadata.csv
    DEFAULT_OUTPUT_DIR = os.environ.get('CANVA_OUTPUT_DIR', str(PROJECT_ROOT / "output"))
    
    # Thư mục cache cho CLIP Interrogator và KeyBERT
    DEFAULT_CACHE_DIR = os.environ.get('CANVA_CACHE_DIR', str(Path(__file__).parent / "data" / "cache"))
    
    # Đảm bảo các thư mục tồn tại
    @classmethod
    def ensure_dirs(cls):
        os.makedirs(cls.DEFAULT_OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.DEFAULT_CACHE_DIR, exist_ok=True)

# Cấu hình AI model
class ModelConfig:
    # CLIP Interrogator model
    CLIP_MODEL_NAME = os.environ.get('CANVA_CLIP_MODEL', "ViT-L/14")
    
    # KeyBERT model
    KEYBERT_MODEL_NAME = os.environ.get('CANVA_KEYBERT_MODEL', "all-MiniLM-L6-v2")
    
    # Số lượng tags cần sinh
    NUM_TAGS = int(os.environ.get('CANVA_NUM_TAGS', "25"))
    
    # Mức độ đa dạng của tags (0-1)
    TAG_DIVERSITY = float(os.environ.get('CANVA_TAG_DIVERSITY', "0.7"))

# Cấu hình thực thi
class ExecutionConfig:
    # Sử dụng GPU nếu khả dụng
    USE_GPU = os.environ.get('CANVA_USE_GPU', "True").lower() in ('true', '1', 'yes')
    
    # Kích thước batch xử lý
    BATCH_SIZE = int(os.environ.get('CANVA_BATCH_SIZE', "32"))
    
    # Số lượng worker xử lý song song (None = tự động)
    NUM_WORKERS = os.environ.get('CANVA_NUM_WORKERS', None)
    if NUM_WORKERS:
        NUM_WORKERS = int(NUM_WORKERS)
    
    # Có sử dụng cache hay không
    USE_CACHE = os.environ.get('CANVA_USE_CACHE', "True").lower() in ('true', '1', 'yes')

# Tạo thư mục nếu chưa tồn tại
PathConfig.ensure_dirs()

# In ra thông tin cấu hình khi import module
if __name__ == "__main__":
    print("=== Cấu hình Tagging ===")
    print(f"Thư mục đầu vào: {PathConfig.DEFAULT_INPUT_DIR}")
    print(f"Thư mục đầu ra: {PathConfig.DEFAULT_OUTPUT_DIR}")
    print(f"Thư mục cache: {PathConfig.DEFAULT_CACHE_DIR}")
    print(f"Sử dụng GPU: {ExecutionConfig.USE_GPU}")
    print(f"CLIP model: {ModelConfig.CLIP_MODEL_NAME}")
    print(f"Số lượng tags: {ModelConfig.NUM_TAGS}") 