# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites

- Docker and Docker Compose installed
- Optional: OpenRouter API key or Ollama for local models
- Optional: Notion integration token

### 2. Setup

```bash
# Clone and setup
git clone <your-repo>
cd peronal_knowledgebase
./setup.sh

# Edit environment variables
nano .env
```

### 3. Start the Application

```bash
docker-compose up -d
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables (.env)

```env
# LLM Configuration (choose one)
OPENROUTER_API_KEY=your_openrouter_key
# OR for local models:
LLM_PROVIDER=ollama
MODEL_NAME=llama2

# Notion Integration (optional)
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_database_id
```

### Free LLM Options

1. **OpenRouter**: Sign up at https://openrouter.ai for free credits
2. **Ollama**: Install locally with `ollama pull llama2`

## 📚 Usage

### 1. Upload Documents

- Go to the "Upload" tab
- Drag & drop PDF, TXT, or MD files
- Files are automatically processed and added to your knowledgebase

### 2. Sync Notion (Optional)

- Configure Notion integration in .env
- Go to "Notion" tab
- Click "Sync Now" to import your workspace

### 3. Start Chatting

- Go to the "Chat" tab
- Ask questions about your uploaded documents
- View source documents for each response

## 🛠️ Development

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start

# Qdrant (in another terminal)
docker run -p 6333:6333 qdrant/qdrant
```

### API Endpoints

- `POST /api/v1/chat` - Send message and get AI response
- `POST /api/v1/upload` - Upload documents
- `POST /api/v1/notion/sync` - Sync Notion content
- `GET /api/v1/chat/history` - Get chat history

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **API key errors**: Check your .env file configuration
3. **File upload fails**: Check file size (max 10MB) and type
4. **Notion sync fails**: Verify token and database permissions

### Logs

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

## 📖 Features

- ✅ **Document Upload**: PDF, TXT, MD support
- ✅ **Notion Integration**: Sync workspace content
- ✅ **RAG-powered Chat**: Intelligent responses with sources
- ✅ **Vector Search**: Fast semantic search with Qdrant
- ✅ **Chat History**: Persistent conversations
- ✅ **Modern UI**: Clean, responsive interface
- ✅ **Docker Support**: Easy deployment
- ✅ **API Documentation**: Auto-generated docs

## 🤝 Support

- Check the main README.md for detailed documentation
- Review API docs at http://localhost:8000/docs
- Open an issue for bugs or feature requests
