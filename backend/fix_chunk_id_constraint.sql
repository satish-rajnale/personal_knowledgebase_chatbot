-- Fix chunk_id unique constraint for ON CONFLICT to work
-- Run this script in your PostgreSQL database

-- First, check if the constraint already exists
DO $$
BEGIN
    -- Add unique constraint on chunk_id if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'document_chunks' 
        AND constraint_name = 'document_chunks_chunk_id_key'
        AND constraint_type = 'UNIQUE'
    ) THEN
        -- Add the unique constraint
        ALTER TABLE document_chunks ADD CONSTRAINT document_chunks_chunk_id_key UNIQUE (chunk_id);
        RAISE NOTICE 'Added unique constraint on chunk_id';
    ELSE
        RAISE NOTICE 'Unique constraint on chunk_id already exists';
    END IF;
END $$;

-- Verify the constraint was added
SELECT 
    constraint_name, 
    constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'document_chunks' 
AND constraint_type = 'UNIQUE';
