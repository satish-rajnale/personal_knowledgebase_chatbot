"""
Unified LangChain service for document processing, chunking, and embeddings
Replaces all custom implementations with battle-tested LangChain components
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# LangChain imports for version 1.0.2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Sentence transformers for direct embedding access
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class LangChainService:
    """
    Unified service for document processing using LangChain components
    Handles chunking, embeddings, and document preparation
    """
    
    def __init__(self):
        """Initialize LangChain components"""
        self.text_splitter = self._get_text_splitter()
        self.embedding_model = self._get_embedding_model()
        self.dimensions = 384  # all-MiniLM-L6-v2 dimensions
        
        logger.info("✅ LangChainService initialized")
        logger.info(f"   Text splitter: chunk_size={self.text_splitter._chunk_size}, overlap={self.text_splitter._chunk_overlap}")
        logger.info(f"   Embedding model: {self.embedding_model.model_name}")
        logger.info(f"   Embedding dimensions: {self.dimensions}")
    
    def _get_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Get optimized text splitter for semantic search"""
        return RecursiveCharacterTextSplitter(
            chunk_size=400,  # ~100 tokens, optimal for semantic search
            chunk_overlap=50,  # 12.5% overlap for context preservation
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence endings
                "! ",    # Exclamation sentences
                "? ",    # Question sentences
                "; ",    # Semicolon breaks
                ": ",    # Colon breaks
                " ",     # Word boundaries
                ""       # Character boundaries (fallback)
            ],
            length_function=len,
            is_separator_regex=False
        )
    
    def _get_embedding_model(self) -> HuggingFaceEmbeddings:
        """Get HuggingFace embedding model with optimal settings"""
        try:
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={
                    'normalize_embeddings': True,  # Normalize for cosine similarity
                    'batch_size': 32
                }
            )
        except Exception as e:
            logger.error(f"❌ Failed to load HuggingFace embeddings: {e}")
            # Fallback to direct sentence-transformers
            return self._get_fallback_embedding_model()
    
    def _get_fallback_embedding_model(self):
        """Fallback embedding model using sentence-transformers directly"""
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            class FallbackEmbeddings:
                def __init__(self, model):
                    self.model = model
                    self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
                
                def embed_documents(self, texts: List[str]) -> List[List[float]]:
                    """Embed multiple documents"""
                    embeddings = self.model.encode(
                        texts, 
                        normalize_embeddings=True,
                        batch_size=32
                    )
                    return embeddings.tolist()
                
                def embed_query(self, text: str) -> List[float]:
                    """Embed a single query"""
                    embedding = self.model.encode(
                        [text], 
                        normalize_embeddings=True
                    )
                    return embedding[0].tolist()
            
            return FallbackEmbeddings(model)
            
        except Exception as e:
            logger.error(f"❌ Fallback embedding model failed: {e}")
            raise RuntimeError("No embedding model available")
    
    async def process_documents(self, documents: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        """
        Process documents using LangChain components
        
        Args:
            documents: List of document dictionaries with 'page_content' and 'metadata'
            user_id: User ID for the documents
            
        Returns:
            List of processed chunks with embeddings and metadata
        """
        try:
            logger.info(f"🔧 Processing {len(documents)} documents for user {user_id}")
            
            all_chunks = []
            
            for doc_idx, doc in enumerate(documents):
                logger.info(f"📄 Processing document {doc_idx + 1}/{len(documents)}")
                logger.info(f"   Content length: {len(doc.get('page_content', ''))} characters")
                
                # Convert to LangChain Document format
                langchain_doc = Document(
                    page_content=doc.get('page_content', ''),
                    metadata=doc.get('metadata', {})
                )
                
                # Split document into chunks
                chunks = self.text_splitter.split_documents([langchain_doc])
                logger.info(f"   Created {len(chunks)} chunks")
                
                # Process each chunk
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_text = chunk.page_content
                    chunk_metadata = chunk.metadata.copy()
                    
                    # Add chunk-specific metadata
                    chunk_metadata.update({
                        'chunk_id': chunk_idx,
                        'chunk_index': chunk_idx,  # Add chunk_index as integer
                        'chunk_size': len(chunk_text),
                        'user_id': user_id,
                        'processed_at': datetime.utcnow().isoformat()
                    })
                    
                    # Generate embedding for chunk
                    try:
                        embedding = await self._get_embedding_async(chunk_text)
                        
                        chunk_data = {
                            'text': chunk_text,
                            'metadata': chunk_metadata,
                            'embedding': embedding,
                            'chunk_id': f"{chunk_metadata.get('page_id', 'unknown')}_{chunk_idx}"
                        }
                        
                        all_chunks.append(chunk_data)
                        
                        logger.debug(f"   Chunk {chunk_idx}: {len(chunk_text)} chars, embedding: {len(embedding)} dims")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to embed chunk {chunk_idx}: {e}")
                        continue
            
            logger.info(f"✅ Processed {len(all_chunks)} total chunks")
            return all_chunks
            
        except Exception as e:
            logger.error(f"❌ Error processing documents: {e}")
            raise
    
    async def _get_embedding_async(self, text: str) -> List[float]:
        """Get embedding for a single text asynchronously"""
        try:
            # Run embedding generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self.embedding_model.embed_query, 
                text
            )
            return embedding
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            # Return zero vector as fallback
            return [0.0] * self.dimensions
    
    async def get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for a search query"""
        try:
            return await self._get_embedding_async(query)
        except Exception as e:
            logger.error(f"❌ Query embedding failed: {e}")
            return [0.0] * self.dimensions
    
    def get_chunk_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed chunks"""
        if not chunks:
            return {}
        
        chunk_sizes = [len(chunk['text']) for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'avg_chunk_size': sum(chunk_sizes) / len(chunk_sizes),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes),
            'total_characters': sum(chunk_sizes)
        }

# Global instance
langchain_service = LangChainService()
