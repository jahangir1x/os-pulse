-- Drop the foreign key constraint between events and sessions
ALTER TABLE events DROP CONSTRAINT IF EXISTS fk_sessions_events;

-- Make session_id nullable in events table
ALTER TABLE events ALTER COLUMN session_id DROP NOT NULL;
