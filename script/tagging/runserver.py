#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import argparse
from pathlib import Path

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("tagging.log")
    ]
)
logger = logging.getLogger("main")

# Import các module
from pipeline.batch import BatchProcessor
from pipeline.export import MetadataExporter
from config import PathConfig, ModelConfig, ExecutionConfig

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Tự động sinh metadata cho icon PNG")
    
    parser.add_argument(
        "input_dir", 
        type=str, 
        nargs='?',  # Làm tham số tùy chọn 
        default=PathConfig.DEFAULT_INPUT_DIR,
        help=f"Thư mục gốc chứa các thư mục icon (mặc định: {PathConfig.DEFAULT_INPUT_DIR})"
    )
    
    parser.add_argument(
        "--output_dir", 
        type=str,
        default=PathConfig.DEFAULT_OUTPUT_DIR,
        help=f"Thư mục đầu ra (mặc định: {PathConfig.DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--batch_size", 
        type=int,
        default=ExecutionConfig.BATCH_SIZE,
        help=f"Số ảnh xử lý mỗi lần (mặc định: {ExecutionConfig.BATCH_SIZE})"
    )
    
    parser.add_argument(
        "--gpu", 
        type=bool,
        default=ExecutionConfig.USE_GPU,
        help=f"Sử dụng GPU nếu có (mặc định: {ExecutionConfig.USE_GPU})"
    )
    
    parser.add_argument(
        "--workers", 
        type=int,
        default=ExecutionConfig.NUM_WORKERS,
        help="Số luồng xử lý song song (mặc định: tự phát hiện)"
    )
    
    parser.add_argument(
        "--cache_dir", 
        type=str,
        default=PathConfig.DEFAULT_CACHE_DIR,
        help=f"Thư mục lưu cache (mặc định: {PathConfig.DEFAULT_CACHE_DIR})"
    )
    
    parser.add_argument(
        "--num_tags", 
        type=int,
        default=ModelConfig.NUM_TAGS,
        help=f"Số lượng tags cần sinh (mặc định: {ModelConfig.NUM_TAGS})"
    )
    
    return parser.parse_args()

def main():
    """Entrypoint chính của ứng dụng"""
    # Parse arguments
    args = parse_args()
    
    # Hiển thị thông tin cấu hình
    logger.info("=== CLIP Interrogator - Sinh Metadata Icon ===")
    logger.info(f"Thư mục đầu vào: {args.input_dir}")
    logger.info(f"Thư mục đầu ra: {args.output_dir}")
    logger.info(f"Sử dụng GPU: {args.gpu}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Cache: {args.cache_dir}")
    logger.info(f"Số lượng tags: {args.num_tags}")
    
    # Kiểm tra thư mục đầu vào
    if not os.path.isdir(args.input_dir):
        logger.error(f"Thư mục đầu vào không tồn tại: {args.input_dir}")
        return 1
    
    # Bắt đầu xử lý
    start_time = time.time()
    
    try:
        # Khởi tạo batch processor
        batch_processor = BatchProcessor(
            use_gpu=args.gpu,
            batch_size=args.batch_size,
            workers=args.workers,
            cache_dir=args.cache_dir
        )
        
        # Xử lý hàng loạt
        logger.info("Bắt đầu xử lý batch...")
        batch_results = batch_processor.process_batch(args.input_dir)
        
        if not batch_results:
            logger.error("Không có kết quả nào được sinh ra!")
            return 1
        
        # Khởi tạo exporter
        exporter = MetadataExporter(output_base_dir=args.output_dir)
        
        # Xuất kết quả
        logger.info("Bắt đầu xuất kết quả...")
        success_count = exporter.export_batch_results(batch_results, args.input_dir)
        
        # Tính thời gian
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        logger.info(f"Hoàn thành! Đã xử lý {success_count} thư mục")
        logger.info(f"Tổng thời gian: {int(hours)}h {int(minutes)}m {int(seconds)}s")
        
        return 0
        
    except Exception as e:
        logger.error(f"Lỗi không xử lý được: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
