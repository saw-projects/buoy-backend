CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    password_last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    auth_jwt VARCHAR(255),
    -- auth_provider VARCHAR(255),
    -- auth_jwt_last_updated TIMESTAMP,
    -- frontend_jwt VARCHAR(255),
    -- frontend_jwt_last_updated TIMESTAMP,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(255) PRIMARY KEY NOT NULL,
    user_id INTEGER NOT NULL,
    input_text TEXT NOT NULL,
    result_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    error_description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
);
