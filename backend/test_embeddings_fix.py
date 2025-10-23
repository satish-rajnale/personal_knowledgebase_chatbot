#!/usr/bin/env python3
"""
Test script to verify embedding service works without hanging
"""

import asyncio
import time
from app.services.embedding_service import get_embeddings, embedding_service

async def test_embeddings():
    """Test embedding generation with timeout"""
    print("🧪 Testing embedding service...")
    
    # Test texts
    texts = [
        "Machine learning is a subset of artificial intelligence",
        "Natural language processing helps computers understand human language",
        "Deep learning uses neural networks with multiple layers"
    ]
    
    print(f"📝 Testing with {len(texts)} texts...")
    
    try:
        # Test with timeout
        start_time = time.time()
        
        # Run in thread pool with timeout
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            embeddings = await asyncio.wait_for(
                loop.run_in_executor(executor, get_embeddings, texts),
                timeout=15.0  # 15 second timeout
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Embedding generation completed in {duration:.2f} seconds")
        print(f"   Generated {len(embeddings)} embeddings")
        print(f"   Embedding dimensions: {len(embeddings[0]) if embeddings else 0}")
        
        # Test individual embedding
        single_text = ["Test embedding generation"]
        single_embedding = get_embeddings(single_text)
        print(f"✅ Single embedding test passed: {len(single_embedding[0])} dimensions")
        
        return True
        
    except asyncio.TimeoutError:
        print("❌ Embedding generation timed out!")
        return False
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return False

async def test_model_availability():
    """Test if model is available and working"""
    print("🔍 Checking model availability...")
    
    if embedding_service.model_available:
        print("✅ Model is available")
        print(f"   Model: {embedding_service.model_name}")
        print(f"   Dimensions: {embedding_service.dimensions}")
    else:
        print("⚠️ Model is not available, using fallback")
    
    return embedding_service.model_available

async def main():
    """Main test function"""
    print("🚀 Embedding Service Test")
    print("=" * 40)
    
    # Test model availability
    model_available = await test_model_availability()
    print()
    
    # Test embedding generation
    success = await test_embeddings()
    print()
    
    if success:
        print("🎉 All tests passed! Embedding service is working correctly.")
    else:
        print("❌ Tests failed! There may be an issue with the embedding service.")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        exit(1)
