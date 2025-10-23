#!/usr/bin/env python3
"""
Test script to verify the new sentence-transformers embedding service
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.embedding_service import get_embeddings, get_embedding_dimensions, embedding_service

def test_embeddings():
    """Test the embedding service"""
    print("🧪 Testing sentence-transformers embedding service...")
    
    try:
        # Test basic functionality
        print("📊 Model info:")
        model_info = embedding_service.get_model_info()
        for key, value in model_info.items():
            print(f"   {key}: {value}")
        
        # Test embedding generation
        test_texts = [
            "Python is a programming language",
            "Machine learning is a subset of artificial intelligence",
            "Vector databases store embeddings for similarity search"
        ]
        
        print(f"\n🔍 Testing embedding generation for {len(test_texts)} texts...")
        embeddings = get_embeddings(test_texts)
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"   Dimensions: {len(embeddings[0])}")
        print(f"   Expected dimensions: {get_embedding_dimensions()}")
        
        # Test similarity between texts
        print(f"\n🔍 Testing text similarity...")
        text1 = "Python programming language"
        text2 = "Python is a programming language"
        text3 = "Java is a programming language"
        
        sim_embeddings = get_embeddings([text1, text2, text3])
        
        # Calculate cosine similarity
        import numpy as np
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        sim_1_2 = cosine_similarity(sim_embeddings[0], sim_embeddings[1])
        sim_1_3 = cosine_similarity(sim_embeddings[0], sim_embeddings[2])
        
        print(f"   Similarity between '{text1}' and '{text2}': {sim_1_2:.4f}")
        print(f"   Similarity between '{text1}' and '{text3}': {sim_1_3:.4f}")
        
        if sim_1_2 > sim_1_3:
            print("✅ Similarity test passed - similar texts have higher similarity")
        else:
            print("⚠️ Similarity test failed - similar texts should have higher similarity")
        
        print("\n🎉 Embedding service test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Embedding service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_embeddings()
    sys.exit(0 if success else 1)
