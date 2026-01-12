"""
认证API路由
"""
from flask import Blueprint, request, jsonify, g
from .config import AuthConfig
from .jwt_utils import JWTManager
from .decorators import token_required

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': '无效请求',
            'message': '请求体必须是JSON格式'
        }), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'error': '参数缺失',
            'message': '用户名和密码不能为空'
        }), 400
    
    # 验证用户
    user_info = AuthConfig.verify_user(username, password)
    if not user_info:
        return jsonify({
            'error': '认证失败',
            'message': '用户名或密码错误'
        }), 401
    
    # 创建令牌
    tokens = JWTManager.create_tokens(user_info)
    
    return jsonify({
        'message': '登录成功',
        'data': tokens
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """刷新访问令牌"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': '无效请求',
            'message': '请求体必须是JSON格式'
        }), 400
    
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({
            'error': '参数缺失',
            'message': '刷新令牌不能为空'
        }), 400
    
    try:
        # 刷新访问令牌
        new_access_token = JWTManager.refresh_access_token(refresh_token)
        
        return jsonify({
            'message': '令牌刷新成功',
            'data': {
                'access_token': new_access_token,
                'token_type': 'Bearer',
                'expires_in': int(AuthConfig.ACCESS_TOKEN_EXPIRES.total_seconds())
            }
        }), 200
    except ValueError as e:
        return jsonify({
            'error': '令牌刷新失败',
            'message': str(e)
        }), 401

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """获取当前用户信息"""
    return jsonify({
        'message': '获取用户信息成功',
        'data': {
            'user': g.user_info
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """用户登出"""
    # 注意：JWT是无状态的，客户端需要删除本地存储的令牌
    # 如果需要服务端控制，可以在这里将令牌加入黑名单
    return jsonify({
        'message': '登出成功',
        'data': None
    }), 200

@auth_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    """获取用户列表（仅管理员）"""
    # 检查是否是管理员
    if g.role != 'admin':
        return jsonify({
            'error': '权限不足',
            'message': '需要管理员权限'
        }), 403
    
    # 从数据库获取用户列表
    conn = AuthConfig.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, name, email, role, created_at, updated_at
        FROM users
        ORDER BY id
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'message': '获取用户列表成功',
        'data': {
            'users': [dict(user) for user in users],
            'total': len(users)
        }
    }), 200
