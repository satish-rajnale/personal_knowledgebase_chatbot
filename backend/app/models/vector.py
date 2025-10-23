from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Optional
import uuid

from .base import Base

class DocumentChunk(Base):
    """Model for document chunks with vector embeddings"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    
    # Document content
    text = Column(Text, nullable=False)
    document_metadata = Column(Text, nullable=True)  # JSON string of metadata
    
    # Source information
    source_type = Column(String, nullable=False)  # "upload", "notion", etc.
    source_id = Column(String, nullable=True)  # Original document/page ID
    source_url = Column(String, nullable=True)  # URL to original document
    
    # Vector embedding (384 dimensions for sentence-transformers)
    embedding = Column(String, nullable=False)  # JSON string of embedding
    embedding_vector = Column(String, nullable=True)  # Will be converted to vector column in DB
    
    # Chunk information
    chunk_index = Column(Integer, default=0)  # Order within document
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="document_chunks")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_source', 'user_id', 'source_type'),
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_source_id', 'source_id'),
    )

# Add relationship to User model
# This will be added to the User model in user.py
