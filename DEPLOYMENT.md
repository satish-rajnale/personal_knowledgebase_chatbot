# 🚀 Deployment Guide

This guide will help you deploy your Personal Knowledgebase Chatbot for free.

## 📋 Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Railway Account** - For backend deployment (free tier)
3. **Vercel Account** - For frontend deployment (free tier)
4. **Qdrant Cloud Account** - For vector database (free tier)

## 🎯 Step-by-Step Deployment

### 1. Backend Deployment (Railway)

#### Step 1: Sign up for Railway

- Go to [railway.app](https://railway.app)
- Sign up with your GitHub account
- Get $5 free credit monthly

#### Step 2: Deploy Backend

1. Click "New Project" → "Deploy from GitHub repo"
2. Select your repository
3. Railway will auto-detect the Dockerfile in `backend/`
4. Add environment variables:
   ```
   OPENROUTER_API_KEY=your_openrouter_key
   NOTION_TOKEN=your_notion_token
   NOTION_DATABASE_ID=your_page_id
   QDRANT_URL=https://your-qdrant-cluster.qdrant.io
   QDRANT_COLLECTION_NAME=knowledgebase
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   ```

#### Step 3: Get Backend URL

- Railway will provide a URL like: `https://your-app.railway.app`
- Save this URL for frontend configuration

### 2. Vector Database (Qdrant Cloud)

#### Step 1: Sign up for Qdrant Cloud

- Go to [cloud.qdrant.io](https://cloud.qdrant.io)
- Sign up for free tier
- Create a new cluster

#### Step 2: Configure Qdrant

1. Get your cluster URL and API key
2. Update backend environment variables:
   ```
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your_qdrant_api_key
   ```

### 3. Frontend Deployment (Vercel)

#### Step 1: Sign up for Vercel

- Go to [vercel.com](https://vercel.com)
- Sign up with your GitHub account

#### Step 2: Deploy Frontend

1. Click "New Project" → "Import Git Repository"
2. Select your repository
3. Configure build settings:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

#### Step 3: Configure Environment Variables

Add these environment variables in Vercel:

```
REACT_APP_API_URL=https://your-backend-url.railway.app
```

#### Step 4: Deploy

- Click "Deploy"
- Vercel will build and deploy your React app
- You'll get a URL like: `https://your-app.vercel.app`

### 4. Update Configuration

#### Update Backend CORS

In Railway, update the `CORS_ORIGINS` environment variable:

```
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

#### Update Frontend API URL

In Vercel, ensure `REACT_APP_API_URL` points to your Railway backend:

```
REACT_APP_API_URL=https://your-backend-url.railway.app
```

## 🔧 Alternative Deployment Options

### Render (Backend Alternative)

- Go to [render.com](https://render.com)
- Connect GitHub repository
- Choose "Web Service"
- Set build command: `pip install -r requirements.txt`
- Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Netlify (Frontend Alternative)

- Go to [netlify.com](https://netlify.com)
- Drag and drop your `frontend/build` folder
- Or connect GitHub for auto-deployment

## 🚨 Important Notes

### Free Tier Limitations

- **Railway**: $5/month credit (usually sufficient for small apps)
- **Vercel**: Unlimited deployments, 100GB bandwidth
- **Qdrant Cloud**: 1GB storage, 1000 requests/day
- **Render**: Sleeps after 15 minutes of inactivity

### Environment Variables

Make sure to set all required environment variables:

- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `NOTION_TOKEN` - Your Notion integration token
- `NOTION_DATABASE_ID` - Your Notion page ID
- `QDRANT_URL` - Your Qdrant cluster URL
- `CORS_ORIGINS` - Your frontend domain

### Database Considerations

- **SQLite**: Works for small apps, but consider PostgreSQL for production
- **Vector Database**: Qdrant Cloud free tier is sufficient for testing

## 🎉 Success!

After deployment, your app will be available at:

- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-app.railway.app`
- **API Docs**: `https://your-app.railway.app/docs`

## 🔄 Continuous Deployment

Both Railway and Vercel support automatic deployments:

- Push to your GitHub repository
- Both platforms will automatically rebuild and deploy
- No manual intervention needed

## 📞 Support

If you encounter issues:

1. Check the deployment logs in Railway/Vercel
2. Verify environment variables are set correctly
3. Test the API endpoints using the `/docs` endpoint
4. Check CORS configuration if frontend can't connect to backend
