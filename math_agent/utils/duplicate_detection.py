from .similarity_utils import SIMILARITY_THRESHOLD
from django.core.cache import cache
import hashlib
import re
import logging

logger = logging.getLogger(__name__)

class EnhancedSimilarityChecker:
    def __init__(self):
        self.similarity_threshold = SIMILARITY_THRESHOLD
        self.cache_timeout = 30 * 24 * 3600  # 30 days
        
    def create_problem_fingerprint(self, question, subject, topic):
        """Create a fingerprint for exact duplicate detection"""
        # Normalize the text
        normalized = self.normalize_text(question)
        fingerprint_input = f"{subject}|{topic}|{normalized}"
        return hashlib.md5(fingerprint_input.encode()).hexdigest()
    
    def normalize_text(self, text):
        """Normalize text for better comparison"""
        if not text:
            return ""
        
        # Convert to lowercase
        normalized = text.lower()
        
        # Replace numbers with placeholder
        normalized = re.sub(r'-?\d+\.?\d*', '[NUM]', normalized)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def is_exact_duplicate(self, question, subject, topic):
        """Check if this is an exact duplicate using cache"""
        fingerprint = self.create_problem_fingerprint(question, subject, topic)
        cache_key = f"exact_duplicate_{fingerprint}"
        
        if cache.get(cache_key):
            return True, fingerprint
        
        return False, fingerprint
    
    def cache_problem(self, question, subject, topic):
        """Cache problem to prevent future exact duplicates"""
        _, fingerprint = self.is_exact_duplicate(question, subject, topic)
        cache_key = f"exact_duplicate_{fingerprint}"
        cache.set(cache_key, True, self.cache_timeout)
    
    def enhanced_similarity_check(self, question, subject, topic, embedding, existing_similar_problems):
        """Enhanced similarity check that works with your existing system"""
        
        # 1. Check for exact duplicates first (fastest)
        is_exact, fingerprint = self.is_exact_duplicate(question, subject, topic)
        if is_exact:
            return True, "exact_duplicate", 1.0, {}
        
        # 2. If your existing system found similar problems, analyze them
        if existing_similar_problems:
            max_similarity = max(existing_similar_problems.values())
            
            # Check if any similarity is above a stricter threshold for rejection
            if max_similarity > 0.9:  # Very high similarity
                return True, "very_similar", max_similarity, existing_similar_problems
            elif max_similarity > 0.8:  # High similarity
                logger.warning(f"High similarity detected: {max_similarity:.3f}")
                return False, "high_similarity", max_similarity, existing_similar_problems
        
        # 3. Cache this problem for future checks
        self.cache_problem(question, subject, topic)
        
        return False, "unique", 0.0, existing_similar_problems or {}