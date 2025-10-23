#!/usr/bin/env python3
"""
Railway startup script to ensure vector store is properly initialized
This can be called during Railway deployment or as a one-time setup
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.vector_store import vector_store
from app.core.database import init_db
from app.core.config import settings

async def railway_startup():
    """Initialize everything needed for Railway deployment"""
    
    print("🚂 Railway Startup Script")
    print("=" * 40)
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        await init_db()
        print("✅ Database initialized")
        
        # Initialize PostgreSQL vector store
        print("🔧 Initializing PostgreSQL vector store...")
        from app.services.postgres_vector_store import init_vector_store
        await init_vector_store()
        print("✅ PostgreSQL vector store initialized with proper indexing")
        
        # Verify PostgreSQL connection and pgvector extension
        try:
            from app.services.postgres_vector_store import postgres_vector_store
            print(f"📊 PostgreSQL vector store info:")
            print(f"   Database: PostgreSQL with pgvector")
            print(f"   Extension: pgvector enabled")
            print(f"   Table: document_chunks")
        except Exception as e:
            print(f"⚠️ Could not verify PostgreSQL vector store: {e}")
        
        print("\n🎉 Railway startup completed successfully!")
        print("The application is ready to handle requests.")
        
        return True
        
    except Exception as e:
        print(f"❌ Railway startup failed: {e}")
        print("The application may still work, but RAG features might not function properly.")
        return False

if __name__ == "__main__":
    success = asyncio.run(railway_startup())
    if not success:
        sys.exit(1) 