#!/usr/bin/env python3
"""
Resend API Test Script
Tests Resend API configuration for sending emails.
"""

import os
import asyncio
import httpx
from datetime import datetime

async def test_resend_api():
    """Test Resend API for sending emails"""
    
    # Get environment variables
    resend_api_key = os.getenv('RESEND_API_KEY')
    admin_email = os.getenv('ADMIN_EMAIL')
    
    if not resend_api_key:
        print("❌ RESEND_API_KEY not configured")
        return False
    
    if not admin_email:
        print("❌ ADMIN_EMAIL not configured")
        return False
    
    print(f"🔧 Testing Resend API...")
    print(f"   API Key: {resend_api_key[:10]}...")
    print(f"   Admin Email: {admin_email}")
    
    try:
        html_content = f"""
        <html>
        <body>
            <h2>🧪 Resend API Test</h2>
            <p>This is a test email from your AI Knowledge Assistant using Resend API.</p>
            <p><strong>Test Details:</strong></p>
            <ul>
                <li>Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li>Provider: Resend API</li>
                <li>To: {admin_email}</li>
            </ul>
            <p>✅ If you receive this email, your Resend API configuration is working correctly!</p>
            <hr>
            <p><em>AI Knowledge Assistant</em></p>
        </body>
        </html>
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {resend_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": "onboarding@resend.dev",
                    "to": [admin_email],
                    "subject": f"🧪 Resend API Test - AI Knowledge Assistant ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
                    "html": html_content
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                print("✅ Resend API test successful!")
                print(f"📧 Test email sent to: {admin_email}")
                print("   Check your inbox for the test message.")
                return True
            else:
                print(f"❌ Resend API test failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Resend API test error: {e}")
        return False

async def main():
    """Main function"""
    print("🧪 AI Knowledge Assistant - Resend API Test")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and configure your Resend API key.")
        return
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file loaded successfully")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment variables")
    
    # Test Resend API
    success = await test_resend_api()
    
    if success:
        print("\n🎉 Resend API configuration is working correctly!")
        print("   Your app can now send email notifications via Resend.")
    else:
        print("\n❌ Resend API configuration failed!")
        print("   Please check:")
        print("   - RESEND_API_KEY is set correctly")
        print("   - ADMIN_EMAIL is set correctly")
        print("   - Your Resend account is active")

if __name__ == "__main__":
    asyncio.run(main()) 