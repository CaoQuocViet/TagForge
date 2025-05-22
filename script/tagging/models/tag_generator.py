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
        # Common English stopwords plus domain-specific terms
        return [
            # Basic English stopwords
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
            'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than', 'such',
            'when', 'where', 'how', 'why', 'while', 'with', 'without', 'of', 'at', 'by',
            'for', 'from', 'to', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'should', 'now',
            
            # Domain-specific stopwords
            'showing', 'shown', 'shows', 'image', 'graphic', 'illustration', 'icon', 'icons',
            'stylized', 'simple', 'vector', 'design', 'style', 'artwork', 'background',
            'close', 'up', 'black', 'white', 'dark', 'light', 'color', 'colored',
            'resolution', 'pixel', 'pixels', 'px', 'full', 'frame', 'shot', 'view',
            'seen', 'looking', 'appears', 'showing', 'featuring', 'depicts', 'depicting',
            'contains', 'containing', 'consists', 'consisting', 'represents', 'representing',
            'photo', 'photograph', 'picture', 'pic', 'img', 'jpeg', 'jpg', 'png', 'svg',
            'file', 'files', 'format', 'formats', 'size', 'sizes', 'dimension', 'dimensions',
            'overlay', 'overlays', 'overlay', 'overlaying', 'overlaid',
            'isolated', 'against', 'background', 'bg', 'clipart', 'stock',
            'single', 'multiple', 'various', 'different', 'several', 'many',
            'set', 'collection', 'group', 'pack', 'bundle',
            'new', 'old', 'modern', 'contemporary', 'traditional',
            'high', 'low', 'quality', 'detailed', 'simple', 'complex',
            'made', 'created', 'designed', 'drawn', 'illustrated',
            'using', 'used', 'usage', 'utilize', 'utilized',
            'like', 'similar', 'type', 'kind', 'sort',
            'part', 'piece', 'element', 'component',
            'version', 'variant', 'variation', 'alternative',
            
            # Numbers and measurements
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
            'x', 'px', 'pixel', 'pixels', 'resolution'
        ]
    
    def _clean_tags(self, tags_list, min_length=2):
        """Clean the list of tags"""
        clean_tags = []
        seen_words = set()  # Track unique words
        
        for tag, score in tags_list:
            # Skip if tag is None or empty
            if not tag:
                continue
                
            # Convert to string and clean
            tag = str(tag).strip().lower()
            
            # Remove punctuation at start/end and within
            tag = tag.translate(str.maketrans('', '', string.punctuation))
            
            # Remove any non-ASCII characters
            tag = ''.join(c for c in tag if ord(c) < 128)
            
            # Skip if too short, in stopwords, or already seen
            if (len(tag) >= min_length and 
                tag not in self.stopwords and 
                tag not in seen_words and 
                tag.isalpha()):
                clean_tags.append((tag, score))
                seen_words.add(tag)
        
        return clean_tags
    
    def generate_tags(self, description, image_path=None, num_tags=25, diversity=0.7, use_cache=True):
        """Generate tags from description with cache support"""
        if not description:
            logger.warning("Empty description provided")
            return []
            
        # Clean description
        description = ' '.join(word for word in description.split() 
                             if word.isalpha() and len(word) > 1 
                             and not any(char in word for char in '0123456789'))
        
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
                stop_words=self.stopwords,       # Use our custom stopwords
                min_df=0.0,                      # Allow terms that appear in any document
                max_df=1.0,                      # Allow terms that appear in all documents
                lowercase=True,                  # Convert to lowercase
                max_features=None               # No limit on vocabulary size
            )
            
            # Extract keywords with diversity (MMR)
            try:
                # First pass: get single words with high diversity
                keywords_single = self.kw_model.extract_keywords(
                    description,
                    keyphrase_ngram_range=(1, 1),    # Single words only
                    stop_words=self.stopwords,
                    use_mmr=True,                    # Use MMR for diverse results
                    diversity=0.7,                   # Moderate diversity for single words
                    top_n=30,                        # Get more for filtering
                    vectorizer=vectorizer
                )
                
                # Second pass: get phrases with lower diversity
                keywords_phrases = self.kw_model.extract_keywords(
                    description,
                    keyphrase_ngram_range=(2, 2),    # Two-word phrases only
                    stop_words=self.stopwords,
                    use_mmr=True,                    # Use MMR for diverse results
                    diversity=0.5,                   # Lower diversity for phrases
                    top_n=10,                        # Fewer phrases
                    vectorizer=vectorizer
                )
                
                # Combine and clean
                keywords = keywords_single + keywords_phrases
                
            except Exception as kw_error:
                logger.error(f"Error extracting keywords: {kw_error}")
                return []
            
            # Clean the tags list
            clean_keywords = self._clean_tags(keywords)
            
            # Get top n tags, ensuring we have enough
            top_tags = []
            seen = set()
            
            # First add single-word tags
            for tag, _ in clean_keywords:
                if len(tag.split()) == 1 and tag not in seen:
                    top_tags.append(tag)
                    seen.add(tag)
                if len(top_tags) >= num_tags * 0.7:  # 70% single words
                    break
            
            # Then add phrases
            for tag, _ in clean_keywords:
                if len(tag.split()) > 1 and tag not in seen:
                    top_tags.append(tag)
                    seen.add(tag)
                if len(top_tags) >= num_tags:
                    break
            
            # Save to cache if image_path is provided
            if cache_path:
                save_to_cache({"tags": top_tags}, cache_path)
            
            return top_tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return [] 