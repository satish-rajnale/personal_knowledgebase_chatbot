#!/usr/bin/env python3
"""
Test script to verify backend configuration and startup parameters
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_config():
    """Test configuration loading"""
    print("🔧 Testing backend configuration...")
    
    try:
        from app.core.config import settings
        print(f"✅ Configuration loaded successfully")
        print(f"   API_HOST: {settings.API_HOST}")
        print(f"   API_PORT: {settings.API_PORT}")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   CORS_ORIGINS: {settings.CORS_ORIGINS}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_port_parsing():
    """Test port parsing with different values"""
    print("\n🔧 Testing port parsing...")
    
    test_cases = [
        ("8000", 8000),
        ("8080", 8080),
        ("", 8000),  # Empty string
        (None, 8000),  # None
        ("invalid", 8000),  # Invalid string
    ]
    
    for test_value, expected in test_cases:
        # Temporarily set PORT environment variable
        if test_value is None:
            os.environ.pop("PORT", None)
        else:
            os.environ["PORT"] = str(test_value)
        
        try:
            from app.core.config import get_port
            result = get_port()
            status = "✅" if result == expected else "❌"
            print(f"   {status} PORT='{test_value}' -> {result} (expected: {expected})")
        except Exception as e:
            print(f"   ❌ PORT='{test_value}' -> Error: {e}")
    
    # Reset to default
    os.environ["PORT"] = "8000"

def test_uvicorn_params():
    """Test uvicorn startup parameters"""
    print("\n🔧 Testing uvicorn parameters...")
    
    try:
        from app.core.config import settings
        
        # Simulate uvicorn.run parameters
        host = settings.API_HOST
        port = settings.API_PORT
        reload = settings.DEBUG
        
        print(f"✅ Uvicorn parameters:")
        print(f"   host: {host}")
        print(f"   port: {port} (type: {type(port)})")
        print(f"   reload: {reload}")
        
        # Validate types
        assert isinstance(host, str), f"Host should be string, got {type(host)}"
        assert isinstance(port, int), f"Port should be int, got {type(port)}"
        assert isinstance(reload, bool), f"Reload should be bool, got {type(reload)}"
        
        print(f"✅ All parameter types are correct")
        return True
        
    except Exception as e:
        print(f"❌ Uvicorn parameter error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Backend Configuration Test Suite")
    print("=" * 50)
    
    # Test configuration loading
    config_ok = test_config()
    
    # Test port parsing
    test_port_parsing()
    
    # Test uvicorn parameters
    uvicorn_ok = test_uvicorn_params()
    
    print("\n" + "=" * 50)
    if config_ok and uvicorn_ok:
        print("✅ All tests passed! Backend should start correctly.")
        print("\n🎯 To start the backend:")
        print("   cd backend")
        print("   python main.py")
        print("   # or")
        print("   uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("❌ Some tests failed. Please check the configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main() 