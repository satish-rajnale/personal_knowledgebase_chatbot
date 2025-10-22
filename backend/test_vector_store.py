#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.vector_store import vector_store

async def test_vector_store():
    """Test vector store functionality"""
    print("🔍 Testing Vector Store...")
    
    try:
        # Get collection info
        collection_info = vector_store.client.get_collection(vector_store.collection_name)
        print(f"✅ Collection: {collection_info.name}")
        print(f"   Points count: {collection_info.points_count}")
        print(f"   Vectors count: {collection_info.vectors_count}")
        
        # Try to search for all documents (no filter)
        print("\n🔍 Searching for all documents...")
        try:
            results = vector_store.client.search(
                collection_name=vector_store.collection_name,
                query_vector=[0.0] * 384,  # Dummy vector
                limit=10,
                with_payload=True
            )
            
            print(f"✅ Found {len(results)} documents")
            
            for i, result in enumerate(results[:5]):  # Show first 5
                payload = result.payload
                print(f"  📄 Doc {i+1}:")
                print(f"     ID: {result.id}")
                print(f"     Score: {result.score:.3f}")
                print(f"     User ID: {payload.get('user_id', 'None')}")
                print(f"     Source: {payload.get('metadata', {}).get('source', 'Unknown')}")
                print(f"     Source Type: {payload.get('source_type', 'Unknown')}")
                print(f"     Text preview: {payload.get('text', '')[:100]}...")
                print()
                
        except Exception as e:
            print(f"❌ Error searching: {e}")
            
        # Try to search with a specific user filter
        print("\n🔍 Searching for specific user...")
        test_user_id = "4c5ea73e-0e3a-414f-8d14-d36f4c5aa4a4"  # From our test
        
        try:
            results = vector_store.client.search(
                collection_name=vector_store.collection_name,
                query_vector=[0.0] * 384,  # Dummy vector
                limit=10,
                query_filter={
                    "must": [
                        {
                            "key": "user_id",
                            "match": {"value": test_user_id}
                        }
                    ]
                },
                with_payload=True
            )
            
            print(f"✅ Found {len(results)} documents for user {test_user_id}")
            
            for i, result in enumerate(results[:3]):  # Show first 3
                payload = result.payload
                print(f"  📄 Doc {i+1}:")
                print(f"     Score: {result.score:.3f}")
                print(f"     Source: {payload.get('metadata', {}).get('source', 'Unknown')}")
                print(f"     Text preview: {payload.get('text', '')[:100]}...")
                print()
                
        except Exception as e:
            print(f"❌ Error searching with user filter: {e}")
            
    except Exception as e:
        print(f"❌ Error testing vector store: {e}")

if __name__ == "__main__":
    asyncio.run(test_vector_store())
