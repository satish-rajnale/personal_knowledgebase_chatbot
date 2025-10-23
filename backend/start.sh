#!/bin/bash

# Create data directory if it doesn't exist
mkdir -p /app/data

# Create uploads directory if it doesn't exist
mkdir -p /app/uploads
chmod 777 /app/uploads

# Wait for PostgreSQL database to be ready
echo "🔍 Waiting for PostgreSQL database to be ready..."
python wait_for_db.py

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed, exiting..."
    exit 1
fi

# Initialize vector store (this will be handled by the startup event in main.py)
echo "🚀 Starting application with automatic vector store initialization..."

# Start the application with hot reloading
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload 