"""
Resend Email Service
Uses Resend API for reliable email delivery
"""

import os
import httpx
from typing import Optional
from pydantic import BaseModel

class EmailRequest(BaseModel):
    to: str
    subject: str
    html: str
    from_email: Optional[str] = None

class ResendService:
    def __init__(self):
        self.api_key = os.getenv('RESEND_API_KEY')
        self.base_url = "https://api.resend.com"
        self.default_from = os.getenv('ADMIN_EMAIL', 'noreply@resend.dev')
        
    async def send_email(self, to: str, subject: str, html_content: str, from_email: Optional[str] = None) -> bool:
        """Send email using Resend API"""
        
        if not self.api_key:
            print("❌ RESEND_API_KEY not configured")
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": from_email or self.default_from,
                        "to": [to],
                        "subject": subject,
                        "html": html_content
                    }
                )
                
                if response.status_code == 200:
                    print(f"✅ Email sent successfully to {to}")
                    return True
                else:
                    print(f"❌ Failed to send email: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Email sending error: {e}")
            return False
    
    async def send_contact_form_notification(self, form_data: dict) -> bool:
        """Send contact form notification"""
        
        html_content = f"""
        <html>
        <body>
            <h2>📧 New Contact Form Submission</h2>
            <p><strong>Name:</strong> {form_data.get('name', 'N/A')}</p>
            <p><strong>Email:</strong> {form_data.get('email', 'N/A')}</p>
            <p><strong>Subject:</strong> {form_data.get('subject', 'N/A')}</p>
            <p><strong>Message:</strong></p>
            <p>{form_data.get('message', 'N/A')}</p>
            <hr>
            <p><em>Sent from AI Knowledge Assistant</em></p>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=os.getenv('ADMIN_EMAIL'),
            subject=f"Contact Form: {form_data.get('subject', 'New Message')}",
            html_content=html_content
        )
    
    async def send_usage_alert(self, user_email: str, usage_data: dict) -> bool:
        """Send usage limit alert"""
        
        html_content = f"""
        <html>
        <body>
            <h2>⚠️ Usage Limit Alert</h2>
            <p>Hello,</p>
            <p>You're approaching your daily usage limit for AI Knowledge Assistant.</p>
            <p><strong>Current Usage:</strong> {usage_data.get('daily_query_count', 0)} / {usage_data.get('daily_limit', 10)} queries</p>
            <p>Please upgrade your plan or wait until tomorrow for your limit to reset.</p>
            <hr>
            <p><em>AI Knowledge Assistant</em></p>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=user_email,
            subject="Usage Limit Alert - AI Knowledge Assistant",
            html_content=html_content
        ) 