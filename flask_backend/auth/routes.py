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

@auth_bp.route('/users', methods=['POST'])
@token_required
def create_user():
    """创建新用户（仅管理员）"""
    # 检查是否是管理员
    if g.role != 'admin':
        return jsonify({
            'error': '权限不足',
            'message': '需要管理员权限'
        }), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': '无效请求',
            'message': '请求体必须是JSON格式'
        }), 400
    
    # 验证必填字段
    required_fields = ['username', 'password', 'name', 'email', 'role']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'error': '参数缺失',
                'message': f'{field}不能为空'
            }), 400
    
    username = data['username']
    password = data['password']
    name = data['name']
    email = data['email']
    role = data['role']
    
    # 验证角色
    if role not in ['admin', 'user']:
        return jsonify({
            'error': '参数错误',
            'message': '角色必须是admin或user'
        }), 400
    
    # 检查用户名是否已存在
    conn = AuthConfig.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({
            'error': '用户已存在',
            'message': '用户名已被使用'
        }), 409
    
    # 创建密码哈希
    import bcrypt
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 插入新用户
    cursor.execute('''
        INSERT INTO users (username, password_hash, name, email, role, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    ''', (username, password_hash, name, email, role))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': '用户创建成功',
        'data': {
            'id': user_id,
            'username': username,
            'name': name,
            'email': email,
            'role': role
        }
    }), 201

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    """删除用户（仅管理员）"""
    # 检查是否是管理员
    if g.role != 'admin':
        return jsonify({
            'error': '权限不足',
            'message': '需要管理员权限'
        }), 403
    
    conn = AuthConfig.get_db_connection()
    cursor = conn.cursor()
    
    # 获取当前用户的ID
    cursor.execute('SELECT id FROM users WHERE username = ?', (g.username,))
    current_user = cursor.fetchone()
    
    if not current_user:
        conn.close()
        return jsonify({
            'error': '用户不存在',
            'message': '当前用户不存在'
        }), 404
    
    current_user_id = current_user['id']
    
    # 不能删除自己
    if user_id == current_user_id:
        conn.close()
        return jsonify({
            'error': '操作不允许',
            'message': '不能删除自己的账户'
        }), 400
    
    # 检查要删除的用户是否存在
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({
            'error': '未找到',
            'message': '请求的资源不存在'
        }), 404
    
    # 删除用户
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': '用户删除成功',
        'data': {
            'id': user_id,
            'username': user['username']
        }
    }), 200

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """更新用户信息（仅管理员）"""
    # 检查是否是管理员
    if g.role != 'admin':
        return jsonify({
            'error': '权限不足',
            'message': '需要管理员权限'
        }), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': '无效请求',
            'message': '请求体必须是JSON格式'
        }), 400
    
    conn = AuthConfig.get_db_connection()
    cursor = conn.cursor()
    
    # 检查用户是否存在
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({
            'error': '未找到',
            'message': '请求的资源不存在'
        }), 404
    
    # 构建更新字段
    update_fields = []
    update_values = []
    
    if 'name' in data:
        update_fields.append('name = ?')
        update_values.append(data['name'])
    
    if 'email' in data:
        update_fields.append('email = ?')
        update_values.append(data['email'])
    
    if 'role' in data:
        if data['role'] not in ['admin', 'user']:
            conn.close()
            return jsonify({
                'error': '参数错误',
                'message': '角色必须是admin或user'
            }), 400
        update_fields.append('role = ?')
        update_values.append(data['role'])
    
    if 'password' in data and data['password']:
        import bcrypt
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        update_fields.append('password_hash = ?')
        update_values.append(password_hash)
    
    if not update_fields:
        conn.close()
        return jsonify({
            'error': '参数缺失',
            'message': '没有提供更新字段'
        }), 400
    
    # 添加更新时间
    update_fields.append('updated_at = datetime("now")')
    
    # 执行更新
    update_values.append(user_id)
    update_query = f'UPDATE users SET {", ".join(update_fields)} WHERE id = ?'
    
    cursor.execute(update_query, update_values)
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': '用户更新成功',
        'data': {
            'id': user_id,
            'username': user['username']
        }
    }), 200
