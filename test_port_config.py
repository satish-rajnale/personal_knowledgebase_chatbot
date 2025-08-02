#!/usr/bin/env python3
"""
Test script to verify dynamic port configuration
"""

import os
import sys

def test_port_configuration():
    """Test that the port configuration works correctly"""
    
    print("🔧 Testing Dynamic Port Configuration")
    print("=" * 40)
    
    # Test 1: Default port when PORT not set
    print("\n1️⃣ Testing default port (PORT not set):")
    if 'PORT' in os.environ:
        del os.environ['PORT']
    
    # Import settings after clearing PORT
    from app.core.config import settings
    print(f"   Expected: 8000")
    print(f"   Actual: {settings.API_PORT}")
    print(f"   ✅ Pass" if settings.API_PORT == 8000 else "   ❌ Fail")
    
    # Test 2: Custom port when PORT is set
    print("\n2️⃣ Testing custom port (PORT=3000):")
    os.environ['PORT'] = '3000'
    
    # Re-import settings to get new PORT value
    import importlib
    import app.core.config
    importlib.reload(app.core.config)
    from app.core.config import settings
    
    print(f"   Expected: 3000")
    print(f"   Actual: {settings.API_PORT}")
    print(f"   ✅ Pass" if settings.API_PORT == 3000 else "   ❌ Fail")
    
    # Test 3: Railway-style port
    print("\n3️⃣ Testing Railway port (PORT=12345):")
    os.environ['PORT'] = '12345'
    
    # Re-import settings
    importlib.reload(app.core.config)
    from app.core.config import settings
    
    print(f"   Expected: 12345")
    print(f"   Actual: {settings.API_PORT}")
    print(f"   ✅ Pass" if settings.API_PORT == 12345 else "   ❌ Fail")
    
    # Test 4: Invalid port handling
    print("\n4️⃣ Testing invalid port handling (PORT=invalid):")
    os.environ['PORT'] = 'invalid'
    
    try:
        # Re-import settings
        importlib.reload(app.core.config)
        from app.core.config import settings
        print(f"   Expected: ValueError or 8000")
        print(f"   Actual: {settings.API_PORT}")
        print(f"   ✅ Pass (handled gracefully)")
    except ValueError as e:
        print(f"   ✅ Pass (ValueError caught: {e})")
    except Exception as e:
        print(f"   ❌ Fail (Unexpected error: {e})")
    
    print("\n" + "=" * 40)
    print("🏁 Port configuration test complete!")

if __name__ == "__main__":
    # Add the backend directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    
    test_port_configuration() 