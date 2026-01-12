# 智慧水利监测数据API - 带用户认证版本

基于Flask的后端API服务，提供水利监测数据的RESTful接口，包含完整的用户认证和权限控制系统。

## 功能特性

- **数据访问**: 提供四种监测类型的数据访问：引张线、静力水准、水位、倒垂线
- **用户认证**: 完整的JWT令牌认证系统
- **权限控制**: 基于角色的权限管理（管理员/普通用户）
- **数据操作**: 支持数据的增删改查操作
- **统计分析**: 提供数据统计和摘要信息
- **跨域支持**: 支持跨域请求（CORS）
- **健康检查**: 服务健康状态监控

## 用户角色和权限

### 管理员 (admin)
- **用户名**: admin
- **密码**: admin123
- **权限**: 
  - 读取所有数据
  - 创建新的测量记录
  - 更新现有测量记录
  - 删除测量记录
  - 查看用户列表

### 普通用户 (user)
- **用户名**: user
- **密码**: user123
- **权限**:
  - 读取所有数据
  - 查看自己的用户信息

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行服务（带认证版本）

```bash
python app_with_auth.py
```

服务将在 http://localhost:5000 启动。

### 3. 验证安装

访问 http://localhost:5000/api/health 检查服务状态。

## API接口文档

### 认证相关接口

#### 用户登录
- `POST /api/auth/login` - 用户登录，获取访问令牌

**请求体：**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例：**
```json
{
  "message": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user_info": {
      "username": "admin",
      "role": "admin",
      "email": "admin@example.com",
      "name": "系统管理员"
    }
  }
}
```

#### 刷新令牌
- `POST /api/auth/refresh` - 使用刷新令牌获取新的访问令牌

**请求体：**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 获取当前用户信息
- `GET /api/auth/me` - 获取当前登录用户信息（需要认证）

#### 用户登出
- `POST /api/auth/logout` - 用户登出（需要认证）

#### 获取用户列表
- `GET /api/auth/users` - 获取所有用户列表（仅管理员）

### 数据访问接口（需要认证）

所有数据访问接口都需要在请求头中添加认证令牌：
```
Authorization: Bearer <access_token>
```

#### 基础信息
- `GET /` - 获取API基本信息
- `GET /api/health` - 健康检查

#### 监测类型
- `GET /api/types` - 获取所有监测类型（需要读取权限）

#### 仪器列表
- `GET /api/instruments` - 获取所有仪器列表（需要读取权限）

#### 测量数据查询
- `GET /api/measurements` - 获取测量数据（需要读取权限）

**查询参数：**
- `type_id` (可选): 监测类型ID
- `instrument_id` (可选): 仪器ID
- `start_time` (可选): 开始时间 (格式: YYYY-MM-DD HH:MM:SS)
- `end_time` (可选): 结束时间 (格式: YYYY-MM-DD HH:MM:SS)
- `limit` (可选): 返回记录数，默认100

#### 统计数据
- `GET /api/statistics` - 获取总体统计数据（需要读取权限）

#### 数据摘要
- `GET /api/measurements/summary` - 获取按时间分组的摘要数据（需要读取权限）

**查询参数：**
- `interval` (可选): 时间间隔，可选值: day, month, year，默认day

### 数据操作接口（需要管理员权限）

#### 创建测量记录
- `POST /api/measurements` - 创建新的测量记录（需要写入权限）

**请求体：**
```json
{
  "type_id": 1,
  "instrument_id": "IP1",
  "measure_time": "2024-01-01 12:00:00",
  "value": 25.5,
  "water_level": 50.2
}
```

#### 更新测量记录
- `PUT /api/measurements/{id}` - 更新测量记录（需要写入权限）

#### 删除测量记录
- `DELETE /api/measurements/{id}` - 删除测量记录（需要写入权限）

## 权限说明

### 读取权限 (read)
- 所有认证用户都拥有读取权限
- 允许访问所有GET接口（数据查询、统计等）

### 写入权限 (write)
- 仅管理员拥有写入权限
- 允许访问POST、PUT、DELETE接口（数据增删改）

## 使用示例

### 1. 用户登录获取令牌

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. 使用令牌查询数据

```bash
curl -X GET http://localhost:5000/api/measurements?limit=5 \
  -H "Authorization: Bearer <access_token>"
```

