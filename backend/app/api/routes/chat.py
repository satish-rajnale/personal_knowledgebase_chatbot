from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import uuid
from datetime import datetime

from app.models.chat import ChatSession, ChatMessage, get_db
from app.services.vector_store import search_documents
from app.services.llm import generate_chat_response
from app.api.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message and get AI response with RAG"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get or create chat session
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            session = ChatSession(session_id=session_id)
            db.add(session)
            db.commit()
            db.refresh(session)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        
        # Search for relevant documents
        relevant_docs = await search_documents(request.message, top_k=5)
        
        # Generate AI response
        ai_response = await generate_chat_response(request.message, relevant_docs)
        
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
        
        return ChatResponse(
            message=ai_response,
            session_id=session_id,
            sources=relevant_docs
        )
        
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
        
        return [{
            "session_id": session.session_id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": len(session.messages)
        } for session in sessions]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}") 