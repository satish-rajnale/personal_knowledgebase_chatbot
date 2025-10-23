#!/usr/bin/env python3
"""
Debug server with debugpy for remote debugging
"""
import debugpy
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def start_debug_server():
    """Start the debug server with debugpy"""
    print("🔧 Starting debug server...")
    
    # Configure debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("🔍 Debug server listening on port 5678")
    print("🔗 Connect your debugger to localhost:5678")
    
    # Wait for debugger to attach (optional)
    if os.getenv("DEBUG_WAIT_FOR_ATTACH", "false").lower() == "true":
        print("⏳ Waiting for debugger to attach...")
        debugpy.wait_for_client()
        print("✅ Debugger attached!")
    
    # Import and run the main application
    from main import app
    import uvicorn
    
    print("🚀 Starting FastAPI server with debugging enabled...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in Docker
        log_level="info"  # Use info level for better container logs
    )

if __name__ == "__main__":
    start_debug_server()
