-- Migration: 001_initial_schema.sql
-- Description: Initial database schema for contract management
-- Created: 2025-08-22

-- Create enum types
CREATE TYPE contract_status AS ENUM (
    'pending',
    'in_progress', 
    'awaiting_review',
    'completed',
    'cancelled',
    'failed'
);

CREATE TYPE contract_priority AS ENUM (
    'low',
    'medium',
    'high',
    'immediate'
);

-- Create contracts table
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Contract metadata
    allowed_files JSONB,
    completion_criteria JSONB,
    dependencies JSONB,
    
    -- Status and assignment
    status contract_status DEFAULT 'pending' NOT NULL,
    progress_percentage INTEGER DEFAULT 0 NOT NULL,
    assigned_to VARCHAR(100),
    priority contract_priority DEFAULT 'medium' NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Notes and coordination
    captain_notes TEXT,
    worker_notes TEXT,
    tester_notes TEXT,
    coordination_notes TEXT,
    
    -- Additional metadata
    metadata JSONB
);

-- Create contract_logs table
CREATE TABLE contract_logs (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    
    -- Log entry details
    action VARCHAR(100) NOT NULL,
    actor VARCHAR(100) NOT NULL,
    message TEXT,
    
    -- Data changes
    old_values JSONB,
    new_values JSONB,
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Additional context
    metadata JSONB
);

-- Create system_config table
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    value_type VARCHAR(50) DEFAULT 'string' NOT NULL,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_contracts_contract_id ON contracts(contract_id);
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_contracts_priority ON contracts(priority);
CREATE INDEX idx_contracts_assigned_to ON contracts(assigned_to);
CREATE INDEX idx_contracts_status_priority ON contracts(status, priority);
CREATE INDEX idx_contracts_assigned_status ON contracts(assigned_to, status);
CREATE INDEX idx_contracts_created_updated ON contracts(created_at, updated_at);

CREATE INDEX idx_contract_logs_contract_id ON contract_logs(contract_id);
CREATE INDEX idx_contract_logs_action ON contract_logs(action);
CREATE INDEX idx_contract_logs_actor ON contract_logs(actor);
CREATE INDEX idx_contract_logs_timestamp ON contract_logs(timestamp);
CREATE INDEX idx_contract_logs_contract_timestamp ON contract_logs(contract_id, timestamp);
CREATE INDEX idx_contract_logs_action_actor ON contract_logs(action, actor);

CREATE INDEX idx_system_config_key ON system_config(key);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_contracts_updated_at 
    BEFORE UPDATE ON contracts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at 
    BEFORE UPDATE ON system_config 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial system configuration
INSERT INTO system_config (key, value, value_type, description) VALUES
    ('database_version', '1.0.0', 'string', 'Current database schema version'),
    ('migration_timestamp', CURRENT_TIMESTAMP::text, 'string', 'Timestamp of last migration'),
    ('backup_enabled', 'true', 'bool', 'Enable automatic database backups'),
    ('backup_interval_hours', '24', 'int', 'Backup interval in hours');

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO megamind;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO megamind;
