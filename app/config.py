import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL', '')
    
    # ML Model Configuration
    MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models_store')
    MODEL_VERSION = '1.0.0'
    
    # Disease Detection Thresholds
    RISK_THRESHOLDS = {
        'diabetes': {'low': 0.3, 'medium': 0.5, 'high': 0.7},
        'hypertension': {'low': 0.3, 'medium': 0.5, 'high': 0.7},
        'liver_disease': {'low': 0.25, 'medium': 0.45, 'high': 0.65},
        'cardiac_risk': {'low': 0.35, 'medium': 0.55, 'high': 0.75},
        'mental_health': {'low': 0.3, 'medium': 0.5, 'high': 0.7}
    }
    
    # Feature Engineering Settings
    LAB_TREND_WINDOW = 6  # months
    ACTIVITY_AGGREGATION_DAYS = 30
    
    # Application Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'csv', 'json', 'pdf'}
    
    # CORS Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
