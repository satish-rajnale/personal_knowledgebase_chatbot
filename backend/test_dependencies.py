#!/usr/bin/env python3
"""
Test script to verify all dependencies can be imported correctly.
Run this to check if there are any import issues before building.
"""

def test_imports():
    """Test importing all required packages"""
    try:
        print("Testing imports...")
        
        # Core FastAPI
        import fastapi
        print("✅ FastAPI imported successfully")
        
        # LangChain
        import langchain
        print("✅ LangChain imported successfully")
        
        import langchain_community
        print("✅ LangChain Community imported successfully")
        
        import langchain_openai
        print("✅ LangChain OpenAI imported successfully")
        
        import langchain_text_splitters
        print("✅ LangChain Text Splitters imported successfully")
        
        import langchain_core
        print("✅ LangChain Core imported successfully")
        
        # Vector Database
        import qdrant_client
        print("✅ Qdrant Client imported successfully")
        
        # Embeddings
        import sentence_transformers
        print("✅ Sentence Transformers imported successfully")
        
        # Document Processing
        import pypdf
        print("✅ PyPDF imported successfully")
        
        import markdown
        print("✅ Markdown imported successfully")
        
        # Notion
        import notion_client
        print("✅ Notion Client imported successfully")
        
        # HTTP Client
        import httpx
        print("✅ HTTPX imported successfully")
        
        # Async File Operations
        import aiofiles
        print("✅ AIOFiles imported successfully")
        
        # Database
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
        
        print("\n🎉 All dependencies imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1) 