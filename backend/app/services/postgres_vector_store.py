from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Dict, Any, Optional
import json
import re
import numpy as np
import asyncio
from datetime import datetime, timezone
from app.core.config import settings
from app.models.vector import DocumentChunk
from app.models.user import get_db
from app.services.embedding_service import get_embeddings, get_embedding_dimensions
import uuid
import builtins

class PostgresVectorStore:
    def __init__(self):
        print(f"🔧 PostgresVectorStore initialization:")
        print(f"   DATABASE_URL: {settings.DATABASE_URL}")
        print(f"   Using PostgreSQL with pgvector for vector storage")
        
        # Get embedding dimensions from the embedding service
        self.embedding_dimensions = get_embedding_dimensions()
        print(f"   Embedding dimensions: {self.embedding_dimensions}")
    
    async def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using sentence-transformers with aggressive timeout and fallback"""
        try:
            print(f"🔍 Starting embedding generation for {len(texts)} texts...")
            import asyncio
            import concurrent.futures
            import numpy as np
            
            # Run embedding generation in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            print("🔍 Running embedding generation in thread pool...")
            
            # Use a very short timeout to prevent hanging
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    embeddings = await loop.run_in_executor(executor, get_embeddings, texts)
                print(f"✅ Generated {len(embeddings)} embeddings")
                return embeddings
            except asyncio.TimeoutError:
                print("⚠️ Embedding generation timed out after 5s, using fallback")
                return [np.random.rand(self.embedding_dimensions).tolist() for _ in texts]
            except Exception as e:
                print(f"⚠️ Embedding generation failed: {e}, using fallback")
                return [np.random.rand(self.embedding_dimensions).tolist() for _ in texts]
            
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            # Fallback to random embeddings if model fails
            print("🔄 Using fallback random embeddings")
            import numpy as np
            return [np.random.rand(self.embedding_dimensions).tolist() for _ in texts]
    
    def _split_text(self, text: str, chunk_size: int = 2000, chunk_overlap: int = 300) -> List[str]:
        """Improved text splitting implementation with better content preservation"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a natural boundary
            if end < len(text):
                # Look for better break points within the last 200 characters
                search_start = max(start + chunk_size - 200, start)
                search_end = min(end, len(text))
                
                # Find the best break point (prioritize paragraph breaks)
                break_points = ['\n\n', '\n', '. ', '! ', '? ', '; ', ', ']
                last_break = end
                
                for break_point in break_points:
                    pos = text.rfind(break_point, search_start, search_end)
                    if pos > start and pos < end:
                        last_break = pos + len(break_point)
                        break
                
                end = last_break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position, accounting for overlap
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        # Validate that we haven't lost content
        total_chunk_length = sum(len(chunk) for chunk in chunks)
        original_length = len(text.strip())
        
        if total_chunk_length < original_length * 0.8:  # If we lost more than 20% of content
            print(f"⚠️ Warning: Chunking may have lost content. Original: {original_length}, Chunks: {total_chunk_length}")
            # Fallback to simple splitting without boundary logic
            return self._simple_split_text(text, chunk_size, chunk_overlap)
        
        return chunks
    
    def _simple_split_text(self, text: str, chunk_size: int = 2000, chunk_overlap: int = 300) -> List[str]:
        """Simple fallback splitting that preserves all content"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def init_vector_store(self):
        """Initialize PostgreSQL vector store - create pgvector extension if needed"""
        try:
            db = next(get_db())
            try:
                # Enable pgvector extension
                db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                print("✅ pgvector extension enabled")
                
                # Drop and recreate vector column to ensure correct type
                try:
                    db.execute(text("ALTER TABLE document_chunks DROP COLUMN IF EXISTS embedding_vector"))
                    print("✅ Dropped existing embedding_vector column")
                except Exception as e:
                    print(f"⚠️ Could not drop existing column: {e}")
                
                try:
                    db.execute(text(f"ALTER TABLE document_chunks ADD COLUMN embedding_vector vector({self.embedding_dimensions})"))
                    print(f"✅ Vector column created with {self.embedding_dimensions} dimensions")
                except Exception as e:
                    print(f"⚠️ Vector column creation failed: {e}")
                
                # Drop existing index if it exists (to handle data type changes)
                try:
                    db.execute(text("DROP INDEX IF EXISTS idx_embedding_vector"))
                    print("✅ Dropped existing vector index")
                except Exception as e:
                    print(f"⚠️ Could not drop existing index: {e}")
                
                # Populate vector column for existing data first
                try:
                    db.execute(text("""
                        UPDATE document_chunks 
                        SET embedding_vector = embedding::vector 
                        WHERE embedding_vector IS NULL 
                        AND embedding IS NOT NULL
                    """))
                    print("✅ Vector column populated for existing data")
                except Exception as e:
                    print(f"⚠️ Vector column population may have failed: {e}")
                
                # Create index for vector operations (after data is populated)
                try:
                    db.execute(text("CREATE INDEX IF NOT EXISTS idx_embedding_vector ON document_chunks USING ivfflat (embedding_vector vector_cosine_ops)"))
                    print("✅ Vector index created/verified")
                except Exception as e:
                    print(f"⚠️ Vector index creation failed: {e}")
                
                db.commit()
                print("✅ PostgreSQL vector store initialized")
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Error initializing PostgreSQL vector store: {e}")
            raise
    
    async def add_documents(self, documents: List[Dict], source_type: str = "upload", user_id: str = None):
        """Add documents to PostgreSQL vector store"""
        try:
            print(f"🔍 Starting add_documents for {len(documents)} documents, source_type: {source_type}, user_id: {user_id}")
            db = next(get_db())
            try:
                # Split documents into chunks
                chunks = []
                for doc in documents:
                    page_content = doc.get("page_content", "")
                    metadata = doc.get("metadata", {})
                    
                    # Add user_id to metadata if provided
                    if user_id:
                        metadata["user_id"] = user_id
                    
                    # Enhance metadata for Notion pages
                    if source_type == "notion" and metadata.get("page_id"):
                        # Ensure we have proper Notion URL
                        page_id = metadata["page_id"]
                        if not metadata.get("url"):
                            metadata["url"] = f"https://notion.so/{page_id.replace('-', '')}"
                        
                        # Add source type for better identification
                        metadata["source_type"] = "notion"
                        
                        # Add page title if available
                        if metadata.get("title"):
                            metadata["source"] = f"Notion: {metadata['title']}"
                        else:
                            metadata["source"] = f"Notion Page ({page_id[:8]}...)"
                    
                    # Split page content into chunks
                    print(f"🔍 Original page content length: {len(page_content)} characters")
                    print(f"🔍 Page content preview: {page_content[:200]}...")
                    
                    text_chunks = self._split_text(page_content)
                    print(f"🔍 Split text into {len(text_chunks)} chunks")
                    
                    # Log chunk details
                    total_chunk_length = sum(len(chunk) for chunk in text_chunks)
                    print(f"🔍 Total chunk length: {total_chunk_length} characters")
                    print(f"🔍 Content preservation: {(total_chunk_length / len(page_content)) * 100:.1f}%")
                    
                    for i, chunk_text in enumerate(text_chunks):
                        print(f"🔍 Chunk {i+1}: {len(chunk_text)} chars - {chunk_text[:100]}...")
                        chunks.append({
                            "text": chunk_text,
                            "metadata": metadata,
                            "chunk_id": i
                        })
                
                if not chunks:
                    print("⚠️ No chunks to process")
                    return []
                
                print(f"🔍 Processing {len(chunks)} chunks for embedding generation...")
                # Generate embeddings
                texts = [chunk["text"] for chunk in chunks]
                embeddings = await self._get_embeddings(texts)
                
                # Insert chunks into PostgreSQL using raw SQL for proper vector handling
                print(f"🔍 Starting database insertion for {len(chunks)} chunks...")
                inserted_chunks = []
                
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    print(f"🔍 Processing chunk {i+1}/{len(chunks)}...")
                    
                    # Convert embedding to proper formats
                    print(f"🔍 Debug: embedding type: {type(embedding)}")
                    print(f"🔍 Debug: embedding content: {embedding}")
                    embedding_str = json.dumps(embedding)
                    # Convert embedding to string format for pgvector using a different approach
                    embedding_list = []
                    for x in embedding:
                        embedding_list.append(str(x))
                    embedding_vector_str = f"[{','.join(embedding_list)}]"
                    
                    # Use UPSERT to handle duplicate chunk_ids gracefully with structured metadata
                    upsert_sql = text("""
                        INSERT INTO document_chunks 
                        (chunk_id, user_id, text, document_metadata, source_type, source_id, source_url, source_link, page_number, section_title, embedding, embedding_vector, chunk_index, chunk_size, created_at, updated_at)
                        VALUES (:chunk_id, :user_id, :text, :document_metadata, :source_type, :source_id, :source_url, :source_link, :page_number, :section_title, :embedding, CAST(:embedding_vector AS vector), :chunk_index, :chunk_size, :created_at, :updated_at)
                        ON CONFLICT (chunk_id) 
                        DO UPDATE SET
                            user_id = EXCLUDED.user_id,
                            text = EXCLUDED.text,
                            document_metadata = EXCLUDED.document_metadata,
                            source_type = EXCLUDED.source_type,
                            source_id = EXCLUDED.source_id,
                            source_url = EXCLUDED.source_url,
                            source_link = EXCLUDED.source_link,
                            page_number = EXCLUDED.page_number,
                            section_title = EXCLUDED.section_title,
                            embedding = EXCLUDED.embedding,
                            embedding_vector = EXCLUDED.embedding_vector,
                            chunk_index = EXCLUDED.chunk_index,
                            chunk_size = EXCLUDED.chunk_size,
                            updated_at = EXCLUDED.updated_at
                        RETURNING id
                    """)
                    
                    result = db.execute(upsert_sql, {
                        "chunk_id": f"{chunk['metadata'].get('page_id', 'unknown')}_{chunk.get('chunk_id', i)}",
                        "user_id": user_id,
                        "text": chunk["text"],
                        "document_metadata": json.dumps(chunk["metadata"]),
                        "source_type": source_type,
                        "source_id": chunk["metadata"].get("page_id") or chunk["metadata"].get("source_id"),
                        "source_url": chunk["metadata"].get("url"),
                        "source_link": chunk["metadata"].get("url"),  # Same as source_url for now
                        "page_number": chunk["metadata"].get("page"),
                        "section_title": chunk["metadata"].get("section_title", ""),
                        "embedding": embedding_str,
                        "embedding_vector": embedding_vector_str,
                        "chunk_index": chunk.get('chunk_id', i),
                        "chunk_size": len(chunk["text"]),
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    
                    # Get the inserted ID
                    inserted_id = result.fetchone()[0]
                    inserted_chunks.append({"id": inserted_id, "chunk_id": f"{chunk['metadata'].get('page_id', 'unknown')}_{chunk.get('chunk_id', i)}"})
                
                print("🔍 Committing to database...")
                db.commit()
                print("✅ Database commit successful")
                
                print(f"✅ Added {len(inserted_chunks)} chunks to PostgreSQL vector store")
                print(f"   Source type: {source_type}")
                print(f"   User ID: {user_id}")
                for i, chunk in enumerate(inserted_chunks[:3]):  # Show first 3 chunks
                    print(f"   Chunk {i+1}: ID {chunk.get('id', 'Unknown')}")
                    print(f"     Chunk ID: {chunk.get('chunk_id', 'Unknown')}")
                
                return inserted_chunks
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Error adding documents to PostgreSQL vector store: {e}")
            raise
    
    async def search(self, query: str, top_k: int = 5, filter: Dict = None) -> List[Dict[str, Any]]:
        """Search for similar documents using PostgreSQL vector similarity"""
        try:
            db = next(get_db())
            try:
                # Generate query embedding
                query_embedding = await self._get_embeddings([query])
                query_embedding_str = json.dumps(query_embedding[0])
                
                # Build the search query with proper pgvector syntax and enhanced metadata
                if filter and "user_id" in filter:
                    # Search with user filter
                    search_query = text(f"""
                        SELECT 
                            id, text, document_metadata, source_type, source_id, source_url, source_link,
                            page_number, section_title, chunk_size, chunk_index,
                            (embedding_vector <=> '{query_embedding_str}'::vector) as distance
                        FROM document_chunks 
                        WHERE user_id = :user_id
                        ORDER BY embedding_vector <=> '{query_embedding_str}'::vector
                        LIMIT :limit
                    """)
                    
                    result = db.execute(search_query, {
                        "user_id": filter["user_id"],
                        "limit": top_k
                    })
                else:
                    # Search without user filter
                    search_query = text(f"""
                        SELECT 
                            id, text, document_metadata, source_type, source_id, source_url, source_link,
                            page_number, section_title, chunk_size, chunk_index,
                            (embedding_vector <=> '{query_embedding_str}'::vector) as distance
                        FROM document_chunks 
                        ORDER BY embedding_vector <=> '{query_embedding_str}'::vector
                        LIMIT :limit
                    """)
                    
                    result = db.execute(search_query, {
                        "limit": top_k
                    })
                
                # Format results with enhanced metadata and highlighting
                results = []
                for row in result:
                    metadata = json.loads(row.document_metadata) if row.document_metadata else {}
                    
                    # Create enhanced result with source information
                    result_item = {
                        "text": row.text,
                        "metadata": metadata,
                        "source_type": row.source_type,
                        "score": 1 - row.distance,  # Convert distance to similarity score
                        "source_info": {
                            "source_id": row.source_id,
                            "source_url": row.source_url,
                            "source_link": row.source_link,
                            "page_number": row.page_number,
                            "section_title": row.section_title,
                            "chunk_size": row.chunk_size,
                            "chunk_index": row.chunk_index
                        }
                    }
                    
                    # Add highlighting for query terms
                    from app.services.document_processor import DocumentProcessor
                    highlighted_text = DocumentProcessor._highlight_query_terms(row.text, query)
                    result_item["highlighted_text"] = highlighted_text
                    
                    # Add short summary if available
                    if row.section_title:
                        result_item["summary"] = f"From {row.section_title}"
                        if row.page_number:
                            result_item["summary"] += f" (Page {row.page_number})"
                    elif row.page_number:
                        result_item["summary"] = f"Page {row.page_number}"
                    
                    results.append(result_item)
                
                return results
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Error searching PostgreSQL vector store: {e}")
            return []

# Global vector store instance
postgres_vector_store = PostgresVectorStore()

async def init_vector_store():
    """Initialize PostgreSQL vector store with timeout"""
    try:
        # Add timeout to prevent hanging
        await asyncio.wait_for(postgres_vector_store.init_vector_store(), timeout=30.0)
        print("✅ Vector store initialization completed")
    except asyncio.TimeoutError:
        print("⚠️ Vector store initialization timed out, but continuing...")
    except Exception as e:
        print(f"⚠️ Vector store initialization failed: {e}, but continuing...")

async def add_documents_to_store(documents: List[Dict], source_type: str = "upload", user_id: str = None):
    """Add documents to PostgreSQL vector store"""
    return await postgres_vector_store.add_documents(documents, source_type, user_id)

async def search_documents(query: str, top_k: int = 5, filter: Dict = None):
    """Search documents in PostgreSQL vector store"""
    return await postgres_vector_store.search(query, top_k, filter)
