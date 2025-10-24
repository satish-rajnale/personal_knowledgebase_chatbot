#!/usr/bin/env python3
"""
Integration test for LangChain service
Verifies chunking quality, embedding generation, and search functionality
"""

import asyncio
import sys
import os
import json
from typing import List, Dict, Any

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.langchain_service import langchain_service
from app.services.postgres_vector_store import postgres_vector_store
from app.core.database import get_db

async def test_langchain_chunking():
    """Test LangChain chunking with a long document"""
    print("🧪 Testing LangChain chunking...")
    
    # Create a long test document (2000+ words)
    long_text = """
    Introduction to Machine Learning

    Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience. Unlike traditional programming, where explicit instructions are provided, machine learning systems learn patterns from data.

    Types of Machine Learning

    There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning.

    Supervised Learning

    Supervised learning involves training a model on labeled data, where the input features and corresponding output labels are known. The goal is to learn a mapping from inputs to outputs so that the model can make accurate predictions on new, unseen data.

    Common supervised learning algorithms include:
    - Linear regression for predicting continuous values
    - Logistic regression for binary classification
    - Decision trees for interpretable decision making
    - Random forests for ensemble learning
    - Support vector machines for high-dimensional data
    - Neural networks for complex pattern recognition

    Unsupervised Learning

    Unsupervised learning deals with finding hidden patterns in data without labeled examples. The algorithm must discover the underlying structure of the data on its own.

    Key unsupervised learning techniques include:
    - Clustering algorithms like K-means and hierarchical clustering
    - Dimensionality reduction techniques like PCA and t-SNE
    - Association rule learning for market basket analysis
    - Anomaly detection for identifying outliers

    Reinforcement Learning

    Reinforcement learning is concerned with how agents ought to take actions in an environment to maximize cumulative reward. The agent learns through trial and error, receiving feedback in the form of rewards or penalties.

    Applications of Machine Learning

    Machine learning has found applications across numerous domains:

    Healthcare: Medical diagnosis, drug discovery, personalized treatment plans
    Finance: Fraud detection, algorithmic trading, credit scoring
    Technology: Search engines, recommendation systems, autonomous vehicles
    Marketing: Customer segmentation, targeted advertising, churn prediction
    Manufacturing: Predictive maintenance, quality control, supply chain optimization

    Challenges in Machine Learning

    Despite its potential, machine learning faces several challenges:

    Data Quality: Poor quality data leads to poor model performance
    Overfitting: Models that memorize training data but fail to generalize
    Bias and Fairness: Ensuring models don't perpetuate societal biases
    Interpretability: Understanding how complex models make decisions
    Scalability: Handling large datasets and real-time predictions
    Privacy: Protecting sensitive information while enabling learning

    Best Practices

    To build successful machine learning systems, practitioners should:

    1. Start with clear problem definition and success metrics
    2. Collect and prepare high-quality data
    3. Choose appropriate algorithms for the task
    4. Validate models using proper evaluation techniques
    5. Monitor performance in production
    6. Continuously improve based on feedback

    Future of Machine Learning

    The field of machine learning continues to evolve rapidly. Emerging trends include:

    - Deep learning and neural network architectures
    - Automated machine learning (AutoML)
    - Federated learning for privacy-preserving training
    - Explainable AI for model interpretability
    - Edge computing for real-time inference
    - Quantum machine learning for quantum advantage

    Conclusion

    Machine learning represents a powerful paradigm shift in how we approach problem-solving with computers. By enabling systems to learn from data, we can tackle complex problems that would be difficult or impossible to solve with traditional programming approaches. As the field continues to mature, we can expect even more innovative applications and breakthroughs in the years to come.
    """
    
    # Create test document
    test_doc = {
        "page_content": long_text,
        "metadata": {
            "title": "Introduction to Machine Learning",
            "source": "Test Document",
            "page_id": "test_ml_guide",
            "source_type": "TEST"
        }
    }
    
    # Process with LangChain service
    processed_chunks = await langchain_service.process_documents([test_doc], "test_user")
    
    print(f"📊 Chunking Results:")
    print(f"   Original text length: {len(long_text)} characters")
    print(f"   Number of chunks created: {len(processed_chunks)}")
    
    if processed_chunks:
        chunk_sizes = [len(chunk['text']) for chunk in processed_chunks]
        print(f"   Average chunk size: {sum(chunk_sizes) / len(chunk_sizes):.0f} characters")
        print(f"   Min chunk size: {min(chunk_sizes)} characters")
        print(f"   Max chunk size: {max(chunk_sizes)} characters")
        
        # Verify chunk quality
        for i, chunk in enumerate(processed_chunks[:3]):  # Show first 3 chunks
            print(f"   Chunk {i+1}: {len(chunk['text'])} chars - {chunk['text'][:100]}...")
    
    # Verify embeddings
    if processed_chunks:
        embedding_dims = len(processed_chunks[0]['embedding'])
        print(f"   Embedding dimensions: {embedding_dims}")
        
        # Check if embeddings are semantic (not random)
        first_embedding = processed_chunks[0]['embedding']
        is_semantic = not all(abs(x) < 0.1 for x in first_embedding[:10])  # Not all near zero
        print(f"   Embeddings appear semantic: {is_semantic}")
    
    return len(processed_chunks) > 1  # Should create multiple chunks

