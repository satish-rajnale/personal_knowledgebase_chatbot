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

# Store OAuth states for callback identification
oauth_states = {}  # {state: user_id}

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

class GoogleSignInRequest(BaseModel):
    id_token: str
    access_token: Optional[str] = None
    user_info: Optional[dict] = None

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

@router.post("/auth/google/signin", response_model=LoginResponse)
async def google_signin(
    request: GoogleSignInRequest,
    db: Session = Depends(get_db)
):
    """Sign in with Google ID token"""
    try:
        print(f"🔄 Google Sign-In request received")
        
        # Verify Google ID token
        google_user_info = await _verify_google_token(request.id_token)
        
        if not google_user_info:
            raise HTTPException(status_code=400, detail="Invalid Google ID token")
        
        print(f"✅ Google token verified for user: {google_user_info.get('email', 'Unknown')}")
        
        # Check if user already exists
        user = db.query(User).filter(User.email == google_user_info['email']).first()
        
        if not user:
            # Create new user with Google info
            user = User(
                user_id=str(uuid.uuid4()),
                email=google_user_info['email'],
                is_anonymous=False
            )
            db.add(user)
            print(f"✅ Created new user: {user.email}")
        else:
            print(f"✅ Found existing user: {user.email}")
        
        # Update user with Google information
        user.google_user_id = google_user_info.get('sub')
        user.google_user_email = google_user_info.get('email')
        user.google_user_name = google_user_info.get('name')
        
        # Store Google tokens if provided
        if request.access_token:
            user.google_access_token = request.access_token
            # Set token expiration (Google tokens typically expire in 1 hour)
            from datetime import datetime, timedelta
            user.google_token_expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        # Create JWT token
        auth_service = AuthService()
        token = auth_service.create_jwt_token(user.user_id)
        
        print(f"✅ Google Sign-In successful for user: {user.email}")
        
        return LoginResponse(
            token=token,
            user_id=user.user_id,
            is_anonymous=user.is_anonymous,
            email=user.email
        )
        
    except Exception as e:
        print(f"❌ Google Sign-In failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Google Sign-In failed: {str(e)}")

async def _verify_google_token(id_token: str) -> Optional[dict]:
    """Verify Google ID token and extract user information"""
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            # Verify the token with Google
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            )
            
            if response.status_code != 200:
                print(f"❌ Google token verification failed: {response.status_code}")
                return None
            
            token_info = response.json()
            
            # Verify the token is for our app
            from app.core.config import settings
            if token_info.get('aud') != settings.GOOGLE_CLIENT_ID:
                print(f"❌ Invalid audience in Google token: {token_info.get('aud')}")
                return None
            
            # Extract user information
            user_info = {
                'sub': token_info.get('sub'),
                'email': token_info.get('email'),
                'name': token_info.get('name'),
                'picture': token_info.get('picture'),
                'email_verified': token_info.get('email_verified', False)
            }
            
            print(f"✅ Google token verified for: {user_info['email']}")
            return user_info
            
    except Exception as e:
        print(f"❌ Error verifying Google token: {str(e)}")
        return None

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
    """Get Notion OAuth authorization URL (web version)"""
    return await _generate_notion_auth_url(
        user=user,
        db=db,
        use_mobile_redirect=False
    )

