# Production configuration for Flask app
import os
import secrets

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
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
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS in production
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
