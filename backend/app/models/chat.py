from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import List, Optional
import os

from .base import Base

class ChatSession(Base):
    """Model for chat sessions"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True)  # Link to user
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """Model for individual chat messages"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    sources = Column(Text, nullable=True)  # JSON string of source documents
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")

# Database setup
def get_database_url():
    from app.core.config import settings
    return settings.DATABASE_URL

engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def create_tables():
    # For PostgreSQL, we don't need to create directories
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 