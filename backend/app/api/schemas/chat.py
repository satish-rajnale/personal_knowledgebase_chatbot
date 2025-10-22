from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    sources: List[Dict[str, Any]]

class ChatMessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime
    sources: Optional[List[Dict[str, Any]]] = None

class ChatHistoryResponse(BaseModel):
    session_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] 