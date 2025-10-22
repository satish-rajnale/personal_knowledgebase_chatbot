"""
Firebase Authentication Routes
Handles Firebase-based authentication and Google Drive integration
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

from app.models.user import get_db, User
from app.services.auth import AuthService, get_current_user_optional
from app.services.firebase_auth import firebase_auth_service
from app.core.config import settings

router = APIRouter()

class FirebaseSignInRequest(BaseModel):
    """Request model for Firebase sign-in"""
    id_token: str  # Firebase ID token
    access_token: Optional[str] = None  # Google access token for Drive access

class LoginResponse(BaseModel):
    """Response model for successful login"""
    access_token: str
    token_type: str = "bearer"
    user: dict
    expires_in: int = 3600  # 1 hour

@router.post("/auth/firebase/signin", response_model=LoginResponse)
async def firebase_signin(
    request: FirebaseSignInRequest,
    db: Session = Depends(get_db)
):
    """Sign in with Firebase ID token"""
    try:
        print(f"🔄 Firebase Sign-In request received")
        
        # Verify Firebase ID token
        firebase_user_info = await firebase_auth_service.verify_firebase_token(request.id_token)
        
        if not firebase_user_info:
            raise HTTPException(status_code=400, detail="Invalid Firebase ID token")
        
        print(f"✅ Firebase token verified for user: {firebase_user_info.get('email', 'Unknown')}")
        
        # Check if user exists in database
        user = db.query(User).filter(User.email == firebase_user_info['email']).first()
        
        if not user:
            # Create new user with Firebase info
            print(f"👤 Creating new user for: {firebase_user_info['email']}")
            user = User(
                user_id=str(uuid.uuid4()),
                email=firebase_user_info['email'],
                is_anonymous=False,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
                notion_connected=False,
                usage={"daily_requests": 0, "daily_limit": settings.DAILY_QUERY_LIMIT, "total_requests": 0},
                recent_activity=[],
                recent_syncs=[],
                # Firebase-specific fields
                firebase_uid=firebase_user_info.get('uid'),
                firebase_email=firebase_user_info.get('email'),
                firebase_name=firebase_user_info.get('name'),
                firebase_photo_url=firebase_user_info.get('photo_url'),
            )
            db.add(user)
        else:
            # Update user with Firebase information
            user.firebase_uid = firebase_user_info.get('uid')
            user.firebase_email = firebase_user_info.get('email')
            user.firebase_name = firebase_user_info.get('name')
            user.firebase_photo_url = firebase_user_info.get('photo_url')
            user.last_login = datetime.utcnow()
        
        # Store Google access token if provided (for Google Drive access)
        if request.access_token:
            user.google_access_token = request.access_token
            # Set token expiration (Google tokens typically expire in 1 hour)
            user.google_token_expires_at = datetime.utcnow() + timedelta(hours=1)
        
        db.commit()
        db.refresh(user)
        
        # Generate JWT token
        auth_service = AuthService()
        access_token = auth_service.create_access_token(data={"sub": user.user_id})
        
        print(f"✅ Firebase Sign-In successful for user: {user.email}")
        
        return LoginResponse(
            access_token=access_token,
            user={
                "user_id": user.user_id,
                "email": user.email,
                "is_anonymous": user.is_anonymous,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "notion_connected": user.notion_connected,
                "notion_workspace_name": user.notion_workspace_name,
                "usage": user.usage,
                "recent_activity": user.recent_activity,
                "recent_syncs": user.recent_syncs,
                "firebase_uid": user.firebase_uid,
                "firebase_name": user.firebase_name,
                "firebase_photo_url": user.firebase_photo_url,
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Firebase Sign-In failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Firebase Sign-In failed: {str(e)}")

@router.post("/auth/firebase/verify-token")
async def verify_firebase_token(
    request: FirebaseSignInRequest,
    db: Session = Depends(get_db)
):
    """Verify Firebase token and return user info"""
    try:
        # Verify Firebase ID token
        firebase_user_info = await firebase_auth_service.verify_firebase_token(request.id_token)
        
        if not firebase_user_info:
            raise HTTPException(status_code=400, detail="Invalid Firebase ID token")
        
        # Check if user exists in database
        user = db.query(User).filter(User.email == firebase_user_info['email']).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "valid": True,
            "user": {
                "user_id": user.user_id,
                "email": user.email,
                "firebase_uid": user.firebase_uid,
                "firebase_name": user.firebase_name,
                "firebase_photo_url": user.firebase_photo_url,
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Firebase token verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Token verification failed: {str(e)}")

@router.get("/auth/firebase/google-drive-status")
async def get_google_drive_status(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get Google Drive connection status for current user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Check if user has valid Google access token
    has_valid_token = (
        current_user.google_access_token and 
        current_user.google_token_expires_at and 
        current_user.google_token_expires_at > datetime.utcnow()
    )
    
    return {
        "user_connected": has_valid_token,
        "user_email": current_user.firebase_email,
        "user_name": current_user.firebase_name,
        "token_expires_at": current_user.google_token_expires_at.isoformat() if current_user.google_token_expires_at else None,
    }

@router.post("/auth/firebase/update-google-token")
async def update_google_token(
    request: FirebaseSignInRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Update Google access token for current user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not request.access_token:
        raise HTTPException(status_code=400, detail="Access token required")
    
    try:
        # Verify the access token with Google
        google_user_info = await firebase_auth_service.verify_google_access_token(request.access_token)
        
        if not google_user_info:
            raise HTTPException(status_code=400, detail="Invalid Google access token")
        
        # Update user's Google token
        current_user.google_access_token = request.access_token
        current_user.google_token_expires_at = datetime.utcnow() + timedelta(hours=1)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Google access token updated successfully",
            "user_email": google_user_info.get('email'),
            "user_name": google_user_info.get('name'),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to update Google token: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to update Google token: {str(e)}")
