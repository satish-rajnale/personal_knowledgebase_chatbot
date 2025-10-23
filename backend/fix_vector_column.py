#!/usr/bin/env python3
"""
Fix the vector column in PostgreSQL for existing data
"""

import sys
import os
from sqlalchemy import create_engine, text

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def fix_vector_column():
    """Fix the vector column for existing data"""
    print("🔧 Fixing PostgreSQL vector column...")
    
    try:
        # Connect to PostgreSQL
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Enable pgvector extension
            print("📋 Enabling pgvector extension...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("✅ pgvector extension enabled")
            
            # Add vector column if it doesn't exist
            print("📋 Adding vector column...")
            try:
                conn.execute(text("ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS embedding_vector vector(384)"))
                conn.commit()
                print("✅ Vector column added")
            except Exception as e:
                print(f"⚠️ Vector column may already exist: {e}")
            
            # Populate vector column for existing data
            print("📋 Populating vector column for existing data...")
            try:
                result = conn.execute(text("""
                    UPDATE document_chunks 
                    SET embedding_vector = embedding::vector 
                    WHERE embedding_vector IS NULL 
                    AND embedding IS NOT NULL
                """))
                conn.commit()
                print(f"✅ Updated {result.rowcount} rows with vector data")
            except Exception as e:
                print(f"❌ Failed to populate vector column: {e}")
                return False
            
            # Create index for vector operations
            print("📋 Creating vector index...")
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_embedding_vector ON document_chunks USING ivfflat (embedding_vector vector_cosine_ops)"))
                conn.commit()
                print("✅ Vector index created")
            except Exception as e:
                print(f"⚠️ Vector index may already exist: {e}")
            
            # Test vector operations
            print("🧪 Testing vector operations...")
            try:
                test_result = conn.execute(text("SELECT '[1,2,3]'::vector <=> '[1,2,4]'::vector as distance"))
                distance = test_result.fetchone()[0]
                print(f"✅ Vector operations working (test distance: {distance})")
            except Exception as e:
                print(f"❌ Vector operations test failed: {e}")
                return False
            
            print("🎉 Vector column fix completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Failed to fix vector column: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_vector_column()
    sys.exit(0 if success else 1)
