from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr
import uuid
import httpx

from app.models.user import get_db
from app.services.auth import AuthService, get_current_user_optional
from app.models.user import User

router = APIRouter()

# Simple cache to track used OAuth codes (in production, use Redis)
used_oauth_codes = set()

# Cleanup old codes periodically (every 1000 codes)
def cleanup_used_codes():
    """Clean up old OAuth codes to prevent memory leaks"""
    if len(used_oauth_codes) > 1000:
        # Keep only the last 500 codes
        codes_list = list(used_oauth_codes)
        used_oauth_codes.clear()
        used_oauth_codes.update(codes_list[-500:])
        print(f"🧹 Cleaned up OAuth codes cache, kept {len(used_oauth_codes)} codes")

# Pydantic models for request/response
class AnonymousLoginRequest(BaseModel):
    pass

class EmailLoginRequest(BaseModel):
    email: EmailStr

class LoginResponse(BaseModel):
    token: str
    user_id: str
    is_anonymous: bool
    email: Optional[str] = None

class UserProfileResponse(BaseModel):
    user_id: str
    email: Optional[str] = None
    is_anonymous: bool
    created_at: str
    last_login: Optional[str] = None
    notion_connected: bool
    notion_workspace_name: Optional[str] = None
    usage: dict
    recent_activity: list
    recent_syncs: list

class ContactFormRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

@router.post("/auth/anonymous", response_model=LoginResponse)
async def create_anonymous_user(db: Session = Depends(get_db)):
    """Create an anonymous user account"""
    auth_service = AuthService()
    user = auth_service.create_anonymous_user(db)
    token = auth_service.create_jwt_token(user.user_id)
    
    return LoginResponse(
        token=token,
        user_id=user.user_id,
        is_anonymous=True
    )

@router.post("/auth/email", response_model=LoginResponse)
async def login_with_email(
    request: EmailLoginRequest,
    db: Session = Depends(get_db)
):
    """Login or register with email"""
    auth_service = AuthService()
    
    # Check if user exists
    user = auth_service.get_user_by_email(db, request.email)
    
    if not user:
        # Create new user
        user = auth_service.create_user_with_email(db, request.email)
    
    # Update last login
    auth_service.update_user_login(db, user.user_id)
    
    # Create JWT token
    token = auth_service.create_jwt_token(user.user_id)
    
    return LoginResponse(
        token=token,
        user_id=user.user_id,
        is_anonymous=user.is_anonymous,
        email=user.email
    )

