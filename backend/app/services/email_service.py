import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import httpx
import os
from pydantic import BaseModel

from app.core.config import settings

class ContactFormRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.admin_email = settings.ADMIN_EMAIL
        
        # Formspree configuration (free tier alternative)
        self.formspree_endpoint = "https://formspree.io/f/xpzgwqgw"  # Replace with your Formspree endpoint
    
    async def send_contact_form_notification(self, request: ContactFormRequest) -> bool:
        """Send contact form notification via Resend API, SMTP, or Formspree"""
        try:
            # Try Resend API first (most reliable)
            if await self._send_via_resend(request):
                return True
            
            # Fallback to Formspree (free tier)
            if await self._send_via_formspree(request):
                return True
            
            # Fallback to SMTP if configured
            if self.smtp_host and self.smtp_username and self.smtp_password:
                return await self._send_via_smtp(request)
            
            # If none is configured, just log it
            print(f"Contact form submission: {request.name} ({request.email}) - {request.subject}")
            return True
            
        except Exception as e:
            print(f"Failed to send contact form notification: {str(e)}")
            return False
    
    async def _send_via_resend(self, request: ContactFormRequest) -> bool:
        """Send contact form via Resend API"""
        try:
            resend_api_key = os.getenv('RESEND_API_KEY')
            if not resend_api_key:
                print("❌ RESEND_API_KEY not configured")
                return False
            
            html_content = f"""
            <html>
            <body>
                <h2>📧 New Contact Form Submission</h2>
                <p><strong>Name:</strong> {request.name}</p>
                <p><strong>Email:</strong> {request.email}</p>
                <p><strong>Subject:</strong> {request.subject}</p>
                <p><strong>Message:</strong></p>
                <p>{request.message}</p>
                <hr>
                <p><em>Sent from AI Knowledge Assistant</em></p>
            </body>
            </html>
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {resend_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": "onboarding@resend.dev",
                        "to": [self.admin_email],
                        "subject": f"Contact Form: {request.subject}",
                        "html": html_content
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print(f"✅ Contact form sent via Resend API to {self.admin_email}")
                    return True
                else:
                    print(f"❌ Resend API error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Resend API error: {str(e)}")
            return False

    async def _send_via_formspree(self, request: ContactFormRequest) -> bool:
        """Send contact form via Formspree (free tier)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.formspree_endpoint,
                    data={
                        "name": request.name,
                        "email": request.email,
                        "subject": request.subject,
                        "message": request.message,
                        "_subject": f"Contact Form: {request.subject}"
                    },
                    timeout=10.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"Formspree error: {str(e)}")
            return False
    
    async def _send_via_smtp(self, request: ContactFormRequest) -> bool:
        """Send contact form via SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.admin_email
            msg['Subject'] = f"Contact Form: {request.subject}"
            
            body = f"""
            New contact form submission:
            
            Name: {request.name}
            Email: {request.email}
            Subject: {request.subject}
            
            Message:
            {request.message}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"SMTP error: {str(e)}")
            return False
    
    async def send_usage_alert(self, user_id: str, email: str, usage_percentage: int) -> bool:
        """Send usage alert when user approaches limit"""
        try:
            subject = f"Usage Alert - {usage_percentage}% of daily limit reached"
            message = f"""
            Hello,
            
            You have used {usage_percentage}% of your daily query limit.
            You can continue using the service, but please be mindful of your usage.
            
            Best regards,
            Your AI Knowledge Assistant Team
            """
            
            request = ContactFormRequest(
                name="System Alert",
                email="system@yourdomain.com",
                subject=subject,
                message=message
            )
            
            return await self.send_contact_form_notification(request)
            
        except Exception as e:
            print(f"Failed to send usage alert: {str(e)}")
            return False
    
    async def send_admin_notification(self, subject: str, message: str) -> bool:
        """Send notification to admin"""
        try:
            request = ContactFormRequest(
                name="System",
                email="system@yourdomain.com",
                subject=subject,
                message=message
            )
            
            return await self.send_contact_form_notification(request)
            
        except Exception as e:
            print(f"Failed to send admin notification: {str(e)}")
            return False 