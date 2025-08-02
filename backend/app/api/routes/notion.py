from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.models.chat import get_db
from app.services.notion_service import sync_notion_database
from app.services.vector_store import add_documents_to_store

router = APIRouter()

@router.post("/notion/sync")
async def sync_notion(
    db: Session = Depends(get_db)
):
    """Sync content from Notion database"""
    try:
        # Sync documents from Notion
        documents = await sync_notion_database()
        
        if not documents:
            return {
                "message": "No documents found in Notion database or database is empty",
                "documents_synced": 0
            }
        
        # Add to vector store
        await add_documents_to_store(documents, source_type="notion")
        
        return {
            "message": f"Successfully synced {len(documents)} documents from Notion",
            "documents_synced": len(documents),
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

@router.get("/notion/status")
async def notion_status():
    """Check Notion integration status"""
    try:
        from app.core.config import settings
        
        status = {
            "configured": bool(settings.NOTION_TOKEN and settings.NOTION_DATABASE_ID),
            "token_configured": bool(settings.NOTION_TOKEN),
            "database_configured": bool(settings.NOTION_DATABASE_ID)
        }
        
        if not status["configured"]:
            status["message"] = "Notion integration not fully configured. Please set NOTION_TOKEN and NOTION_DATABASE_ID in your .env file."
        else:
            status["message"] = "Notion integration is configured and ready to use."
        
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking Notion status: {str(e)}"
        ) 