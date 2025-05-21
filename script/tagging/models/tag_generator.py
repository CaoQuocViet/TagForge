#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import string
from keybert import KeyBERT
from sklearn.feature_extraction.text import CountVectorizer

# Sửa import từ tương đối sang tuyệt đối
from models.utils import get_cache_path, save_to_cache, load_from_cache, setup_cache_dir

logger = logging.getLogger("tag_generator")

class TagGenerator:
    """Sinh tags từ mô tả sử dụng KeyBERT"""
    
    def __init__(self, model_name="all-MiniLM-L6-v2", device=None, cache_dir="data/cache"):
        self.cache_dir = setup_cache_dir(cache_dir)
        
        # Khởi tạo KeyBERT
        try:
            # Device có thể là "cpu" hoặc "cuda" hoặc None (tự phát hiện)
            self.kw_model = KeyBERT(model=model_name, device=device)
            logger.info(f"Đã khởi tạo KeyBERT với model {model_name}")
            
            # Danh sách stopwords
            self.stopwords = self._load_stopwords()
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo KeyBERT: {e}")
            raise
    
    def _load_stopwords(self):
        """Tải danh sách stopwords phổ biến"""
        # Danh sách stopwords tiếng Anh phổ biến
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
        """Làm sạch danh sách tags"""
        clean_tags = []
        
        for tag, score in tags_list:
            # Loại bỏ dấu câu đầu/cuối
            tag = tag.strip(string.punctuation)
            
            # Loại bỏ tag quá ngắn
            if len(tag) >= min_length:
                clean_tags.append((tag, score))
        
        return clean_tags
    
    def generate_tags(self, description, image_path=None, num_tags=25, use_cache=True):
        """Sinh ra tags từ mô tả với hỗ trợ cache"""
        # Tạo đường dẫn file cache nếu có image_path
        cache_path = None
        if image_path and use_cache:
            cache_path = get_cache_path(image_path, prefix="tags_", cache_dir=self.cache_dir)
            
            # Kiểm tra cache
            cached_data = load_from_cache(cache_path)
            if cached_data:
                logger.info(f"Sử dụng tags từ cache cho {os.path.basename(image_path)}")
                return cached_data["tags"]
        
        # Nếu không có cache hoặc không dùng cache, sinh tags mới
        try:
            logger.info(f"Đang sinh tags cho {'ảnh ' + os.path.basename(image_path) if image_path else 'mô tả'}")
            
            # Cấu hình CountVectorizer cho KeyBERT
            vectorizer = CountVectorizer(
                ngram_range=(1, 2),              # Cả từ đơn và cụm từ
                stop_words=self.stopwords,       # Loại bỏ stopwords
                min_df=1,                        # Tần suất tối thiểu
                lowercase=True                   # Chuyển về chữ thường
            )
            
            # Trích xuất từ khóa với đa dạng từ (MMR)
            keywords = self.kw_model.extract_keywords(
                description,
                keyphrase_ngram_range=(1, 2),
                stop_words=self.stopwords,
                use_mmr=True,                    # Sử dụng MMR để đa dạng hóa kết quả
                diversity=0.7,                   # Mức độ đa dạng (0-1)
                top_n=40,                        # Lấy nhiều hơn để có thể lọc
                vectorizer=vectorizer
            )
            
            # Làm sạch danh sách tags
            clean_keywords = self._clean_tags(keywords)
            
            # Lấy num_tags tags đầu tiên
            top_tags = [tag for tag, _ in clean_keywords[:num_tags]]
            
            # Lưu vào cache nếu có image_path
            if cache_path:
                save_to_cache({"tags": top_tags}, cache_path)
            
            return top_tags
        except Exception as e:
            logger.error(f"Lỗi khi sinh tags: {e}")
            return [] 