#!/usr/bin/env python3
"""
Fix database schema by adding missing columns
This script adds the missing columns that the new chunking system requires
"""

import os
import sys
import psycopg2
from psycopg2 import sql

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def add_missing_columns():
    """Add missing columns to document_chunks table"""
    print("🔧 Adding missing columns to document_chunks table...")
    
    try:
        # Parse database URL
        db_url = settings.DATABASE_URL
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgres://')
        
        # Connect to database
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check which columns already exist
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'document_chunks'
        """)
        existing_columns = [row[0] for row in cur.fetchall()]
        print(f"📋 Existing columns: {existing_columns}")
        
        # Add missing columns
        missing_columns = [
            ("page_number", "INTEGER"),
            ("section_title", "VARCHAR"),
            ("chunk_size", "INTEGER DEFAULT 0")
        ]
        
        for column_name, column_type in missing_columns:
            if column_name not in existing_columns:
                try:
                    cur.execute(f"ALTER TABLE document_chunks ADD COLUMN {column_name} {column_type}")
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"⚠️  Could not add column {column_name}: {e}")
            else:
                print(f"✅ Column {column_name} already exists")
        
        # Update chunk_size for existing records
        try:
            cur.execute("""
                UPDATE document_chunks 
                SET chunk_size = LENGTH(text) 
                WHERE chunk_size IS NULL OR chunk_size = 0
            """)
            print("✅ Updated chunk_size for existing records")
        except Exception as e:
            print(f"⚠️  Could not update chunk_size: {e}")
        
        # Commit changes
        conn.commit()
        print("🎉 Database schema update completed successfully!")
        
        # Verify the columns were added
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'document_chunks' 
            AND column_name IN ('page_number', 'section_title', 'chunk_size')
            ORDER BY column_name
        """)
        
        columns = cur.fetchall()
        print(f"📋 New columns:")
        for col in columns:
            print(f"   {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to update database schema: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Database Schema Fix Script")
    print("=" * 50)
    
    if add_missing_columns():
        print("\n🎉 Database schema is now up to date!")
        print("The new chunking system should work correctly.")
    else:
        print("\n❌ Failed to update database schema")
        print("Please run the SQL script manually:")
        print("psql -d your_database -f add_columns.sql")

if __name__ == "__main__":
    main()
