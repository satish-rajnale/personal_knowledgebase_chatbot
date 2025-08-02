# Health Endpoints Documentation

This document describes the health check endpoints available in the Personal Knowledgebase Chatbot API.

## Available Endpoints

### 1. Root Health Check

- **URL**: `/`
- **Method**: `GET`
- **Description**: Simple endpoint to verify the API is running
- **Response**: Basic status information

**Example Response:**

```json
{
  "message": "Personal Knowledgebase Chatbot API",
  "version": "1.0.0",
  "status": "running"
}
```

### 2. Basic Health Check

- **URL**: `/health`
- **Method**: `GET`
- **Description**: Basic health check with endpoint information
- **Response**: Status and available endpoints

**Example Response:**

```json
{
  "status": "healthy",
  "message": "Personal Knowledgebase Chatbot API is running",
  "version": "1.0.0",
  "endpoints": {
    "chat": "/api/v1/chat",
    "upload": "/api/v1/upload",
    "notion": "/api/v1/notion",
    "detailed_health": "/api/v1/health"
  }
}
```

### 3. Detailed Health Check

- **URL**: `/api/v1/health`
- **Method**: `GET`
- **Description**: Comprehensive health check that tests all services
- **Response**: Detailed status of all components

**Example Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "vector_store": "healthy",
    "llm": "healthy"
  },
  "environment": {
    "debug": true,
    "llm_provider": "openrouter",
    "qdrant_url": "https://your-cluster.qdrant.io",
    "qdrant_api_key_set": true,
    "notion_token_set": true,
    "openrouter_api_key_set": true
  }
}
```

## Status Codes

- **200 OK**: All services are healthy
- **503 Service Unavailable**: One or more services are unhealthy
- **500 Internal Server Error**: Critical error occurred

## Testing Health Endpoints

### Using curl

```bash
# Test root endpoint
curl http://localhost:8000/

# Test basic health
curl http://localhost:8000/health

# Test detailed health
curl http://localhost:8000/api/v1/health
```

### Using the test script

```bash
# Test local server
python test_health.py

# Test deployed server
python test_health.py https://your-railway-app.railway.app
```

## Monitoring Integration

### Railway

Railway automatically uses `/health` for health checks with a 300-second timeout.

### Docker

You can use these endpoints for Docker health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Load Balancers

Configure your load balancer to use `/health` for health checks.

## Troubleshooting

### Common Issues

1. **Database Connection Failed**

   - Check if SQLite database file exists and has proper permissions
   - Verify database URL configuration

2. **Vector Store Connection Failed**

   - Verify Qdrant URL and API key are correct
   - Check if Qdrant Cloud cluster is accessible

3. **LLM Service Failed**
   - Verify API keys are set correctly
   - Check if the LLM provider is accessible

### Debug Mode

When `DEBUG=True`, the API provides more detailed error information in health check responses.
