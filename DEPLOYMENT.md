# Deployment Guide - AI Knowledge Assistant SaaS

This guide covers deploying the AI Knowledge Assistant as a multi-user SaaS application using free-tier services.

## 🚀 Quick Deployment Overview

### Recommended Stack (Free Tier)
- **Backend**: Railway (free up to $5/month)
- **Frontend**: Vercel (free for 1 team, 100GB bandwidth/month)
- **Vector DB**: Qdrant Cloud (free tier)
- **Database**: SQLite (included) or NeonDB (free PostgreSQL)
- **Email**: Formspree (free tier) or SMTP

### Estimated Monthly Cost
- **Free Tier**: $0/month
- **Growth Tier**: $10-20/month (when you exceed free limits)

## 📋 Prerequisites

Before deployment, ensure you have:

1. **GitHub Account**: For code repository
2. **Railway Account**: For backend hosting
3. **Vercel Account**: For frontend hosting
4. **Qdrant Cloud Account**: For vector database
5. **Notion Account**: For OAuth integration
6. **OpenRouter Account**: For LLM API

## 🔧 Step 1: Prepare Your Repository

### 1.1 Fork/Clone the Repository
```bash
git clone <your-repo-url>
cd peronal_knowledgebase
```

### 1.2 Update Configuration
Create environment-specific configuration files:

**Backend Environment Variables** (`.env.production`):
```env
# LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
MODEL_NAME=openai/gpt-3.5-turbo

# Notion Integration (OAuth)
NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret
NOTION_REDIRECT_URI=https://your-frontend-domain.vercel.app/auth/notion/callback

# Vector Database
QDRANT_URL=https://your-qdrant-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=knowledgebase

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-in-production
DAILY_QUERY_LIMIT=10

# App Configuration
DEBUG=false
CORS_ORIGINS=https://your-frontend-domain.vercel.app
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:////app/data/chat_history.db

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ADMIN_EMAIL=admin@yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
```

**Frontend Environment Variables** (`.env.production`):
```env
REACT_APP_API_URL=https://your-backend-domain.railway.app
```

## 🚂 Step 2: Deploy Backend to Railway

### 2.1 Connect Railway to GitHub
1. Go to [Railway](https://railway.app/)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

### 2.2 Configure Railway Settings
1. **Set Root Directory**: `backend`
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `python main.py`

### 2.3 Set Environment Variables
In Railway dashboard, go to "Variables" tab and add:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret
NOTION_REDIRECT_URI=https://your-frontend-domain.vercel.app/auth/notion/callback
QDRANT_URL=https://your-qdrant-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
JWT_SECRET=your-super-secret-jwt-key
DAILY_QUERY_LIMIT=10
DEBUG=false
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

### 2.4 Deploy
1. Railway will automatically deploy when you push to main branch
2. Get your backend URL from Railway dashboard
3. Test the health endpoint: `https://your-backend.railway.app/health`

## 🌐 Step 3: Deploy Frontend to Vercel

### 3.1 Connect Vercel to GitHub
1. Go to [Vercel](https://vercel.com/)
2. Sign in with GitHub
3. Click "New Project"
4. Import your repository

### 3.2 Configure Vercel Settings
1. **Framework Preset**: Create React App
2. **Root Directory**: `frontend`
3. **Build Command**: `npm run build`
4. **Output Directory**: `build`

### 3.3 Set Environment Variables
In Vercel dashboard, go to "Environment Variables" and add:

```env
REACT_APP_API_URL=https://your-backend-domain.railway.app
```

### 3.4 Deploy
1. Vercel will automatically deploy when you push to main branch
2. Get your frontend URL from Vercel dashboard
3. Test the application: `https://your-frontend.vercel.app`

## 🗄️ Step 4: Set Up Qdrant Cloud

### 4.1 Create Qdrant Cloud Account
1. Go to [Qdrant Cloud](https://cloud.qdrant.io/)
2. Sign up for free account
3. Create a new cluster

### 4.2 Configure Cluster
1. **Region**: Choose closest to your users
2. **Size**: Start with free tier (1GB)
3. **Name**: `ai-knowledge-assistant`

### 4.3 Get Connection Details
1. Copy the cluster URL
2. Generate an API key
3. Update Railway environment variables

## 🔗 Step 5: Configure Notion OAuth

### 5.1 Create Notion Integration
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Set name: "AI Knowledge Assistant"
4. Set redirect URI: `https://your-frontend.vercel.app/auth/notion/callback`

### 5.2 Get OAuth Credentials
1. Copy Client ID
2. Copy Client Secret
3. Update Railway environment variables

## 📧 Step 6: Set Up Email (Optional)

### Option A: Formspree (Recommended for Free Tier)
1. Go to [Formspree](https://formspree.io/)
2. Create free account
3. Create a new form
4. Copy the form endpoint
5. Update the email service configuration

### Option B: SMTP (Gmail)
1. Enable 2-factor authentication on Gmail
2. Generate app password
3. Update Railway environment variables

## 🔒 Step 7: Security Configuration

### 7.1 Generate Secure JWT Secret
```bash
# Generate a secure random string
openssl rand -base64 32
```

### 7.2 Update CORS Settings
Ensure CORS_ORIGINS includes your frontend domain:
```env
CORS_ORIGINS=https://your-frontend.vercel.app
```

### 7.3 Set Production Environment
```env
DEBUG=false
```

## 🧪 Step 8: Testing Your Deployment

### 8.1 Test Backend Health
```bash
curl https://your-backend.railway.app/health
```

### 8.2 Test Frontend
1. Visit your Vercel URL
2. Try anonymous login
3. Test Notion connection
4. Test chat functionality

### 8.3 Test Email
1. Submit contact form
2. Check if email is received

## 📊 Step 9: Monitoring and Analytics

### 9.1 Railway Monitoring
- Check Railway dashboard for logs
- Monitor resource usage
- Set up alerts for errors

### 9.2 Vercel Analytics
- Enable Vercel Analytics
- Monitor frontend performance
- Track user interactions

### 9.3 Application Monitoring
- Check `/health` endpoint regularly
- Monitor database size
- Track API usage

## 🔄 Step 10: Continuous Deployment

### 10.1 GitHub Actions (Optional)
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: |
          # Railway CLI deployment
      - name: Deploy to Vercel
        run: |
          # Vercel deployment
```

### 10.2 Environment Management
- Use different branches for staging/production
- Set up environment-specific variables
- Test changes in staging first

## 🚀 Step 11: Scaling Considerations

### 11.1 When to Upgrade
- **Railway**: When you exceed free tier limits
- **Vercel**: When you exceed bandwidth limits
- **Qdrant**: When you need more storage/compute

### 11.2 Database Migration
- Consider migrating to PostgreSQL (NeonDB free tier)
- Set up database backups
- Plan for data migration

### 11.3 Performance Optimization
- Enable caching
- Optimize vector search
- Monitor API response times

## 🛠️ Troubleshooting

### Common Issues

#### Backend Won't Start
1. Check Railway logs
2. Verify environment variables
3. Check Python dependencies

#### Frontend Can't Connect to Backend
1. Verify CORS settings
2. Check API URL configuration
3. Test backend health endpoint

#### Notion OAuth Issues
1. Verify redirect URI
2. Check client ID/secret
3. Ensure proper OAuth flow

#### Vector Search Not Working
1. Check Qdrant connection
2. Verify API key
3. Test collection creation

### Debug Commands
```bash
# Check backend logs
railway logs

# Check frontend build
vercel logs

# Test API endpoints
curl -X GET https://your-backend.railway.app/health
```

## 📈 Next Steps

### 11.1 Custom Domain
1. Add custom domain to Vercel
2. Update Notion redirect URI
3. Update CORS settings

### 11.2 SSL Certificate
- Vercel and Railway provide SSL automatically
- Ensure all URLs use HTTPS

### 11.3 Backup Strategy
1. Set up database backups
2. Backup environment variables
3. Document deployment process

## 🎯 Success Metrics

Track these metrics to ensure successful deployment:

- **Uptime**: >99.9%
- **Response Time**: <2 seconds
- **Error Rate**: <1%
- **User Registration**: Successful OAuth flow
- **Chat Functionality**: Working RAG responses

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review Railway and Vercel documentation
3. Check application logs
4. Test individual components
5. Contact support if needed

## 🚀 Launch Checklist

- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Notion OAuth working
- [ ] Chat functionality tested
- [ ] Email notifications working
- [ ] Usage limits configured
- [ ] Security settings applied
- [ ] Monitoring set up
- [ ] Documentation updated
- [ ] Team access configured

Your AI Knowledge Assistant SaaS is now ready for users! 🎉
