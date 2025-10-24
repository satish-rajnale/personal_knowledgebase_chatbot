"""
Embedding service using sentence-transformers for high-quality embeddings
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        """Initialize the embedding service with a pre-trained model"""
        print("🔧 Initializing EmbeddingService...")
        
        # Use all-MiniLM-L6-v2 - a lightweight but effective model
        # 384 dimensions, good for general text similarity
        self.model_name = "all-MiniLM-L6-v2"
        self.dimensions = 384
        
        try:
            print(f"📥 Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(f"✅ Model loaded successfully")
            print(f"   Model: {self.model_name}")
            print(f"   Dimensions: {self.dimensions}")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using sentence-transformers
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each as a list of floats)
        """
        try:
            if not texts:
                return []
            
            print(f"🔍 EmbeddingService: Processing {len(texts)} texts...")
            print(f"🔍 EmbeddingService: Model type: {type(self.model)}")
            
            # Use sentence-transformers model directly
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,  # Normalize for cosine similarity
                batch_size=32,
                show_progress_bar=False
            )
            
            # Convert to list of lists
            embeddings_list = embeddings.tolist()
            
            print(f"✅ Generated {len(embeddings_list)} embeddings with {len(embeddings_list[0])} dimensions")
            return embeddings_list
            
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}")
    
    def get_embedding_dimensions(self) -> int:
        """Get the number of dimensions for embeddings"""
        return self.dimensions
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        return {
            "model_name": self.model_name,
            "dimensions": self.dimensions,
            "max_sequence_length": self.model.max_seq_length,
            "model_type": "sentence-transformers"
        }

# Global embedding service instance
embedding_service = EmbeddingService()

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Convenience function to get embeddings"""
    return embedding_service.get_embeddings(texts)

def get_embedding_dimensions() -> int:
    """Get embedding dimensions"""
    return embedding_service.get_embedding_dimensions()
