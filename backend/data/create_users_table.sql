-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- 插入默认用户（密码使用bcrypt哈希）
-- 默认密码：admin123 的bcrypt哈希
INSERT OR IGNORE INTO users (username, password_hash, name, email, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0L6kfCuCr0OjWYlKpR3bVZ2oB7WnNQY8Jm6XaK', '系统管理员', 'admin@example.com', 'admin'),
('user', '$2b$12$LQv3c1yqBWVHxkd0L6kfCuCr0OjWYlKpR3bVZ2oB7WnNQY8Jm6XaK', '普通用户', 'user@example.com', 'user');
