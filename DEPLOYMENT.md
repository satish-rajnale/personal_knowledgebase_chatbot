# Deployment Guide

This guide will help you deploy your Personal Knowledgebase Chatbot to free cloud platforms.

## Architecture

- **Backend (FastAPI)**: Railway
- **Frontend (React)**: Vercel  
- **Vector Database**: Qdrant Cloud
- **Port Configuration**: Dynamic (uses Railway's PORT environment variable)

## Backend Deployment (Railway)

### 1. Prepare Your Repository

Ensure your repository has the following files:
- `Dockerfile.optimized` - Multi-stage Docker build
- `railway.toml` - Railway configuration
- `.railwayignore` - Files to exclude from Railway build
- `backend/` - Your FastAPI application

### 2. Deploy to Railway

1. **Sign up/Login**: Go to [Railway](https://railway.app) and sign up with GitHub
2. **Create Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select Repository**: Choose your personal knowledgebase repository
4. **Deploy**: Railway will automatically detect the Dockerfile and deploy

### 3. Configure Environment Variables

In Railway dashboard, go to your service → Variables tab and add:

```bash
# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster-id.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# LLM Configuration  
OPENROUTER_API_KEY=your_openrouter_api_key

# Notion Integration
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_notion_page_id

# App Configuration
DEBUG=false
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

### 4. Railway Configuration

The `railway.toml` file configures:
- **Health checks**: Uses `/health` endpoint
- **Port**: Automatically uses Railway's `PORT` environment variable
- **Restart policy**: Automatic restart on failure

## Frontend Deployment (Vercel)

### 1. Prepare Frontend

Ensure your frontend has:
- `vercel.json` - Vercel configuration
- Updated API URL in environment variables

### 2. Deploy to Vercel

1. **Sign up/Login**: Go to [Vercel](https://vercel.com) and sign up with GitHub
2. **Import Project**: Click "New Project" → Import your repository
3. **Configure**: 
   - Framework Preset: `Create React App`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`

### 3. Configure Environment Variables

In Vercel dashboard, add:
```bash
REACT_APP_API_URL=https://your-railway-app.railway.app
```

## Vector Database (Qdrant Cloud)

### 1. Setup Qdrant Cloud

Follow the detailed guide in `QDRANT_SETUP.md`:
1. Sign up at [Qdrant Cloud](https://cloud.qdrant.io)
2. Create a free cluster
3. Get your connection details (URL + API Key)

### 2. Configure Backend

Update Railway environment variables with your Qdrant Cloud details.

## Port Configuration

The application automatically handles dynamic port assignment:

- **Local Development**: Uses port 8000 by default
- **Railway**: Uses the `PORT` environment variable provided by Railway
- **Docker**: Exposes port 8000, Railway maps it to their assigned port

### Configuration Files:

- `backend/app/core/config.py`: Reads `PORT` environment variable
- `backend/main.py`: Uses settings for port configuration
- `Dockerfile.optimized`: Exposes port 8000
- `backend/start.sh`: Starts uvicorn with dynamic port

## Testing Deployment

### 1. Test Backend Health

```bash
# Test Railway deployment
curl https://your-railway-app.railway.app/health

# Test detailed health
curl https://your-railway-app.railway.app/api/v1/health
```

### 2. Test Frontend

Visit your Vercel URL and test:
- File upload functionality
- Chat with AI
- Notion sync

### 3. Test Port Configuration

```bash
# Test local port configuration
python test_port_config.py

# Test health endpoints
python test_health.py https://your-railway-app.railway.app
```

## Troubleshooting

### Common Issues

1. **Port Binding Issues**
   - Ensure `API_HOST=0.0.0.0` in configuration
   - Verify Railway's `PORT` environment variable is set

2. **CORS Errors**
   - Update `CORS_ORIGINS` in Railway to include your Vercel domain
   - Ensure frontend `REACT_APP_API_URL` points to Railway

3. **Qdrant Connection Issues**
   - Verify `QDRANT_URL` and `QDRANT_API_KEY` are set correctly
   - Check Qdrant Cloud cluster is accessible

4. **Build Failures**
   - Check Railway logs for build errors
   - Verify Dockerfile paths are correct
   - Ensure all required files are present

### Free Tier Limitations

- **Railway**: 500 hours/month, 512MB RAM, 1GB storage
- **Vercel**: 100GB bandwidth/month, 100 serverless function executions/day
- **Qdrant Cloud**: 1GB storage, 1000 operations/second

## Monitoring

- **Railway**: Built-in logs and metrics
- **Vercel**: Analytics and function logs
- **Health Endpoints**: Use `/health` and `/api/v1/health` for monitoring

## Next Steps

1. Set up monitoring and alerts
2. Configure custom domains
3. Implement CI/CD pipelines
4. Add authentication if needed
