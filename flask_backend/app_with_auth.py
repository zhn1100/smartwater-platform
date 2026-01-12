#!/usr/bin/env python3
"""
Flask后端应用 - 智慧水利监测数据API（带用户认证）
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import pandas as pd
from datetime import datetime, timedelta

# 导入认证模块
from auth import auth_bp, read_permission_required, write_permission_required

# 创建Flask应用
app = Flask(__name__)

# CORS配置 - 生产环境更安全
if os.environ.get('FLASK_ENV') == 'production':
    # 生产环境：只允许特定来源
    frontend_url = os.environ.get('FRONTEND_URL', 'https://frontend-smartwater-platform.ondigitalocean.app')
    CORS(app, resources={
        r"/api/*": {
            "origins": [frontend_url],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": False,
            "max_age": 600
        }
    })
else:
    # 开发环境：允许所有来源
    CORS(app, resources={r"/api/*": {"origins": "*"}})

# 注册认证蓝图
app.register_blueprint(auth_bp)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '../backend/data/monitoring.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 返回字典格式的结果
    return conn

# ==================== 健康检查端点 ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': '智慧水利监测数据API',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'features': ['数据查询', '统计分析', '用户认证', '权限控制']
    })

@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({
        'message': '欢迎使用智慧水利监测数据API',
        'version': '2.0.0',
        'endpoints': {
            'auth': '/api/auth/*',
            'data': '/api/types, /api/instruments, /api/measurements',
            'stats': '/api/statistics',
            'health': '/api/health'
        },
        'documentation': '/api/docs'
    })

# ==================== 监测类型端点 ====================
@app.route('/api/types', methods=['GET'])
@read_permission_required
def get_monitoring_types():
    """获取监测类型列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM monitoring_type ORDER BY id')
    types = cursor.fetchall()
    
    conn.close()
    
    return jsonify([dict(type) for type in types])

# ==================== 仪器端点 ====================
@app.route('/api/instruments', methods=['GET'])
@read_permission_required
def get_instruments():
    """获取仪器列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT instrument_id, type_id
        FROM measurement
        ORDER BY instrument_id
    ''')
    instruments = cursor.fetchall()
    
    # 获取类型名称
    cursor.execute('SELECT id, name FROM monitoring_type')
    type_map = {id: name for id, name in cursor.fetchall()}
    
    conn.close()
    
    result = []
    for inst in instruments:
        result.append({
            'instrument_id': inst['instrument_id'],
            'type_id': inst['type_id'],
            'type_name': type_map.get(inst['type_id'], '未知类型')
        })
    
    return jsonify(result)

# ==================== 测量数据端点 ====================
@app.route('/api/measurements', methods=['GET'])
@read_permission_required
def get_measurements():
    """获取测量数据"""
    # 获取查询参数
    type_id = request.args.get('type_id', type=int)
    instrument_id = request.args.get('instrument_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    limit = request.args.get('limit', default=100, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 构建查询
    query = '''
        SELECT m.*, t.name as type_name, t.unit
        FROM measurement m
        JOIN monitoring_type t ON m.type_id = t.id
        WHERE 1=1
    '''
    params = []
    
    if type_id:
        query += ' AND m.type_id = ?'
        params.append(type_id)
    
    if instrument_id:
        query += ' AND m.instrument_id = ?'
        params.append(instrument_id)
    
    if start_time:
        query += ' AND m.measure_time >= ?'
        params.append(start_time)
    
    if end_time:
        query += ' AND m.measure_time <= ?'
        params.append(end_time)
    
    query += ' ORDER BY m.measure_time DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    measurements = cursor.fetchall()
    
    conn.close()
    
    return jsonify([dict(m) for m in measurements])

# ==================== 统计数据端点 ====================
@app.route('/api/statistics', methods=['GET'])
@read_permission_required
def get_statistics():
    """获取统计数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 总记录数
    cursor.execute('SELECT COUNT(*) FROM measurement')
    total_measurements = cursor.fetchone()[0]
    
    # 按类型统计
    cursor.execute('''
        SELECT t.name, COUNT(*) as count, AVG(m.value) as avg_value
        FROM measurement m
        JOIN monitoring_type t ON m.type_id = t.id
        GROUP BY t.id, t.name
    ''')
    type_stats = cursor.fetchall()
    
    # 时间范围
    cursor.execute('SELECT MIN(measure_time), MAX(measure_time) FROM measurement')
    time_range = cursor.fetchone()
    
    # 仪器数量
    cursor.execute('SELECT COUNT(DISTINCT instrument_id) FROM measurement')
    instrument_count = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_measurements': total_measurements,
        'type_statistics': [
            {
                'name': stat['name'],
                'count': stat['count'],
                'avg_value': round(stat['avg_value'] or 0, 2)
            }
            for stat in type_stats
        ],
        'time_range': {
            'start': time_range[0],
            'end': time_range[1]
        },
        'instrument_count': instrument_count
    })

