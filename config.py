import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    WEBSITE_PASSWORD = os.getenv('WEBSITE_PASSWORD', 'hatch123')
    
    # Flask configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File storage paths
    STATIC_FOLDER = 'static'
    IMAGES_FOLDER = os.path.join(STATIC_FOLDER, 'images')
    AUDIO_FOLDER = os.path.join(STATIC_FOLDER, 'audio')
    
    # Ensure directories exist
    @staticmethod
    def init_app(app):
        os.makedirs(Config.IMAGES_FOLDER, exist_ok=True)
        os.makedirs(Config.AUDIO_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
