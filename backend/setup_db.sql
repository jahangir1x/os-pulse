-- OS-Pulse Database Setup
-- Run this if you need to set up the database manually

-- Create database (run this as postgres superuser)
-- CREATE DATABASE ospulse;

-- Connect to ospulse database and run the following:

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(255) PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monitoring_started TIMESTAMP NULL,
    monitoring_ended TIMESTAMP NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE
);

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    source VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    is_sent BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key constraint
ALTER TABLE events 
ADD CONSTRAINT fk_events_session 
FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_session_id ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_is_sent ON events(is_sent);
CREATE INDEX IF NOT EXISTS idx_events_session_sent ON events(session_id, is_sent);

-- Insert sample data (optional)
-- INSERT INTO sessions (id, file_name, is_active) 
-- VALUES ('test-session-1', 'sample.txt', false);