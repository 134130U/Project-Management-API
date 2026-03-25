-- =====================================
-- DATABASE
-- =====================================

-- We use 'projects' instead of 'project_management' to match .env/docker-compose.yml
-- but since this script might be run manually, we keep it consistent.

CREATE DATABASE projects;

-- =====================================
-- USER
-- =====================================

CREATE USER admin WITH PASSWORD 'admin';

ALTER DATABASE projects OWNER TO admin;

GRANT ALL PRIVILEGES ON DATABASE projects TO admin;

-- =====================================
-- CONNECT
-- =====================================

\c projects;

-- =====================================
-- EXTENSIONS
-- =====================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =====================================
-- TABLES
-- =====================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE updates (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    update_id INTEGER REFERENCES updates(id) ON DELETE CASCADE,
    storage_key TEXT,
    filename TEXT,
    size INTEGER,
    mime_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================
-- INDEXES
-- =====================================

CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_updates_project ON updates(project_id);
CREATE INDEX idx_files_update ON files(update_id);
CREATE INDEX idx_users_email ON users(email);

-- =====================================
-- PERMISSIONS
-- =====================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;