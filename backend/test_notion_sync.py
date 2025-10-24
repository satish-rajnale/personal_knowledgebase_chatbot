#!/usr/bin/env python3
"""
Debug script for testing Notion sync functionality
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.notion_service import NotionService
from app.services.postgres_vector_store import postgres_vector_store
from app.core.config import settings

async def test_notion_sync():
    """Test Notion sync functionality with debugging"""
    print("🔍 Starting Notion sync debug test...")
    
    try:
        # Initialize vector store
        print("🔧 Initializing vector store...")
        await postgres_vector_store.init_vector_store()
        print("✅ Vector store initialized")
        
        # Test with a dummy Notion service (you'll need to provide real tokens)
        print("🔧 Testing Notion service...")
        
        # You can set your Notion token here for testing
        notion_token = os.getenv("NOTION_TOKEN", "your_notion_token_here")
        
        if notion_token == "your_notion_token_here":
            print("⚠️ Please set NOTION_TOKEN environment variable for real testing")
            print("🔄 Testing with mock data...")
            
            # Test with mock data
            mock_documents = [
                {
                    "page_content": "This is a test document for debugging.",
                    "metadata": {
                        "page_id": "test-page-123",
                        "title": "Test Page",
                        "url": "https://notion.so/test-page-123",
                        "source_type": "NOTION"
                    }
                }
            ]
            
            print(f"🔍 Testing with {len(mock_documents)} mock documents...")
            result = await postgres_vector_store.add_documents(
                mock_documents, 
                source_type="NOTION", 
                user_id="debug-user-123"
            )
            print(f"✅ Mock sync completed: {len(result)} chunks added")
            
        else:
            # Test with real Notion service
            notion_service = NotionService(user_token=notion_token)
            
            print("🔍 Getting user pages...")
            pages = await notion_service.get_user_pages()
            print(f"✅ Found {len(pages)} pages")
            
            if pages:
                # Test syncing first page
                page_ids = [pages[0]["id"]]
                print(f"🔍 Syncing page: {page_ids[0]}")
                
                documents = await notion_service.sync_user_pages(page_ids)
                print(f"✅ Synced {len(documents)} documents")
                
                if documents:
                    result = await postgres_vector_store.add_documents(
                        documents, 
                        source_type="NOTION", 
                        user_id="debug-user-123"
                    )
                    print(f"✅ Real sync completed: {len(result)} chunks added")
        
        print("🎉 Notion sync debug test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during Notion sync test: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(test_notion_sync())
