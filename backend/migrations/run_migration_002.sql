-- Run this SQL to make session_id optional in events table
-- This allows storing events without a sessionId and removes foreign key constraint

-- Drop the foreign key constraint between events and sessions
ALTER TABLE events DROP CONSTRAINT IF EXISTS fk_sessions_events;

-- Make session_id nullable
ALTER TABLE events ALTER COLUMN session_id DROP NOT NULL;

-- Verify the changes
SELECT 
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_name = 'events';

SELECT column_name, is_nullable, data_type 
FROM information_schema.columns 
WHERE table_name = 'events' AND column_name = 'session_id';
