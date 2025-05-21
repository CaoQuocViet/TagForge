#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import multiprocessing
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

# Changed from relative to absolute import
from pipeline.processor import ImageProcessor
from models.utils import find_png_dirs

logger = logging.getLogger("batch")

class BatchProcessor:
    """Process batches of PNG directories"""
    
    def __init__(self, use_gpu=True, batch_size=32, workers=None, cache_dir="data/cache"):
        self.use_gpu = use_gpu
        self.batch_size = batch_size
        self.cache_dir = cache_dir
        
        # Default number of workers is logical CPU count minus 1 (keep 1 core for system)
        # GPU uses only 1 worker since it can't parallelize GPU processing
        if workers is None:
            self.workers = 1 if use_gpu else max(1, multiprocessing.cpu_count() - 1)
        else:
            self.workers = max(1, int(workers))
        
        logger.info(f"Initialized BatchProcessor: use_gpu={use_gpu}, batch_size={batch_size}, workers={self.workers}")
    
    def process_directory(self, png_dir):
        """
        Process all PNG images in a directory
        
        Args:
            png_dir: Path to directory containing PNG files
            
        Returns:
            List of processed metadata
        """
        # Find all PNG files in the directory
        png_files = sorted([f for f in Path(png_dir).glob("*.png")])
        
        if not png_files:
            logger.warning(f"No PNG files found in {png_dir}")
            return []
        
        logger.info(f"Found {len(png_files)} PNG files in {png_dir}")
        
        # Initialize processor
        processor = ImageProcessor(use_gpu=self.use_gpu, cache_dir=self.cache_dir)
        
        results = []
        
        # Process each image
        for png_file in tqdm(png_files, desc=f"Processing {os.path.basename(png_dir)}"):
            metadata = processor.process_image(str(png_file), use_cache=True)
            if metadata:
                results.append(metadata)
        
        return results
    
    def process_batch(self, input_dir):
        """
        Process multiple PNG directories in batch
        
        Args:
            input_dir: Root directory containing subdirectories with PNGs
            
        Returns:
            Dict with target directory as key and metadata list as value
        """
        # Find all PNG directories
        png_dirs = find_png_dirs(input_dir)
        
        if not png_dirs:
            logger.error(f"No PNG directories found in {input_dir}")
            return {}
        
        logger.info(f"Found {len(png_dirs)} PNG directories to process")
        
        # Store results
        results = {}
        
        # If processing with only 1 worker (GPU/single-threaded CPU)
        if self.workers == 1:
            for png_dir in png_dirs:
                # Process this directory
                target_dir = self._get_target_directory(png_dir)
                logger.info(f"Processing directory: {target_dir}")
                
                # Process and save results
                metadata_list = self.process_directory(png_dir)
                results[target_dir] = metadata_list
        else:
            # Parallel processing on multiple CPUs
            with ProcessPoolExecutor(max_workers=self.workers) as executor:
                # Create mapping from future -> dir to track
                future_to_dir = {
                    executor.submit(self.process_directory, png_dir): self._get_target_directory(png_dir)
                    for png_dir in png_dirs
                }
                
                # Track progress
                for future in tqdm(as_completed(future_to_dir), total=len(png_dirs), desc="Processing directories"):
                    target_dir = future_to_dir[future]
                    try:
                        metadata_list = future.result()
                        results[target_dir] = metadata_list
                    except Exception as e:
                        logger.error(f"Error processing directory {target_dir}: {e}")
        
        return results
    
    def _get_target_directory(self, png_dir):
        """
        Get target directory name from PNG path
        Example: input/110790-speeches/png -> 110790-speeches
        """
        # Get parent directory of PNG directory
        parent_dir = Path(png_dir).parent
        return os.path.basename(parent_dir) 