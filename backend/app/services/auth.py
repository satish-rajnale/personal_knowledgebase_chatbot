from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import jwt
import uuid
import json
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.user import User, UsageLog, NotionSync, get_db
from app.core.config import settings

# JWT Configuration
JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24 * 7  # 7 days

security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.jwt_secret = JWT_SECRET
        self.jwt_algorithm = JWT_ALGORITHM
        self.jwt_expiry_hours = JWT_EXPIRY_HOURS
    
    def create_anonymous_user(self, db: Session) -> User:
        """Create a new anonymous user"""
        user = User(
            user_id=str(uuid.uuid4()),
            is_anonymous=True,
            email=None
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def create_user_with_email(self, db: Session, email: str) -> User:
        """Create a new user with email"""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return existing_user
        
        user = User(
            user_id=str(uuid.uuid4()),
            email=email,
            is_anonymous=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Get user by user_id"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def create_jwt_token(self, user_id: str) -> str:
        """Create JWT token for user"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiry_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def update_user_login(self, db: Session, user_id: str):
        """Update user's last login time"""
        user = self.get_user_by_id(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
    
    def check_daily_usage_limit(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Check if user has exceeded daily usage limit"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if we need to reset daily count
        now = datetime.utcnow()
        last_reset = user.last_query_reset or user.created_at
        
        # Reset if it's a new day (UTC)
        if (now.date() > last_reset.date()):
            user.daily_query_count = 0
            user.last_query_reset = now
            db.commit()
        
        # Check if user has exceeded limit
        daily_limit = settings.DAILY_QUERY_LIMIT
        remaining_queries = max(0, daily_limit - user.daily_query_count)
        
        return {
            "daily_query_count": user.daily_query_count,
            "daily_limit": daily_limit,
            "remaining_queries": remaining_queries,
            "can_make_query": user.daily_query_count < daily_limit,
            "total_queries": user.total_queries
        }
    
    def increment_usage(self, db: Session, user_id: str, action: str, details: Optional[Dict] = None):
        """Increment user usage and log the action"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Increment daily and total query counts for chat actions
        if action == "chat":
            user.daily_query_count += 1
            user.total_queries += 1
        
        # Log the usage
        usage_log = UsageLog(
            user_id=user_id,
            action=action,
            details=json.dumps(details) if details else None
        )
        
        db.add(usage_log)
        db.commit()
        db.refresh(user)
    
    def get_user_stats(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recent usage logs
        recent_logs = db.query(UsageLog).filter(
            UsageLog.user_id == user_id
        ).order_by(UsageLog.created_at.desc()).limit(10).all()
        
        # Get Notion sync stats
        notion_syncs = db.query(NotionSync).filter(
            NotionSync.user_id == user_id
        ).order_by(NotionSync.created_at.desc()).limit(5).all()
        
        return {
            "user_id": user.user_id,
            "email": user.email,
            "is_anonymous": user.is_anonymous,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "notion_connected": bool(user.notion_token),
            "notion_workspace_name": user.notion_workspace_name,
            "usage": self.check_daily_usage_limit(db, user_id),
            "recent_activity": [
                {
                    "action": log.action,
                    "created_at": log.created_at,
                    "details": json.loads(log.details) if log.details else None
                } for log in recent_logs
            ],
            "recent_syncs": [
                {
                    "page_title": sync.page_title,
                    "status": sync.status,
                    "created_at": sync.created_at,
                    "error_message": sync.error_message
                } for sync in notion_syncs
            ]
        }

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    auth_service = AuthService()
    user_id = auth_service.verify_jwt_token(credentials.credentials)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# Dependency to get current user (optional - for anonymous access)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from JWT token (optional)"""
    if not credentials:
        return None
    
    auth_service = AuthService()
    user_id = auth_service.verify_jwt_token(credentials.credentials)
    
    if not user_id:
        return None
    
    user = auth_service.get_user_by_id(db, user_id)
    return user 