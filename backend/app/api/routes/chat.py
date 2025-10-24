from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import uuid
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.user import User, get_db
from app.models.chat import ChatSession, ChatMessage
from app.services.vector_store import search_documents
from app.services.llm import generate_chat_response
from app.api.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services.llm import LLMService
from app.services.auth import get_current_user_optional, AuthService
from app.core.config import settings
import traceback

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

# Simple health check endpoint
@router.get("/")
async def root():
    """
    Simple root endpoint to verify the API is running
    """
    return {
        "message": "Personal Knowledge Base API is running",
        "status": "ok",
        "version": "1.0.0"
    }

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the application and its dependencies are working
    """
    health_status = {
        "status": "healthy",
        "timestamp": None,
        "version": "1.0.0",
        "services": {
            "database": "unknown",
            "vector_store": "unknown",
            "llm": "unknown"
        },
        "environment": {
            "debug": settings.DEBUG,
            "llm_provider": settings.LLM_PROVIDER,
            "database_url": settings.DATABASE_URL,
            "openrouter_api_key_set": bool(settings.OPENROUTER_API_KEY)
        }
    }
    
    try:
        from datetime import datetime
        health_status["timestamp"] = datetime.utcnow().isoformat()
    except:
        pass
    
    # Check database connection
    try:
        db = next(get_db())
        # Try a simple query using text() for SQLAlchemy 2.0 compatibility
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check vector store connection
    try:
        from app.services.postgres_vector_store import postgres_vector_store
        # Just check if the vector store can be instantiated
        if hasattr(postgres_vector_store, 'embedding_dimensions'):
            health_status["services"]["vector_store"] = "healthy"
        else:
            health_status["services"]["vector_store"] = "unhealthy: missing embedding_dimensions"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["vector_store"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check LLM service
    try:
        from app.services.llm import llm_service
        # Try a simple test call - use a simple method that doesn't require async
        # Just check if the service can be instantiated and has required attributes
        if hasattr(llm_service, 'provider') and hasattr(llm_service, 'model_name'):
            health_status["services"]["llm"] = "healthy"
        else:
            health_status["services"]["llm"] = "unhealthy: missing required attributes"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["llm"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Return appropriate HTTP status
    if health_status["status"] == "healthy":
        return health_status
    elif health_status["status"] == "degraded":
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)

@router.post("/chat", response_model=ChatResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response with RAG"""
    try:
        # Check usage limits if user is authenticated and limit is enabled
        auth_service = AuthService()
        if user:
            usage = auth_service.check_daily_usage_limit(db, user.user_id)
            if not usage["can_make_query"] and usage["limit_enabled"]:
                raise HTTPException(
                    status_code=429, 
                    detail=f"Daily query limit exceeded. You have used {usage['daily_query_count']}/{usage['daily_limit']} queries today."
                )
        
        # Generate session ID if not provided
        session_id = chat_request.session_id or str(uuid.uuid4())
        
        # Get or create chat session
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            session = ChatSession(
                session_id=session_id,
                user_id=user.user_id if user else None
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=chat_request.message
        )
        db.add(user_message)
        db.commit()
        
        # Search for relevant documents (user-specific if authenticated)
        search_filter = None
        if user:
            # Filter documents by user_id in metadata
            search_filter = {"user_id": user.user_id}
            print(f"🔍 Searching for user: {user.user_id}")
        else:
            print(f"🔍 Searching without user filter (anonymous)")
        
        print(f"🔍 Query: {chat_request.message}")
        print(f"🔍 Search filter: {search_filter}")
        
        relevant_docs = await search_documents(chat_request.message, top_k=5, filter=search_filter)
        
        print(f"🔍 Found {len(relevant_docs)} relevant documents")
        for i, doc in enumerate(relevant_docs):
            print(f"  📄 Doc {i+1}: {doc.get('metadata', {}).get('source', 'Unknown')} (score: {doc.get('score', 0):.3f})")
            print(f"     Text: {doc.get('text', '')[:100]}...")
        
        # Generate AI response
        ai_response = await generate_chat_response(chat_request.message, relevant_docs)
        
        # Save AI response
        ai_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=ai_response,
            sources=json.dumps([{
                "text": doc.get("text", "")[:200] + "...",
                "source": doc.get("metadata", {}).get("source", "Unknown"),
                "score": doc.get("score", 0)
            } for doc in relevant_docs])
        )
        db.add(ai_message)
        db.commit()
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        db.commit()
        
        # Increment usage for authenticated users
        if user:
            auth_service.increment_usage(db, user.user_id, "chat", {
                "message_length": len(chat_request.message),
                "response_length": len(ai_response),
                "sources_count": len(relevant_docs)
            })
        
        return ChatResponse(
            message=ai_response,
            session_id=session_id,
            sources=relevant_docs
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.get("/chat/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    session_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat history"""
    try:
        query = db.query(ChatMessage).order_by(ChatMessage.created_at.desc())
        
        if session_id:
            query = query.filter(ChatMessage.session_id == session_id)
        
        messages = query.limit(limit).all()
        
        # Group messages by session
        sessions = {}
        for msg in messages:
            if msg.session_id not in sessions:
                sessions[msg.session_id] = []
            sessions[msg.session_id].append(msg)
        
        # Format response
        history = []
        for session_id, session_messages in sessions.items():
            # Sort messages by creation time
            session_messages.sort(key=lambda x: x.created_at)
            
            # Get session info
            session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
            
            history.append(ChatHistoryResponse(
                session_id=session_id,
                created_at=session.created_at if session else session_messages[0].created_at,
                updated_at=session.updated_at if session else session_messages[-1].created_at,
                messages=[{
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at,
                    "sources": json.loads(msg.sources) if msg.sources else None
                } for msg in session_messages]
            ))
        
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat history: {str(e)}")

@router.delete("/chat/history")
async def clear_chat_history(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Clear chat history"""
    try:
        if session_id:
            # Clear specific session
            db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
            db.query(ChatSession).filter(ChatSession.session_id == session_id).delete()
        else:
            # Clear all history
            db.query(ChatMessage).delete()
            db.query(ChatSession).delete()
        
        db.commit()
        
        return {"message": "Chat history cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing chat history: {str(e)}")

@router.get("/chat/sessions")
async def get_chat_sessions(db: Session = Depends(get_db)):
    """Get all chat sessions"""
    try:
        sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
        return [
            {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            }
            for session in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat sessions: {str(e)}")

@router.get("/debug/vector-store")
async def debug_vector_store(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Debug endpoint to check vector store contents for a user"""
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        from app.services.postgres_vector_store import search_documents
        
        # Search for all documents for this user using PostgreSQL
        search_filter = {"user_id": user.user_id}
        
        # Get all documents for this user (using a dummy query)
        try:
            # Use a simple query to get user's documents
            results = await search_documents(
                query="test",  # Dummy query
                top_k=100,
                filter=search_filter
            )
            
            documents = []
            for result in results:
                documents.append({
                    "text": result["text"],
                    "score": result["score"],
                    "metadata": result["metadata"],
                    "source_type": result["source_type"]
                })
            
            return {
                "user_id": user.user_id,
                "collection_info": {
                    "name": "document_chunks",
                    "vectors_count": len(results),
                    "points_count": len(results)
                },
                "user_documents_count": len(documents),
                "documents": documents[:10]  # Return first 10 for debugging
            }
            
        except Exception as e:
            return {
                "user_id": user.user_id,
                "collection_info": {
                    "name": collection_info.name,
                    "vectors_count": collection_info.vectors_count,
                    "points_count": collection_info.points_count
                },
                "error": f"Failed to search user documents: {str(e)}",
                "user_documents_count": 0,
                "documents": []
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error debugging vector store: {str(e)}") 