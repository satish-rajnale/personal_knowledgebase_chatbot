#!/usr/bin/env node

// Simple test script to verify Notion OAuth endpoint
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function testNotionConnection() {
  console.log('🧪 Testing Notion OAuth connection...');
  console.log(`📍 API Base URL: ${API_BASE_URL}`);
  
  try {
    // Test 1: Check if backend is running
    console.log('\n1️⃣ Testing backend connectivity...');
    const healthResponse = await fetch(`${API_BASE_URL}/health`);
    if (healthResponse.ok) {
      console.log('✅ Backend is running');
    } else {
      console.log('❌ Backend is not responding');
      return;
    }
    
    // Test 2: Check if Notion OAuth endpoint exists
    console.log('\n2️⃣ Testing Notion OAuth endpoint...');
    const notionResponse = await fetch(`${API_BASE_URL}/api/v1/auth/notion/authorize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-token'
      }
    });
    
    if (notionResponse.status === 401) {
      console.log('✅ Notion OAuth endpoint exists (401 is expected without valid token)');
    } else if (notionResponse.status === 500) {
      const errorText = await notionResponse.text();
      console.log('❌ Notion OAuth endpoint error:', errorText);
    } else {
      console.log(`⚠️  Unexpected response: ${notionResponse.status}`);
    }
    
    // Test 3: Check environment variables
    console.log('\n3️⃣ Checking configuration...');
    const configResponse = await fetch(`${API_BASE_URL}/api/v1/auth/notion/authorize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (configResponse.status === 500) {
      const errorText = await configResponse.text();
      if (errorText.includes('NOTION_CLIENT_ID')) {
        console.log('❌ NOTION_CLIENT_ID is not configured');
        console.log('💡 Please set NOTION_CLIENT_ID in your .env file');
      } else {
        console.log('❌ Configuration error:', errorText);
      }
    }
    
  } catch (error) {
    console.log('❌ Network error:', error.message);
    console.log('💡 Make sure your backend server is running on port 8000');
  }
  
  console.log('\n📋 Next steps:');
  console.log('1. Set NOTION_CLIENT_ID and NOTION_CLIENT_SECRET in your .env file');
  console.log('2. Restart your backend server');
  console.log('3. Try the "Connect Notion" button again');
}

testNotionConnection(); 