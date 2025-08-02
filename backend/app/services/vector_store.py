from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
from typing import List, Dict, Any
import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from app.core.config import settings

class VectorStore:
    def __init__(self):
        print(f"🔧 VectorStore initialization:")
        print(f"   QDRANT_URL: {settings.QDRANT_URL}")
        print(f"   QDRANT_API_KEY: {'Set' if settings.QDRANT_API_KEY else 'Not set'}")
        print(f"   QDRANT_COLLECTION_NAME: {settings.QDRANT_COLLECTION_NAME}")
        
        # Initialize Qdrant client with API key if available
        if settings.QDRANT_API_KEY:
            print(f"🔗 Connecting to Qdrant Cloud: {settings.QDRANT_URL}")
            try:
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY.strip()  # Remove any whitespace
                )
                print(f"✅ Connected to Qdrant Cloud: {settings.QDRANT_URL}")
            except Exception as e:
                print(f"❌ Failed to connect to Qdrant Cloud: {e}")
                print(f"   URL: {settings.QDRANT_URL}")
                print(f"   API Key length: {len(settings.QDRANT_API_KEY) if settings.QDRANT_API_KEY else 0}")
                raise
        else:
            print(f"🔗 Connecting to local Qdrant: {settings.QDRANT_URL}")
            try:
                self.client = QdrantClient(settings.QDRANT_URL)
                print(f"✅ Connected to local Qdrant: {settings.QDRANT_URL}")
            except Exception as e:
                print(f"❌ Failed to connect to local Qdrant: {e}")
                raise
        
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        # Use TF-IDF for lightweight embeddings
        self.vectorizer = TfidfVectorizer(
            max_features=384,  # Match the expected vector size
            stop_words='english',
            ngram_range=(1, 3),  # Use 1-3 grams for better feature coverage
            min_df=1,  # Include all terms
            max_df=0.95,  # Exclude very common terms
            lowercase=True,
            strip_accents='unicode'
        )
        self.is_fitted = False
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using TF-IDF"""
        try:
            if not self.is_fitted:
                # Fit the vectorizer on the first batch
                vectors = self.vectorizer.fit_transform(texts).toarray()
                self.is_fitted = True
            else:
                # Transform new texts
                vectors = self.vectorizer.transform(texts).toarray()
            
            # Ensure vectors are 384-dimensional by padding with zeros
            padded_vectors = []
            for vector in vectors:
                if len(vector) < 384:
                    # Pad with zeros to reach 384 dimensions
                    padded_vector = np.pad(vector, (0, 384 - len(vector)), 'constant')
                elif len(vector) > 384:
                    # Truncate to 384 dimensions
                    padded_vector = vector[:384]
                else:
                    padded_vector = vector
                
                # Normalize vector to unit length for cosine similarity
                norm = np.linalg.norm(padded_vector)
                if norm > 0:
                    padded_vector = padded_vector / norm
                else:
                    # If vector is all zeros, use a small random vector
                    padded_vector = np.random.rand(384) * 0.01
                
                padded_vectors.append(padded_vector.tolist())
            
            return padded_vectors
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            # Fallback: return random vectors of correct dimension
            return [np.random.rand(384).tolist() for _ in texts]
    
    def _split_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Simple text splitting implementation"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(start + chunk_size - 100, start)
                search_end = min(end, len(text))
                
                # Find the last sentence ending
                sentence_endings = ['.', '!', '?', '\n\n']
                last_break = end
                
                for ending in sentence_endings:
                    pos = text.rfind(ending, search_start, search_end)
                    if pos > start and pos < end:
                        last_break = pos + len(ending)
                        break
                
                end = last_break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position, accounting for overlap
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def init_collection(self):
        """Initialize Qdrant collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection with proper configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # Size for TF-IDF vectors
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created Qdrant collection: {self.collection_name}")
            else:
                print(f"✅ Using existing Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            print(f"❌ Error initializing Qdrant collection: {e}")
            raise
    
    async def add_documents(self, documents: List[Dict], source_type: str = "upload"):
        """Add documents to vector store"""
        try:
            # Split documents into chunks
            chunks = []
            for doc in documents:
                text = doc.get("page_content", "")
                metadata = doc.get("metadata", {})
                
                # Split text into chunks
                text_chunks = self._split_text(text)
                
                for i, chunk_text in enumerate(text_chunks):
                    chunks.append({
                        "text": chunk_text,
                        "metadata": metadata,
                        "chunk_id": i
                    })
            
            if not chunks:
                return []
            
            # Generate embeddings
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self._get_embeddings(texts)
            
            # Prepare points for Qdrant
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        "metadata": chunk["metadata"],
                        "source_type": source_type,
                        "chunk_id": chunk["chunk_id"]
                    }
                )
                points.append(point)
            
            # Insert into Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            print(f"✅ Added {len(points)} chunks to vector store")
            return points
            
        except Exception as e:
            print(f"❌ Error adding documents to vector store: {e}")
            raise
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self._get_embeddings([query])[0]
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "text": result.payload["text"],
                    "metadata": result.payload["metadata"],
                    "source_type": result.payload["source_type"],
                    "score": result.score
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching vector store: {e}")
            return []

# Global vector store instance
vector_store = VectorStore()

async def init_vector_store():
    """Initialize vector store"""
    await vector_store.init_collection()

async def add_documents_to_store(documents: List[Dict], source_type: str = "upload"):
    """Add documents to vector store"""
    return await vector_store.add_documents(documents, source_type)

async def search_documents(query: str, top_k: int = 5):
    """Search documents in vector store"""
    return await vector_store.search(query, top_k) 