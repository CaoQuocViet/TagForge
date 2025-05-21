#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import torch
from PIL import Image
import logging
from clip_interrogator import Config, Interrogator
from .utils import get_cache_path, save_to_cache, load_from_cache, setup_cache_dir

logger = logging.getLogger("clip_model")

class ClipInterrogatorModel:
    """Wrapper cho CLIP Interrogator để sinh mô tả từ ảnh"""
    
    def __init__(self, clip_model_name="ViT-L/14", device=None, cache_dir="data/cache"):
        self.cache_dir = setup_cache_dir(cache_dir)
        
        # Xác định device (CPU/GPU)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Sử dụng device: {self.device}")
        
        # Khởi tạo CLIP Interrogator
        try:
            config = Config(clip_model_name=clip_model_name)
            config.device = self.device
            
            # Nếu chạy trên GPU thì không cần offload (đủ VRAM)
            if self.device == "cuda":
                config.blip_offload = False
                logger.info("Sử dụng GPU đầy đủ (không offload)")
            
            self.ci = Interrogator(config)
            logger.info(f"Đã khởi tạo CLIP Interrogator với model {clip_model_name}")
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo CLIP Interrogator: {e}")
            raise
    
    def generate_description(self, image_path, use_cache=True):
        """Sinh mô tả từ ảnh với cache"""
        # Tạo đường dẫn file cache
        cache_path = get_cache_path(image_path, prefix="desc_", cache_dir=self.cache_dir)
        
        # Kiểm tra cache nếu được yêu cầu
        if use_cache:
            cached_data = load_from_cache(cache_path)
            if cached_data:
                logger.info(f"Sử dụng description từ cache cho {os.path.basename(image_path)}")
                return cached_data["description"]
        
        # Nếu không có cache hoặc không dùng cache, sinh mô tả mới
        try:
            # Đọc ảnh
            image = Image.open(image_path).convert('RGB')
            
            # Sinh mô tả
            logger.info(f"Đang sinh mô tả cho {os.path.basename(image_path)}")
            description = self.ci.interrogate(image)
            
            # Lưu cache
            save_to_cache({"description": description}, cache_path)
            
            return description
        except Exception as e:
            logger.error(f"Lỗi khi sinh mô tả cho {image_path}: {e}")
            return None
        
    def __del__(self):
        """Giải phóng tài nguyên khi đối tượng bị hủy"""
        if hasattr(self, 'ci'):
            del self.ci
        torch.cuda.empty_cache() 