#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path

# Changed from relative to absolute import
from models.clip_model import ClipInterrogatorModel
from models.tag_generator import TagGenerator
from models.utils import clean_filename, extract_title

logger = logging.getLogger("processor")

class ImageProcessor:
    """Process individual images to generate metadata"""
    
    def __init__(self, use_gpu=True, cache_dir="data/cache"):
        # Determine device
        device = "cuda" if use_gpu else "cpu"
        
        # Initialize models
        self.clip_model = ClipInterrogatorModel(device=device, cache_dir=cache_dir)
        self.tag_generator = TagGenerator(device=device, cache_dir=cache_dir)
        
        logger.info(f"ImageProcessor initialized with device={device}")
    
    def process_image(self, image_path, use_cache=True):
        """
        Process an image to generate metadata
        
        Args:
            image_path: Path to the PNG image file
            use_cache: Whether to use cache
            
        Returns:
            Dict containing image metadata or None if error
        """
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Get filename
            filename = os.path.basename(image_path)
            
            # 1. Generate description from image
            description = self.clip_model.generate_description(image_path, use_cache=use_cache)
            
            if not description:
                logger.error(f"Could not generate description for {filename}")
                return None
            
            # 2. Generate tags from description
            tags = self.tag_generator.generate_tags(
                description, 
                image_path=image_path,
                num_tags=25,
                use_cache=use_cache
            )
            
            if not tags:
                logger.warning(f"Could not generate tags for {filename}")
                tags = []
            
            # 3. Create metadata
            metadata = {
                "filename": clean_filename(filename),     # Convert .png to .svg
                "title": extract_title(filename),         # Remove index number and extension
                "keywords": ",".join(tags),               # Join tags with commas
                "Artist": "",                             # Leave empty
                "description": description                # Detailed description
            }
            
            logger.info(f"Finished processing image: {filename}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None 