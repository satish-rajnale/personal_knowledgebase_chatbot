#!/usr/bin/env python3
"""
Test script to verify PostgreSQL vector search functionality
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.postgres_vector_store import search_documents, init_vector_store

async def test_vector_search():
    """Test the vector search functionality"""
    print("🧪 Testing PostgreSQL vector search...")
    
    try:
        # Initialize vector store
        print("🔧 Initializing vector store...")
        await init_vector_store()
        print("✅ Vector store initialized")
        
        # Test search
        print("🔍 Testing vector search...")
        results = await search_documents(
            query="Python programming",
            top_k=5,
            filter={"user_id": "defc888f-b828-43b1-a718-d7d592276ebc"}
        )
        
        print(f"✅ Search completed successfully!")
        print(f"📊 Found {len(results)} results")
        
        for i, result in enumerate(results[:3]):  # Show first 3 results
            print(f"   Result {i+1}:")
            print(f"     Text: {result['text'][:100]}...")
            print(f"     Score: {result['score']:.4f}")
            print(f"     Source: {result['source_type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_vector_search())
    sys.exit(0 if success else 1)
