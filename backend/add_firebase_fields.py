#!/usr/bin/env python3
"""
Database migration script to add Firebase fields to User table
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add Firebase fields to the User table"""
    
    db_path = "chat_history.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting database migration...")
        
        # Check if Firebase fields already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        firebase_fields = [
            ('firebase_uid', 'VARCHAR'),
            ('firebase_email', 'VARCHAR'),
            ('firebase_name', 'VARCHAR'),
            ('firebase_photo_url', 'VARCHAR')
        ]
        
        added_fields = []
        
        for field_name, field_type in firebase_fields:
            if field_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}")
                    added_fields.append(field_name)
                    print(f"✅ Added column: {field_name}")
                except sqlite3.Error as e:
                    print(f"❌ Error adding column {field_name}: {e}")
            else:
                print(f"ℹ️  Column {field_name} already exists")
        
        # Commit changes
        conn.commit()
        
        if added_fields:
            print(f"✅ Migration completed successfully! Added {len(added_fields)} fields: {', '.join(added_fields)}")
        else:
            print("✅ Migration completed - no new fields needed")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()
