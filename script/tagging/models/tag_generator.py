#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import string
from keybert import KeyBERT
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import wordnet
from gensim.models import KeyedVectors
from gensim.models.word2vec import Word2Vec
import numpy as np
from collections import defaultdict

# Changed from relative to absolute import
from models.utils import get_cache_path, save_to_cache, load_from_cache, setup_cache_dir

logger = logging.getLogger("tag_generator")

class TagGenerator:
    """Generate tags from descriptions using KeyBERT with automatic synonym expansion"""
    
    def __init__(self, model_name="distilbert-base-nli-mean-tokens", device=None, cache_dir="data/cache"):
        self.cache_dir = setup_cache_dir(cache_dir)
        self.model_name = model_name
        
        # Initialize NLP components
        try:
            # Download required NLTK data
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            
            # Load pre-trained word vectors (will download if not present)
            try:
                self.word_vectors = KeyedVectors.load_word2vec_format(
                    'models/GoogleNews-vectors-negative300.bin.gz', 
                    binary=True
                )
            except Exception as e:
                logger.warning(f"Could not load pre-trained word vectors: {e}")
                self.word_vectors = None
            
            logger.info("Initialized NLP components successfully")
            
        except Exception as e:
            logger.error(f"Error initializing NLP components: {e}")
            raise
        
        # Initialize KeyBERT
        try:
            # Load the sentence transformer model
            logger.info(f"Loading SentenceTransformer model {model_name}...")
            model = SentenceTransformer(model_name)
            
            if device == "cuda":
                model = model.to("cuda")
            
            self.kw_model = KeyBERT(model=model)
            logger.info(f"KeyBERT initialized successfully with model {model_name}")
            
            # Stopwords list
            self.stopwords = self._load_stopwords()
            
        except Exception as e:
            logger.error(f"Error initializing KeyBERT: {e}")
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
    
    def _get_wordnet_synonyms(self, word):
        """Get synonyms and related words from WordNet"""
        related_words = set()
        
        # Get all synsets for the word
        for synset in wordnet.synsets(word):
            # Add lemma names (synonyms)
            for lemma in synset.lemmas():
                synonym = lemma.name().replace('_', ' ')
                if synonym != word and len(synonym) > 2:
                    related_words.add(synonym)
            
            # Add hypernyms (more general terms)
            for hypernym in synset.hypernyms():
                for lemma in hypernym.lemmas():
                    word = lemma.name().replace('_', ' ')
                    if len(word) > 2:
                        related_words.add(word)
            
            # Add hyponyms (more specific terms)
            for hyponym in synset.hyponyms():
                for lemma in hyponym.lemmas():
                    word = lemma.name().replace('_', ' ')
                    if len(word) > 2:
                        related_words.add(word)
        
        return list(related_words)

    def _get_similar_words(self, word, threshold=0.5):
        """Get similar words using word vectors"""
        similar_words = []
        
        if self.word_vectors and word in self.word_vectors:
            try:
                # Find similar words using word vectors
                similar = self.word_vectors.most_similar(word, topn=10)
                for similar_word, score in similar:
                    if score >= threshold and len(similar_word) > 2:
                        similar_words.append(similar_word)
            except Exception as e:
                logger.warning(f"Error getting similar words for '{word}': {e}")
        
        return similar_words

    def _get_related_words(self, word, max_words=10):
        """Get related words using multiple NLP techniques"""
        related = set()
        
        # Clean the word
        word = word.lower().strip()
        if not word or word in self.stopwords:
            return []
            
        # 1. Get WordNet synonyms and related words
        wordnet_related = self._get_wordnet_synonyms(word)
        related.update(wordnet_related[:5])  # Add up to 5 WordNet related words
        
        # 2. Get similar words using word vectors
        vector_similar = self._get_similar_words(word)
        related.update(vector_similar[:5])  # Add up to 5 vector-based similar words
        
        # 3. Get compound variations if word is compound
        parts = word.split()
        if len(parts) > 1:
            for part in parts:
                part_related = self._get_wordnet_synonyms(part)[:2]
                related.update(part_related)
        
        # Filter out stopwords and short words
        related = {w for w in related if w not in self.stopwords and len(w) > 2}
        
        return list(related)[:max_words]

    def _expand_keywords(self, keywords, target_count=25):
        """Expand keywords using NLP-based related words"""
        expanded = set(keywords)
        
        # First pass: Add direct related words
        for word in keywords:
            related = self._get_related_words(word, max_words=5)
            expanded.update(related)
        
        # Second pass: Add secondary related words if needed
        if len(expanded) < target_count:
            secondary_related = set()
            for word in expanded.copy():
                related = self._get_related_words(word, max_words=3)
                secondary_related.update(related)
            expanded.update(secondary_related)
        
        # Third pass: Add tertiary related words if still needed
        if len(expanded) < target_count:
            tertiary_related = set()
            for word in list(expanded)[:5]:  # Only use top 5 words
                if self.word_vectors and word in self.word_vectors:
                    try:
                        similar = self.word_vectors.most_similar(word, topn=3)
                        tertiary_related.update(w for w, _ in similar)
                    except Exception as e:
                        logger.warning(f"Error in word vector expansion for '{word}': {e}")
            expanded.update(tertiary_related)
        
        # Filter and sort by relevance
        result = list(expanded)
        if len(result) > target_count:
            # If we have word vectors, sort by similarity to original keywords
            if self.word_vectors:
                def get_max_similarity(word):
                    if word not in self.word_vectors:
                        return 0
                    return max(self.word_vectors.similarity(word, k) 
                             for k in keywords if k in self.word_vectors)
                
                result.sort(key=lambda x: get_max_similarity(x) if x in self.word_vectors else 0, 
                          reverse=True)
            result = result[:target_count]
        
        return result

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
                    top_n=15,                        # Get more for filtering
                    vectorizer=vectorizer
                )
                
                # Second pass: get phrases with lower diversity
                keywords_phrases = self.kw_model.extract_keywords(
                    description,
                    keyphrase_ngram_range=(2, 2),    # Two-word phrases only
                    stop_words=self.stopwords,
                    use_mmr=True,                    # Use MMR for diverse results
                    diversity=0.5,                   # Lower diversity for phrases
                    top_n=5,                         # Fewer phrases
                    vectorizer=vectorizer
                )
                
                # Add title-based keywords if available
                title_keywords = []
                if image_path:
                    title = os.path.splitext(os.path.basename(image_path))[0]
                    title_parts = title.split('-')
                    if len(title_parts) > 1:
                        title_text = ' '.join(title_parts[1:])  # Skip the number prefix
                        title_keywords = self.kw_model.extract_keywords(
                            title_text,
                            keyphrase_ngram_range=(1, 2),
                            stop_words=self.stopwords,
                            use_mmr=True,
                            diversity=0.7,
                            top_n=5,
                            vectorizer=vectorizer
                        )
                
                # Combine all keywords
                all_keywords = keywords_single + keywords_phrases + title_keywords
                
                # Clean and deduplicate
                clean_keywords = self._clean_tags(all_keywords)
                
                # Get initial tags
                initial_tags = []
                seen = set()
                
                # First add title-based tags
                for tag, score in clean_keywords:
                    if any(title_part in tag for title_part in title_parts[1:]):
                        if tag not in seen:
                            initial_tags.append(tag)
                            seen.add(tag)
                
                # Then add single-word tags
                for tag, score in clean_keywords:
                    if len(tag.split()) == 1 and tag not in seen:
                        initial_tags.append(tag)
                        seen.add(tag)
                    if len(initial_tags) >= 10:  # Get first 10 single words
                        break
                
                # Then add phrases
                for tag, score in clean_keywords:
                    if len(tag.split()) > 1 and tag not in seen:
                        initial_tags.append(tag)
                        seen.add(tag)
                    if len(initial_tags) >= 12:  # Add 2 more phrases
                        break
                
                # Add common category tags based on title/content
                category_tags = {
                    'speech': ['communication', 'message', 'chat', 'talk', 'conversation', 'dialogue'],
                    'message': ['communication', 'chat', 'text', 'conversation', 'dialogue', 'social'],
                    'bubble': ['speech', 'chat', 'talk', 'communication', 'message', 'dialogue'],
                    'balloon': ['speech', 'message', 'communication', 'chat', 'talk', 'dialogue']
                }
                
                for category, related_tags in category_tags.items():
                    if category in ' '.join(initial_tags).lower():
                        for tag in related_tags:
                            if tag not in seen and len(initial_tags) < num_tags:
                                initial_tags.append(tag)
                                seen.add(tag)
                
                # Expand tags using NLP
                if len(initial_tags) < num_tags:
                    expanded_tags = self._expand_keywords(initial_tags, num_tags)
                    final_tags = expanded_tags
                else:
                    final_tags = initial_tags[:num_tags]
                
                # Save to cache if image_path is provided
                if cache_path:
                    save_to_cache({"tags": final_tags}, cache_path)
                
                return final_tags
                
            except Exception as kw_error:
                logger.error(f"Error extracting keywords: {kw_error}")
                return []
            
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return [] 