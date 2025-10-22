#!/usr/bin/env python3
"""
Script to fix vector store issues by reinitializing with proper indexing
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.vector_store import vector_store
from app.core.config import settings

async def fix_vector_store():
    """Fix vector store by reinitializing with proper indexing"""
    
    print("🔧 Fixing Vector Store Issues")
    print("=" * 40)
    
    try:
        # Get current collection info
        print("📊 Current collection info:")
        try:
            collection_info = vector_store.client.get_collection(vector_store.collection_name)
            print(f"   Collection: {collection_info.name}")
            print(f"   Vectors: {collection_info.vectors_count}")
            print(f"   Points: {collection_info.points_count}")
        except Exception as e:
            print(f"   Error getting collection info: {e}")
        
        # Reinitialize collection with proper indexing
        print("\n🔄 Reinitializing collection with proper indexing...")
        await vector_store.init_collection()
        
        # Verify the index was created
        print("\n✅ Verification:")
        try:
            collection_info = vector_store.client.get_collection(vector_store.collection_name)
            print(f"   Collection: {collection_info.name}")
            print(f"   Vectors: {collection_info.vectors_count}")
            print(f"   Points: {collection_info.points_count}")
            
            # Try to create the index again (should succeed or show it already exists)
            try:
                vector_store.client.create_payload_index(
                    collection_name=vector_store.collection_name,
                    field_name="user_id",
                    field_schema="keyword"
                )
                print("   ✅ user_id index created successfully")
            except Exception as index_error:
                if "already exists" in str(index_error).lower():
                    print("   ℹ️ user_id index already exists")
                else:
                    print(f"   ⚠️ Index creation issue: {index_error}")
            
        except Exception as e:
            print(f"   ❌ Error verifying collection: {e}")
        
        print("\n🎉 Vector store fix completed!")
        print("\nNext steps:")
        print("1. Restart your backend server")
        print("2. Try syncing Notion pages again")
        print("3. Test the chat functionality")
        
    except Exception as e:
        print(f"❌ Error fixing vector store: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(fix_vector_store())
    if not success:
        sys.exit(1) 