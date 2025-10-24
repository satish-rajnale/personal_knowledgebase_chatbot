-- Add missing columns to document_chunks table
-- Run this script in your PostgreSQL database

-- Add page_number column
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS page_number INTEGER;

-- Add section_title column  
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS section_title VARCHAR;

-- Add chunk_size column
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS chunk_size INTEGER DEFAULT 0;

-- Update existing records to have chunk_size calculated from text length
UPDATE document_chunks 
SET chunk_size = LENGTH(text) 
WHERE chunk_size IS NULL OR chunk_size = 0;

-- Verify the columns were added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'document_chunks' 
AND column_name IN ('page_number', 'section_title', 'chunk_size')
ORDER BY column_name;
