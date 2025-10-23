# This file is deprecated - use postgres_vector_store.py instead
# Keeping for backward compatibility during migration

from app.services.postgres_vector_store import (
    init_vector_store,
    add_documents_to_store,
    search_documents,
    postgres_vector_store as vector_store,
    PostgresVectorStore
)

# Legacy compatibility - redirect to PostgreSQL implementation
VectorStore = PostgresVectorStore

__all__ = [
    "init_vector_store",
    "add_documents_to_store", 
    "search_documents",
    "vector_store",
    "VectorStore"
]