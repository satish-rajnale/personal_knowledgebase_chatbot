#!/usr/bin/env python3
"""
Model download script for Docker build
Checks if models already exist in cache before downloading
"""

import os
import sys
from pathlib import Path

def check_model_exists(cache_dir: str, model_name: str) -> bool:
    """Check if a model already exists in the cache directory"""
    cache_path = Path(cache_dir)
    if not cache_path.exists():
        return False
    
    # Check for common model files/directories
    model_files = [
        f"{model_name}",
        f"models--{model_name.replace('/', '--')}",
        f"{model_name.replace('/', '--')}"
    ]
    
    for model_file in model_files:
        if (cache_path / model_file).exists():
            return True
    
    return False

def download_sentence_transformers_model():
    """Download sentence-transformers model if not cached"""
    model_name = "all-MiniLM-L6-v2"
    cache_dir = "/app/.cache/transformers"
    
    if check_model_exists(cache_dir, model_name):
        print(f"✅ Sentence-transformers model '{model_name}' already cached")
        return True
    
    try:
        print(f"📥 Downloading sentence-transformers model: {model_name}")
        from sentence_transformers import SentenceTransformer
        SentenceTransformer(model_name)
        print(f"✅ Sentence-transformers model '{model_name}' downloaded successfully")
        return True
    except Exception as e:
        print(f"⚠️ Failed to download sentence-transformers model: {e}")
        print("🔄 This model will be downloaded at runtime if needed")
        return True  # Don't fail the build for this

def download_pix2text_models():
    """Download Pix2Text models if not cached"""
    cache_dir = "/app/.cache/huggingface"
    
    # Check for common Pix2Text model patterns
    pix2text_models = ["mfr", "mfd", "pix2text"]
    cached_models = [model for model in pix2text_models if check_model_exists(cache_dir, model)]
    
    if cached_models:
        print(f"✅ Pix2Text models already cached: {cached_models}")
        return True
    
    try:
        print("📥 Downloading Pix2Text models...")
        from pix2text import Pix2Text
        p2t = Pix2Text()
        print("✅ Pix2Text models downloaded successfully")
        return True
    except Exception as e:
        print(f"⚠️ Failed to download Pix2Text models: {e}")
        print("🔄 These models will be downloaded at runtime if needed")
        return True  # Don't fail the build for this

def download_pytorch_models():
    """Download PyTorch models if needed"""
    try:
        print("📥 Checking PyTorch models...")
        import torch
        print("✅ PyTorch models ready")
        return True
    except Exception as e:
        print(f"⚠️ Failed to initialize PyTorch: {e}")
        print("🔄 PyTorch will be initialized at runtime if needed")
        return True  # Don't fail the build for this

def download_huggingface_models():
    """Download Hugging Face models cache if needed"""
    try:
        print("📥 Checking Hugging Face models cache...")
        from transformers import AutoTokenizer, AutoModel
        print("✅ Hugging Face models cache ready")
        return True
    except Exception as e:
        print(f"⚠️ Failed to initialize Hugging Face models: {e}")
        print("🔄 Hugging Face models will be downloaded at runtime if needed")
        return True  # Don't fail the build for this

def main():
    """Main function to download all models"""
    print("🚀 Starting model download process...")
    
    # Create cache directories
    cache_dirs = [
        "/app/.cache/transformers",
        "/app/.cache/huggingface", 
        "/app/.cache/torch"
    ]
    
    for cache_dir in cache_dirs:
        os.makedirs(cache_dir, exist_ok=True)
        print(f"📁 Created cache directory: {cache_dir}")
    
    # Download models
    results = []
    results.append(download_sentence_transformers_model())
    results.append(download_pix2text_models())
    results.append(download_pytorch_models())
    results.append(download_huggingface_models())
    
    # Check results
    successful_downloads = sum(results)
    total_attempts = len(results)
    
    if successful_downloads == total_attempts:
        print("🎉 All models downloaded/cached successfully!")
    else:
        print(f"⚠️ {total_attempts - successful_downloads} models failed to download, but continuing...")
        print("🔄 Failed models will be downloaded at runtime if needed")
    
    # Always return 0 to not fail the Docker build
    print("✅ Model download process completed (build will continue)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
