#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import argparse
import torch
from pathlib import Path

# Thêm đường dẫn gốc của dự án vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("tagging.log", encoding='utf-8')
    ]
)
logger = logging.getLogger("main")

# Kiểm tra GPU
cuda_available = False
try:
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        logger.info(f"CUDA available - GPU: {torch.cuda.get_device_name(0)}")
    else:
        logger.warning("CUDA not available - using CPU")
except Exception as e:
    logger.warning(f"Error checking CUDA: {e}")

# Import các module
from pipeline.batch import BatchProcessor
from pipeline.export import MetadataExporter
from config import PathConfig, ModelConfig, ExecutionConfig

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Icon PNG Metadata Generator")
    
    parser.add_argument(
        "input_dir", 
        type=str, 
        nargs='?',  # Làm tham số tùy chọn 
        default=PathConfig.DEFAULT_INPUT_DIR,
        help=f"Input directory containing icon folders (default: {PathConfig.DEFAULT_INPUT_DIR})"
    )
    
    parser.add_argument(
        "--output_dir", 
        type=str,
        default=PathConfig.DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {PathConfig.DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--batch_size", 
        type=int,
        default=ExecutionConfig.BATCH_SIZE,
        help=f"Number of images to process in each batch (default: {ExecutionConfig.BATCH_SIZE})"
    )
    
    parser.add_argument(
        "--gpu", 
        type=bool,
        default=ExecutionConfig.USE_GPU,
        help=f"Use GPU if available (default: {ExecutionConfig.USE_GPU})"
    )
    
    parser.add_argument(
        "--workers", 
        type=int,
        default=ExecutionConfig.NUM_WORKERS,
        help="Number of parallel workers (default: auto-detect)"
    )
    
    parser.add_argument(
        "--cache_dir", 
        type=str,
        default=PathConfig.DEFAULT_CACHE_DIR,
        help=f"Cache directory (default: {PathConfig.DEFAULT_CACHE_DIR})"
    )
    
    parser.add_argument(
        "--num_tags", 
        type=int,
        default=ModelConfig.NUM_TAGS,
        help=f"Number of tags to generate (default: {ModelConfig.NUM_TAGS})"
    )
    
    return parser.parse_args()

def main():
    """Entrypoint chính của ứng dụng"""
    # Parse arguments
    args = parse_args()
    
    # Hiển thị thông tin cấu hình
    logger.info("=== CLIP Interrogator - Icon Metadata Generator ===")
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Use GPU: {args.gpu and cuda_available}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Cache: {args.cache_dir}")
    logger.info(f"Number of tags: {args.num_tags}")
    
    # Kiểm tra thư mục đầu vào
    if not os.path.isdir(args.input_dir):
        logger.error(f"Input directory does not exist: {args.input_dir}")
        return 1
    
    # Bắt đầu xử lý
    start_time = time.time()
    
    try:
        # Khởi tạo batch processor
        batch_processor = BatchProcessor(
            use_gpu=args.gpu and cuda_available,
            batch_size=args.batch_size,
            workers=args.workers,
            cache_dir=args.cache_dir
        )
        
        # Xử lý hàng loạt
        logger.info("Starting batch processing...")
        batch_results = batch_processor.process_batch(args.input_dir)
        
        if not batch_results:
            logger.error("No results were generated!")
            return 1
        
        # Khởi tạo exporter
        exporter = MetadataExporter(output_base_dir=args.output_dir)
        
        # Xuất kết quả
        logger.info("Starting export process...")
        success_count = exporter.export_batch_results(batch_results, args.input_dir)
        
        # Tính thời gian
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        logger.info(f"Completed! Processed {success_count} directories")
        logger.info(f"Total time: {int(hours)}h {int(minutes)}m {int(seconds)}s")
        
        return 0
        
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
