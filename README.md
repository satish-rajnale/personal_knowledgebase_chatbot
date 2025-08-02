# AI-Powered Personal Knowledgebase Chatbot

A full-stack AI-powered personal knowledgebase chatbot that allows you to upload documents, sync from Notion, and chat with your knowledge using RAG (Retrieval-Augmented Generation).

## 🚀 Features

- **Document Upload**: Support for `.txt`, `.md`, and `.pdf` files
- **Notion Integration**: Sync pages and blocks from your Notion workspace
- **RAG-powered Chat**: Intelligent responses using your uploaded knowledge
- **Vector Search**: Fast semantic search using Qdrant vector database
- **Chat History**: Persistent conversation history
- **Modern UI**: Clean, responsive interface

## 🏗️ Architecture

- **Backend**: FastAPI with RAG implementation using LangChain
- **Vector DB**: Qdrant for efficient similarity search
- **LLM**: OpenRouter API or Ollama for local inference
- **Frontend**: React with modern UI components
- **Storage**: SQLite for chat history, Qdrant for vectors

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Docker and Docker Compose
- Notion API token (optional)
- OpenRouter API key (optional)

### Quick Start with Docker

1. **Clone and setup environment**:
   ```bash
   git clone <repository>
   cd peronal_knowledgebase
   cp .env.example .env
   ```

2. **Configure environment variables**:
   ```bash
   # Edit .env file with your API keys
   OPENROUTER_API_KEY=your_openrouter_key
   NOTION_TOKEN=your_notion_token
   NOTION_DATABASE_ID=your_database_id
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development

1. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Start Qdrant**:
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
OLLAMA_BASE_URL=http://localhost:11434
LLM_PROVIDER=openrouter  # or "ollama"
MODEL_NAME=openai/gpt-3.5-turbo  # or "llama2" for Ollama

# Notion Integration
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_database_id

# Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=knowledgebase

# App Configuration
DEBUG=true
CORS_ORIGINS=http://localhost:3000
```

### Notion Setup

1. **Create a Notion Integration**:
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Give it a name and select your workspace
   - Copy the "Internal Integration Token"

2. **Share your database**:
   - Open your Notion database
   - Click "Share" → "Invite" → Select your integration
   - Copy the database ID from the URL

3. **Add to .env**:
   ```env
   NOTION_TOKEN=secret_your_token_here
   NOTION_DATABASE_ID=your_database_id
   ```

### Free LLM Options

#### OpenRouter (Recommended)
- Sign up at https://openrouter.ai
- Get free credits for various models
- Supports GPT-3.5, Claude, and other models

#### Ollama (Local)
- Install Ollama: https://ollama.ai
- Pull a model: `ollama pull llama2`
- Set `LLM_PROVIDER=ollama` in `.env`

## 📁 Project Structure

```
peronal_knowledgebase/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── public/
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔌 API Endpoints

- `POST /chat` - Send a message and get AI response
- `POST /upload` - Upload documents (.txt, .md, .pdf)
- `POST /notion/sync` - Sync content from Notion
- `GET /chat/history` - Get chat history
- `DELETE /chat/history` - Clear chat history

## 🚀 Usage

1. **Upload Documents**: Drag and drop or click to upload your knowledge files
2. **Sync Notion**: Click "Sync Notion" to import your workspace content
3. **Start Chatting**: Ask questions about your uploaded knowledge
4. **View Sources**: Each response shows the relevant source documents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details 