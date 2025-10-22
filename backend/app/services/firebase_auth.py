"""
Firebase Authentication Service
Handles Firebase ID token verification and user management
"""

import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class FirebaseAuthService:
    """Service for handling Firebase Authentication"""
    
    def __init__(self):
        self.firebase_project_id = getattr(settings, 'FIREBASE_PROJECT_ID', None)
        if not self.firebase_project_id:
            logger.warning("FIREBASE_PROJECT_ID not set in environment variables")
    
    async def verify_firebase_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token and extract user information
        
        Args:
            id_token: Firebase ID token from client
            
        Returns:
            Dict containing user information if token is valid, None otherwise
        """
        try:
            logger.info("🔄 Verifying Firebase ID token...")
            
            # Verify the token with Firebase
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key={settings.FIREBASE_API_KEY}",
                    params={"idToken": id_token}
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Firebase token verification failed: {response.status_code}")
                    return None
                
                token_info = response.json()
                
                if not token_info.get('users'):
                    logger.error("❌ No users found in Firebase response")
                    return None
                
                user_info = token_info['users'][0]
                
                # Extract user information
                firebase_user = {
                    'uid': user_info.get('localId'),
                    'email': user_info.get('email'),
                    'email_verified': user_info.get('emailVerified', False),
                    'name': user_info.get('displayName'),
                    'photo_url': user_info.get('photoUrl'),
                    'provider_id': user_info.get('providerId'),
                    'firebase_claims': user_info.get('customClaims', {}),
                }
                
                logger.info(f"✅ Firebase token verified for: {firebase_user['email']}")
                return firebase_user
                
        except Exception as e:
            logger.error(f"❌ Error verifying Firebase token: {str(e)}")
            return None
    
    async def verify_google_access_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Google access token (for Google Drive access)
        
        Args:
            access_token: Google access token
            
        Returns:
            Dict containing user information if token is valid, None otherwise
        """
        try:
            logger.info("🔄 Verifying Google access token...")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Google access token verification failed: {response.status_code}")
                    return None
                
                user_info = response.json()
                
                logger.info(f"✅ Google access token verified for: {user_info.get('email')}")
                return user_info
                
        except Exception as e:
            logger.error(f"❌ Error verifying Google access token: {str(e)}")
            return None

# Global instance
firebase_auth_service = FirebaseAuthService()
