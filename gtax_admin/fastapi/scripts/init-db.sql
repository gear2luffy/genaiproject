-- Database initialization script for Docker
-- This runs when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE taskdb TO postgres;

-- Create additional indexes for search (optional)
-- These will be created by Alembic migrations, but can be pre-created here
