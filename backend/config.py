"""
Configuration management for AetherSegment AI
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    GOOGLE_CLOUD_REGION = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
    BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'aethersegment_cdp')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    
    # Gemini Model Configuration
    GEMINI_MODEL = 'gemini-2.5-flash'  # Gemini 2.5 Flash
    GEMINI_TEMPERATURE = 0.3
    GEMINI_MAX_OUTPUT_TOKENS = 8192  # Increased for chain-of-thought reasoning
    
    # Uplift Model Configuration
    UPLIFT_MODEL_TYPE = 'TLearner'  # Options: TLearner, XLearner, SLearner
    UPLIFT_BASE_ESTIMATOR = 'xgboost'
    
    # Segmentation Thresholds
    MIN_SEGMENT_SIZE = 100
    MAX_SEGMENT_SIZE = 50000
    DEFAULT_UPLIFT_THRESHOLD = 0.65
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GOOGLE_CLOUD_PROJECT:
            raise ValueError("GOOGLE_CLOUD_PROJECT is required")
        if not cls.GOOGLE_APPLICATION_CREDENTIALS:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is required")
        return True

