from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid
import httpx
import json
from datetime import datetime, timedelta

from app.models.user import get_db, User
from app.services.auth import get_current_user_optional

router = APIRouter()

# Store OAuth states for callback identification (same pattern as Notion)
google_oauth_states = {}  # {state: user_id}

# Google OAuth scopes for Drive access
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly", 
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

class GoogleOAuthResponse(BaseModel):
    auth_url: str
    state: str
    redirect_uri: str
    platform: str
    mobile_redirect_uri: str

class GoogleCallbackResponse(BaseModel):
    message: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None

class GoogleFileResponse(BaseModel):
    id: str
    name: str
    mime_type: str
    size: Optional[int] = None
    modified_time: str
    web_view_link: Optional[str] = None

class GoogleFilesResponse(BaseModel):
    files: List[GoogleFileResponse]
    total: int

@router.post("/auth/google/authorize/mobile")
async def authorize_google_mobile(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get Google OAuth authorization URL (mobile version)"""
    return await _generate_google_auth_url(
        user=user,
        db=db,
        use_mobile_redirect=True
    )

async def _generate_google_auth_url(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    use_mobile_redirect: bool = False
):
    """Generate Google OAuth authorization URL"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from app.core.config import settings
    
    if not settings.GOOGLE_CLIENT_ID:
        print("❌ GOOGLE_CLIENT_ID not configured")
        raise HTTPException(status_code=500, detail="Google integration not configured. Please set GOOGLE_CLIENT_ID in your environment variables.")
    
    # Google OAuth uses HTTPS redirect URI
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    print(f"🔧 Google OAuth configuration:")
    print(f"   Client ID: {'Set' if settings.GOOGLE_CLIENT_ID else 'Not set'}")
    print(f"   Client Secret: {'Set' if settings.GOOGLE_CLIENT_SECRET else 'Not set'}")
    print(f"   Redirect URI (HTTPS for Google): {redirect_uri}")
    print(f"   Mobile redirect URI: {settings.GOOGLE_MOBILE_REDIRECT_URI}")
    print(f"   Platform: {'Mobile' if use_mobile_redirect else 'Web'}")
    
    # Generate state parameter for security
    state = str(uuid.uuid4())
    
    # Store state with user ID for callback identification
    google_oauth_states[state] = user.user_id

    # Build Google OAuth URL
    scopes = " ".join(GOOGLE_SCOPES)
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&response_type=code&scope={scopes}&redirect_uri={redirect_uri}&state={state}&access_type=offline&prompt=consent"
    
    return GoogleOAuthResponse(
        auth_url=auth_url,
        state=state,
        redirect_uri=redirect_uri,
        platform="mobile" if use_mobile_redirect else "web",
        mobile_redirect_uri=settings.GOOGLE_MOBILE_REDIRECT_URI
    )

@router.get("/auth/google/callback")
async def google_callback_get(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback (GET version for mobile apps)"""
    try:
        # Get user ID from state
        user_id = google_oauth_states.get(state)
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
        
        # Get user from database
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        result = await _process_google_callback(
            code=code,
            state=state,
            user=user,
            db=db
        )
        
        # Clean up the state after successful processing
        google_oauth_states.pop(state, None)
        
        # If successful, redirect to mobile app with success status
        from app.core.config import settings
        mobile_redirect_uri = settings.GOOGLE_MOBILE_REDIRECT_URI
        success_url = f"{mobile_redirect_uri}?status=success&email={result.get('user_email', 'Unknown')}&name={result.get('user_name', 'Unknown')}"
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=success_url)
        
    except Exception as e:
        # If failed, redirect to mobile app with error status
        from app.core.config import settings
        mobile_redirect_uri = settings.GOOGLE_MOBILE_REDIRECT_URI
        error_url = f"{mobile_redirect_uri}?status=error&message={str(e)}"
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url)

async def _process_google_callback(
    code: str,
    state: str,
    user: User,
    db: Session
):
    """Common logic for processing Google OAuth callback"""
    print(f"🔄 Google callback received for user: {user.user_id}")
    print(f"📝 Code: {code[:10]}...")
    print(f"🔐 State: {state}")
    
    from app.core.config import settings
    
    if not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google integration not configured")
    
    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"OAuth token exchange failed: {response.text}")
            
            token_data = response.json()
            print(f"✅ Token exchange successful")
            
            # Get user info from Google
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            
            if user_info_response.status_code != 200:
                raise Exception(f"Failed to get user info: {user_info_response.text}")
            
            user_info = user_info_response.json()
            print(f"✅ User info retrieved: {user_info.get('email', 'Unknown')}")
            
            # Update user with Google tokens and info
            user.google_access_token = token_data["access_token"]
            user.google_refresh_token = token_data.get("refresh_token")
            user.google_user_id = user_info.get("id")
            user.google_user_email = user_info.get("email")
            user.google_user_name = user_info.get("name")
            
            # Set token expiration
            if "expires_in" in token_data:
                user.google_token_expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
            
            db.commit()
            print(f"✅ User {user.user_id} updated with Google tokens")
            print(f"📧 Email: {user.google_user_email}")
            
            result = {
                "message": "Google connected successfully",
                "user_email": user.google_user_email,
                "user_name": user.google_user_name
            }
            print(f"✅ Returning success response: {result}")
            return result
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect Google: {str(e)}")

@router.get("/google-drive/status")
async def google_drive_status(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Check Google Drive connection status"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    is_connected = bool(user.google_access_token and user.google_user_email)
    
    return {
        "oauth_configured": bool(user.google_access_token),
        "user_connected": is_connected,
        "user_email": user.google_user_email,
        "user_name": user.google_user_name,
        "message": "Google Drive connected" if is_connected else "Google Drive not connected"
    }

@router.get("/google-drive/files")
async def get_google_drive_files(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    page_size: int = 10,
    page_token: Optional[str] = None
):
    """Get Google Drive files for the authenticated user"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not user.google_access_token:
        raise HTTPException(status_code=400, detail="Google Drive not connected")
    
    try:
        # Check if token is expired and refresh if needed
        if user.google_token_expires_at and user.google_token_expires_at <= datetime.utcnow():
            await _refresh_google_token(user, db)
        
        # Get files from Google Drive
        async with httpx.AsyncClient() as client:
            params = {
                "pageSize": page_size,
                "fields": "nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink)"
            }
            
            if page_token:
                params["pageToken"] = page_token
            
            response = await client.get(
                "https://www.googleapis.com/drive/v3/files",
                headers={"Authorization": f"Bearer {user.google_access_token}"},
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get Google Drive files: {response.text}")
            
            data = response.json()
            
            files = []
            for file_info in data.get("files", []):
                files.append(GoogleFileResponse(
                    id=file_info["id"],
                    name=file_info["name"],
                    mime_type=file_info.get("mimeType", ""),
                    size=int(file_info["size"]) if file_info.get("size") else None,
                    modified_time=file_info.get("modifiedTime", ""),
                    web_view_link=file_info.get("webViewLink")
                ))
            
            return GoogleFilesResponse(
                files=files,
                total=len(files)
            )
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get Google Drive files: {str(e)}")

async def _refresh_google_token(user: User, db: Session):
    """Refresh Google access token using refresh token"""
    if not user.google_refresh_token:
        raise Exception("No refresh token available")
    
    from app.core.config import settings
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": user.google_refresh_token,
                "grant_type": "refresh_token"
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
        
        token_data = response.json()
        
        # Update user with new access token
        user.google_access_token = token_data["access_token"]
        if "expires_in" in token_data:
            user.google_token_expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
        
        db.commit()
        print(f"✅ Refreshed Google token for user {user.user_id}")

@router.post("/google-drive/disconnect")
async def disconnect_google_drive(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Disconnect Google Drive integration"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Clear Google tokens and info
    user.google_access_token = None
    user.google_refresh_token = None
    user.google_token_expires_at = None
    user.google_user_id = None
    user.google_user_email = None
    user.google_user_name = None
    
    db.commit()
    
    return {"message": "Google Drive disconnected successfully"}


