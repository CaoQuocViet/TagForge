#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import torch
from PIL import Image
import logging
import re
from clip_interrogator import Config, Interrogator
from transformers import BlipProcessor, BlipForConditionalGeneration
from models.utils import get_cache_path, save_to_cache, load_from_cache, setup_cache_dir

logger = logging.getLogger("clip_model")

class ClipInterrogatorModel:
    """Wrapper for CLIP Interrogator to generate descriptions from images"""
    
    def __init__(self, clip_model_name="ViT-L-14/laion2b_s32b_b82k", device=None, cache_dir="data/cache"):
        self.cache_dir = setup_cache_dir(cache_dir)
        
        # Determine device (CPU/GPU)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        try:
            # Initialize BLIP model for better captions
            logger.info("Loading BLIP model...")
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
            self.blip_model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-large"
            ).to(self.device)
            
            # Initialize CLIP Interrogator for additional details
            logger.info("Loading CLIP Interrogator...")
            config = Config()
            config.clip_model_name = clip_model_name
            config.device = self.device
            
            if self.device == "cuda":
                config.blip_offload = False
                config.chunk_size = 2048 if torch.cuda.get_device_properties(0).total_memory >= 16e9 else 1024
            
            self.ci = Interrogator(config)
            logger.info("Models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    def _generate_blip_caption(self, image):
        """Generate a clean caption using BLIP"""
        try:
            # Process image
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            
            # Generate caption with improved parameters
            outputs = self.blip_model.generate(
                **inputs,
                max_new_tokens=30,          # Shorter to avoid rambling
                min_length=15,              # Ensure reasonable length
                num_beams=7,                # More beams for better quality
                length_penalty=1.5,         # Favor slightly longer sentences
                temperature=0.7,            # Lower temperature for more focused output
                repetition_penalty=1.2,     # Avoid repetitive phrases
                no_repeat_ngram_size=2      # Prevent repeating word pairs
            )
            
            # Decode caption
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            return caption.strip()
            
        except Exception as e:
            logger.error(f"Error generating BLIP caption: {e}")
            return None
    
    def _get_clip_details(self, image):
        """Get additional details from CLIP"""
        try:
            # Get medium and artist details with fast mode
            clip_details = self.ci.interrogate_fast(image)
            
            # Extract relevant keywords with improved filtering
            keywords = []
            seen = set()  # Track unique words
            
            for word in clip_details.split(','):
                word = word.strip().lower()
                # More strict filtering
                if (len(word) > 2 and                     # Skip short words
                    word not in seen and                  # Skip duplicates
                    not any(char.isdigit() for char in word) and  # Skip numbers
                    not any(char in '!@#$%^&*()[]{}|\\/,.<>?`~' for char in word) and  # Skip special chars
                    not any(tech_term in word for tech_term in ['jpg', 'jpeg', 'png', 'svg', 'image', 'photo', 'resolution'])):  # Skip technical terms
                    keywords.append(word)
                    seen.add(word)
            
            # Return top 3 most relevant keywords to avoid noise
            return keywords[:3]
            
        except Exception as e:
            logger.error(f"Error getting CLIP details: {e}")
            return []
    
    def _clean_description(self, description):
        """Clean and format the description"""
        if not description:
            return None
            
        # Basic cleaning
        description = description.lower()
        
        # Remove redundant phrases
        redundant_phrases = [
            r'\bthe includes\b',
            r'\bthe image includes\b',
            r'\ban of\b',
            r'\ban image of\b',
            r'\ba picture of\b',
            r'\bthis is\b',
            r'\bwe can see\b',
            r'\bthere is\b',
            r'\bthere are\b'
        ]
        
        for phrase in redundant_phrases:
            description = re.sub(phrase, '', description)
        
        # Remove technical terms and metadata
        tech_patterns = [
            r'\b\d+(?:px|pixels|k|mp)?\b',  # Numbers with units
            r'\b(?:jpg|jpeg|png|gif|svg|eps|ai)\b',  # File extensions
            r'\b(?:image|photo|picture|icon|graphic|vector)\b',  # Media types
            r'\b(?:showing|displays|featuring|depicting)\b',  # Descriptive verbs
            r'\b(?:high|low|quality|resolution)\b',  # Quality terms
            r'\b(?:style|design|artwork|illustration)\b',  # Style terms
            r'\b(?:background|overlay|layer)\b',  # Technical terms
            r'\b(?:isolated|white|black)\s+(?:background|bg)\b',  # Background descriptions
            r'(?:on|with|against)\s+(?:white|black)\s+(?:background|bg)\b',
            r'\b(?:clip\s*art|stock\s*(?:image|photo|picture))\b',  # Stock terms
            r'\b(?:sticker|badge|label)\b'  # Common icon terms
        ]
        
        for pattern in tech_patterns:
            description = re.sub(pattern, '', description)
        
        # Remove special characters but keep periods and apostrophes
        description = re.sub(r'[^\w\s\'.]', ' ', description)
        
        # Clean up whitespace
        description = re.sub(r'\s+', ' ', description)
        description = description.strip()
        
        # Split into sentences and clean each one
        sentences = []
        for s in description.split('.'):
            s = s.strip()
            if s:
                # Remove redundant words at start of sentence
                s = re.sub(r'^\s*(?:and|also|additionally|moreover|furthermore)\s+', '', s)
                # Capitalize first letter
                s = s[0].upper() + s[1:] if s else ''
                sentences.append(s)
        
        # Join sentences and ensure proper punctuation
        if sentences:
            description = '. '.join(sentences)
            if not description.endswith('.'):
                description += '.'
                
            # Final cleanup of any double spaces or periods
            description = re.sub(r'\s+', ' ', description)
            description = re.sub(r'\.+', '.', description)
            description = description.strip()
        
        return description
    
    def generate_description(self, image_path, use_cache=True):
        """Generate description from image with caching"""
        # Check cache
        cache_path = get_cache_path(image_path, prefix="desc_", cache_dir=self.cache_dir)
        if use_cache:
            cached_data = load_from_cache(cache_path)
            if cached_data:
                logger.info(f"Using cached description for {os.path.basename(image_path)}")
                return cached_data["description"]
        
        try:
            # Load and validate image
            try:
                image = Image.open(image_path).convert('RGB')
            except Exception as img_error:
                logger.error(f"Error reading image {image_path}: {img_error}")
                return None
            
            logger.info(f"Generating description for {os.path.basename(image_path)}")
            
            # Generate main caption using BLIP
            main_caption = self._generate_blip_caption(image)
            if not main_caption:
                return None
            
            # Get additional details from CLIP
            clip_keywords = self._get_clip_details(image)
            
            # Combine and clean description
            if clip_keywords:
                # Use more natural language to incorporate keywords
                keyword_str = ', '.join(clip_keywords)
                if len(clip_keywords) == 1:
                    full_description = f"{main_caption} It features {keyword_str}."
                else:
                    full_description = f"{main_caption} It features elements like {keyword_str}."
            else:
                full_description = main_caption
            
            # Clean and validate final description
            description = self._clean_description(full_description)
            if not description or len(description.split()) < 5:
                logger.warning(f"Generated description too short for {image_path}")
                return None
            
            # Save to cache
            save_to_cache({"description": description}, cache_path)
            return description
            
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return None
    
    def __del__(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'ci'):
                del self.ci
            if hasattr(self, 'blip_model'):
                del self.blip_model
            torch.cuda.empty_cache()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}") 