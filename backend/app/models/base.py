"""
Shared Base class for all SQLAlchemy models
"""

from sqlalchemy.ext.declarative import declarative_base

# Create a shared Base class that all models will use
Base = declarative_base() 