### 3. 创建新的测量记录（管理员）

```bash
curl -X POST http://localhost:5000/api/measurements \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type_id": 1,
    "instrument_id": "TEST01",
    "measure_time": "2024-01-15 10:30:00",
    "value": 30.5
  }'
```

## 模块化架构

### 认证模块结构
```
flask_backend/auth/
├── __init__.py          # 模块导出
├── config.py           # 认证配置
├── jwt_utils.py        # JWT工具类
├── decorators.py       # 权限装饰器
└── routes.py           # 认证路由
```

### 主要组件

1. **AuthConfig**: 认证配置类，管理用户信息和权限设置
2. **JWTManager**: JWT令牌的创建、验证和刷新
3. **权限装饰器**: 
   - `@token_required`: 验证JWT令牌
   - `@read_permission_required`: 需要读取权限
   - `@write_permission_required`: 需要写入权限（管理员）
4. **认证路由**: 用户登录、登出、令牌刷新等API

## 配置说明

### 环境变量
复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

主要配置项：
- `SECRET_KEY`: JWT签名密钥（生产环境必须修改）
- `JWT_ACCESS_TOKEN_EXPIRES_HOURS`: 访问令牌有效期（小时）
- `JWT_REFRESH_TOKEN_EXPIRES_DAYS`: 刷新令牌有效期（天）

### 用户管理
默认用户配置在 `auth/config.py` 的 `AuthConfig.USERS` 中：

```python
USERS = {
    'admin': {
        'password': 'admin123',  # 生产环境必须修改
        'role': 'admin',
        'email': 'admin@example.com',
        'name': '系统管理员'
    },
    'user': {
        'password': 'user123',
        'role': 'user',
        'email': 'user@example.com',
        'name': '普通用户'
    }
}
```

## 数据单位说明

- **水位**: 单位是米 (m)
- **引张线**: 单位是毫米 (mm)
- **静力水准**: 单位是毫米 (mm)
- **倒垂线**: 单位是毫米 (mm)

## 数据库结构

### monitoring_type 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 监测类型名称 |
| description | TEXT | 描述 |
| unit | TEXT | 单位 |

### measurement 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| type_id | INTEGER | 监测类型ID |
| instrument_id | TEXT | 仪器编号 |
| measure_time | TEXT | 观测时间 |
| value | REAL | 测量值 |
| water_level | REAL | 水位值（仅引张线有） |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |

## 部署说明

### 生产环境部署

1. 使用Gunicorn作为WSGI服务器：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_with_auth:app
```

2. 配置环境变量：
```bash
export SECRET_KEY=your-production-secret-key
export FLASK_ENV=production
```

3. 使用Nginx作为反向代理（可选）

### 安全建议

1. **修改默认密码**: 生产环境必须修改默认用户密码
2. **使用强密钥**: 使用复杂的SECRET_KEY
3. **HTTPS**: 生产环境必须使用HTTPS
4. **令牌有效期**: 根据安全需求调整令牌有效期
5. **用户管理**: 考虑实现动态用户管理系统

## 故障排除

### 常见问题

1. **认证失败**
   - 检查用户名和密码是否正确
   - 验证令牌是否过期
   - 确认请求头格式正确：`Authorization: Bearer <token>`

2. **权限不足**
   - 确认用户角色是否有相应权限
   - 管理员操作需要admin角色

3. **数据库连接失败**
   - 检查数据库文件路径是否正确
   - 确保有读写权限

4. **导入数据失败**
   - 检查Excel文件路径
   - 确保openpyxl已安装

### 日志查看

Flask默认在控制台输出日志，生产环境建议配置日志文件。

## 开发说明

### 添加新用户

修改 `auth/config.py` 中的 `AuthConfig.USERS`：

```python
USERS = {
    # ... 现有用户 ...
    'newuser': {
        'password': 'newpassword',
        'role': 'user',  # 或 'admin'
        'email': 'newuser@example.com',
        'name': '新用户'
    }
}
```

### 添加新的API端点

1. 在 `app_with_auth.py` 中添加新的路由函数
2. 使用适当的权限装饰器
3. 更新API文档
4. 测试新端点

### 数据更新

要更新监测数据，运行数据导入脚本：
```bash
python data_import.py
```

## 许可证

MIT License
