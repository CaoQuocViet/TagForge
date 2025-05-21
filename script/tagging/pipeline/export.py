#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger("export")

class MetadataExporter:
    """Xuất metadata ra CSV và quản lý thư mục đầu ra"""
    
    def __init__(self, output_base_dir="E:/WORK/canva/output"):
        self.output_base_dir = Path(output_base_dir)
        
        # Tạo thư mục gốc đầu ra nếu chưa tồn tại
        os.makedirs(output_base_dir, exist_ok=True)
        
        logger.info(f"Khởi tạo MetadataExporter với output_dir: {output_base_dir}")
    
    def export_metadata(self, target_dir, metadata_list, input_root_dir):
        """
        Xuất metadata ra CSV và tạo cấu trúc thư mục đầu ra
        
        Args:
            target_dir: Tên thư mục đích (ví dụ: "110790-speeches")
            metadata_list: Danh sách metadata của các ảnh
            input_root_dir: Thư mục gốc đầu vào để tìm thư mục svg
            
        Returns:
            Bool thành công hay không
        """
        if not metadata_list:
            logger.warning(f"Danh sách metadata trống cho {target_dir}")
            return False
        
        # Tạo thư mục đích
        output_dir = self.output_base_dir / target_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Path đến file csv
        csv_path = output_dir / "metadata.csv"
        
        try:
            # Tạo DataFrame từ metadata
            df = pd.DataFrame(metadata_list)
            
            # Đảm bảo thứ tự cột theo yêu cầu
            column_order = ["filename", "title", "keywords", "Artist", "description"]
            df = df[column_order]
            
            # Ghi ra CSV
            df.to_csv(csv_path, index=False)
            
            logger.info(f"Đã xuất metadata thành công: {csv_path}")
            
            # Copy thư mục SVG và PNG nếu cần
            self._copy_asset_folders(target_dir, input_root_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi xuất metadata cho {target_dir}: {e}")
            return False
    
    def export_batch_results(self, batch_results, input_root_dir):
        """
        Xuất kết quả hàng loạt
        
        Args:
            batch_results: Dict với key là tên thư mục, value là list metadata
            input_root_dir: Thư mục gốc đầu vào
            
        Returns:
            Số lượng thư mục đã xử lý thành công
        """
        success_count = 0
        
        for target_dir, metadata_list in batch_results.items():
            if self.export_metadata(target_dir, metadata_list, input_root_dir):
                success_count += 1
        
        logger.info(f"Đã xuất thành công {success_count}/{len(batch_results)} thư mục")
        return success_count
    
    def _copy_asset_folders(self, target_dir, input_root_dir):
        """
        Copy thư mục svg và png nếu cần thiết
        
        Args:
            target_dir: Tên thư mục đích
            input_root_dir: Thư mục gốc đầu vào
        """
        # Thư mục chủ đề trong input
        input_theme_dir = Path(input_root_dir) / target_dir
        
        # Đích đến
        output_theme_dir = self.output_base_dir / target_dir
        
        # Các thư mục cần copy
        asset_folders = ["svg"]  # Chỉ copy svg, không cần png vì đã có metadata
        
        for folder in asset_folders:
            src_dir = input_theme_dir / folder
            dst_dir = output_theme_dir / folder
            
            if src_dir.exists() and src_dir.is_dir():
                if dst_dir.exists():
                    logger.info(f"Xóa thư mục đích cũ: {dst_dir}")
                    shutil.rmtree(dst_dir)
                
                logger.info(f"Copy thư mục {folder} từ {src_dir} sang {dst_dir}")
                shutil.copytree(src_dir, dst_dir)
            else:
                logger.warning(f"Không tìm thấy thư mục nguồn {src_dir}") 