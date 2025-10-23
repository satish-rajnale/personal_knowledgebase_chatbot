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
    print(f"🔄 Notion sync requested for {len(request.page_ids)} pages by user {user.user_id if user else 'unknown'}")
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not user.notion_token:
        raise HTTPException(status_code=400, detail="Notion not connected. Please connect your Notion account first.")
    
    try:
        # Create Notion service with user's token
        notion_service = NotionService(user_token=user.notion_token)
        
        # Sync documents from specified pages
        print(f"🔍 Starting sync for pages: {request.page_ids}")
        documents = await notion_service.sync_user_pages(request.page_ids)
        
        if not documents:
            return {
                "message": "No content found in specified Notion pages",
                "documents_synced": 0
            }
        
        print("Suncing notion pages", documents)
        
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

@router.get("/notion/embeddings")
async def get_notion_embeddings(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get information about synced Notion pages and their embeddings"""
    print(f"🔍 get_notion_embeddings called for user {user.user_id if user else 'unknown'}")
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not user.notion_token:
        raise HTTPException(status_code=400, detail="Notion not connected. Please connect your Notion account first.")
    
    try:
        # Get all Notion documents for this user using PostgreSQL
        print("🔍 Searching for Notion embeddings...")
        from app.services.postgres_vector_store import search_documents
        
        # Use a simple query to get all Notion documents for this user
        results = await search_documents(
            query="notion",  # Simple query to find Notion documents
            top_k=1000,  # Get a large number to find all Notion docs
            filter={
                "user_id": user.user_id,
                "source_type": "notion"
            }
        )
        
        print(f"🔍 Found {len(results)} Notion documents")
        
        # Group by page_id to get unique pages
        pages = {}
        for result in results:
            metadata = result.get("metadata", {})
            page_id = metadata.get("page_id")
            
            if page_id:
                if page_id not in pages:
                    pages[page_id] = {
                        "page_id": page_id,
                        "title": metadata.get("title", f"Page {page_id[:8]}..."),
                        "url": metadata.get("url", f"https://notion.so/{page_id.replace('-', '')}"),
                        "chunks_count": 0,
                        "last_edited_time": metadata.get("last_edited_time"),
                        "created_time": metadata.get("created_time"),
                        "total_score": 0
                    }
                
                pages[page_id]["chunks_count"] += 1
                pages[page_id]["total_score"] += result.get("score", 0)
        
        # Convert to list and sort by total score
        pages_list = list(pages.values())
        pages_list.sort(key=lambda x: x["total_score"], reverse=True)
        
        print(f"✅ Returning {len(pages_list)} pages with {sum(page['chunks_count'] for page in pages_list)} total chunks")
        
        return {
            "user_id": user.user_id,
            "total_pages": len(pages_list),
            "total_chunks": sum(page["chunks_count"] for page in pages_list),
            "pages": pages_list[:50]  # Return top 50 pages
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Notion embeddings: {str(e)}") 