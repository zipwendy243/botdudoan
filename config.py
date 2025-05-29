"""
Configuration file for Nova88 Telegram Bot deployment
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Environment variables configuration
class Config:
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://username:password@localhost/nova88_bot'
    
    # Telegram Bot configuration
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
    
    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'your-secret-key-here'
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Server configuration
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_ENV') == 'development'