from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv

# Enable debugpy if DEBUG is true
if os.getenv("DEBUG", "false").lower() == "true":
    try:
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))
        print("🔍 Debug server listening on port 5678")
        if os.getenv("DEBUG_WAIT_FOR_ATTACH", "false").lower() == "true":
            print("⏳ Waiting for debugger to attach...")
            debugpy.wait_for_client()
            print("✅ Debugger attached!")
    except ImportError:
        print("⚠️ debugpy not available, debugging disabled")

# Import all models to ensure they are registered with SQLAlchemy
from app.models import User, UsageLog, NotionSync, ChatSession, ChatMessage

from app.api.routes import chat, upload, notion, auth, google, firebase_auth, pdf_upload
from app.core.config import settings
from app.core.database import init_db
from app.services.vector_store import vector_store

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Knowledge Assistant - Multi-User SaaS",
    description="AI-powered knowledge assistant with multi-user support, Notion integration, and usage tracking",
    version="2.0.0"
)

# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth.router, tags=["auth"])
app.include_router(firebase_auth.router, tags=["firebase-auth"])
app.include_router(chat.router, tags=["chat"])
app.include_router(upload.router, tags=["upload"])
app.include_router(notion.router, tags=["notion"])
app.include_router(google.router, tags=["google"])
app.include_router(pdf_upload.router, tags=["pdf-upload"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and vector store on startup"""
    print("🚀 Starting up application...")
    
    # Initialize database
    await init_db()
    
    # Initialize vector store with proper indexing
    try:
        print("🔧 Initializing PostgreSQL vector store...")
        from app.services.postgres_vector_store import init_vector_store
        await init_vector_store()
        print("✅ PostgreSQL vector store initialized successfully")
    except Exception as e:
        print(f"⚠️ Warning: Vector store initialization failed: {e}")
        print("   The application will continue, but RAG features may not work properly")
    
    print("✅ Application startup complete")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Personal Knowledgebase Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }

# Remove the simple health endpoint since we have a detailed one in chat router
# The detailed health check is available at /health from the chat router
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    ) 