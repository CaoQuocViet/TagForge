#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import torch
from PIL import Image
import logging
from clip_interrogator import Config, Interrogator
from models.utils import get_cache_path, save_to_cache, load_from_cache, setup_cache_dir

logger = logging.getLogger("clip_model")

class ClipInterrogatorModel:
    """Wrapper for CLIP Interrogator to generate descriptions from images"""
    
    def __init__(self, clip_model_name="ViT-L-14/laion2b_s32b_b82k", device=None, cache_dir="data/cache"):
        self.cache_dir = setup_cache_dir(cache_dir)
        
        # Determine device (CPU/GPU)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Initialize CLIP Interrogator
        try:
            # Configure CLIP Interrogator
            config = Config()
            config.clip_model_name = clip_model_name
            config.device = self.device
            
            # GPU optimizations
            if self.device == "cuda":
                config.blip_offload = False
                config.chunk_size = 2048 if torch.cuda.get_device_properties(0).total_memory >= 16e9 else 1024
                logger.info(f"Using GPU with chunk_size={config.chunk_size}")
            
            # Initialize interrogator with error handling
            logger.info("Loading CLIP Interrogator...")
            try:
                self.ci = Interrogator(config)
                logger.info(f"CLIP Interrogator initialized successfully with model {clip_model_name}")
            except Exception as model_error:
                logger.error(f"Error loading model {clip_model_name}: {model_error}")
                # Try fallback model if primary fails
                fallback_model = "ViT-L-14"
                logger.info(f"Trying fallback model: {fallback_model}")
                config.clip_model_name = fallback_model
                self.ci = Interrogator(config)
                logger.info(f"Successfully initialized with fallback model {fallback_model}")
                
        except Exception as e:
            logger.error(f"Critical error initializing CLIP Interrogator: {e}")
            raise
    
    def generate_description(self, image_path, use_cache=True):
        """Generate description from image with caching"""
        # Create cache file path
        cache_path = get_cache_path(image_path, prefix="desc_", cache_dir=self.cache_dir)
        
        # Check cache if requested
        if use_cache:
            cached_data = load_from_cache(cache_path)
            if cached_data:
                logger.info(f"Using cached description for {os.path.basename(image_path)}")
                return cached_data["description"]
        
        # If no cache or not using cache, generate new description
        try:
            # Read and validate image
            try:
                image = Image.open(image_path).convert('RGB')
            except Exception as img_error:
                logger.error(f"Error reading image {image_path}: {img_error}")
                return None
            
            # Generate description with timeout handling
            logger.info(f"Generating description for {os.path.basename(image_path)}")
            try:
                description = self.ci.interrogate(image)
                
                # Validate description
                if not description or len(description.strip()) < 10:
                    logger.warning(f"Generated description too short or empty for {image_path}")
                    return None
                
                # Save to cache
                save_to_cache({"description": description}, cache_path)
                
                return description
                
            except Exception as desc_error:
                logger.error(f"Error during description generation: {desc_error}")
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error processing {image_path}: {e}")
            return None
        
    def __del__(self):
        """Clean up resources when object is destroyed"""
        try:
            if hasattr(self, 'ci'):
                del self.ci
            torch.cuda.empty_cache()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}") 