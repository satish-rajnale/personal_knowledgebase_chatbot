#!/usr/bin/env python3
"""
Test script to verify debug server is working
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_debug_server():
    """Test if debug server can be started"""
    print("🔍 Testing debug server...")
    
    # Check environment variables
    debug = os.getenv("DEBUG", "false")
    debug_wait = os.getenv("DEBUG_WAIT_FOR_ATTACH", "false")
    
    print(f"DEBUG: {debug}")
    print(f"DEBUG_WAIT_FOR_ATTACH: {debug_wait}")
    
    if debug.lower() == "true":
        try:
            import debugpy
            print("✅ debugpy imported successfully")
            
            # Try to listen on port 5678
            debugpy.listen(("0.0.0.0", 5678))
            print("✅ Debug server listening on port 5678")
            
            if debug_wait.lower() == "true":
                print("⏳ Waiting for debugger to attach...")
                debugpy.wait_for_client()
                print("✅ Debugger attached!")
            else:
                print("🔍 Debug server ready (not waiting for attachment)")
                
        except ImportError as e:
            print(f"❌ debugpy import failed: {e}")
        except Exception as e:
            print(f"❌ Debug server error: {e}")
    else:
        print("⚠️ DEBUG not set to true")

if __name__ == "__main__":
    test_debug_server()
