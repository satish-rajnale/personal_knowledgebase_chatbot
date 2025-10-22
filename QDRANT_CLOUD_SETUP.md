# 🚀 Quick Qdrant Cloud Setup for Railway

## 🔧 Fix the Qdrant Connection Error

The error shows your app is trying to connect to `http://qdrant:6333` (local Docker service) instead of your Qdrant Cloud cluster.

## 📋 Step 1: Get Your Qdrant Cloud Details

1. **Log into Qdrant Cloud**: [cloud.qdrant.io](https://cloud.qdrant.io)
2. **Go to your cluster**
3. **Copy these details**:
   - **Cluster URL**: `https://your-cluster-id.qdrant.io`
   - **API Key**: Your cluster's API key

## 🎯 Step 2: Update Railway Environment Variables

In your Railway project dashboard:

1. **Go to Variables tab**
2. **Add/Update these variables**:

```bash
QDRANT_URL=https://your-actual-cluster-id.qdrant.io
QDRANT_API_KEY=your_actual_api_key_here
QDRANT_COLLECTION_NAME=knowledgebase
```

## 🔍 Step 3: Verify Your Qdrant Cloud URL

Your Qdrant Cloud URL should look like:

- ✅ `https://abc123-def456.qdrant.io`
- ❌ `http://qdrant:6333` (local Docker)
- ❌ `http://localhost:6333` (local)

## 🚀 Step 4: Redeploy

1. **Save the environment variables** in Railway
2. **Redeploy your service**
3. **Check the logs** - should see:
   ```
   🔗 Connected to Qdrant Cloud: https://your-cluster-id.qdrant.io
   ✅ Created Qdrant collection: knowledgebase
   ```

## 🎯 Example Configuration

**In Railway Variables:**

```
QDRANT_URL=https://abc123-def456.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
QDRANT_COLLECTION_NAME=knowledgebase
```

## ❌ Common Issues

### Issue: "Name or service not known"

**Cause**: Wrong Qdrant URL
**Fix**: Use your Qdrant Cloud URL, not local Docker URL

### Issue: "Authentication failed"

**Cause**: Wrong or missing API key
**Fix**: Copy the correct API key from Qdrant Cloud dashboard

### Issue: "Connection timeout"

**Cause**: Network issues or wrong URL
**Fix**: Verify URL format and try again

## ✅ Success Indicators

When working correctly, you'll see:

```
🔗 Connected to Qdrant Cloud: https://your-cluster-id.qdrant.io
✅ Created Qdrant collection: knowledgebase
✅ Database and vector store initialized successfully
```

## 🆘 Need Help?

1. **Check Qdrant Cloud dashboard** for correct URL and API key
2. **Verify Railway environment variables** are set correctly
3. **Redeploy** after updating variables
4. **Check Railway logs** for connection status