async def test_embedding_quality():
    """Test embedding quality and consistency"""
    print("\n🧪 Testing embedding quality...")
    
    # Test similar texts should have similar embeddings
    text1 = "Machine learning is a subset of artificial intelligence"
    text2 = "ML is a branch of AI that focuses on learning from data"
    text3 = "The weather is sunny today and I love pizza"
    
    # Get embeddings
    embedding1 = await langchain_service.get_query_embedding(text1)
    embedding2 = await langchain_service.get_query_embedding(text2)
    embedding3 = await langchain_service.get_query_embedding(text3)
    
    # Calculate cosine similarity
    import numpy as np
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_1_2 = cosine_similarity(embedding1, embedding2)
    sim_1_3 = cosine_similarity(embedding1, embedding3)
    
    print(f"📊 Embedding Quality Results:")
    print(f"   Similar texts similarity: {sim_1_2:.3f}")
    print(f"   Different texts similarity: {sim_1_3:.3f}")
    print(f"   Similar texts more similar: {sim_1_2 > sim_1_3}")
    
    return sim_1_2 > sim_1_3

async def test_search_functionality():
    """Test search functionality with the processed chunks"""
    print("\n🧪 Testing search functionality...")
    
    try:
        # Test search with a query
        query = "What is supervised learning?"
        results = await postgres_vector_store.search(
            query=query,
            top_k=3,
            filter={"user_id": "test_user"}
        )
        
        print(f"📊 Search Results:")
        print(f"   Query: '{query}'")
        print(f"   Results found: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"   Result {i+1}: Score {result.get('score', 0.0):.3f}")
            print(f"     Text: {result['text'][:100]}...")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

async def test_chunk_size_limits():
    """Test that chunks are within optimal size limits"""
    print("\n🧪 Testing chunk size limits...")
    
    # Create a very long document
    very_long_text = "This is a test sentence. " * 200  # ~5000 characters
    
    test_doc = {
        "page_content": very_long_text,
        "metadata": {
            "title": "Very Long Test Document",
            "source": "Test Document",
            "page_id": "test_long_doc",
            "source_type": "TEST"
        }
    }
    
    processed_chunks = await langchain_service.process_documents([test_doc], "test_user")
    
    print(f"📊 Chunk Size Analysis:")
    print(f"   Original text: {len(very_long_text)} characters")
    print(f"   Chunks created: {len(processed_chunks)}")
    
    if processed_chunks:
        chunk_sizes = [len(chunk['text']) for chunk in processed_chunks]
        avg_size = sum(chunk_sizes) / len(chunk_sizes)
        max_size = max(chunk_sizes)
        
        print(f"   Average chunk size: {avg_size:.0f} characters")
        print(f"   Max chunk size: {max_size} characters")
        print(f"   Within 400 char limit: {max_size <= 400}")
        print(f"   Multiple chunks created: {len(processed_chunks) > 1}")
        
        return max_size <= 400 and len(processed_chunks) > 1
    
    return False

async def main():
    """Run all integration tests"""
    print("🚀 Starting LangChain Integration Tests")
    print("=" * 50)
    
    tests = [
        ("LangChain Chunking", test_langchain_chunking),
        ("Embedding Quality", test_embedding_quality),
        ("Search Functionality", test_search_functionality),
        ("Chunk Size Limits", test_chunk_size_limits)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        except Exception as e:
            print(f"❌ ERROR {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! LangChain integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())
