from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
from typing import List, Optional
import os
import uuid

from .base import Base

class User(Base):
    """Model for user accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=True)
    is_anonymous = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Notion Integration
    notion_token = Column(Text, nullable=True)
    notion_workspace_id = Column(String, nullable=True)
    notion_workspace_name = Column(String, nullable=True)
    
    # Google OAuth Integration (Legacy)
    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    google_token_expires_at = Column(DateTime, nullable=True)
    google_user_id = Column(String, nullable=True)
    google_user_email = Column(String, nullable=True)
    google_user_name = Column(String, nullable=True)
    
    # Firebase Integration
    firebase_uid = Column(String, nullable=True, index=True)
    firebase_email = Column(String, nullable=True)
    firebase_name = Column(String, nullable=True)
    firebase_photo_url = Column(String, nullable=True)
    
    # Usage tracking
    daily_query_count = Column(Integer, default=0)
    last_query_reset = Column(DateTime, default=datetime.utcnow)
    total_queries = Column(Integer, default=0)
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    notion_syncs = relationship("NotionSync", back_populates="user", cascade="all, delete-orphan")

class UsageLog(Base):
    """Model for tracking user usage"""
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    action = Column(String)  # "chat", "sync", "upload"
    details = Column(Text, nullable=True)  # JSON string with additional details
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="usage_logs")

class NotionSync(Base):
    """Model for tracking Notion sync operations"""
    __tablename__ = "notion_syncs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    page_id = Column(String)
    page_title = Column(String)
    status = Column(String)  # "success", "failed", "pending"
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="notion_syncs")

# Note: ChatSession and ChatMessage models are defined in chat.py
# Import them from there to avoid duplication

# Database setup
def get_database_url():
    from app.core.config import settings
    return settings.DATABASE_URL

engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def create_tables():
    # Ensure database directory exists
    db_url = get_database_url()
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        if db_path != ":memory:":
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
    
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 