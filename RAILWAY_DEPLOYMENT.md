# 🚂 Railway Deployment Guide

## Overview

This guide explains how to deploy the AI Knowledge Assistant to Railway with automatic vector store initialization.

## ✅ Automatic Vector Store Initialization

The application now includes **automatic vector store initialization** that runs on every deployment:

### **How It Works:**

1. **Startup Event** (`backend/main.py`):
   ```python
   @app.on_event("startup")
   async def startup_event():
       """Initialize database and vector store on startup"""
       print("🚀 Starting up application...")
       
       # Initialize database
       await init_db()
       
       # Initialize vector store with proper indexing
       try:
           print("🔧 Initializing vector store...")
           await vector_store.init_collection()
           print("✅ Vector store initialized successfully")
       except Exception as e:
           print(f"⚠️ Warning: Vector store initialization failed: {e}")
           print("   The application will continue, but RAG features may not work properly")
       
       print("✅ Application startup complete")
   ```

2. **Vector Store Service** (`backend/app/services/vector_store.py`):
   - Automatically creates collection if it doesn't exist
   - Creates `user_id` index for filtering
   - Handles TF-IDF embedding generation
   - Provides fallback search methods

## 🚀 Deployment Steps

### **Step 1: Prepare Environment Variables**

Create a `.env` file in the root directory with your Railway configuration:

```bash
# LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
LLM_PROVIDER=openrouter
MODEL_NAME=openai/gpt-3.5-turbo

# Notion OAuth Configuration
NOTION_CLIENT_ID=your_notion_client_id_here
NOTION_CLIENT_SECRET=your_notion_client_secret_here
NOTION_REDIRECT_URI=https://your-app.railway.app/auth/notion/callback

# Vector Database (Choose one option)

# Option A: Qdrant Cloud (Recommended for production)
QDRANT_URL=https://your-qdrant-cloud-url.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=knowledgebase

# Option B: Local Qdrant (For testing)
# QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=
# QDRANT_COLLECTION_NAME=knowledgebase

# App Configuration
DEBUG=false
CORS_ORIGINS=https://your-frontend.vercel.app
API_HOST=0.0.0.0
API_PORT=8000

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-in-production
DAILY_QUERY_LIMIT=10

# Database
DATABASE_URL=sqlite:///./chat_history.db

# Email Configuration
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USERNAME=resend
SMTP_PASSWORD=your_resend_api_key
ADMIN_EMAIL=your_email@domain.com
RESEND_API_KEY=your_resend_api_key

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
```

### **Step 2: Deploy to Railway**

1. **Connect your repository** to Railway
2. **Set environment variables** in Railway dashboard
3. **Deploy** the application

### **Step 3: Monitor Deployment Logs**

Watch the Railway deployment logs for these messages:

```
🚀 Starting up application...
📊 Initializing database...
✅ Database initialized
🔧 Initializing vector store...
✅ Vector store initialized successfully
✅ Application startup complete
```

## 🔧 Manual Setup (If Needed)

If automatic initialization fails, you can manually run the setup:

### **Option 1: Use Railway Console**

1. Go to your Railway project
2. Open the **Console** tab
3. Run the setup script:
   ```bash
   cd backend
   python railway_startup.py
   ```

### **Option 2: Use Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Connect to your project
railway link

# Run setup script
railway run python backend/railway_startup.py
```

## 🧪 Testing After Deployment

### **1. Health Check**
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "Personal Knowledgebase Chatbot API is running",
  "version": "1.0.0"
}
```

### **2. Vector Store Debug**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://your-app.railway.app/api/v1/debug/vector-store
```

Expected response:
```json
{
  "user_id": "user_123",
  "collection_info": {
    "name": "knowledgebase",
    "vectors_count": 0,
    "points_count": 0
  },
  "user_documents_count": 0,
  "documents": []
}
```

### **3. Test Chat**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}' \
  https://your-app.railway.app/api/v1/chat
```

## 🚨 Troubleshooting

### **Issue 1: Vector Store Initialization Fails**

**Symptoms:**
```
⚠️ Warning: Vector store initialization failed: Connection refused
```

**Solutions:**
1. Check Qdrant URL and API key
2. Verify network connectivity
3. Use local Qdrant for testing

### **Issue 2: TF-IDF Embedding Errors**

**Symptoms:**
```
❌ Error generating embeddings: max_df corresponds to < documents than min_df
```

**Solutions:**
- The application now handles this automatically with fallback methods
- Check if you have enough documents for meaningful embeddings

### **Issue 3: User Filter Not Working**

**Symptoms:**
```
❌ Error searching vector store: Index required but not found for "user_id"
```

**Solutions:**
- The application now creates the index automatically
- If it fails, the search falls back to Python filtering

### **Issue 4: Notion Sync Issues**

**Symptoms:**
```
❌ Error syncing Notion: OAuth token exchange failed
```

**Solutions:**
1. Check Notion OAuth configuration
2. Verify redirect URI matches Railway URL
3. Ensure Notion integration has proper permissions

## 📊 Monitoring

### **Railway Metrics**
- Monitor CPU and memory usage
- Check request logs for errors
- Watch for rate limiting issues

### **Application Logs**
- Vector store initialization status
- Search query performance
- Notion sync success/failure rates

### **Health Endpoints**
- `/health` - Basic health check
- `/api/v1/health` - Detailed service status
- `/api/v1/debug/vector-store` - Vector store status

## 🔄 Continuous Deployment

The application is designed to work with Railway's continuous deployment:

1. **Automatic initialization** runs on every deployment
2. **Graceful error handling** prevents deployment failures
3. **Fallback mechanisms** ensure functionality even if some services fail
4. **Health checks** verify deployment success

## 🎉 Success Indicators

Your Railway deployment is successful when you see:

1. ✅ **Startup logs** show successful initialization
2. ✅ **Health check** returns `200 OK`
3. ✅ **Vector store debug** shows proper collection info
4. ✅ **Chat API** responds with AI-generated responses
5. ✅ **Notion sync** works for authenticated users

The vector store will now automatically initialize on every Railway deployment! 🚂✨ 