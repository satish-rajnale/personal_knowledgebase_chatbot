#!/usr/bin/env python3
"""
Simple model download script for Docker build
Only downloads the most critical models
"""

import os
import sys

def main():
    """Main function to download critical models only"""
    print("🚀 Starting simple model download process...")
    
    # Create cache directories
    cache_dirs = [
        "/app/.cache/transformers",
        "/app/.cache/huggingface", 
        "/app/.cache/torch"
    ]
    
    for cache_dir in cache_dirs:
        os.makedirs(cache_dir, exist_ok=True)
        print(f"📁 Created cache directory: {cache_dir}")
    
    # Only download the most critical model (sentence-transformers)
    try:
        print("📥 Downloading sentence-transformers model...")
        from sentence_transformers import SentenceTransformer
        SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence-transformers model downloaded successfully")
    except Exception as e:
        print(f"⚠️ Failed to download sentence-transformers model: {e}")
        print("🔄 This model will be downloaded at runtime if needed")
    
    print("✅ Model download process completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
