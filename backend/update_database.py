#!/usr/bin/env python3
"""
Database Update Script
Updates the database schema to include user_id in chat_sessions table.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def update_database():
    """Update database schema"""
    
    # Add the backend directory to the path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.core.config import settings
    from app.models.chat import Base as ChatBase
    from app.models.user import Base as UserBase
    
    # Create engine
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
    
    print("🔧 Updating database schema...")
    
    try:
        # Check if user_id column exists in chat_sessions
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(chat_sessions)"))
            columns = [row[1] for row in result.fetchall()]
            
            if "user_id" not in columns:
                print("📝 Adding user_id column to chat_sessions table...")
                conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN user_id VARCHAR"))
                conn.commit()
                print("✅ user_id column added successfully!")
            else:
                print("✅ user_id column already exists!")
        
        # Create any missing tables
        print("📝 Creating missing tables...")
        UserBase.metadata.create_all(bind=engine)
        ChatBase.metadata.create_all(bind=engine)
        print("✅ Database schema updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = update_database()
    if success:
        print("\n🎉 Database update completed successfully!")
    else:
        print("\n❌ Database update failed!")
        sys.exit(1) 