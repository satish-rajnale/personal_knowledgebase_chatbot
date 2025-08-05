# Import all models to ensure they are registered
from app.models import Base, User, UsageLog, NotionSync, ChatSession, ChatMessage
from app.models.user import create_tables as create_user_tables
from app.models.chat import create_tables as create_chat_tables
from app.services.vector_store import init_vector_store
import asyncio

async def init_db():
    """Initialize both SQLite database and Qdrant vector store"""
    # Create SQLite tables for users and chat
    create_user_tables()
    create_chat_tables()
    
    # Initialize Qdrant vector store
    await init_vector_store()
    
    print("✅ Database and vector store initialized successfully") 