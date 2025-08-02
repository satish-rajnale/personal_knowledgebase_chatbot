from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid
from typing import List, Dict, Any
import json
import re
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
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
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # all-MiniLM-L6-v2 embedding size
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created Qdrant collection: {self.collection_name}")
            else:
                print(f"✅ Qdrant collection already exists: {self.collection_name}")
                
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
            embeddings = self.embedding_model.encode(texts)
            
            # Prepare points for Qdrant
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding.tolist(),
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
            query_embedding = self.embedding_model.encode([query])
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding[0].tolist(),
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