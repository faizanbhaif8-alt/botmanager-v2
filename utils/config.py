"""
Configuration management for Bot Manager V2
Handles environment variables and API keys
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # GitHub Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', '')
    
    # AI API Keys (OpenRouter as primary, DeepSeek as fallback)
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    
    # ElevenLabs Configuration
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
    
    # API Endpoints
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
    
    # Model Configuration
    PRIMARY_MODEL = "deepseek/deepseek-chat"
    FALLBACK_MODEL = "anthropic/claude-3.5-sonnet"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        if not cls.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN is not set")
        if not cls.GITHUB_USERNAME:
            errors.append("GITHUB_USERNAME is not set")
        if not cls.OPENROUTER_API_KEY and not cls.DEEPSEEK_API_KEY:
            errors.append("No AI API keys configured")
        return errors