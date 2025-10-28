DROP INDEX IF EXISTS idx_events_session_sent;
DROP INDEX IF EXISTS idx_events_is_sent;
DROP INDEX IF EXISTS idx_events_timestamp;
DROP INDEX IF EXISTS idx_events_session_id;

DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS sessions;