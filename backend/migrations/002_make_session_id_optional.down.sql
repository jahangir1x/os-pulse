-- Revert session_id to NOT NULL in events table
UPDATE events SET session_id = 'unknown' WHERE session_id IS NULL OR session_id = '';
ALTER TABLE events ALTER COLUMN session_id SET NOT NULL;

-- Re-add the foreign key constraint
ALTER TABLE events ADD CONSTRAINT fk_sessions_events 
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE;
