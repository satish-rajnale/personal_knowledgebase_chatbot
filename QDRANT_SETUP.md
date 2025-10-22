# 🗄️ Qdrant Cloud Setup Guide

This guide will help you set up Qdrant Cloud for free to use as your vector database.

## 📋 Prerequisites

1. **Email Account** - For Qdrant Cloud registration
2. **Credit Card** - Required for verification (no charges on free tier)

## 🚀 Step-by-Step Setup

### Step 1: Sign Up for Qdrant Cloud

1. Go to [cloud.qdrant.io](https://cloud.qdrant.io)
2. Click "Get Started" or "Sign Up"
3. Enter your email and create a password
4. Verify your email address
5. Add payment method (required for verification, no charges on free tier)

### Step 2: Create Your First Cluster

1. **Log in** to Qdrant Cloud dashboard
2. Click **"Create Cluster"**
3. Choose **"Free"** plan
4. Select a **region** close to your users (e.g., US East, Europe)
5. Give your cluster a **name** (e.g., "knowledgebase-vectors")
6. Click **"Create Cluster"**

### Step 3: Get Connection Details

After cluster creation, you'll get:

1. **Cluster URL**: `https://your-cluster-id.qdrant.io`
2. **API Key**: Generated automatically
3. **Collection Name**: You'll create this in your app

**Save these details!** You'll need them for your backend configuration.

### Step 4: Configure Your Backend

Update your backend environment variables:

```bash
# In Railway or your deployment platform
QDRANT_URL=https://your-cluster-id.qdrant.io
QDRANT_API_KEY=your_api_key_here
QDRANT_COLLECTION_NAME=knowledgebase
```

### Step 5: Test the Connection

Your backend will automatically:
1. Connect to Qdrant Cloud
2. Create the collection if it doesn't exist
3. Start storing vectors

## 🔧 Alternative: Self-Hosted Qdrant

If you prefer to host Qdrant yourself, here are the options:

### Railway Deployment

1. **Create new Railway project**
2. **Add service** → **Deploy from Docker image**
3. **Use image**: `qdrant/qdrant:latest`
4. **Add environment variables**:
   ```
   QDRANT__SERVICE__HTTP_PORT=6333
   QDRANT__SERVICE__GRPC_PORT=6334
   ```
5. **Deploy** and get the service URL

### Render Deployment

1. **Create new Web Service** on Render
2. **Connect GitHub repository** with Qdrant Dockerfile
3. **Build Command**: `docker build -t qdrant .`
4. **Start Command**: `docker run -p 6333:6333 qdrant/qdrant`
5. **Deploy** and get the service URL

## 📊 Free Tier Limitations

### Qdrant Cloud Free Tier:
- **Storage**: 1GB
- **Requests**: 1000/day
- **Clusters**: 1
- **Collections**: Unlimited
- **Vectors**: Up to 1GB total

### Railway Free Tier:
- **Credit**: $5/month
- **Storage**: 1GB persistent disk
- **Uptime**: Always on

### Render Free Tier:
- **Hours**: 750/month
- **Storage**: 1GB persistent disk
- **Uptime**: Sleeps after 15 minutes

## 🎯 Recommended Setup

**For your Personal Knowledgebase Chatbot:**

1. **Use Qdrant Cloud** (recommended)
   - No setup required
   - Managed service
   - Free tier is sufficient for personal use
   - Automatic backups and security

2. **Environment Variables**:
   ```bash
   QDRANT_URL=https://your-cluster-id.qdrant.io
   QDRANT_API_KEY=your_api_key_here
   QDRANT_COLLECTION_NAME=knowledgebase
   ```

3. **Collection Configuration**:
   - **Name**: `knowledgebase`
   - **Vector Size**: 384 (for sentence-transformers/all-MiniLM-L6-v2)
   - **Distance**: Cosine

## 🔍 Monitoring Your Usage

### Qdrant Cloud Dashboard:
- **Metrics**: Requests, storage usage
- **Collections**: View and manage collections
- **API Keys**: Manage authentication
- **Logs**: View request logs

### Check Usage:
1. Log into Qdrant Cloud dashboard
2. Go to your cluster
3. View **"Metrics"** tab
4. Monitor **"Storage"** and **"Requests"**

## 🚨 Important Notes

### Security:
- **API Key**: Keep it secure, don't commit to GitHub
- **Environment Variables**: Use your deployment platform's secure storage
- **HTTPS**: Qdrant Cloud provides SSL automatically

### Performance:
- **Free tier limits**: 1000 requests/day
- **Storage**: 1GB should be sufficient for personal documents
- **Upgrade**: Easy to upgrade if you need more

### Backup:
- **Qdrant Cloud**: Automatic backups included
- **Self-hosted**: Set up your own backup strategy

## 🎉 Success!

After setup, your vector database will be:
- **Accessible**: From anywhere in the world
- **Secure**: HTTPS and API key authentication
- **Scalable**: Easy to upgrade when needed
- **Reliable**: Managed service with uptime guarantees

Your Personal Knowledgebase Chatbot will now have a professional vector database for storing and searching your document embeddings! 