# Model Caching Strategy

This document explains how models are cached to avoid re-downloading during development and ensure reliable production deployments.

## 🎯 **Problem Solved**

- **Development**: Models are cached in Docker volumes to avoid re-downloading on every rebuild
- **Production**: All models are pre-downloaded in the Docker image for offline deployment
- **Bandwidth**: Significant reduction in download time and bandwidth usage

## 📁 **Cache Structure**

```
/app/.cache/
├── transformers/     # Sentence-transformers models
├── huggingface/      # Hugging Face models (Pix2Text, etc.)
└── torch/           # PyTorch models
```

## 🔧 **Implementation**

### **1. Docker Volumes**
- `models_cache` volume persists across container restarts
- Mounted at `/app/.cache` in the container
- Shared between development and production environments

### **2. Intelligent Download Script**
- `backend/download_models.py` checks if models already exist
- Only downloads missing models
- Provides detailed logging of download status

### **3. Environment Variables**
```bash
TRANSFORMERS_CACHE=/app/.cache/transformers
HF_HOME=/app/.cache/huggingface
TORCH_HOME=/app/.cache/torch
```

## 🚀 **Usage**

### **Development**
```bash
# First build - downloads all models
docker-compose build backend

# Subsequent rebuilds - uses cached models
docker-compose build backend
```

### **Production**
```bash
# Models are pre-downloaded in the image
docker build -t your-app .
```

## 📊 **Benefits**

| Scenario | Before | After |
|----------|--------|-------|
| First build | 5-10 min | 5-10 min |
| Rebuild | 5-10 min | 1-2 min |
| Production | Requires internet | Offline ready |
| Bandwidth | ~500MB per build | ~500MB first time only |

## 🔍 **Model Details**

### **Sentence-Transformers**
- Model: `all-MiniLM-L6-v2`
- Size: ~80MB
- Purpose: Text embeddings
- Dimensions: 384

### **Pix2Text**
- Models: MFR (Mathematical Formula Recognition)
- Size: ~200MB
- Purpose: OCR and formula extraction
- Features: Text, LaTeX, diagrams

### **PyTorch**
- Models: Base PyTorch models
- Size: ~100MB
- Purpose: ML framework dependencies

### **Hugging Face**
- Models: Various transformer models
- Size: ~100MB
- Purpose: NLP and ML model hub

## 🛠 **Troubleshooting**

### **Clear Cache**
```bash
# Remove the models cache volume
docker volume rm personal_knowledgebase_chatbot_models_cache

# Rebuild to re-download models
docker-compose build backend
```

### **Check Cache Status**
```bash
# List volumes
docker volume ls

# Inspect cache volume
docker volume inspect personal_knowledgebase_chatbot_models_cache
```

### **Manual Model Download**
```bash
# Run the download script manually
docker-compose exec backend python download_models.py
```

## 📝 **Notes**

- Models are cached per Docker volume, not per project
- Cache persists across `docker-compose down` and `docker-compose up`
- Production images include all models for offline deployment
- Development uses cached models for faster rebuilds
