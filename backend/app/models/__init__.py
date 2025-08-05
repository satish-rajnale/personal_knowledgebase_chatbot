"""
Models initialization
Imports all models to ensure they are registered with SQLAlchemy
"""

# Import base first
from .base import Base

# Import all models to ensure they are registered
from .user import User, UsageLog, NotionSync
from .chat import ChatSession, ChatMessage

# Export all models
__all__ = [
    "Base",
    "User",
    "UsageLog", 
    "NotionSync",
    "ChatSession",
    "ChatMessage"
] 