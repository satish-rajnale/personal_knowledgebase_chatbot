# 🔗 Notion OAuth Setup Guide

## 🎯 Overview

To enable Notion integration in your AI Knowledge Assistant, you need to set up OAuth credentials in your Notion workspace and configure them in your application.

## 📋 Prerequisites

1. **Notion Account**: You need a Notion account with admin access to create integrations
2. **Domain**: Your application needs to be accessible via HTTPS (for production) or localhost (for development)

## 🚀 Step-by-Step Setup

### **1. Create Notion Integration**

1. **Go to [Notion Integrations](https://www.notion.so/my-integrations)**
2. **Click "New integration"**
3. **Fill in the details:**
   - **Name**: `AI Knowledge Assistant` (or your preferred name)
   - **Associated workspace**: Select your workspace
   - **Capabilities**: Enable the following:
     - ✅ **Read content**
     - ✅ **Update content** (optional, for future features)
     - ✅ **Insert content** (optional, for future features)
4. **Click "Submit"**

### **2. Get Your Credentials**

After creating the integration, you'll get:

- **Internal Integration Token** (you don't need this for OAuth)
- **OAuth Client ID** (you need this)
- **OAuth Client Secret** (you need this)

### **3. Configure OAuth Settings**

1. **In your integration settings, go to "OAuth" tab**
2. **Add Redirect URIs:**
   - **Development**: `http://localhost:3000/auth/notion/callback`
   - **Production**: `https://yourdomain.com/auth/notion/callback`
3. **Save the settings**

### **4. Update Your Environment Variables**

Add these to your `.env` file:

```bash
# Notion OAuth Configuration
NOTION_CLIENT_ID=your_notion_client_id_here
NOTION_CLIENT_SECRET=your_notion_client_secret_here
NOTION_REDIRECT_URI=http://localhost:3000/auth/notion/callback
```

### **5. Update Frontend Callback Handler**

The frontend needs to handle the OAuth callback. Add this to your React app:

```javascript
// In your App.js or routing configuration
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    // Handle Notion OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');

    if (code && state) {
      // Exchange code for token
      handleNotionCallback(code, state);
    }
  }, []);

  const handleNotionCallback = async (code, state) => {
    try {
      const response = await fetch('/api/v1/auth/notion/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ code, state })
      });

      if (response.ok) {
        // Redirect to dashboard or show success message
        window.location.href = '/dashboard';
      }
    } catch (error) {
      console.error('Notion callback error:', error);
    }
  };

  return (
    // Your app components
  );
}
```

## 🔧 Troubleshooting

### **Common Issues:**

1. **"Notion integration not configured"**

   - Check that `NOTION_CLIENT_ID` and `NOTION_CLIENT_SECRET` are set in your `.env` file
   - Restart your backend server after updating environment variables

2. **"Invalid redirect URI"**

   - Make sure the redirect URI in your Notion integration matches exactly
   - Check for trailing slashes or protocol mismatches

3. **"OAuth token exchange failed"**

   - Verify your client ID and secret are correct
   - Check that the redirect URI matches between frontend and backend
   - Ensure your integration has the correct permissions

4. **"User not found" or authentication errors**
   - Make sure the user is logged in before trying to connect Notion
   - Check that the JWT token is valid

### **Testing the Integration:**

1. **Start your backend server**
2. **Start your frontend application**
3. **Log in to your application**
4. **Go to the Notion integration section**
5. **Click "Connect Notion"**
6. **You should be redirected to Notion's authorization page**
7. **Authorize the integration**
8. **You should be redirected back to your app**

## 🎯 Next Steps

Once OAuth is working:

1. **Test the connection** by syncing a few pages
2. **Set up your Notion template** (see `NOTION_TEMPLATE.md`)
3. **Configure production settings** for deployment
4. **Add error handling** for edge cases

## 📚 Additional Resources

- [Notion API Documentation](https://developers.notion.com/)
- [Notion OAuth Guide](https://developers.notion.com/docs/create-a-notion-integration#step-2-save-the-credentials)
- [Notion Integration Capabilities](https://developers.notion.com/docs/create-a-notion-integration#capabilities)

---

**Need help?** Check the troubleshooting section above or refer to the Notion developer documentation.