@router.post("/auth/notion/authorize/mobile")
async def authorize_notion_mobile(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get Notion OAuth authorization URL (mobile version)"""
    return await _generate_notion_auth_url(
        user=user,
        db=db,
        use_mobile_redirect=True
    )

async def _generate_notion_auth_url(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    use_mobile_redirect: bool = False
):
    """Generate Notion OAuth authorization URL"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from app.core.config import settings
    
    if not settings.NOTION_CLIENT_ID:
        print("❌ NOTION_CLIENT_ID not configured")
        raise HTTPException(status_code=500, detail="Notion integration not configured. Please set NOTION_CLIENT_ID in your environment variables.")
    
    # Notion only accepts HTTPS URLs, so we always use the HTTPS redirect URI for OAuth
    # We'll handle the mobile redirect after processing the callback
    redirect_uri = settings.NOTION_REDIRECT_URI  # Always use HTTPS for Notion OAuth
    
    print(f"🔧 Notion OAuth configuration:")
    print(f"   Client ID: {'Set' if settings.NOTION_CLIENT_ID else 'Not set'}")
    print(f"   Client Secret: {'Set' if settings.NOTION_CLIENT_SECRET else 'Not set'}")
    print(f"   Redirect URI (HTTPS for Notion): {redirect_uri}")
    print(f"   Mobile redirect URI: {settings.NOTION_MOBILE_REDIRECT_URI}")
    print(f"   Platform: {'Mobile' if use_mobile_redirect else 'Web'}")
    
    # Generate state parameter for security
    state = str(uuid.uuid4())
    
    # Store state with user ID for callback identification
    # For now, we'll use a simple in-memory store (use Redis in production)
    oauth_states[state] = user.user_id

    auth_url = f"https://api.notion.com/v1/oauth/authorize?client_id={settings.NOTION_CLIENT_ID}&response_type=code&owner=user&state={state}&redirect_uri={redirect_uri}"
    
    return {
        "auth_url": auth_url,
        "state": state,
        "redirect_uri": redirect_uri,
        "platform": "mobile" if use_mobile_redirect else "web",
        "mobile_redirect_uri": settings.NOTION_MOBILE_REDIRECT_URI
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
    """Handle Notion OAuth callback (POST version for web apps)"""
    return await _process_notion_callback(
        code=request.code,
        state=request.state,
        user=user,
        db=db
    )

@router.get("/auth/notion/callback")
async def notion_callback_get(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle Notion OAuth callback (GET version for mobile apps)"""
    try:
        # Get user ID from state
        user_id = oauth_states.get(state)
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
        
        # Get user from database
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        result = await _process_notion_callback(
            code=code,
            state=state,
            user=user,
            db=db
        )
        
        # Clean up the state after successful processing
        oauth_states.pop(state, None)
        
        # If successful, redirect to frontend with success status
        from app.core.config import settings
        # Use frontend URL for redirect (fallback to mobile redirect if not set)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        success_url = f"{frontend_url}?status=success&workspace={result.get('workspace_name', 'Unknown')}"
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=success_url)
        
    except Exception as e:
        # If failed, redirect to frontend with error status
        from app.core.config import settings
        # Use frontend URL for redirect (fallback to mobile redirect if not set)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        error_url = f"{frontend_url}?status=error&message={str(e)}"
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=error_url)

async def _process_notion_callback(
    code: str,
    state: str,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Common logic for processing Notion OAuth callback"""
    print(f"🔄 Notion callback received for user: {user.user_id if user else 'None'}")
    print(f"📝 Code: {code[:10]}...")
    print(f"🔐 State: {state}")
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Check if this OAuth code has already been used
    if code in used_oauth_codes:
        print(f"⚠️ OAuth code already used: {code[:10]}...")
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
        used_oauth_codes.add(code)
        cleanup_used_codes()  # Cleanup if needed
        
        # Exchange code for access token
        # Note: NotionService requires a token, but for OAuth exchange we don't have one yet
        # So we'll use the exchange_code_for_token method directly
        
        # Try both redirect URIs to support both web and mobile
        redirect_uris_to_try = [settings.NOTION_REDIRECT_URI, settings.NOTION_MOBILE_REDIRECT_URI]
        token_data = None
        
        for redirect_uri in redirect_uris_to_try:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.notion.com/v1/oauth/token",
                        auth=(settings.NOTION_CLIENT_ID, settings.NOTION_CLIENT_SECRET),
                        data={
                            "grant_type": "authorization_code",
                            "code": code,
                            "redirect_uri": redirect_uri
                        }
                    )
                    
                    if response.status_code == 200:
                        token_data = response.json()
                        print(f"✅ Token exchange successful with redirect URI: {redirect_uri}")
                        break
                    else:
                        print(f"⚠️ Token exchange failed with redirect URI {redirect_uri}: {response.status_code} - {response.text}")
                        
            except Exception as e:
                print(f"⚠️ Exception with redirect URI {redirect_uri}: {e}")
                continue
        
        if not token_data:
            print(f"❌ OAuth token exchange failed with all redirect URIs")
            # Remove from used codes if exchange failed
            used_oauth_codes.discard(code)
            raise Exception(f"OAuth token exchange failed with all redirect URIs")
        
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
        used_oauth_codes.discard(code)
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