from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.api.routes import chat, upload, notion
from app.core.config import settings
from app.core.database import init_db

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Personal Knowledgebase Chatbot",
    description="AI-powered chatbot for your personal knowledgebase",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(notion.router, prefix="/api/v1", tags=["notion"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and vector store on startup"""
    await init_db()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Personal Knowledgebase Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Personal Knowledgebase Chatbot API is running",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/v1/chat",
            "upload": "/api/v1/upload",
            "notion": "/api/v1/notion",
            "detailed_health": "/api/v1/health"
        }
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    ) 