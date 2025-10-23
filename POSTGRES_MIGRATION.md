# PostgreSQL + pgvector Migration Guide

This guide helps you migrate from SQLite + Qdrant to PostgreSQL + pgvector for a unified database solution.

## Benefits of PostgreSQL + pgvector

- **Unified Database**: Single PostgreSQL instance for both metadata and vectors
- **ACID Compliance**: Better data consistency and reliability
- **Easier Backup/Restore**: Single database to manage
- **Better Performance**: No network calls between databases
- **Cost Effective**: No separate vector database costs
- **Advanced Features**: Full SQL capabilities with vector operations

## Prerequisites

1. **PostgreSQL 12+** with pgvector extension
2. **Python 3.8+** with updated dependencies
3. **Existing data backup** (recommended)

## Installation

### 1. Install PostgreSQL with pgvector

#### Option A: Using Docker (Recommended)
```bash
# Create a docker-compose.yml for PostgreSQL with pgvector
docker run -d \
  --name postgres-vector \
  -e POSTGRES_DB=knowledgebase \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  pgvector/pgvector:pg15
```

#### Option B: Manual Installation
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Install pgvector
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### 2. Update Environment Variables

Update your `.env` file:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/knowledgebase

# Remove Qdrant configuration (commented out)
# QDRANT_URL=http://qdrant:6333
# QDRANT_API_KEY=your_api_key
# QDRANT_COLLECTION_NAME=knowledgebase
```

### 3. Install Python Dependencies

```bash
# Install new dependencies
pip install psycopg2-binary

# Remove Qdrant dependency
pip uninstall qdrant-client
```

## Migration Process

### 1. Setup PostgreSQL Database

```bash
# Run the setup script
python setup_postgres.py
```

This will:
- Test PostgreSQL connection
- Install pgvector extension
- Create all necessary tables
- Test vector operations

### 2. Migrate Existing Data

If you have existing SQLite data:

```bash
# Run the migration script
python migrate_to_postgres.py
```

This will:
- Migrate user data from SQLite to PostgreSQL
- Migrate chat sessions and messages
- Migrate usage logs and Notion syncs
- Note: Vector data needs to be re-indexed

### 3. Re-index Vector Data

After migration, you'll need to re-sync your documents:

1. **Re-upload files** through the application
2. **Re-sync Notion pages** through the Notion integration
3. **Test vector search** functionality

## Database Schema

### New Tables

#### `document_chunks` - Vector Storage
```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR UNIQUE,
    user_id VARCHAR REFERENCES users(user_id),
    text TEXT NOT NULL,
    metadata TEXT,  -- JSON metadata
    source_type VARCHAR NOT NULL,
    source_id VARCHAR,
    source_url VARCHAR,
    embedding TEXT NOT NULL,  -- JSON array of floats
    chunk_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create vector column for pgvector
ALTER TABLE document_chunks ADD COLUMN embedding_vector vector(384);

-- Create indexes for performance
CREATE INDEX idx_user_source ON document_chunks(user_id, source_type);
CREATE INDEX idx_user_created ON document_chunks(user_id, created_at);
CREATE INDEX idx_source_id ON document_chunks(source_id);
```

### Existing Tables (Updated)
- `users` - User accounts and authentication
- `chat_sessions` - Chat conversation sessions
- `chat_messages` - Individual chat messages
- `usage_logs` - User activity tracking
- `notion_syncs` - Notion integration tracking

## Configuration Changes

### Database Configuration
- **Before**: SQLite + Qdrant
- **After**: PostgreSQL with pgvector

### Vector Store Implementation
- **Before**: `app/services/vector_store.py` (Qdrant)
- **After**: `app/services/postgres_vector_store.py` (PostgreSQL)

### Model Updates
- Added `DocumentChunk` model for vector storage
- Updated database connections for PostgreSQL
- Removed SQLite-specific code

## Testing the Migration

### 1. Test Database Connection
```python
from app.core.database import init_db
import asyncio

# Test database initialization
asyncio.run(init_db())
```

### 2. Test Vector Operations
```python
from app.services.postgres_vector_store import search_documents

# Test vector search
results = await search_documents("test query", top_k=5)
print(f"Found {len(results)} results")
```

### 3. Test Document Upload
1. Upload a test document
2. Verify it's stored in `document_chunks` table
3. Test search functionality

## Troubleshooting

### Common Issues

#### 1. PostgreSQL Connection Failed
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -U user -d knowledgebase
```

#### 2. pgvector Extension Not Found
```bash
# Install pgvector extension
sudo -u postgres psql -d knowledgebase -c "CREATE EXTENSION vector;"
```

#### 3. Vector Operations Not Working
```sql
-- Test vector operations
SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector;
```

### Performance Optimization

#### 1. Database Indexes
```sql
-- Create additional indexes for better performance
CREATE INDEX idx_embedding_vector ON document_chunks USING ivfflat (embedding_vector vector_cosine_ops);
```

#### 2. Connection Pooling
```python
# Update database configuration for better performance
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300
)
```

## Rollback Plan

If you need to rollback to the old system:

1. **Restore SQLite database** from backup
2. **Restore Qdrant data** from backup
3. **Revert code changes** to previous commit
4. **Update environment variables** to old configuration

## Support

For issues with the migration:

1. Check the logs for error messages
2. Verify PostgreSQL and pgvector installation
3. Test database connectivity
4. Review the migration script output

## Next Steps

After successful migration:

1. **Monitor performance** - Check query times and resource usage
2. **Optimize indexes** - Add indexes based on usage patterns
3. **Backup strategy** - Set up regular PostgreSQL backups
4. **Scale planning** - Consider read replicas for high traffic

## Benefits Realized

- ✅ **Unified database** for easier management
- ✅ **Better data consistency** with ACID compliance
- ✅ **Simplified architecture** with fewer moving parts
- ✅ **Cost reduction** by eliminating separate vector database
- ✅ **Enhanced reliability** with PostgreSQL's proven stability
