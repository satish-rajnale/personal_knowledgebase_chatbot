#!/usr/bin/env python3
"""
Debug script to test the search functionality
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.postgres_vector_store import search_documents

async def debug_search():
    """Debug the search functionality"""
    print("🔍 Debugging search functionality...")
    
    try:
        # Test 1: Check if there are any documents in the database
        print("\n1. Checking database contents...")
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Check total document count
            result = conn.execute(text("SELECT COUNT(*) FROM document_chunks"))
            total_count = result.fetchone()[0]
            print(f"   Total documents in database: {total_count}")
            
            # Check by source type
            result = conn.execute(text("SELECT source_type, COUNT(*) FROM document_chunks GROUP BY source_type"))
            source_counts = result.fetchall()
            print(f"   Documents by source type: {dict(source_counts)}")
            
            # Check by user_id
            result = conn.execute(text("SELECT user_id, COUNT(*) FROM document_chunks GROUP BY user_id"))
            user_counts = result.fetchall()
            print(f"   Documents by user: {dict(user_counts)}")
            
            # Check if embeddings are NULL
            result = conn.execute(text("SELECT COUNT(*) FROM document_chunks WHERE embedding_vector IS NULL"))
            null_embeddings = result.fetchone()[0]
            print(f"   Documents with NULL embeddings: {null_embeddings}")
            
            # Show sample documents
            result = conn.execute(text("""
                SELECT id, source_type, user_id, LEFT(text, 100) as text_preview, 
                       source_id, source_url, chunk_size
                FROM document_chunks 
                ORDER BY created_at DESC 
                LIMIT 5
            """))
            sample_docs = result.fetchall()
            print(f"\n   Sample documents:")
            for doc in sample_docs:
                print(f"     ID: {doc[0]}, Type: {doc[1]}, User: {doc[2]}")
                print(f"     Text: {doc[3]}...")
                print(f"     Source ID: {doc[4]}, URL: {doc[5]}")
                print(f"     Size: {doc[6]}")
                print()
        
        # Test 2: Try searching with different queries
        print("\n2. Testing search functionality...")
        
        # Get a user_id from the database
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DISTINCT user_id FROM document_chunks LIMIT 1"))
            user_row = result.fetchone()
            if user_row:
                test_user_id = user_row[0]
                print(f"   Testing with user_id: {test_user_id}")
                
                # Test search with user filter
                print("   Testing search with user filter...")
                try:
                    results = await search_documents(
                        query="test",
                        top_k=10,
                        filter={"user_id": test_user_id}
                    )
                    print(f"   Found {len(results)} documents")
                    for i, result in enumerate(results[:3]):
                        print(f"     Result {i+1}: {result.get('text', '')[:100]}...")
                        print(f"       Score: {result.get('score', 0):.3f}")
                        print(f"       Source: {result.get('metadata', {}).get('source', 'Unknown')}")
                except Exception as e:
                    print(f"   Search failed: {e}")
                
                # Test search without filter
                print("   Testing search without filter...")
                try:
                    results = await search_documents(
                        query="test",
                        top_k=10
                    )
                    print(f"   Found {len(results)} documents")
                except Exception as e:
                    print(f"   Search failed: {e}")
            else:
                print("   No users found in database")
        
        # Test 3: Check embedding generation
        print("\n3. Testing embedding generation...")
        try:
            from app.services.embedding_service import EmbeddingService
            embedding_service = EmbeddingService()
            
            test_text = "This is a test document for debugging."
            embeddings = await embedding_service.get_embeddings([test_text])
            print(f"   Generated embedding for test text: {len(embeddings[0])} dimensions")
            print(f"   First 5 values: {embeddings[0][:5]}")
        except Exception as e:
            print(f"   Embedding generation failed: {e}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_search())
