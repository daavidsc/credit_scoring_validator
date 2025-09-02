# Production configuration for Flask app
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # Flask settings
    DEBUG = False
    TESTING = False
    
    # Gunicorn settings
    PORT = int(os.environ.get('PORT', 8000))
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Report settings
    REPORTS_DIR = 'reports/generated'
    ARCHIVE_DIR = 'reports/archive'
    DATA_DIR = 'data'
    RESULTS_DIR = 'results/responses'
