#!/usr/bin/env python3
"""
Migration script to migrate from SQLite + Qdrant to PostgreSQL + pgvector
This script helps migrate existing data from the old setup to the new PostgreSQL setup.
"""

import os
import sys
import json
import sqlite3
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models import Base, User, UsageLog, NotionSync, ChatSession, ChatMessage
from app.models.user import SessionLocal as UserSessionLocal
from app.models.chat import SessionLocal as ChatSessionLocal

def migrate_sqlite_to_postgres():
    """Migrate data from SQLite to PostgreSQL"""
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    
    # Check if SQLite database exists
    sqlite_path = "./chat_history.db"
    if not os.path.exists(sqlite_path):
        print("❌ SQLite database not found. Nothing to migrate.")
        return
    
    # Connect to SQLite database
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL database
    try:
        pg_engine = create_engine(settings.DATABASE_URL)
        pg_session = sessionmaker(bind=pg_engine)()
        
        # Create tables in PostgreSQL
        print("📋 Creating PostgreSQL tables...")
        Base.metadata.create_all(bind=pg_engine)
        
        # Migrate users table
        print("👥 Migrating users...")
        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()
        
        for user_row in users:
            # Map SQLite columns to PostgreSQL
            user_data = {
                'id': user_row[0],
                'user_id': user_row[1],
                'email': user_row[2],
                'is_anonymous': bool(user_row[3]),
                'created_at': user_row[4],
                'updated_at': user_row[5],
                'last_login': user_row[6],
                'notion_token': user_row[7],
                'notion_workspace_id': user_row[8],
                'notion_workspace_name': user_row[9],
                'google_access_token': user_row[10],
                'google_refresh_token': user_row[11],
                'google_token_expires_at': user_row[12],
                'google_user_id': user_row[13],
                'google_user_email': user_row[14],
                'google_user_name': user_row[15],
                'firebase_uid': user_row[16],
                'firebase_email': user_row[17],
                'firebase_name': user_row[18],
                'firebase_photo_url': user_row[19],
                'daily_query_count': user_row[20],
                'last_query_reset': user_row[21],
                'total_queries': user_row[22]
            }
            
            # Insert into PostgreSQL
            insert_query = text("""
                INSERT INTO users (id, user_id, email, is_anonymous, created_at, updated_at, last_login,
                                 notion_token, notion_workspace_id, notion_workspace_name,
                                 google_access_token, google_refresh_token, google_token_expires_at,
                                 google_user_id, google_user_email, google_user_name,
                                 firebase_uid, firebase_email, firebase_name, firebase_photo_url,
                                 daily_query_count, last_query_reset, total_queries)
                VALUES (:id, :user_id, :email, :is_anonymous, :created_at, :updated_at, :last_login,
                       :notion_token, :notion_workspace_id, :notion_workspace_name,
                       :google_access_token, :google_refresh_token, :google_token_expires_at,
                       :google_user_id, :google_user_email, :google_user_name,
                       :firebase_uid, :firebase_email, :firebase_name, :firebase_photo_url,
                       :daily_query_count, :last_query_reset, :total_queries)
                ON CONFLICT (id) DO NOTHING
            """)
            
            pg_session.execute(insert_query, user_data)
        
        # Migrate usage_logs table
        print("📊 Migrating usage logs...")
        sqlite_cursor.execute("SELECT * FROM usage_logs")
        usage_logs = sqlite_cursor.fetchall()
        
        for log_row in usage_logs:
            log_data = {
                'id': log_row[0],
                'user_id': log_row[1],
                'action': log_row[2],
                'details': log_row[3],
                'created_at': log_row[4]
            }
            
            insert_query = text("""
                INSERT INTO usage_logs (id, user_id, action, details, created_at)
                VALUES (:id, :user_id, :action, :details, :created_at)
                ON CONFLICT (id) DO NOTHING
            """)
            
            pg_session.execute(insert_query, log_data)
        
        # Migrate notion_syncs table
        print("🔗 Migrating Notion syncs...")
        sqlite_cursor.execute("SELECT * FROM notion_syncs")
        notion_syncs = sqlite_cursor.fetchall()
        
        for sync_row in notion_syncs:
            sync_data = {
                'id': sync_row[0],
                'user_id': sync_row[1],
                'page_id': sync_row[2],
                'page_title': sync_row[3],
                'status': sync_row[4],
                'error_message': sync_row[5],
                'created_at': sync_row[6]
            }
            
            insert_query = text("""
                INSERT INTO notion_syncs (id, user_id, page_id, page_title, status, error_message, created_at)
                VALUES (:id, :user_id, :page_id, :page_title, :status, :error_message, :created_at)
                ON CONFLICT (id) DO NOTHING
            """)
            
            pg_session.execute(insert_query, sync_data)
        
        # Migrate chat_sessions table
        print("💬 Migrating chat sessions...")
        sqlite_cursor.execute("SELECT * FROM chat_sessions")
        chat_sessions = sqlite_cursor.fetchall()
        
        for session_row in chat_sessions:
            session_data = {
                'id': session_row[0],
                'session_id': session_row[1],
                'user_id': session_row[2],
                'created_at': session_row[3],
                'updated_at': session_row[4]
            }
            
            insert_query = text("""
                INSERT INTO chat_sessions (id, session_id, user_id, created_at, updated_at)
                VALUES (:id, :session_id, :user_id, :created_at, :updated_at)
                ON CONFLICT (id) DO NOTHING
            """)
            
            pg_session.execute(insert_query, session_data)
        
        # Migrate chat_messages table
        print("💭 Migrating chat messages...")
        sqlite_cursor.execute("SELECT * FROM chat_messages")
        chat_messages = sqlite_cursor.fetchall()
        
        for message_row in chat_messages:
            message_data = {
                'id': message_row[0],
                'session_id': message_row[1],
                'role': message_row[2],
                'content': message_row[3],
                'sources': message_row[4],
                'created_at': message_row[5]
            }
            
            insert_query = text("""
                INSERT INTO chat_messages (id, session_id, role, content, sources, created_at)
                VALUES (:id, :session_id, :role, :content, :sources, :created_at)
                ON CONFLICT (id) DO NOTHING
            """)
            
            pg_session.execute(insert_query, message_data)
        
        # Commit all changes
        pg_session.commit()
        print("✅ Data migration completed successfully!")
        
        # Print migration summary
        print(f"📈 Migration Summary:")
        print(f"   Users: {len(users)}")
        print(f"   Usage logs: {len(usage_logs)}")
        print(f"   Notion syncs: {len(notion_syncs)}")
        print(f"   Chat sessions: {len(chat_sessions)}")
        print(f"   Chat messages: {len(chat_messages)}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        sqlite_conn.close()
        if 'pg_session' in locals():
            pg_session.close()

def migrate_qdrant_to_postgres():
    """Migrate vector data from Qdrant to PostgreSQL"""
    print("🔄 Starting vector data migration from Qdrant to PostgreSQL...")
    
    try:
        # This would require Qdrant client to export data
        # For now, we'll just note that vector data needs to be re-indexed
        print("⚠️  Note: Vector data from Qdrant cannot be automatically migrated.")
        print("   You'll need to re-sync your documents after the migration.")
        print("   This includes:")
        print("   - Re-uploading files")
        print("   - Re-syncing Notion pages")
        print("   - The new PostgreSQL setup will handle vector storage automatically.")
        
    except Exception as e:
        print(f"❌ Vector migration note: {e}")

def main():
    """Main migration function"""
    print("🚀 PostgreSQL Migration Script")
    print("=" * 50)
    
    # Check if PostgreSQL is accessible
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connection successful")
    except Exception as e:
        print(f"❌ Cannot connect to PostgreSQL: {e}")
        print("   Please ensure PostgreSQL is running and DATABASE_URL is correct")
        return
    
    # Migrate SQLite data
    migrate_sqlite_to_postgres()
    
    # Note about vector data
    migrate_qdrant_to_postgres()
    
    print("\n🎉 Migration completed!")
    print("Next steps:")
    print("1. Update your environment variables to use PostgreSQL")
    print("2. Re-sync your documents (files and Notion pages)")
    print("3. Test the application with the new setup")

if __name__ == "__main__":
    main()
