#!/usr/bin/env python3
"""
Script to set up local Qdrant for testing
"""

import subprocess
import sys
import os
import time

def setup_local_qdrant():
    """Set up local Qdrant using Docker"""
    
    print("🔧 Setting up Local Qdrant for Testing")
    print("=" * 40)
    
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker is not available. Please install Docker first.")
        return False
    
    # Check if Qdrant container is already running
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=qdrant", "--format", "{{.Names}}"],
            check=True, capture_output=True, text=True
        )
        if "qdrant" in result.stdout:
            print("✅ Qdrant container is already running")
            return True
    except subprocess.CalledProcessError:
        pass
    
    # Start Qdrant container
    print("🚀 Starting Qdrant container...")
    try:
        subprocess.run([
            "docker", "run", "-d",
            "--name", "qdrant",
            "-p", "6333:6333",
            "-p", "6334:6334",
            "qdrant/qdrant"
        ], check=True)
        print("✅ Qdrant container started successfully")
        
        # Wait for Qdrant to be ready
        print("⏳ Waiting for Qdrant to be ready...")
        time.sleep(5)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Qdrant container: {e}")
        return False

def update_env_file():
    """Update .env file to use local Qdrant"""
    
    env_file = ".env"
    
    # Check if .env file exists
    if not os.path.exists(env_file):
        print(f"❌ {env_file} not found. Please create it from env.example")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Update Qdrant configuration
    updated_content = content.replace(
        "QDRANT_URL=https://your-qdrant-cloud-url.qdrant.io",
        "QDRANT_URL=http://qdrant:6333"
    ).replace(
        "QDRANT_API_KEY=your_qdrant_api_key_here",
        "QDRANT_API_KEY="
    )
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated .env file to use local Qdrant")
    return True

def main():
    """Main function"""
    
    print("This script will set up a local Qdrant instance for testing.")
    print("This is useful when you don't have access to Qdrant Cloud.")
    print()
    
    # Set up local Qdrant
    if not setup_local_qdrant():
        return False
    
    # Update .env file
    if not update_env_file():
        return False
    
    print("\n🎉 Local Qdrant setup completed!")
    print("\nNext steps:")
    print("1. Restart your backend server")
    print("2. The vector store should now work with local Qdrant")
    print("3. Try syncing Notion pages and testing chat")
    print("\nTo stop Qdrant later, run: docker stop qdrant")
    print("To remove Qdrant container, run: docker rm qdrant")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 