#!/usr/bin/env python3
"""
Database migration script to add Google OAuth fields to the User table.
Run this script to update your existing database with the new Google OAuth columns.
"""

import sqlite3
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def migrate_database():
    """Add Google OAuth fields to the User table"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'chat_history.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at: {db_path}")
        print("Please make sure the backend has been started at least once to create the database.")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"🔧 Connected to database: {db_path}")
        
        # Check if Google OAuth columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        google_columns = [
            'google_access_token',
            'google_refresh_token', 
            'google_token_expires_at',
            'google_user_id',
            'google_user_email',
            'google_user_name'
        ]
        
        existing_columns = [col for col in google_columns if col in columns]
        
        if existing_columns:
            print(f"✅ Google OAuth columns already exist: {existing_columns}")
            missing_columns = [col for col in google_columns if col not in columns]
            if missing_columns:
                print(f"⚠️ Missing columns: {missing_columns}")
            else:
                print("✅ All Google OAuth columns are present. No migration needed.")
                return True
        
        # Add missing Google OAuth columns
        print("🔧 Adding Google OAuth columns to users table...")
        
        for column in google_columns:
            if column not in columns:
                if column == 'google_token_expires_at':
                    # DateTime column
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column} DATETIME")
                elif column in ['google_access_token', 'google_refresh_token']:
                    # Text columns for tokens
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column} TEXT")
                else:
                    # String columns
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column} VARCHAR(255)")
                print(f"✅ Added column: {column}")
        
        # Commit the changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        
        print("\n📋 Updated table structure:")
        for column in updated_columns:
            print(f"  - {column}")
        
        print("\n✅ Database migration completed successfully!")
        print("🚀 You can now restart your backend server to use Google OAuth features.")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()
            print("🔌 Database connection closed.")

def main():
    """Main function"""
    print("🚀 Google OAuth Database Migration Script")
    print("=" * 50)
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update your backend configuration with Google OAuth credentials")
        print("2. Restart your backend server")
        print("3. Test the Google OAuth flow")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()


