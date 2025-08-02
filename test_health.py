#!/usr/bin/env python3
"""
Simple test script to verify health endpoints
"""

import requests
import json
import sys

def test_health_endpoints(base_url="http://localhost:8000/health"):
    """Test all health endpoints"""
    
    endpoints = [
        "/",
        "/health", 
        "/api/v1/health"
    ]
    
    print(f"🔍 Testing health endpoints at {base_url}")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n📡 Testing: {endpoint}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                data = response.json()
                
                # Pretty print the response
                if isinstance(data, dict):
                    print("📋 Response:")
                    for key, value in data.items():
                        if isinstance(value, dict):
                            print(f"   {key}:")
                            for sub_key, sub_value in value.items():
                                print(f"     {sub_key}: {sub_value}")
                        else:
                            print(f"   {key}: {value}")
                else:
                    print(f"📋 Response: {data}")
                    
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"📋 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - Is the server running at {base_url}?")
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Health check complete!")

if __name__ == "__main__":
    # Allow custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_health_endpoints(base_url) 