#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import multiprocessing
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from .processor import ImageProcessor
from ..models.utils import find_png_dirs

logger = logging.getLogger("batch")

class BatchProcessor:
    """Xử lý hàng loạt nhiều thư mục PNG"""
    
    def __init__(self, use_gpu=True, batch_size=32, workers=None, cache_dir="data/cache"):
        self.use_gpu = use_gpu
        self.batch_size = batch_size
        self.cache_dir = cache_dir
        
        # Số worker mặc định là số CPU logic trừ 1 (giữ 1 core cho hệ thống)
        # GPU chỉ dùng 1 worker vì không thể song song hóa xử lý GPU
        if workers is None:
            self.workers = 1 if use_gpu else max(1, multiprocessing.cpu_count() - 1)
        else:
            self.workers = max(1, int(workers))
        
        logger.info(f"Khởi tạo BatchProcessor: use_gpu={use_gpu}, batch_size={batch_size}, workers={self.workers}")
    
    def process_directory(self, png_dir):
        """
        Xử lý toàn bộ ảnh PNG trong một thư mục
        
        Args:
            png_dir: Đường dẫn đến thư mục chứa file PNG
            
        Returns:
            List các metadata đã xử lý
        """
        # Tìm tất cả file PNG trong thư mục
        png_files = sorted([f for f in Path(png_dir).glob("*.png")])
        
        if not png_files:
            logger.warning(f"Không tìm thấy file PNG nào trong {png_dir}")
            return []
        
        logger.info(f"Tìm thấy {len(png_files)} file PNG trong {png_dir}")
        
        # Khởi tạo processor
        processor = ImageProcessor(use_gpu=self.use_gpu, cache_dir=self.cache_dir)
        
        results = []
        
        # Xử lý từng ảnh
        for png_file in tqdm(png_files, desc=f"Xử lý {os.path.basename(png_dir)}"):
            metadata = processor.process_image(str(png_file), use_cache=True)
            if metadata:
                results.append(metadata)
        
        return results
    
    def process_batch(self, input_dir):
        """
        Xử lý hàng loạt nhiều thư mục PNG
        
        Args:
            input_dir: Thư mục gốc chứa các thư mục con có PNG
            
        Returns:
            Dict với key là thư mục mục tiêu, value là list metadata
        """
        # Tìm tất cả thư mục PNG
        png_dirs = find_png_dirs(input_dir)
        
        if not png_dirs:
            logger.error(f"Không tìm thấy thư mục PNG nào trong {input_dir}")
            return {}
        
        logger.info(f"Tìm thấy {len(png_dirs)} thư mục PNG để xử lý")
        
        # Lưu kết quả
        results = {}
        
        # Nếu chỉ xử lý trên 1 worker (GPU/CPU đơn luồng)
        if self.workers == 1:
            for png_dir in png_dirs:
                # Xử lý directory này
                target_dir = self._get_target_directory(png_dir)
                logger.info(f"Đang xử lý thư mục: {target_dir}")
                
                # Xử lý và lưu kết quả
                metadata_list = self.process_directory(png_dir)
                results[target_dir] = metadata_list
        else:
            # Xử lý song song trên nhiều CPU
            with ProcessPoolExecutor(max_workers=self.workers) as executor:
                # Tạo ánh xạ từ future -> dir để theo dõi
                future_to_dir = {
                    executor.submit(self.process_directory, png_dir): self._get_target_directory(png_dir)
                    for png_dir in png_dirs
                }
                
                # Theo dõi tiến trình
                for future in tqdm(as_completed(future_to_dir), total=len(png_dirs), desc="Xử lý các thư mục"):
                    target_dir = future_to_dir[future]
                    try:
                        metadata_list = future.result()
                        results[target_dir] = metadata_list
                    except Exception as e:
                        logger.error(f"Xử lý thư mục {target_dir} gặp lỗi: {e}")
        
        return results
    
    def _get_target_directory(self, png_dir):
        """
        Lấy tên thư mục đích từ đường dẫn PNG
        Ví dụ: input/110790-speeches/png -> 110790-speeches
        """
        # Lấy thư mục cha của thư mục PNG
        parent_dir = Path(png_dir).parent
        return os.path.basename(parent_dir) 