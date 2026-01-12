"""
权限装饰器模块
"""
from functools import wraps
from flask import request, jsonify, g
from .jwt_utils import JWTManager
from .config import AuthConfig

def token_required(f):
    """验证JWT令牌的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头获取令牌
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'error': '未授权访问',
                'message': '令牌缺失'
            }), 401
        
        try:
            # 验证令牌
            payload = JWTManager.verify_token(token)
            
            # 检查令牌类型
            if payload.get('type') != 'access':
                return jsonify({
                    'error': '未授权访问',
                    'message': '无效的令牌类型'
                }), 401
            
            # 将用户信息保存到g对象
            g.user_info = payload['user_info']
            g.role = payload['user_info']['role']
            g.username = payload['user_info']['username']
            
        except ValueError as e:
            return jsonify({
                'error': '未授权访问',
                'message': str(e)
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated

def permission_required(permission):
    """检查权限的装饰器"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            # 检查用户角色是否有权限
            if not AuthConfig.has_permission(g.role, permission):
                return jsonify({
                    'error': '权限不足',
                    'message': f'需要 {permission} 权限',
                    'required_permission': permission,
                    'user_role': g.role
                }), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def admin_required(f):
    """要求管理员角色的装饰器"""
    return permission_required('write')(f)

def read_permission_required(f):
    """要求读取权限的装饰器"""
    return permission_required('read')(f)

def write_permission_required(f):
    """要求写入权限的装饰器"""
    return permission_required('write')(f)
