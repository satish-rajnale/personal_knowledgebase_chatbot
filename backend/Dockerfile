FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including minimal OpenCV requirements
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    wget \
    curl \
    git \
    # Minimal OpenCV dependencies
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libopenblas-dev \
    python3-dev \
    python3-numpy \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for model caching
ENV TRANSFORMERS_CACHE=/app/.cache/transformers
ENV HF_HOME=/app/.cache/huggingface
ENV TORCH_HOME=/app/.cache/torch

# Set environment variables for OpenCV headless mode
ENV QT_QPA_PLATFORM=offscreen
ENV DISPLAY=:99
ENV OPENCV_IO_ENABLE_OPENEXR=1

# Create cache directories
RUN mkdir -p /app/.cache/transformers /app/.cache/huggingface /app/.cache/torch

# Copy model download scripts and database wait script
COPY download_models.py .
COPY download_models_simple.py .
COPY wait_for_db.py .

# Pre-download all models during build to ensure they're available at runtime
# This eliminates internet dependency in production deployments
# Models will be cached in the volume for faster rebuilds
# Try full download first, fallback to simple download if needed
RUN python download_models.py || python download_models_simple.py || echo "⚠️ Model download had issues, but continuing with build..."

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Use startup script that includes vector store initialization
CMD ["./start.sh"] 