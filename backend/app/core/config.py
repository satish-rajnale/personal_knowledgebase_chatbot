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
    # Notion only accepts HTTPS URLs; set via environment in deployed environments
    NOTION_REDIRECT_URI: Optional[str] = None
    # This is where we redirect after successful OAuth (back to mobile app)
    NOTION_MOBILE_REDIRECT_URI: Optional[str] = None
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: Optional[str] = None  # Set via environment
    FIREBASE_API_KEY: Optional[str] = None  # Set via environment
    FIREBASE_PRIVATE_KEY: Optional[str] = None  # Firebase private key for server-side operations
    
    # Google OAuth Configuration (Legacy - will be removed)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    GOOGLE_MOBILE_REDIRECT_URI: Optional[str] = None
    
    # Vector Database
    QDRANT_URL: str = "http://qdrant:6333"  # Local Qdrant instance
    QDRANT_API_KEY: Optional[str] = None  # Not needed for local instance
    QDRANT_COLLECTION_NAME: str = "knowledgebase"
    
    # App Configuration
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000,exp://localhost:19000"
    API_HOST: str = "0.0.0.0"  # Bind to all interfaces for Railway
    API_PORT: int = get_port()  # Use Railway's PORT or default to 8000
    
    # Authentication
    JWT_SECRET: str = "change-me-in-env"
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