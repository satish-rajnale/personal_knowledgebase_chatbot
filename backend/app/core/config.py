from pydantic_settings import BaseSettings
from typing import Optional
import os

def get_port() -> int:
    """Safely get port from environment variable"""
    try:
        port_str = os.environ.get("PORT", "8000")
        return int(port_str)
    except (ValueError, TypeError):
        print(f"⚠️  Invalid PORT value '{port_str}', using default 8000")
        return 8000

class Settings(BaseSettings):
    # LLM Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_PROVIDER: str = "openrouter"  # "openrouter" or "ollama"
    MODEL_NAME: str = "openai/gpt-3.5-turbo"
    
    # Notion Integration (OAuth only - no global integration)
    NOTION_CLIENT_ID: Optional[str] = None
    NOTION_CLIENT_SECRET: Optional[str] = None
    NOTION_REDIRECT_URI: str = "http://localhost:3000/auth/notion/callback"
    
    # Vector Database
    QDRANT_URL: str = "https://6f837ae8-48dc-4769-8c49-deaf34a88382.europe-west3-0.gcp.cloud.qdrant.io"
    QDRANT_API_KEY: Optional[str] = None  # Set this via environment variable
    QDRANT_COLLECTION_NAME: str = "knowledgebase"
    
    # App Configuration
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000"
    API_HOST: str = "0.0.0.0"  # Bind to all interfaces for Railway
    API_PORT: int = get_port()  # Use Railway's PORT or default to 8000
    
    # Authentication
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    DAILY_QUERY_LIMIT: int = 10  # Daily query limit per user
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # Database
    DATABASE_URL: str = "sqlite:///./chat_history.db"
    
    # Email Configuration (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    ADMIN_EMAIL: str = "admin@yourdomain.com"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    
    # Monitoring
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Debug: Print configuration (without sensitive data)
print(f"🔧 Configuration loaded:")
print(f"   API_HOST: {settings.API_HOST}")
print(f"   API_PORT: {settings.API_PORT}")
print(f"   QDRANT_URL: {settings.QDRANT_URL}")
print(f"   QDRANT_API_KEY: {'Set' if settings.QDRANT_API_KEY else 'Not set'}")
print(f"   QDRANT_COLLECTION_NAME: {settings.QDRANT_COLLECTION_NAME}")

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True) 