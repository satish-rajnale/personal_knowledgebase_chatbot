#!/bin/bash

echo "🚀 Setting up Personal Knowledgebase Chatbot..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ Created .env file. Please edit it with your API keys."
else
    echo "✅ .env file already exists."
fi

# Create uploads directory
mkdir -p uploads

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - OPENROUTER_API_KEY (or set LLM_PROVIDER=ollama for local models)"
echo ""
echo "2. Start the application:"
echo "   docker-compose up -d"
echo ""
echo "3. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "4. For local development:"
echo "   - Backend: cd backend && pip install -r requirements.txt && uvicorn main:app --reload"
echo "   - Frontend: cd frontend && npm install && npm start"
echo "" 