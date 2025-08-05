from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from app.models.user import User, get_db
from app.services.notion_service import NotionService
from app.services.vector_store import add_documents_to_store
from app.services.auth import get_current_user_optional, AuthService

router = APIRouter()

class SyncPagesRequest(BaseModel):
    page_ids: List[str]

@router.post("/notion/sync")
async def sync_notion(
    request: SyncPagesRequest,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Sync content from specified Notion pages"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not user.notion_token:
        raise HTTPException(status_code=400, detail="Notion not connected. Please connect your Notion account first.")
    
    try:
        # Create Notion service with user's token
        notion_service = NotionService(user_token=user.notion_token)
        
        # Sync documents from specified pages
        documents = await notion_service.sync_user_pages(request.page_ids)
        
        if not documents:
            return {
                "message": "No content found in specified Notion pages",
                "documents_synced": 0
            }
        
        # Add to vector store with user_id
        await add_documents_to_store(documents, source_type="notion", user_id=user.user_id)
        
        # Log the sync operation
        auth_service = AuthService()
        auth_service.increment_usage(db, user.user_id, "notion_sync", {
            "page_ids": request.page_ids,
            "documents_synced": len(documents)
        })
        
        return {
            "message": f"Successfully synced {len(documents)} documents from {len(request.page_ids)} Notion pages",
            "documents_synced": len(documents),
            "pages_synced": len(request.page_ids),
            "source": "notion"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing Notion: {str(e)}"
        )

@router.get("/notion/pages")
async def get_notion_pages(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get all pages accessible to the user"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not user.notion_token:
        raise HTTPException(status_code=400, detail="Notion not connected. Please connect your Notion account first.")
    
    try:
        # Create Notion service with user's token
        notion_service = NotionService(user_token=user.notion_token)
        
        # Get user's pages
        pages = await notion_service.get_user_pages()
        
        # Format response
        formatted_pages = []
        for page in pages:
            formatted_pages.append({
                "id": page["id"],
                "title": notion_service._extract_page_title(page),
                "url": f"https://notion.so/{page['id'].replace('-', '')}",
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time")
            })
        
        return {
            "pages": formatted_pages,
            "total": len(formatted_pages)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting Notion pages: {str(e)}"
        )

@router.get("/notion/databases")
async def get_notion_databases(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get all databases accessible to the user"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not user.notion_token:
        raise HTTPException(status_code=400, detail="Notion not connected. Please connect your Notion account first.")
    
    try:
        # Create Notion service with user's token
        notion_service = NotionService(user_token=user.notion_token)
        
        # Get user's databases
        databases = await notion_service.get_user_databases()
        
        # Format response
        formatted_databases = []
        for database in databases:
            formatted_databases.append({
                "id": database["id"],
                "title": notion_service._extract_page_title(database),
                "url": f"https://notion.so/{database['id'].replace('-', '')}",
                "created_time": database.get("created_time"),
                "last_edited_time": database.get("last_edited_time")
            })
        
        return {
            "databases": formatted_databases,
            "total": len(formatted_databases)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting Notion databases: {str(e)}"
        )

@router.get("/notion/status")
async def notion_status(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Check user's Notion integration status"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        from app.core.config import settings
        
        status = {
            "oauth_configured": bool(settings.NOTION_CLIENT_ID and settings.NOTION_CLIENT_SECRET),
            "user_connected": bool(user.notion_token),
            "workspace_name": user.notion_workspace_name
        }
        
        if not status["oauth_configured"]:
            status["message"] = "Notion OAuth not configured. Please set NOTION_CLIENT_ID and NOTION_CLIENT_SECRET in your .env file."
        elif not status["user_connected"]:
            status["message"] = "Connect your Notion workspace to start syncing content."
        else:
            status["message"] = f"Connected to Notion workspace: {user.notion_workspace_name}"
        
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking Notion status: {str(e)}"
        ) 