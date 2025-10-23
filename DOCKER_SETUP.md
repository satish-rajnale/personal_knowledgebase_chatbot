# Docker Setup with PostgreSQL + pgvector

This guide explains how to run the knowledge base chatbot using Docker with PostgreSQL and pgvector.

## Quick Start

### Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Environment

```bash
# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

## Services Overview

### PostgreSQL with pgvector
- **Image**: `pgvector/pgvector:pg16`
- **Port**: 5432
- **Database**: knowledgebase
- **User**: user
- **Password**: password
- **Features**: pgvector extension for vector operations

### Backend (FastAPI)
- **Port**: 8000
- **Features**: Auto-reload in development
- **Dependencies**: PostgreSQL with health check

### Frontend (React)
- **Port**: 3000
- **Features**: Hot reload in development
- **Dependencies**: Backend service

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@postgres:5432/knowledgebase

# API Configuration
DEBUG=true
CORS_ORIGINS=http://localhost:3000

# Authentication (add your keys)
JWT_SECRET=your-secret-key
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=your-api-key

# Notion Integration
NOTION_CLIENT_ID=your-client-id
NOTION_CLIENT_SECRET=your-client-secret
NOTION_REDIRECT_URI=http://localhost:8000/auth/notion/callback

# LLM Configuration
OPENROUTER_API_KEY=your-api-key
LLM_PROVIDER=openrouter
MODEL_NAME=openai/gpt-3.5-turbo
```

### Production Environment

Create a `.env.prod` file for production:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@postgres:5432/knowledgebase

# API Configuration
DEBUG=false
CORS_ORIGINS=https://yourdomain.com

# Authentication
JWT_SECRET=your-production-secret-key
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=your-api-key

# Notion Integration
NOTION_CLIENT_ID=your-client-id
NOTION_CLIENT_SECRET=your-client-secret
NOTION_REDIRECT_URI=https://yourdomain.com/auth/notion/callback

# LLM Configuration
OPENROUTER_API_KEY=your-api-key
LLM_PROVIDER=openrouter
MODEL_NAME=openai/gpt-3.5-turbo
```

## Docker Commands

### Development

```bash
# Start services
docker-compose up -d

# Start with logs
docker-compose up

# Rebuild and start
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f frontend

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec postgres psql -U user -d knowledgebase
```

### Production

```bash
# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=3
```

## Database Operations

### Connect to PostgreSQL

```bash
# Using docker-compose
docker-compose exec postgres psql -U user -d knowledgebase

# Using external client
psql -h localhost -p 5432 -U user -d knowledgebase
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U user knowledgebase > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U user knowledgebase < backup.sql
```

### Initialize Database

```bash
# Run database setup
docker-compose exec backend python setup_postgres.py

# Run migration (if migrating from SQLite)
docker-compose exec backend python migrate_to_postgres.py
```

## Troubleshooting

### Common Issues

#### 1. PostgreSQL Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres pg_isready -U user -d knowledgebase
```

#### 2. pgvector Extension Not Found
```bash
# Check if extension is installed
docker-compose exec postgres psql -U user -d knowledgebase -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Install extension manually
docker-compose exec postgres psql -U user -d knowledgebase -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

#### 3. Backend Service Not Starting
```bash
# Check backend logs
docker-compose logs backend

# Check if PostgreSQL is healthy
docker-compose exec postgres pg_isready -U user -d knowledgebase

# Restart backend
docker-compose restart backend
```

#### 4. Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Check if backend is accessible
curl http://localhost:8000/health

# Restart frontend
docker-compose restart frontend
```

### Performance Optimization

#### 1. PostgreSQL Tuning
```yaml
# In docker-compose.prod.yml
postgres:
  command: >
    postgres
    -c max_connections=200
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=64MB
    -c checkpoint_completion_target=0.9
    -c wal_buffers=16MB
    -c default_statistics_target=100
    -c random_page_cost=1.1
    -c effective_io_concurrency=200
    -c work_mem=4MB
    -c min_wal_size=1GB
    -c max_wal_size=4GB
```

#### 2. Resource Limits
```yaml
# In docker-compose.prod.yml
backend:
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '0.5'
      reservations:
        memory: 512M
        cpus: '0.25'
```

## Monitoring

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service health
docker-compose exec postgres pg_isready -U user -d knowledgebase
curl http://localhost:8000/health
curl http://localhost:3000
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f postgres
docker-compose logs -f backend
docker-compose logs -f frontend

# View logs with timestamps
docker-compose logs -f -t
```

## Security Considerations

### Production Security

1. **Change default passwords** in production
2. **Use secrets management** for sensitive data
3. **Enable SSL/TLS** for external connections
4. **Restrict network access** to necessary ports only
5. **Regular security updates** for base images

### Network Security

```yaml
# Example network configuration
networks:
  knowledgebase-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U user knowledgebase > "backup_${DATE}.sql"
```

### Recovery

```bash
# Restore from backup
docker-compose exec -T postgres psql -U user knowledgebase < backup_20240101_120000.sql
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Scale with load balancer
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=3
```

### Vertical Scaling

```yaml
# Increase resource limits
backend:
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1.0'
```

## Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| Auto-reload | ✅ | ❌ |
| Debug logging | ✅ | ❌ |
| Hot reload | ✅ | ❌ |
| Resource limits | ❌ | ✅ |
| Health checks | ✅ | ✅ |
| SSL/TLS | ❌ | ✅ |
| Load balancing | ❌ | ✅ |

## Next Steps

1. **Configure environment variables** for your setup
2. **Start services** with `docker-compose up -d`
3. **Initialize database** with setup script
4. **Test vector operations** with sample data
5. **Configure monitoring** and logging
6. **Set up backups** for production
