#!/usr/bin/env python3
"""
Test script to debug Notion RAG integration
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_USER_EMAIL = "test@example.com"  # Change this to your test user email

async def test_notion_rag():
    """Test the Notion RAG integration"""
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Notion RAG Integration")
        print("=" * 50)
        
        # Step 1: Login as test user
        print("\n1️⃣ Logging in as test user...")
        login_response = await client.post(
            f"{BACKEND_URL}/api/v1/auth/email",
            json={"email": TEST_USER_EMAIL}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        login_data = login_response.json()
        token = login_data["token"]
        user_id = login_data["user_id"]
        
        print(f"✅ Logged in as {TEST_USER_EMAIL} (User ID: {user_id})")
        
        # Set authorization header
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Check if user has Notion connected
        print("\n2️⃣ Checking Notion connection...")
        profile_response = await client.get(
            f"{BACKEND_URL}/api/v1/auth/profile",
            headers=headers
        )
        
        if profile_response.status_code != 200:
            print(f"❌ Failed to get profile: {profile_response.status_code}")
            return
        
        profile_data = profile_response.json()
        notion_connected = profile_data.get("notion_connected", False)
        notion_workspace = profile_data.get("notion_workspace_name", "None")
        
        print(f"   Notion connected: {notion_connected}")
        print(f"   Workspace: {notion_workspace}")
        
        if not notion_connected:
            print("❌ User not connected to Notion. Please connect Notion first.")
            return
        
        # Step 3: Debug vector store contents
        print("\n3️⃣ Checking vector store contents...")
        debug_response = await client.get(
            f"{BACKEND_URL}/api/v1/debug/vector-store",
            headers=headers
        )
        
        if debug_response.status_code != 200:
            print(f"❌ Failed to debug vector store: {debug_response.status_code}")
            print(debug_response.text)
            return
        
        debug_data = debug_response.json()
        print(f"   Collection: {debug_data['collection_info']['name']}")
        print(f"   Total vectors: {debug_data['collection_info']['vectors_count']}")
        print(f"   User documents: {debug_data['user_documents_count']}")
        
        if debug_data['user_documents_count'] == 0:
            print("❌ No documents found for user in vector store!")
            print("   This means either:")
            print("   1. No Notion pages have been synced")
            print("   2. The sync process failed")
            print("   3. Documents weren't properly indexed")
            return
        
        # Show some sample documents
        print("\n   Sample documents:")
        for i, doc in enumerate(debug_data['documents'][:3]):
            payload = doc['payload']
            print(f"   {i+1}. {payload.get('metadata', {}).get('source', 'Unknown')}")
            print(f"      Text: {payload.get('text', '')[:100]}...")
        
        # Step 4: Test chat with a simple query
        print("\n4️⃣ Testing chat with simple query...")
        chat_response = await client.post(
            f"{BACKEND_URL}/api/v1/chat",
            headers=headers,
            json={
                "message": "What is GIL?",
                "session_id": "test-session"
            }
        )
        
        if chat_response.status_code != 200:
            print(f"❌ Chat failed: {chat_response.status_code}")
            print(chat_response.text)
            return
        
        chat_data = chat_response.json()
        print(f"   AI Response: {chat_data['message']}")
        print(f"   Sources found: {len(chat_data.get('sources', []))}")
        
        if chat_data.get('sources'):
            print("\n   Sources:")
            for i, source in enumerate(chat_data['sources'][:3]):
                print(f"   {i+1}. {source.get('metadata', {}).get('source', 'Unknown')}")
                print(f"      Score: {source.get('score', 0):.3f}")
                print(f"      Text: {source.get('text', '')[:100]}...")
        else:
            print("   ❌ No sources found!")
        
        # Step 5: Test with a more specific query
        print("\n5️⃣ Testing with specific query...")
        specific_response = await client.post(
            f"{BACKEND_URL}/api/v1/chat",
            headers=headers,
            json={
                "message": "Tell me about Python programming",
                "session_id": "test-session"
            }
        )
        
        if specific_response.status_code == 200:
            specific_data = specific_response.json()
            print(f"   AI Response: {specific_data['message']}")
            print(f"   Sources found: {len(specific_data.get('sources', []))}")
        else:
            print(f"❌ Specific query failed: {specific_response.status_code}")
        
        print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_notion_rag()) 