@router.get("/auth/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get current user profile and stats"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    auth_service = AuthService()
    stats = auth_service.get_user_stats(db, user.user_id)
    
    return UserProfileResponse(
        user_id=stats["user_id"],
        email=stats["email"],
        is_anonymous=stats["is_anonymous"],
        created_at=stats["created_at"].isoformat(),
        last_login=stats["last_login"].isoformat() if stats["last_login"] else None,
        notion_connected=stats["notion_connected"],
        notion_workspace_name=stats["notion_workspace_name"],
        usage=stats["usage"],
        recent_activity=stats["recent_activity"],
        recent_syncs=stats["recent_syncs"]
    )

@router.post("/auth/notion/authorize")
async def authorize_notion(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get Notion OAuth authorization URL"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from app.core.config import settings
    
    if not settings.NOTION_CLIENT_ID:
        print("❌ NOTION_CLIENT_ID not configured")
        raise HTTPException(status_code=500, detail="Notion integration not configured. Please set NOTION_CLIENT_ID in your environment variables.")
    
    print(f"🔧 Notion OAuth configuration:")
    print(f"   Client ID: {'Set' if settings.NOTION_CLIENT_ID else 'Not set'}")
    print(f"   Client Secret: {'Set' if settings.NOTION_CLIENT_SECRET else 'Not set'}")
    print(f"   Redirect URI: {settings.NOTION_REDIRECT_URI}")
    
    # Generate state parameter for security
    state = str(uuid.uuid4())
    
    # Store state in user session (you might want to use Redis for this in production)
    # For now, we'll use a simple approach
    
    auth_url = f"https://api.notion.com/v1/oauth/authorize?client_id={settings.NOTION_CLIENT_ID}&response_type=code&owner=user&state={state}&redirect_uri={settings.NOTION_REDIRECT_URI}"
    
    return {
        "auth_url": auth_url,
        "state": state
    }

class NotionCallbackRequest(BaseModel):
    code: str
    state: str

@router.post("/auth/notion/callback")
async def notion_callback(
    request: NotionCallbackRequest,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Handle Notion OAuth callback"""
    print(f"🔄 Notion callback received for user: {user.user_id if user else 'None'}")
    print(f"📝 Code: {request.code[:10]}...")
    print(f"🔐 State: {request.state}")
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Check if this OAuth code has already been used
    if request.code in used_oauth_codes:
        print(f"⚠️ OAuth code already used: {request.code[:10]}...")
        return {
            "message": "Notion already connected successfully",
            "workspace_name": user.notion_workspace_name or "Unknown"
        }
    
    # Check if user is already connected to Notion
    if user.notion_token and user.notion_workspace_name:
        print(f"⚠️ User {user.user_id} already connected to Notion workspace: {user.notion_workspace_name}")
        return {
            "message": "Notion already connected successfully",
            "workspace_name": user.notion_workspace_name
        }
    
    print(f"🔄 Processing new OAuth code for user {user.user_id}")
    
    from app.core.config import settings
    from app.services.notion_service import NotionService
    
    if not settings.NOTION_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Notion integration not configured")
    
    try:
        # Mark this code as used immediately to prevent duplicate processing
        used_oauth_codes.add(request.code)
        cleanup_used_codes()  # Cleanup if needed
        
        # Exchange code for access token
        # Note: NotionService requires a token, but for OAuth exchange we don't have one yet
        # So we'll use the exchange_code_for_token method directly
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.notion.com/v1/oauth/token",
                auth=(settings.NOTION_CLIENT_ID, settings.NOTION_CLIENT_SECRET),
                data={
                    "grant_type": "authorization_code",
                    "code": request.code,
                    "redirect_uri": settings.NOTION_REDIRECT_URI
                }
            )
            
            if response.status_code != 200:
                print(f"❌ OAuth token exchange failed: {response.status_code} - {response.text}")
                # Remove from used codes if exchange failed
                used_oauth_codes.discard(request.code)
                raise Exception(f"OAuth token exchange failed: {response.text}")
            
            token_data = response.json()
            print(f"✅ Token exchange successful for workspace: {token_data.get('workspace_name', 'Unknown')}")
        
        # Update user with Notion token
        user.notion_token = token_data["access_token"]
        user.notion_workspace_id = token_data.get("workspace_id")
        user.notion_workspace_name = token_data.get("workspace_name")
        
        db.commit()
        print(f"✅ User {user.user_id} updated with Notion token")
        print(f"🏢 Workspace: {user.notion_workspace_name}")
        
        result = {
            "message": "Notion connected successfully",
            "workspace_name": user.notion_workspace_name or "Unknown"
        }
        print(f"✅ Returning success response: {result}")
        return result
        
    except Exception as e:
        # Remove from used codes if any error occurred
        used_oauth_codes.discard(request.code)
        raise HTTPException(status_code=400, detail=f"Failed to connect Notion: {str(e)}")

@router.post("/contact")
async def submit_contact_form(
    request: ContactFormRequest,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Submit contact form"""
    from app.services.email_service import EmailService
    
    try:
        # Log the contact form submission
        if user:
            from app.services.auth import AuthService
            auth_service = AuthService()
            auth_service.increment_usage(db, user.user_id, "contact_form", {
                "name": request.name,
                "email": request.email,
                "subject": request.subject
            })
        
        # Send email notification
        email_service = EmailService()
        await email_service.send_contact_form_notification(request)
        
        return {"message": "Contact form submitted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit contact form: {str(e)}")

@router.post("/auth/logout")
async def logout_user(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Logout user (client-side token clearing is sufficient, but this provides server-side logging)"""
    if user:
        print(f"👋 User {user.user_id} logged out")
        # You could add logout logging here if needed
        # For now, client-side token clearing is sufficient
    
    return {"message": "Logged out successfully"}

@router.get("/auth/usage")
async def get_usage_stats(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get current user usage statistics"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    auth_service = AuthService()
    usage = auth_service.check_daily_usage_limit(db, user.user_id)
    
    return usage 