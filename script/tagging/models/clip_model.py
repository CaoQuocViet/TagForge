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
    
    def __init__(self, clip_model_name="ViT-L/14", device=None, cache_dir="data/cache"):
        self.cache_dir = setup_cache_dir(cache_dir)
        
        # Determine device (CPU/GPU)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Initialize CLIP Interrogator
        try:
            config = Config(clip_model_name=clip_model_name)
            config.device = self.device
            
            # If running on GPU, no need to offload (sufficient VRAM)
            if self.device == "cuda":
                config.blip_offload = False
                logger.info("Using full GPU (no offload)")
            
            self.ci = Interrogator(config)
            logger.info(f"CLIP Interrogator initialized with model {clip_model_name}")
        except Exception as e:
            logger.error(f"Error initializing CLIP Interrogator: {e}")
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
            # Read image
            image = Image.open(image_path).convert('RGB')
            
            # Generate description
            logger.info(f"Generating description for {os.path.basename(image_path)}")
            description = self.ci.interrogate(image)
            
            # Save to cache
            save_to_cache({"description": description}, cache_path)
            
            return description
        except Exception as e:
            logger.error(f"Error generating description for {image_path}: {e}")
            return None
        
    def __del__(self):
        """Free resources when object is destroyed"""
        if hasattr(self, 'ci'):
            del self.ci
        torch.cuda.empty_cache() 