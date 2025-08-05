#!/bin/bash

# Create data directory if it doesn't exist
mkdir -p /app/data

# Create database file if it doesn't exist
touch /app/data/chat_history.db
chmod 666 /app/data/chat_history.db

# Create uploads directory if it doesn't exist
mkdir -p /app/uploads
chmod 777 /app/uploads

# Initialize vector store (this will be handled by the startup event in main.py)
echo "🚀 Starting application with automatic vector store initialization..."

# Start the application with hot reloading
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload 