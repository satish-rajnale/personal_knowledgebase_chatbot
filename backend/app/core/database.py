from app.models.chat import create_tables
from app.services.vector_store import init_vector_store
import asyncio

async def init_db():
    """Initialize both SQLite database and Qdrant vector store"""
    # Create SQLite tables
    create_tables()
    
    # Initialize Qdrant vector store
    await init_vector_store()
    
    print("✅ Database and vector store initialized successfully") 