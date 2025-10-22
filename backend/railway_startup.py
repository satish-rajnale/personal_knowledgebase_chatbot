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
        
        # Initialize vector store with proper indexing
        print("🔧 Initializing vector store...")
        await vector_store.init_collection()
        print("✅ Vector store initialized with proper indexing")
        
        # Verify collection exists and has proper configuration
        try:
            collection_info = vector_store.client.get_collection(vector_store.collection_name)
            print(f"📊 Collection info:")
            print(f"   Name: {collection_info.name}")
            print(f"   Vectors: {collection_info.vectors_count}")
            print(f"   Points: {collection_info.points_count}")
        except Exception as e:
            print(f"⚠️ Could not verify collection: {e}")
        
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