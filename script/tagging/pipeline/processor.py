#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path

# Sửa import từ tương đối sang tuyệt đối
from models.clip_model import ClipInterrogatorModel
from models.tag_generator import TagGenerator
from models.utils import clean_filename, extract_title

logger = logging.getLogger("processor")

class ImageProcessor:
    """Xử lý từng ảnh riêng lẻ để tạo metadata"""
    
    def __init__(self, use_gpu=True, cache_dir="data/cache"):
        # Xác định device
        device = "cuda" if use_gpu else "cpu"
        
        # Khởi tạo các model
        self.clip_model = ClipInterrogatorModel(device=device, cache_dir=cache_dir)
        self.tag_generator = TagGenerator(device=device, cache_dir=cache_dir)
        
        logger.info(f"Đã khởi tạo ImageProcessor với device={device}")
    
    def process_image(self, image_path, use_cache=True):
        """
        Xử lý một ảnh để sinh ra metadata
        
        Args:
            image_path: Đường dẫn đến file ảnh PNG
            use_cache: Có sử dụng cache hay không
            
        Returns:
            Dict chứa metadata của ảnh hoặc None nếu có lỗi
        """
        try:
            logger.info(f"Đang xử lý ảnh: {image_path}")
            
            # Lấy tên file
            filename = os.path.basename(image_path)
            
            # 1. Sinh mô tả từ ảnh
            description = self.clip_model.generate_description(image_path, use_cache=use_cache)
            
            if not description:
                logger.error(f"Không sinh được mô tả cho {filename}")
                return None
            
            # 2. Sinh tags từ mô tả
            tags = self.tag_generator.generate_tags(
                description, 
                image_path=image_path,
                num_tags=25,
                use_cache=use_cache
            )
            
            if not tags:
                logger.warning(f"Không sinh được tags cho {filename}")
                tags = []
            
            # 3. Tạo metadata
            metadata = {
                "filename": clean_filename(filename),     # Chuyển .png thành .svg
                "title": extract_title(filename),         # Loại bỏ số thứ tự và phần mở rộng
                "keywords": ",".join(tags),               # Nối các tags bằng dấu phẩy
                "Artist": "",                             # Để trống
                "description": description                # Mô tả chi tiết
            }
            
            logger.info(f"Đã xử lý xong ảnh: {filename}")
            return metadata
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý ảnh {image_path}: {e}")
            return None 