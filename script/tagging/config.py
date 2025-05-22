#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Path configuration
class PathConfig:
    # Default input directory - contains subdirectories with PNG files
    DEFAULT_INPUT_DIR = os.environ.get('CANVA_INPUT_DIR', str(PROJECT_ROOT / "sample" / "unziped_all"))
    
    # Default output directory - where metadata.csv files will be saved
    DEFAULT_OUTPUT_DIR = os.environ.get('CANVA_OUTPUT_DIR', str(PROJECT_ROOT / "output"))
    
    # Cache directory for CLIP Interrogator and KeyBERT
    DEFAULT_CACHE_DIR = os.environ.get('CANVA_CACHE_DIR', str(Path(__file__).parent / "data" / "cache"))
    
    # Ensure directories exist
    @classmethod
    def ensure_dirs(cls):
        os.makedirs(cls.DEFAULT_OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.DEFAULT_CACHE_DIR, exist_ok=True)

# AI model configuration
class ModelConfig:
    # CLIP Interrogator model
    CLIP_MODEL_NAME = os.environ.get('CANVA_CLIP_MODEL', "ViT-L-14/laion2b_s32b_b82k")
    
    # KeyBERT model
    KEYBERT_MODEL_NAME = os.environ.get('CANVA_KEYBERT_MODEL', "distilbert-base-nli-mean-tokens")
    
    # Number of tags to generate
    NUM_TAGS = int(os.environ.get('CANVA_NUM_TAGS', "25"))
    
    # Tag diversity level (0-1)
    TAG_DIVERSITY = float(os.environ.get('CANVA_TAG_DIVERSITY', "0.7"))

# Execution configuration
class ExecutionConfig:
    # Use GPU if available
    USE_GPU = os.environ.get('CANVA_USE_GPU', "True").lower() in ('true', '1', 'yes')
    
    # Batch processing size
    BATCH_SIZE = int(os.environ.get('CANVA_BATCH_SIZE', "32"))
    
    # Number of parallel workers (None = auto-detect)
    NUM_WORKERS = os.environ.get('CANVA_NUM_WORKERS', None)
    if NUM_WORKERS:
        NUM_WORKERS = int(NUM_WORKERS)
    
    # Whether to use cache
    USE_CACHE = os.environ.get('CANVA_USE_CACHE', "True").lower() in ('true', '1', 'yes')

# Create directories if they don't exist
PathConfig.ensure_dirs()

# Print configuration information when module is imported
if __name__ == "__main__":
    print("=== Tagging Configuration ===")
    print(f"Input directory: {PathConfig.DEFAULT_INPUT_DIR}")
    print(f"Output directory: {PathConfig.DEFAULT_OUTPUT_DIR}")
    print(f"Cache directory: {PathConfig.DEFAULT_CACHE_DIR}")
    print(f"Use GPU: {ExecutionConfig.USE_GPU}")
    print(f"CLIP model: {ModelConfig.CLIP_MODEL_NAME}")
    print(f"Number of tags: {ModelConfig.NUM_TAGS}") 