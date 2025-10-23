#!/usr/bin/env python3
"""
Wait for PostgreSQL database to be ready
"""

import time
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def wait_for_database(max_retries=30, retry_delay=2):
    """
    Wait for PostgreSQL database to be ready
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    """
    database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@postgres:5432/knowledgebase')
    
    print(f"🔍 Waiting for PostgreSQL database to be ready...")
    print(f"   Database URL: {database_url}")
    
    for attempt in range(max_retries):
        try:
            print(f"   Attempt {attempt + 1}/{max_retries}...")
            
            # Create engine and test connection
            engine = create_engine(database_url, pool_pre_ping=True, pool_recycle=300)
            with engine.connect() as conn:
                # Test basic connection
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                
                # Test pgvector extension
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                
                # Commit the extension creation
                conn.commit()
                
            print("✅ Database is ready!")
            return True
            
        except OperationalError as e:
            print(f"   ⏳ Database not ready yet: {e}")
            if attempt < max_retries - 1:
                print(f"   🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Database connection failed after {max_retries} attempts")
                return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    return False

if __name__ == "__main__":
    if wait_for_database():
        print("🚀 Database is ready, starting application...")
        sys.exit(0)
    else:
        print("💥 Database connection failed, exiting...")
        sys.exit(1)