# ==================== 数据摘要端点 ====================
@app.route('/api/measurements/summary', methods=['GET'])
@read_permission_required
def get_measurements_summary():
    """获取数据摘要（按时间间隔分组）"""
    interval = request.args.get('interval', 'month')  # day, week, month, year
    type_id = request.args.get('type_id', type=int)
    limit = request.args.get('limit', default=12, type=int)
    
    # 根据间隔确定日期格式
    if interval == 'day':
        date_format = '%Y-%m-%d'
    elif interval == 'week':
        date_format = '%Y-%W'
    elif interval == 'month':
        date_format = '%Y-%m'
    else:  # year
        date_format = '%Y'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            strftime(?, m.measure_time) as period,
            COUNT(*) as count,
            AVG(m.value) as avg_value,
            MIN(m.value) as min_value,
            MAX(m.value) as max_value
        FROM measurement m
        WHERE 1=1
    '''
    params = [date_format]
    
    if type_id:
        query += ' AND m.type_id = ?'
        params.append(type_id)
    
    query += '''
        GROUP BY period
        ORDER BY period DESC
        LIMIT ?
    '''
    params.append(limit)
    
    cursor.execute(query, params)
    summary = cursor.fetchall()
    
    conn.close()
    
    return jsonify([
        {
            'period': row['period'],
            'count': row['count'],
            'avg_value': round(row['avg_value'] or 0, 2),
            'min_value': round(row['min_value'] or 0, 2),
            'max_value': round(row['max_value'] or 0, 2)
        }
        for row in summary
    ])

# ==================== 写入数据端点（需要管理员权限） ====================
@app.route('/api/measurements', methods=['POST'])
@write_permission_required
def create_measurement():
    """创建新的测量记录（需要写入权限）"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效请求', 'message': '请求体必须是JSON格式'}), 400
    
    # 验证必要字段
    required_fields = ['type_id', 'instrument_id', 'measure_time', 'value']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': '参数缺失', 'message': f'缺少必要字段: {field}'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO measurement (type_id, instrument_id, measure_time, value, water_level)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['type_id'],
            data['instrument_id'],
            data['measure_time'],
            data['value'],
            data.get('water_level')
        ))
        
        measurement_id = cursor.lastrowid
        conn.commit()
        
        # 获取新创建的记录
        cursor.execute('''
            SELECT m.*, t.name as type_name, t.unit
            FROM measurement m
            JOIN monitoring_type t ON m.type_id = t.id
            WHERE m.id = ?
        ''', (measurement_id,))
        
        new_measurement = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'message': '测量记录创建成功',
            'data': dict(new_measurement)
        }), 201
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': '创建失败', 'message': str(e)}), 500

@app.route('/api/measurements/<int:measurement_id>', methods=['PUT'])
@write_permission_required
def update_measurement(measurement_id):
    """更新测量记录（需要写入权限）"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效请求', 'message': '请求体必须是JSON格式'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查记录是否存在
        cursor.execute('SELECT id FROM measurement WHERE id = ?', (measurement_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': '记录不存在', 'message': f'ID为{measurement_id}的记录不存在'}), 404
        
        # 构建更新语句
        update_fields = []
        params = []
        
        if 'value' in data:
            update_fields.append('value = ?')
            params.append(data['value'])
        
        if 'measure_time' in data:
            update_fields.append('measure_time = ?')
            params.append(data['measure_time'])
        
        if 'water_level' in data:
            update_fields.append('water_level = ?')
            params.append(data['water_level'])
        
        if not update_fields:
            conn.close()
            return jsonify({'error': '无效请求', 'message': '没有提供要更新的字段'}), 400
        
        params.append(measurement_id)
        
        update_query = f'''
            UPDATE measurement 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        
        cursor.execute(update_query, params)
        conn.commit()
        
        # 获取更新后的记录
        cursor.execute('''
            SELECT m.*, t.name as type_name, t.unit
            FROM measurement m
            JOIN monitoring_type t ON m.type_id = t.id
            WHERE m.id = ?
        ''', (measurement_id,))
        
        updated_measurement = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'message': '测量记录更新成功',
            'data': dict(updated_measurement)
        }), 200
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': '更新失败', 'message': str(e)}), 500

