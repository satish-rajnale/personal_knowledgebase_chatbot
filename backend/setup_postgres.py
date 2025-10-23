#!/usr/bin/env python3
"""
Setup script for PostgreSQL with pgvector
This script helps set up PostgreSQL with the pgvector extension for vector storage.
"""

import os
import sys
import subprocess
from sqlalchemy import create_engine, text

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def check_postgres_connection():
    """Check if PostgreSQL is accessible"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"❌ Cannot connect to PostgreSQL: {e}")
        return False

def install_pgvector():
    """Install pgvector extension"""
    try:
        print("🔧 Installing pgvector extension...")
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Enable pgvector extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        print("✅ pgvector extension installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install pgvector: {e}")
        return False

def create_database_tables():
    """Create all database tables"""
    try:
        print("📋 Creating database tables...")
        from app.core.database import init_db
        import asyncio
        
        # Run the async init_db function
        asyncio.run(init_db())
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def test_vector_operations():
    """Test vector operations"""
    try:
        print("🧪 Testing vector operations...")
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Test vector operations
            result = conn.execute(text("""
                SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector as distance
            """))
            distance = result.fetchone()[0]
            print(f"✅ Vector operations working (test distance: {distance})")
        return True
    except Exception as e:
        print(f"❌ Vector operations test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 PostgreSQL + pgvector Setup Script")
    print("=" * 50)
    
    # Check PostgreSQL connection
    if not check_postgres_connection():
        print("\n❌ Setup failed: Cannot connect to PostgreSQL")
        print("Please ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. DATABASE_URL is correctly configured")
        print("3. Database exists and is accessible")
        return False
    
    # Install pgvector
    if not install_pgvector():
        print("\n❌ Setup failed: Cannot install pgvector")
        print("Please ensure:")
        print("1. pgvector extension is available in your PostgreSQL installation")
        print("2. You have sufficient privileges to create extensions")
        return False
    
    # Create tables
    if not create_database_tables():
        print("\n❌ Setup failed: Cannot create database tables")
        return False
    
    # Test vector operations
    if not test_vector_operations():
        print("\n❌ Setup failed: Vector operations not working")
        return False
    
    print("\n🎉 PostgreSQL + pgvector setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the migration script if you have existing data: python migrate_to_postgres.py")
    print("2. Start your application: python main.py")
    print("3. Test the vector search functionality")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
