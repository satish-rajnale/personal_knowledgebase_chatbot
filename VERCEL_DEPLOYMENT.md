# Frontend-Only Vercel Deployment Guide

This guide will help you deploy only the frontend (React app) to Vercel while keeping the backend on Railway.

## Prerequisites

- ✅ Backend deployed on Railway
- ✅ GitHub repository with frontend code
- ✅ Vercel account

## Configuration Files

### 1. vercel.json (Root Level)

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/build",
  "framework": "create-react-app",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-railway-app.railway.app/api/$1"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "https://your-railway-app.railway.app"
  }
}
```

**Key Points:**
- `buildCommand`: Navigates to frontend directory and builds
- `outputDirectory`: Points to the built React app
- `rewrites`: Proxies API calls to Railway backend
- `env`: Sets the API URL environment variable

### 2. frontend/package.json

```json
{
  "name": "knowledgebase-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
  // ... other configurations
}
```

**Important:** No `proxy` field in package.json (removed for Vercel deployment)

### 3. frontend/src/services/api.js

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

## Deployment Steps

### Step 1: Prepare Repository

1. **Ensure vercel.json is in root directory**
2. **Remove proxy from frontend/package.json** (already done)
3. **Update Railway URL in vercel.json** with your actual Railway app URL

### Step 2: Deploy to Vercel

1. **Go to [Vercel](https://vercel.com)**
2. **Click "New Project"**
3. **Import your GitHub repository**
4. **Configure project settings:**
   - **Framework Preset**: `Create React App`
   - **Root Directory**: Leave empty (root)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/build`
   - **Install Command**: Leave empty (handled in build command)

### Step 3: Set Environment Variables

In Vercel dashboard → Project Settings → Environment Variables:

```bash
REACT_APP_API_URL=https://your-railway-app.railway.app
```

### Step 4: Deploy

1. **Click "Deploy"**
2. **Wait for build to complete**
3. **Test the deployed application**

## Configuration Details

### Build Process

1. **Vercel reads vercel.json**
2. **Executes**: `cd frontend && npm install && npm run build`
3. **Serves**: `frontend/build` directory
4. **Applies**: Rewrites for API proxying

### API Proxying

The `rewrites` configuration in vercel.json:

```json
{
  "source": "/api/(.*)",
  "destination": "https://your-railway-app.railway.app/api/$1"
}
```

**How it works:**
- Frontend makes request to `/api/v1/chat`
- Vercel rewrites it to `https://your-railway-app.railway.app/api/v1/chat`
- Backend processes the request
- Response is returned to frontend

### Environment Variables

- **Local Development**: Uses `http://localhost:8000`
- **Vercel Production**: Uses Railway URL from environment variable
- **Fallback**: Defaults to localhost if not set

## Testing Deployment

### 1. Test Frontend

Visit your Vercel URL and test:
- ✅ Page loads without errors
- ✅ File upload functionality
- ✅ Chat with AI
- ✅ Notion sync

### 2. Test API Proxying

```bash
# Test API endpoint through Vercel
curl https://your-vercel-app.vercel.app/api/v1/health

# Should return the same as direct Railway call
curl https://your-railway-app.railway.app/api/v1/health
```

### 3. Check Network Tab

In browser DevTools → Network tab:
- API calls should go to your Vercel domain
- Vercel should proxy them to Railway
- No CORS errors should occur

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check if `frontend/` directory exists
   - Verify `package.json` is in frontend directory
   - Check for syntax errors in React code

2. **API Calls Fail**
   - Verify Railway URL is correct in vercel.json
   - Check environment variable is set in Vercel
   - Ensure backend is running on Railway

3. **CORS Errors**
   - Update Railway CORS_ORIGINS to include Vercel domain
   - Check if API proxying is working correctly

4. **Environment Variables Not Working**
   - Ensure variable name starts with `REACT_APP_`
   - Redeploy after setting environment variables
   - Check Vercel build logs

### Debug Steps

1. **Check Vercel Build Logs**
   - Go to Vercel dashboard → Deployments
   - Click on latest deployment
   - Check build logs for errors

2. **Verify Configuration**
   ```bash
   # Test local build
   cd frontend
   npm install
   npm run build
   ```

3. **Check Environment Variables**
   - Vercel dashboard → Settings → Environment Variables
   - Ensure `REACT_APP_API_URL` is set correctly

## File Structure

```
your-repo/
├── vercel.json              # Vercel configuration
├── frontend/                # React application
│   ├── package.json         # Frontend dependencies
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js       # API service (uses env var)
│   │   └── ...
│   └── ...
├── backend/                 # Not deployed to Vercel
└── ...
```

## Benefits of This Setup

1. **Separation of Concerns**: Frontend and backend are separate
2. **Independent Scaling**: Each can scale independently
3. **Easy Updates**: Update frontend without affecting backend
4. **Cost Effective**: Use free tiers for both platforms
5. **No CORS Issues**: API proxying handles cross-origin requests

## Next Steps

1. **Custom Domain**: Configure custom domain in Vercel
2. **Analytics**: Enable Vercel Analytics
3. **Performance**: Monitor Core Web Vitals
4. **CI/CD**: Automatic deployments on git push 