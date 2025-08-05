#!/usr/bin/env python3
"""
Email Configuration Test Script
Tests your SMTP settings to ensure emails can be sent successfully.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_smtp_connection():
    """Test SMTP connection and send a test email"""
    
    # Get environment variables
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    admin_email = os.getenv('ADMIN_EMAIL')
    
    if not all([smtp_host, smtp_username, smtp_password, admin_email]):
        print("❌ Missing email configuration. Please check your .env file.")
        print("Required variables: SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, ADMIN_EMAIL")
        return False
    
    print(f"🔧 Testing SMTP connection...")
    print(f"   Host: {smtp_host}:{smtp_port}")
    print(f"   Username: {smtp_username}")
    print(f"   Admin Email: {admin_email}")
    
    try:
        # Create message
        msg = MIMEMultipart()
        # For Resend, use admin_email as sender if it's different from smtp_username
        sender_email = admin_email if smtp_username == 'resend' else smtp_username
        msg['From'] = sender_email
        msg['To'] = admin_email
        msg['Subject'] = f"🧪 Email Test - AI Knowledge Assistant ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        
        body = f"""
        🎉 Email configuration test successful!
        
        This is a test email from your AI Knowledge Assistant.
        
        📧 Test Details:
        - Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        - SMTP Host: {smtp_host}
        - SMTP Port: {smtp_port}
        - From: {smtp_username}
        - To: {admin_email}
        
        ✅ Your email configuration is working correctly!
        
        You can now receive:
        - Contact form notifications
        - Usage alerts
        - System notifications
        
        Best regards,
        AI Knowledge Assistant
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        print("📡 Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        
        # Login
        print("🔐 Authenticating...")
        server.login(smtp_username, smtp_password)
        
        # Send email
        print("📤 Sending test email...")
        text = msg.as_string()
        # For Resend, use admin_email as sender
        sender = admin_email if smtp_username == 'resend' else smtp_username
        server.sendmail(sender, admin_email, text)
        
        # Close connection
        server.quit()
        
        print("✅ Email test successful!")
        print(f"📧 Test email sent to: {admin_email}")
        print("   Check your inbox for the test message.")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("   Please check your SMTP_USERNAME and SMTP_PASSWORD")
        if "gmail" in smtp_host.lower():
            print("   For Gmail: Make sure you're using an App Password, not your regular password")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ Connection failed: {e}")
        print("   Please check your SMTP_HOST and SMTP_PORT")
        return False
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def main():
    """Main function"""
    print("🧪 AI Knowledge Assistant - Email Configuration Test")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and configure your email settings.")
        return
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file loaded successfully")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment variables")
    
    # Test email configuration
    success = test_smtp_connection()
    
    if success:
        print("\n🎉 Email configuration is working correctly!")
        print("   Your app can now send email notifications.")
    else:
        print("\n❌ Email configuration failed!")
        print("   Please check the EMAIL_SETUP.md guide for troubleshooting.")
        print("   Common issues:")
        print("   - Gmail: Use App Password, not regular password")
        print("   - SendGrid: Check API key permissions")
        print("   - Mailgun: Verify domain or use sandbox domain")

if __name__ == "__main__":
    main() 