#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import string
from keybert import KeyBERT
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer

# Changed from relative to absolute import
from models.utils import get_cache_path, save_to_cache, load_from_cache, setup_cache_dir

logger = logging.getLogger("tag_generator")

class TagGenerator:
    """Generate tags from descriptions using KeyBERT"""
    
    def __init__(self, model_name="distilbert-base-nli-mean-tokens", device=None, cache_dir="data/cache"):
        self.cache_dir = setup_cache_dir(cache_dir)
        self.model_name = model_name
        
        # Initialize KeyBERT
        try:
            # Load the sentence transformer model first
            logger.info(f"Loading SentenceTransformer model {model_name}...")
            model = SentenceTransformer(model_name)
            
            # Move model to specified device
            if device == "cuda":
                model = model.to("cuda")
            
            # Initialize KeyBERT with the model
            self.kw_model = KeyBERT(model=model)
            logger.info(f"KeyBERT initialized successfully with model {model_name}")
            
            # Stopwords list
            self.stopwords = self._load_stopwords()
            
        except Exception as e:
            logger.error(f"Error initializing KeyBERT with model {model_name}: {e}")
            try:
                # Try fallback model
                fallback_model = "distilbert-base-nli-mean-tokens"
                logger.info(f"Trying fallback model: {fallback_model}")
                model = SentenceTransformer(fallback_model)
                if device == "cuda":
                    model = model.to("cuda")
                self.kw_model = KeyBERT(model=model)
                self.stopwords = self._load_stopwords()
                logger.info(f"Successfully initialized with fallback model {fallback_model}")
            except Exception as e2:
                logger.error(f"Fallback initialization also failed: {e2}")
                raise
    
    def _load_stopwords(self):
        """Load list of common stopwords"""
        # Common English stopwords
        common_stopwords = set([
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
            'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than', 'such',
            'when', 'where', 'how', 'why', 'while', 'with', 'without', 'of', 'at', 'by',
            'for', 'from', 'to', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'should', 'now',
            'showing', 'shown', 'shows', 'image', 'graphic', 'illustration', 'icon', 'icons', 
            'stylized', 'simple', 'vector', 'design', 'style', 'artwork'
        ])
        return common_stopwords
    
    def _clean_tags(self, tags_list, min_length=2):
        """Clean the list of tags"""
        clean_tags = []
        
        for tag, score in tags_list:
            # Skip if tag is None or empty
            if not tag:
                continue
                
            # Convert to string and clean
            tag = str(tag).strip().lower()
            
            # Remove punctuation at start/end
            tag = tag.strip(string.punctuation)
            
            # Skip if too short or in stopwords
            if len(tag) >= min_length and tag not in self.stopwords:
                clean_tags.append((tag, score))
        
        return clean_tags
    
    def generate_tags(self, description, image_path=None, num_tags=25, diversity=0.7, use_cache=True):
        """Generate tags from description with cache support"""
        if not description:
            logger.warning("Empty description provided")
            return []
            
        # Create cache file path if image_path is provided
        cache_path = None
        if image_path and use_cache:
            cache_path = get_cache_path(image_path, prefix="tags_", cache_dir=self.cache_dir)
            
            # Check cache
            cached_data = load_from_cache(cache_path)
            if cached_data:
                logger.info(f"Using cached tags for {os.path.basename(image_path)}")
                return cached_data["tags"]
        
        # If no cache or not using cache, generate new tags
        try:
            logger.info(f"Generating tags for {'image ' + os.path.basename(image_path) if image_path else 'description'}")
            
            # Configure CountVectorizer for KeyBERT
            vectorizer = CountVectorizer(
                ngram_range=(1, 2),              # Both single words and phrases
                stop_words=self.stopwords,       # Remove stopwords
                min_df=1,                        # Minimum frequency
                lowercase=True                   # Convert to lowercase
            )
            
            # Extract keywords with diversity (MMR)
            try:
                keywords = self.kw_model.extract_keywords(
                    description,
                    keyphrase_ngram_range=(1, 2),
                    stop_words=self.stopwords,
                    use_mmr=True,                    # Use MMR for diverse results
                    diversity=diversity,             # Diversity level (0-1)
                    top_n=40,                        # Get more for filtering
                    vectorizer=vectorizer
                )
            except Exception as kw_error:
                logger.error(f"Error extracting keywords: {kw_error}")
                return []
            
            # Clean the tags list
            clean_keywords = self._clean_tags(keywords)
            
            # Get top n tags
            top_tags = [tag for tag, _ in clean_keywords[:num_tags]]
            
            # Save to cache if image_path is provided
            if cache_path:
                save_to_cache({"tags": top_tags}, cache_path)
            
            return top_tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return [] 