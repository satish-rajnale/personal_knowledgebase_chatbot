from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # LLM Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_PROVIDER: str = "openrouter"  # "openrouter" or "ollama"
    MODEL_NAME: str = "openai/gpt-3.5-turbo"
    
    # Notion Integration
    NOTION_TOKEN: Optional[str] = None
    NOTION_DATABASE_ID: Optional[str] = None
    
    # Vector Database
    QDRANT_URL: str = "https://6f837ae8-48dc-4769-8c49-deaf34a88382.europe-west3-0.gcp.cloud.qdrant.io"
    QDRANT_API_KEY: Optional[str] = None  # Set this via environment variable
    QDRANT_COLLECTION_NAME: str = "knowledgebase"
    
    # App Configuration
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000"
    API_HOST: str = "0.0.0.0"  # Bind to all interfaces for Railway
    API_PORT: int = int(os.environ.get("PORT", 8000))  # Use Railway's PORT or default to 8000
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "/app/uploads"
    
    # Database
    DATABASE_URL: str = "sqlite:////app/data/chat_history.db"
    
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