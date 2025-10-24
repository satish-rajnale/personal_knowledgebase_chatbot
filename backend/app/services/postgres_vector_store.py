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
from app.services.embedding_service import get_embedding_dimensions
from app.services.langchain_service import langchain_service
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
        """Generate embeddings using LangChain service"""
        try:
            print(f"🔍 Generating embeddings for {len(texts)} texts using LangChain...")
            
            embeddings = []
            for text in texts:
                embedding = await langchain_service._get_embedding_async(text)
                embeddings.append(embedding)
            
            print(f"✅ Generated {len(embeddings)} embeddings using LangChain")
            return embeddings
            
        except Exception as e:
            print(f"❌ Error generating embeddings with LangChain: {e}")
            # Fallback to random embeddings if model fails
            print("🔄 Using fallback random embeddings")
            import numpy as np
            return [np.random.rand(self.embedding_dimensions).tolist() for _ in texts]
    
    async def _process_documents_with_langchain(self, documents: List[Dict], user_id: str) -> List[Dict]:
        """Process documents using LangChain service for optimal chunking and embeddings"""
        try:
            print(f"🔧 Processing {len(documents)} documents with LangChain service...")
            
            # Use LangChain service for document processing
            processed_chunks = await langchain_service.process_documents(documents, user_id)
            
            # Get chunk statistics
            stats = langchain_service.get_chunk_stats(processed_chunks)
            print(f"📊 LangChain processing stats:")
            print(f"   Total chunks: {stats.get('total_chunks', 0)}")
            print(f"   Avg chunk size: {stats.get('avg_chunk_size', 0):.0f} chars")
            print(f"   Min/Max chunk size: {stats.get('min_chunk_size', 0)}/{stats.get('max_chunk_size', 0)} chars")
            
            return processed_chunks
            
        except Exception as e:
            print(f"❌ Error processing documents with LangChain: {e}")
            raise
    
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
    
    async def add_documents(self, documents: List[Dict], source_type: str = "UPLOAD", user_id: str = None):
        """Add documents to PostgreSQL vector store"""
        try:
            print(f"🔍 Starting add_documents for {len(documents)} documents, source_type: {source_type}, user_id: {user_id}")
            db = next(get_db())
            try:
                # Process documents using LangChain service for optimal chunking and embeddings
                print(f"🔧 Processing documents with LangChain service...")
                processed_chunks = await self._process_documents_with_langchain(documents, user_id)
                
                if not processed_chunks:
                    print("⚠️ No chunks processed by LangChain service")
                    return []
                
                print(f"🔍 LangChain processed {len(processed_chunks)} chunks")
                
                # Extract texts and embeddings from processed chunks
                texts = [chunk["text"] for chunk in processed_chunks]
                embeddings = [chunk["embedding"] for chunk in processed_chunks]
                
                # Insert chunks into PostgreSQL using raw SQL for proper vector handling
                print(f"🔍 Starting database insertion for {len(processed_chunks)} chunks...")
                inserted_chunks = []
                
                for i, (chunk, embedding) in enumerate(zip(processed_chunks, embeddings)):
                    print(f"🔍 Processing chunk {i+1}/{len(processed_chunks)}...")
                    
                    # Convert embedding to proper formats
                    print(f"🔍 Debug: embedding type: {type(embedding)}")
                    print(f"🔍 Debug: embedding content: {embedding}")
                    embedding_str = json.dumps(embedding)
                    # Convert embedding to string format for pgvector using a different approach
                    embedding_list = []
                    for x in embedding:
                        embedding_list.append(str(x))
                    embedding_vector_str = f"[{','.join(embedding_list)}]"
                    print(f"🔍 Debug: embedding_vector_str length: {len(embedding_vector_str)}")
                    print(f"🔍 Debug: embedding_vector_str preview: {embedding_vector_str[:100]}...")
                    
                    # Use INSERT with conflict handling
                    # Try ON CONFLICT first, fallback to simple INSERT if constraint doesn't exist
                    upsert_sql = text("""
                        INSERT INTO document_chunks 
                        (chunk_id, user_id, text, document_metadata, source_type, source_id, source_url, page_number, section_title, embedding, embedding_vector, chunk_index, chunk_size, created_at, updated_at)
                        VALUES (:chunk_id, :user_id, :text, :document_metadata, :source_type, :source_id, :source_url, :page_number, :section_title, :embedding, CAST(:embedding_vector AS vector), :chunk_index, :chunk_size, :created_at, :updated_at)
                        ON CONFLICT (chunk_id) 
                        DO UPDATE SET
                            user_id = EXCLUDED.user_id,
                            text = EXCLUDED.text,
                            document_metadata = EXCLUDED.document_metadata,
                            source_type = EXCLUDED.source_type,
                            source_id = EXCLUDED.source_id,
                            source_url = EXCLUDED.source_url,
                            page_number = EXCLUDED.page_number,
                            section_title = EXCLUDED.section_title,
                            embedding = EXCLUDED.embedding,
                            embedding_vector = EXCLUDED.embedding_vector,
                            chunk_index = EXCLUDED.chunk_index,
                            chunk_size = EXCLUDED.chunk_size,
                            updated_at = EXCLUDED.updated_at
                        RETURNING id
                    """)
                    
                    try:
                        result = db.execute(upsert_sql, {
                            "chunk_id": f"{chunk['metadata'].get('page_id', 'unknown')}_{chunk.get('chunk_id', i)}",
                            "user_id": user_id,
                            "text": chunk["text"],
                            "document_metadata": json.dumps(chunk["metadata"]),
                            "source_type": source_type,
                            "source_id": chunk["metadata"].get("page_id") or chunk["metadata"].get("source_id"),
                            "source_url": chunk["metadata"].get("url"),
                            "page_number": chunk["metadata"].get("page"),
                            "section_title": chunk["metadata"].get("section_title", ""),
                            "embedding": embedding_str,
                            "embedding_vector": embedding_vector_str,
                            "chunk_index": chunk["metadata"].get('chunk_index', i),
                            "chunk_size": len(chunk["text"]),
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        })
                    except Exception as e:
                        if "no unique or exclusion constraint" in str(e):
                            print(f"⚠️  ON CONFLICT constraint missing, using simple INSERT")
                            # Fallback to simple INSERT without ON CONFLICT
                            simple_insert_sql = text("""
                                INSERT INTO document_chunks 
                                (chunk_id, user_id, text, document_metadata, source_type, source_id, source_url, page_number, section_title, embedding, embedding_vector, chunk_index, chunk_size, created_at, updated_at)
                                VALUES (:chunk_id, :user_id, :text, :document_metadata, :source_type, :source_id, :source_url, :page_number, :section_title, :embedding, CAST(:embedding_vector AS vector), :chunk_index, :chunk_size, :created_at, :updated_at)
                                RETURNING id
                            """)
                            result = db.execute(simple_insert_sql, {
                                "chunk_id": f"{chunk['metadata'].get('page_id', 'unknown')}_{chunk.get('chunk_id', i)}",
                                "user_id": user_id,
                                "text": chunk["text"],
                                "document_metadata": json.dumps(chunk["metadata"]),
                                "source_type": source_type,
                                "source_id": chunk["metadata"].get("page_id") or chunk["metadata"].get("source_id"),
                                "source_url": chunk["metadata"].get("url"),
                                "page_number": chunk["metadata"].get("page"),
                                "section_title": chunk["metadata"].get("section_title", ""),
                                "embedding": embedding_str,
                                "embedding_vector": embedding_vector_str,
                                "chunk_index": chunk["metadata"].get('chunk_index', i),
                                "chunk_size": len(chunk["text"]),
                                "created_at": datetime.utcnow(),
                                "updated_at": datetime.utcnow()
                            })
                        else:
                            raise
                    
                    # Get the inserted ID
                    inserted_id = result.fetchone()[0]
                    inserted_chunks.append({"id": inserted_id, "chunk_id": f"{chunk['metadata'].get('page_id', 'unknown')}_{chunk.get('chunk_id', i)}"})
                    
                    # Verify the vector was stored correctly
                    verify_query = text("SELECT embedding_vector IS NOT NULL as has_vector FROM document_chunks WHERE id = :id")
                    verify_result = db.execute(verify_query, {"id": inserted_id})
                    has_vector = verify_result.fetchone()[0]
                    print(f"🔍 Debug: Document {inserted_id} has vector: {has_vector}")
                
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
            print(f"🔍 Starting search with query: '{query}', top_k: {top_k}, filter: {filter}")
            db = next(get_db())
            try:
                # Generate query embedding using LangChain service
                print(f"🔍 Generating query embedding with LangChain...")
                query_embedding = await langchain_service.get_query_embedding(query)
                query_embedding_str = json.dumps(query_embedding)
                print(f"🔍 Generated query embedding: {len(query_embedding)} dimensions")
                
                # First, let's check if there are any documents for this user
                if filter and "user_id" in filter:
                    check_query = text("""
                        SELECT COUNT(*) as total_count,
                               COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END) as non_null_embeddings
                        FROM document_chunks 
                        WHERE user_id = :user_id
                    """)
                    check_result = db.execute(check_query, {"user_id": filter["user_id"]})
                    check_row = check_result.fetchone()
                    print(f"🔍 User {filter['user_id']} has {check_row[0]} total documents, {check_row[1]} with embeddings")
                
                # Build the search query with proper pgvector syntax and enhanced metadata
                if filter and "user_id" in filter:
                    # Search with user filter - only include documents with non-null embeddings
                    search_query = text(f"""
                        SELECT 
                            id, text, document_metadata, source_type, source_id, source_url,
                            page_number, section_title, chunk_size, chunk_index,
                            (embedding_vector <=> '{query_embedding_str}'::vector) as distance
                        FROM document_chunks 
                        WHERE user_id = :user_id AND embedding_vector IS NOT NULL
                        ORDER BY embedding_vector <=> '{query_embedding_str}'::vector
                        LIMIT :limit
                    """)
                    
                    result = db.execute(search_query, {
                        "user_id": filter["user_id"],
                        "limit": top_k
                    })
                else:
                    # Search without user filter - only include documents with non-null embeddings
                    search_query = text(f"""
                        SELECT 
                            id, text, document_metadata, source_type, source_id, source_url,
                            page_number, section_title, chunk_size, chunk_index,
                            (embedding_vector <=> '{query_embedding_str}'::vector) as distance
                        FROM document_chunks 
                        WHERE embedding_vector IS NOT NULL
                        ORDER BY embedding_vector <=> '{query_embedding_str}'::vector
                        LIMIT :limit
                    """)
                    
                    result = db.execute(search_query, {
                        "limit": top_k
                    })
                
                # Format results with enhanced metadata and highlighting
                results = []
                all_results = []  # Store all results for fallback
                row_count = 0
                relevance_threshold = 0.3  # Minimum similarity score to include result
                
                for row in result:
                    row_count += 1
                    similarity_score = 1 - row.distance  # Convert distance to similarity score
                    
                    # Store all results for potential fallback
                    all_results.append((row, similarity_score))
                    
                    # Filter out low-relevance results
                    if similarity_score < relevance_threshold:
                        print(f"🔍 Filtering out low-relevance result (score: {similarity_score:.3f})")
                        continue
                    
                    metadata = json.loads(row.document_metadata) if row.document_metadata else {}
                    
                    # Create enhanced result with source information
                    result_item = {
                        "text": row.text,
                        "metadata": metadata,
                        "source_type": row.source_type,
                        "score": similarity_score,
                        "source_info": {
                            "source_id": row.source_id,
                            "source_url": row.source_url,
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
                    print(f"🔍 Keeping relevant result (score: {similarity_score:.3f}): {row.text[:50]}...")
                
                # If no results meet the threshold, return the best result anyway
                if len(results) == 0 and len(all_results) > 0:
                    print(f"🔍 No results met threshold {relevance_threshold}, returning best result")
                    best_row, best_score = max(all_results, key=lambda x: x[1])
                    
                    # Process the best result
                    metadata = json.loads(best_row.document_metadata) if best_row.document_metadata else {}
                    result_item = {
                        "text": best_row.text,
                        "metadata": metadata,
                        "source_type": best_row.source_type,
                        "score": best_score,
                        "source_info": {
                            "source_id": best_row.source_id,
                            "source_url": best_row.source_url,
                            "page_number": best_row.page_number,
                            "section_title": best_row.section_title,
                            "chunk_size": best_row.chunk_size,
                            "chunk_index": best_row.chunk_index
                        }
                    }
                    
                    # Add highlighting
                    from app.services.document_processor import DocumentProcessor
                    highlighted_text = DocumentProcessor._highlight_query_terms(best_row.text, query)
                    result_item["highlighted_text"] = highlighted_text
                    
                    # Add summary
                    if best_row.section_title:
                        result_item["summary"] = f"From {best_row.section_title}"
                        if best_row.page_number:
                            result_item["summary"] += f" (Page {best_row.page_number})"
                    elif best_row.page_number:
                        result_item["summary"] = f"Page {best_row.page_number}"
                    
                    results.append(result_item)
                    print(f"🔍 Fallback: Using best result (score: {best_score:.3f}): {best_row.text[:50]}...")
                
                print(f"🔍 Found {row_count} total results, returning {len(results)} relevant results (threshold: {relevance_threshold})")
                
                # Return results (now using LangChain embeddings)
                if results:
                    print(f"🔍 Returning {len(results)} results with LangChain embeddings")
                    return results
                else:
                    print(f"🔍 No results found, returning empty list")
                    return []
                
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

async def add_documents_to_store(documents: List[Dict], source_type: str = "UPLOAD", user_id: str = None):
    """Add documents to PostgreSQL vector store"""
    return await postgres_vector_store.add_documents(documents, source_type, user_id)

async def search_documents(query: str, top_k: int = 5, filter: Dict = None):
    """Search documents in PostgreSQL vector store"""
    return await postgres_vector_store.search(query, top_k, filter)
