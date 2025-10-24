#!/usr/bin/env python3
"""
Fix database constraints for ON CONFLICT to work
This script adds the missing unique constraint on chunk_id
"""

import os
import sys
import psycopg2
from psycopg2 import sql

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def fix_chunk_id_constraint():
    """Add unique constraint on chunk_id column"""
    print("🔧 Fixing chunk_id unique constraint...")
    
    try:
        # Parse database URL
        db_url = settings.DATABASE_URL
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgres://')
        
        # Connect to database
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check if constraint already exists
        cur.execute("""
            SELECT 1 FROM information_schema.table_constraints 
            WHERE table_name = 'document_chunks' 
            AND constraint_name = 'document_chunks_chunk_id_key'
            AND constraint_type = 'UNIQUE'
        """)
        
        if cur.fetchone():
            print("✅ Unique constraint on chunk_id already exists")
        else:
            # Add the unique constraint
            cur.execute("""
                ALTER TABLE document_chunks 
                ADD CONSTRAINT document_chunks_chunk_id_key UNIQUE (chunk_id)
            """)
            print("✅ Added unique constraint on chunk_id")
        
        # Verify the constraint
        cur.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'document_chunks' 
            AND constraint_type = 'UNIQUE'
        """)
        
        constraints = cur.fetchall()
        print(f"📋 Unique constraints on document_chunks:")
        for constraint in constraints:
            print(f"   {constraint[0]}: {constraint[1]}")
        
        # Commit changes
        conn.commit()
        print("🎉 Database constraints fixed successfully!")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix database constraints: {e}")
        return False

def check_database_schema():
    """Check the current database schema"""
    print("🔍 Checking database schema...")
    
    try:
        # Parse database URL
        db_url = settings.DATABASE_URL
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgres://')
        
        # Connect to database
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check table structure
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'document_chunks'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print(f"📋 document_chunks table structure:")
        for col in columns:
            print(f"   {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'}) {f'DEFAULT {col[3]}' if col[3] else ''}")
        
        # Check constraints
        cur.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'document_chunks'
        """)
        
        constraints = cur.fetchall()
        print(f"📋 Constraints on document_chunks:")
        for constraint in constraints:
            print(f"   {constraint[0]}: {constraint[1]}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to check database schema: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Database Constraints Fix Script")
    print("=" * 50)
    
    # Check current schema
    if check_database_schema():
        print("\n🔧 Fixing constraints...")
        if fix_chunk_id_constraint():
            print("\n🎉 Database is now ready for ON CONFLICT operations!")
        else:
            print("\n❌ Failed to fix constraints")
    else:
        print("\n❌ Failed to check database schema")

if __name__ == "__main__":
    main()
