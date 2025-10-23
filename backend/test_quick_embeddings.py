#!/usr/bin/env python3
"""
Quick test for embedding service without hanging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_embeddings():
    """Test embedding generation quickly"""
    print("🧪 Quick Embedding Test")
    print("=" * 30)
    
    try:
        from app.services.embedding_service import get_embeddings
        
        # Test with simple text
        texts = ["This is a test document for embedding generation"]
        
        print(f"📝 Testing with: {texts[0]}")
        print("🔍 Generating embeddings...")
        
        # This should be fast now (hash-based)
        embeddings = get_embeddings(texts)
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"   Dimensions: {len(embeddings[0]) if embeddings else 0}")
        print(f"   First few values: {embeddings[0][:5] if embeddings else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_embeddings()
    if success:
        print("\n🎉 Embedding service is working!")
        print("🔄 Server should no longer hang during embedding generation")
    else:
        print("\n❌ Embedding service test failed")
        sys.exit(1)
