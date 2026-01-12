# 智慧水利监测平台

基于Vue.js + Flask + Cesium的智慧水利大坝安全监测平台，实现监测数据的动态展示、三维可视化交互和数据分析。

## 功能特性

### 前端功能
- **三维可视化**：使用Cesium.js实现大坝3D模型展示
- **实时监测**：水位、位移、应力等监测数据实时展示
- **数据图表**：ECharts实现多种数据可视化图表
- **用户管理**：管理员/普通用户权限控制
- **响应式设计**：适配桌面和移动端

### 后端功能
- **RESTful API**：提供完整的数据接口
- **用户认证**：JWT令牌认证系统
- **数据管理**：监测数据CRUD操作
- **统计分析**：数据聚合和统计功能
- **权限控制**：基于角色的访问控制

## 技术栈

### 前端
- Vue.js 3 + Composition API
- Element Plus UI组件库
- Cesium.js 三维地理可视化
- ECharts 数据图表
- DataV 数据可视化组件
- Vite 构建工具

### 后端
- Flask Python Web框架
- SQLite 数据库（可升级到PostgreSQL）
- JWT 用户认证
- Gunicorn 生产服务器
- Flask-CORS 跨域支持

## 项目结构

```
smartwater-platform/
├── frontend/                 # 前端Vue应用
│   ├── src/
│   │   ├── api/             # API接口
│   │   ├── components/      # 组件
│   │   ├── pages/          # 页面
│   │   ├── router/         # 路由
│   │   └── styles/         # 样式
│   ├── public/              # 静态资源
│   └── package.json         # 依赖配置
├── flask_backend/           # Flask后端
│   ├── app_with_auth.py     # 主应用
│   ├── requirements.txt     # Python依赖
│   ├── auth/               # 认证模块
│   └── data_import.py      # 数据导入
├── backend/                 # 原始Spring Boot后端
├── app_spec.yaml           # DigitalOcean部署配置
└── README.md               # 项目说明
```

## 快速开始

### 本地开发

1. **后端启动**
```bash
cd flask_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app_with_auth.py
```

2. **前端启动**
```bash
cd frontend
npm install
npm run dev
```

3. **访问应用**
- 前端：http://localhost:5173
- 后端API：http://localhost:5000

### 默认用户
- 管理员：admin / admin123
- 普通用户：user / user123

## 部署到DigitalOcean App Platform

### 准备工作
1. 将代码推送到GitHub仓库
2. 在DigitalOcean创建App Platform应用
3. 配置环境变量：
   - `SECRET_KEY`: Flask应用密钥
   - `JWT_SECRET_KEY`: JWT令牌密钥
   - `VITE_API_URL`: 前端API地址

### 部署配置
项目包含 `app_spec.yaml` 文件，DigitalOcean会自动识别并配置：
- 后端服务：Flask + Gunicorn
- 前端服务：Vue.js构建 + Nginx
- 健康检查：自动监控服务状态

### 环境变量
| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| SECRET_KEY | Flask应用密钥 | 随机字符串 |
| JWT_SECRET_KEY | JWT令牌密钥 | 随机字符串 |
| DATABASE_URL | 数据库连接 | sqlite:///data/monitoring.db |
| VITE_API_URL | 前端API地址 | https://backend-xxx.ondigitalocean.app/api |

## API文档

### 主要端点
- `GET /api/health` - 健康检查
- `GET /api/types` - 监测类型列表
- `GET /api/instruments` - 仪器列表
- `GET /api/measurements` - 测量数据
- `GET /api/statistics` - 统计数据
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册

### 认证
所有API端点（除登录注册外）需要JWT令牌：
```
Authorization: Bearer <token>
```

## 数据模型

### 监测类型 (monitoring_type)
- id: 类型ID
- name: 类型名称（水位、位移、应力等）
- unit: 测量单位

### 测量数据 (measurement)
- id: 记录ID
- type_id: 监测类型ID
- instrument_id: 仪器编号
- measure_time: 测量时间
- value: 测量值
- water_level: 水位值（仅引张线）

### 用户 (users)
- id: 用户ID
- username: 用户名
- password_hash: 密码哈希
- name: 姓名
- email: 邮箱
- role: 角色（admin/user）

## 开发指南

### 添加新的监测类型
1. 在 `backend/data/monitoring.db` 的 `monitoring_type` 表中添加记录
2. 重启后端服务

### 添加新的API端点
1. 在 `flask_backend/app_with_auth.py` 中添加路由
2. 使用适当的权限装饰器：
   - `@read_permission_required`: 需要读取权限
   - `@write_permission_required`: 需要写入权限

### 前端组件开发
1. 在 `frontend/src/components/` 创建Vue组件
2. 在 `frontend/src/api/` 中添加对应的API调用
3. 在页面中导入和使用组件

## 故障排除

### 常见问题

1. **CORS错误**
   - 检查后端CORS配置
   - 验证前端API地址

2. **数据库连接失败**
   - 检查数据库文件路径
   - 验证文件权限

3. **构建失败**
   - 清理node_modules重新安装
   - 检查Node.js版本（需要18+）

4. **3D模型不显示**
   - 检查Cesium访问令牌
   - 验证模型文件路径

### 日志查看
```bash
# 后端日志
cd flask_backend
python app_with_auth.py

# 前端构建日志
cd frontend
npm run build
```

## 许可证

MIT License

## 联系方式

如有问题，请提交GitHub Issue或联系项目维护者。
