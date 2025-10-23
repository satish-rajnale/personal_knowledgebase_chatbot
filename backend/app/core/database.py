# Import all models to ensure they are registered
from app.models import Base, User, UsageLog, NotionSync, ChatSession, ChatMessage, DocumentChunk
from app.models.user import create_tables as create_user_tables
from app.models.chat import create_tables as create_chat_tables
from app.models.vector import DocumentChunk
from app.services.postgres_vector_store import init_vector_store
import asyncio

async def init_db():
    """Initialize PostgreSQL database with pgvector"""
    # Create PostgreSQL tables for users, chat, and vectors
    create_user_tables()
    create_chat_tables()
    
    # Initialize PostgreSQL vector store (creates pgvector extension)
    await init_vector_store()
    
    print("✅ PostgreSQL database with pgvector initialized successfully") 