# Use a smaller base image
FROM python:3.11-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .

# Install dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Copy backend startup script
COPY backend/start.sh .
RUN chmod +x start.sh

# Copy backend application code
COPY backend/ .

# Create uploads directory
RUN mkdir -p uploads

# Clean up Python cache
RUN find /usr/local/lib/python3.11 -name "*.pyc" -delete && \
    find /usr/local/lib/python3.11 -name "__pycache__" -type d -delete

# Expose port
EXPOSE $PORT

# Use startup script
CMD ["./start.sh"] 