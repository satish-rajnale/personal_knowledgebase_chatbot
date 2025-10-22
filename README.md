# AI Knowledge Assistant - Multi-User SaaS

A modern, multi-user SaaS application that allows users to connect their Notion workspace, sync content, and chat with their knowledge using AI-powered RAG (Retrieval-Augmented Generation).

## 🚀 Features

### 🔐 Multi-User Authentication
- **Anonymous Login**: Start using immediately without registration
- **Email-based Authentication**: Secure login with email addresses
- **JWT Token Management**: Secure session management
- **User Profiles**: Track usage and preferences per user

### 📚 Notion Integration
- **OAuth 2.0 Authentication**: Users connect their own Notion workspace securely
- **Page Selection**: Choose specific pages to sync from your workspace
- **Database Support**: Sync entire Notion databases and their content
- **User-driven**: No global integration - each user manages their own connection

### 💬 AI-Powered Chat
- **RAG Technology**: Retrieve relevant information from your knowledge base
- **Multi-source Answers**: Get answers with source citations
- **User-specific Data**: Each user's data is isolated and secure
- **Usage Limits**: Configurable daily query limits

### 📊 Usage Analytics
- **Daily Limits**: Track and enforce usage limits
- **Usage Statistics**: Monitor query usage and patterns
- **Activity Logs**: Detailed logs of user actions
- **Admin Notifications**: Get notified of usage patterns

### 🎨 Modern UI/UX
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live usage statistics and sync status
- **Intuitive Dashboard**: Easy-to-use interface for managing content
- **Contact Support**: Built-in support form

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database (can be upgraded to PostgreSQL)
- **Qdrant**: Vector database for semantic search
- **OpenRouter**: LLM provider (supports GPT-3.5, Claude, and others)
- **JWT**: Secure authentication tokens

### Frontend Stack
- **React**: Modern UI library
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **Axios**: HTTP client for API communication

### Infrastructure
- **Railway**: Backend deployment (free tier available)
- **Vercel**: Frontend deployment (free tier available)
- **Qdrant Cloud**: Vector database hosting (free tier available)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Notion account
- OpenRouter API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd peronal_knowledgebase
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # LLM Configuration
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   MODEL_NAME=openai/gpt-3.5-turbo
   
   # Notion Integration (OAuth)
   NOTION_CLIENT_ID=your_notion_client_id_here
   NOTION_CLIENT_SECRET=your_notion_client_secret_here
   NOTION_REDIRECT_URI=http://localhost:3000/auth/notion/callback
   
   # Vector Database
   QDRANT_URL=https://your-qdrant-cloud-url.qdrant.io
   QDRANT_API_KEY=your_qdrant_api_key_here
   
   # Authentication
   JWT_SECRET=your-super-secret-jwt-key-change-in-production
   DAILY_QUERY_LIMIT=10
   
   # Email Configuration (Optional)
   SMTP_HOST=smtp.gmail.com
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ADMIN_EMAIL=admin@yourdomain.com
   ```

4. **Run the backend**
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   # Create .env file
   echo "REACT_APP_API_URL=http://localhost:8000" > .env
   ```

3. **Run the frontend**
   ```bash
   npm start
   ```

## 🔧 Configuration

### Notion OAuth Setup

1. **Create a Notion Integration**
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Set redirect URI to `http://localhost:3000/auth/notion/callback`
   - Copy the Client ID and Client Secret

2. **Update environment variables**
   ```env
   NOTION_CLIENT_ID=your_client_id
   NOTION_CLIENT_SECRET=your_client_secret
   ```

3. **User Connection**
   - Users will connect their own Notion workspace through the UI
   - No global Notion integration required
   - Each user manages their own OAuth connection

### Qdrant Cloud Setup

1. **Create Qdrant Cloud account**
   - Go to https://cloud.qdrant.io/
   - Create a free account
   - Create a new cluster
   - Copy the URL and API key

2. **Update environment variables**
   ```env
   QDRANT_URL=https://your-cluster-url.qdrant.io
   QDRANT_API_KEY=your_api_key
   ```

### OpenRouter Setup

1. **Get API key**
   - Go to https://openrouter.ai/
   - Create an account
   - Generate an API key

2. **Update environment variables**
   ```env
   OPENROUTER_API_KEY=your_api_key
   ```

## 📦 Deployment

### Backend (Railway)

1. **Connect to Railway**
   ```bash
   railway login
   railway init
   ```

2. **Set environment variables**
   ```bash
   railway variables set OPENROUTER_API_KEY=your_key
   railway variables set NOTION_CLIENT_ID=your_id
   # ... set other variables
   ```

3. **Deploy**
   ```bash
   railway up
   ```

### Frontend (Vercel)

1. **Connect to Vercel**
   ```bash
   npm install -g vercel
   vercel login
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel --prod
   ```

3. **Set environment variables**
   - Go to Vercel dashboard
   - Set `REACT_APP_API_URL` to your Railway backend URL

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **User Isolation**: Each user's data is completely isolated
- **Rate Limiting**: Prevents abuse with configurable limits
- **Input Validation**: All inputs are validated and sanitized
- **CORS Protection**: Configured for production security

## 📈 Usage Limits

- **Free Tier**: 10 queries per day per user
- **Configurable**: Easy to adjust limits in environment variables
- **Reset Daily**: Limits reset at midnight UTC
- **Graceful Degradation**: Friendly messages when limits are reached

## 🛠️ Development

### Project Structure
```
├── backend/
│   ├── app/
│   │   ├── api/routes/     # API endpoints
│   │   ├── core/           # Configuration and database
│   │   ├── models/         # Database models
│   │   └── services/       # Business logic
│   ├── main.py            # Application entry point
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── context/       # React context providers
│   │   └── services/      # API services
│   └── package.json       # Node.js dependencies
└── README.md
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/anonymous` - Create anonymous user
- `POST /api/v1/auth/email` - Login with email
- `GET /api/v1/auth/profile` - Get user profile
- `GET /api/v1/auth/usage` - Get usage statistics

#### Notion Integration
- `POST /api/v1/auth/notion/authorize` - Get Notion OAuth URL
- `POST /api/v1/auth/notion/callback` - Handle OAuth callback
- `GET /api/v1/notion/pages` - Get user's Notion pages
- `GET /api/v1/notion/databases` - Get user's Notion databases
- `POST /api/v1/notion/sync` - Sync selected pages

#### Chat
- `POST /api/v1/chat` - Send chat message
- `GET /api/v1/chat/history` - Get chat history
- `DELETE /api/v1/chat/history` - Clear chat history

#### Support
- `POST /api/v1/contact` - Submit contact form

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests on GitHub
- **Contact**: Use the built-in contact form in the application

## 🚀 Roadmap

- [ ] PostgreSQL database support
- [ ] Advanced analytics dashboard
- [ ] Team collaboration features
- [ ] API rate limiting improvements
- [ ] Mobile app
- [ ] Advanced Notion sync options
- [ ] Multiple LLM provider support
- [ ] Custom embedding models 