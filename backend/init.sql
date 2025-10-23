-- PostgreSQL initialization script for knowledgebase
-- This script runs when the PostgreSQL container starts for the first time

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create database if it doesn't exist (though it should already exist from environment)
-- This is just a safety check
SELECT 'CREATE DATABASE knowledgebase'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'knowledgebase')\gexec

-- Connect to the knowledgebase database
\c knowledgebase;

-- Enable pgvector extension in the knowledgebase database
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a function to convert JSON array to vector
CREATE OR REPLACE FUNCTION json_array_to_vector(json_array TEXT)
RETURNS vector AS $$
BEGIN
    RETURN json_array::vector;
END;
$$ LANGUAGE plpgsql;

-- Note: The document_chunks table will be created by SQLAlchemy models
-- with the following structure:
-- - id: SERIAL PRIMARY KEY
-- - chunk_id: VARCHAR UNIQUE
-- - user_id: VARCHAR REFERENCES users(user_id)
-- - text: TEXT NOT NULL
-- - document_metadata: TEXT (JSON metadata)
-- - source_type: VARCHAR NOT NULL
-- - source_id: VARCHAR
-- - source_url: VARCHAR
-- - embedding: TEXT (JSON array of floats)
-- - embedding_vector: vector(384) (pgvector column)
-- - chunk_index: INTEGER DEFAULT 0
-- - created_at: TIMESTAMP DEFAULT NOW()
-- - updated_at: TIMESTAMP DEFAULT NOW()

-- Create indexes for better performance (will be created by SQLAlchemy models)
-- These are just examples - the actual indexes will be created by the application

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL with pgvector initialized successfully for knowledgebase';
END $$;