@app.route('/api/measurements/<int:measurement_id>', methods=['DELETE'])
@write_permission_required
def delete_measurement(measurement_id):
    """删除测量记录（需要写入权限）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查记录是否存在
        cursor.execute('SELECT id FROM measurement WHERE id = ?', (measurement_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': '记录不存在', 'message': f'ID为{measurement_id}的记录不存在'}), 404
        
        # 删除记录
        cursor.execute('DELETE FROM measurement WHERE id = ?', (measurement_id,))
        conn.commit()
        
        conn.close()
        
        return jsonify({
            'message': '测量记录删除成功',
            'data': {'id': measurement_id}
        }), 200
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': '删除失败', 'message': str(e)}), 500

# ==================== 用户管理端点（需要管理员权限） ====================
@app.route('/api/users', methods=['GET'])
@write_permission_required
def get_users():
    """获取用户列表（需要管理员权限）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, name, email, role, created_at, updated_at
        FROM users
        ORDER BY id
    ''')
    users = cursor.fetchall()
    
    conn.close()
    
    return jsonify([dict(user) for user in users])

@app.route('/api/users', methods=['POST'])
@write_permission_required
def create_user():
    """创建新用户（需要管理员权限）"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效请求', 'message': '请求体必须是JSON格式'}), 400
    
    # 验证必要字段
    required_fields = ['username', 'password', 'name', 'email', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': '参数缺失', 'message': f'缺少必要字段: {field}'}), 400
    
    # 验证角色
    if data['role'] not in ['admin', 'user']:
        return jsonify({'error': '参数错误', 'message': '角色必须是admin或user'}), 400
    
    # 检查用户名是否已存在
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE username = ?', (data['username'],))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': '用户已存在', 'message': '用户名已存在'}), 400
    
    try:
        # 使用bcrypt哈希密码
        import bcrypt
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, name, email, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['username'],
            password_hash,
            data['name'],
            data['email'],
            data['role']
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # 获取新创建的用户
        cursor.execute('''
            SELECT id, username, name, email, role, created_at, updated_at
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        new_user = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'message': '用户创建成功',
            'data': dict(new_user)
        }), 201
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': '创建失败', 'message': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@write_permission_required
def delete_user(user_id):
    """删除用户（需要管理员权限）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查用户是否存在
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': '用户不存在', 'message': f'ID为{user_id}的用户不存在'}), 404
        
        # 不能删除默认管理员用户（id为1）
        if user_id == 1:
            conn.close()
            return jsonify({'error': '禁止删除', 'message': '不能删除默认管理员用户'}), 400
        
        # 删除用户
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        
        conn.close()
        
        return jsonify({
            'message': '用户删除成功',
            'data': {'id': user_id}
        }), 200
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': '删除失败', 'message': str(e)}), 500

# ==================== 错误处理 ====================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '未找到', 'message': '请求的资源不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误', 'message': '服务器处理请求时发生错误'}), 500

# ==================== 主函数 ====================
if __name__ == '__main__':
    print("启动智慧水利监测数据API（带用户认证）...")
    print("默认用户:")
    print("  管理员: admin / admin123")
    print("  普通用户: user / user123")
    print("API文档: http://localhost:5000/")
    app.run(host='0.0.0.0', port=5000, debug=True)
