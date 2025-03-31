-- Initial database schema

-- Create test_items table
CREATE TABLE IF NOT EXISTS test_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert some test data
INSERT INTO test_items (name, description) VALUES
    ('Test Item 1', 'This is the first test item'),
    ('Test Item 2', 'This is the second test item'),
    ('Test Item 3', 'This is the third test item');

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_test_items_updated_at
    BEFORE UPDATE ON test_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 0001_initial.sql completed successfully';
END $$;
