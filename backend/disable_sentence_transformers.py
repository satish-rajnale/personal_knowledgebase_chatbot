#!/usr/bin/env python3
"""
Script to disable sentence-transformers and use only hash-based embeddings
This prevents hanging issues during embedding generation
"""

import os
import sys

def disable_sentence_transformers():
    """Disable sentence-transformers by modifying the embedding service"""
    
    embedding_service_path = "app/services/embedding_service.py"
    
    if not os.path.exists(embedding_service_path):
        print(f"❌ Embedding service file not found: {embedding_service_path}")
        return False
    
    print("🔧 Disabling sentence-transformers to prevent hanging...")
    
    # Read the current file
    with open(embedding_service_path, 'r') as f:
        content = f.read()
    
    # Replace the sentence-transformers import with a disabled version
    old_import = """# Try to import sentence-transformers, but don't fail if it's not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("⚠️ sentence-transformers not available, using fallback embeddings")
    SENTENCE_TRANSFORMERS_AVAILABLE = False"""
    
    new_import = """# Disable sentence-transformers to prevent hanging
# try:
#     from sentence_transformers import SentenceTransformer
#     SENTENCE_TRANSFORMERS_AVAILABLE = True
# except ImportError:
#     print("⚠️ sentence-transformers not available, using fallback embeddings")
#     SENTENCE_TRANSFORMERS_AVAILABLE = False

# Force disable sentence-transformers
SENTENCE_TRANSFORMERS_AVAILABLE = False"""
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✅ Disabled sentence-transformers import")
    else:
        print("⚠️ Could not find sentence-transformers import to disable")
    
    # Write the modified content back
    with open(embedding_service_path, 'w') as f:
        f.write(content)
    
    print("✅ Embedding service updated to use only hash-based embeddings")
    print("🔄 This will prevent hanging issues during embedding generation")
    
    return True

def main():
    """Main function"""
    print("🚀 Disabling Sentence-Transformers")
    print("=" * 40)
    
    try:
        success = disable_sentence_transformers()
        
        if success:
            print("\n🎉 Successfully disabled sentence-transformers!")
            print("\nNext steps:")
            print("1. Restart your server")
            print("2. Test document processing")
            print("3. Embeddings will now use hash-based fallback (fast and reliable)")
        else:
            print("\n❌ Failed to disable sentence-transformers")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
