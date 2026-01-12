"""
认证模块配置
"""
import os
import sqlite3
import bcrypt
from datetime import timedelta

class AuthConfig:
    """认证配置类"""
    
    # JWT配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # 数据库路径
    DB_PATH = os.path.join(os.path.dirname(__file__), '../../backend/data/monitoring.db')
    
    # 权限配置
    PERMISSIONS = {
        'admin': ['read', 'write', 'delete', 'manage_users'],
        'user': ['read']
    }
    
    @classmethod
    def get_db_connection(cls):
        """获取数据库连接"""
        conn = sqlite3.connect(cls.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    @classmethod
    def get_user(cls, username):
        """从数据库获取用户信息"""
        conn = cls.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, name, email, role
            FROM users
            WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    @classmethod
    def verify_user(cls, username, password):
        """验证用户"""
        user = cls.get_user(username)
        if user:
            # 使用bcrypt验证密码
            try:
                if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    return {
                        'username': user['username'],
                        'role': user['role'],
                        'email': user['email'],
                        'name': user['name']
                    }
            except Exception:
                # 如果bcrypt验证失败，尝试直接比较（向后兼容）
                if user['password_hash'] == password:
                    return {
                        'username': user['username'],
                        'role': user['role'],
                        'email': user['email'],
                        'name': user['name']
                    }
        return None
    
    @classmethod
    def has_permission(cls, role, permission):
        """检查角色是否有权限"""
        return permission in cls.PERMISSIONS.get(role, [])
