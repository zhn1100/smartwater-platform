# Flask后端API文档

## 概述
智慧水利监测数据API（带用户认证）是一个基于Flask的后端服务，提供监测数据的查询、统计和管理功能。

## 认证系统
- 使用JWT令牌进行用户认证
- 支持两种角色：管理员(`admin`)和普通用户(`user`)
- 权限控制：
  - `read_permission_required`: 读取权限（所有用户）
  - `write_permission_required`: 写入权限（仅管理员）

### 默认用户
- 管理员: `admin` / `admin123`
- 普通用户: `user` / `user123`

## API端点

### 1. 健康检查
- `GET /api/health` - 健康检查端点
- `GET /` - 首页，显示API基本信息

### 2. 监测类型管理
- `GET /api/types` - 获取监测类型列表
  - 返回：引张线、静力水准、倒垂线、水位等类型

### 3. 仪器管理
- `GET /api/instruments` - 获取仪器列表
  - 按`instrument_id`分组
  - 返回包含`type_id`和`type_name`的仪器信息

### 4. 测量数据查询
- `GET /api/measurements` - 获取测量数据

**查询参数：**
- `type_id` (可选): 监测类型ID
- `instrument_id` (可选): 仪器ID（如"上游"、"下游"）
- `start_time` (可选): 开始时间（格式: `YYYY-MM-DD HH:MM:SS`）
- `end_time` (可选): 结束时间（格式: `YYYY-MM-DD HH:MM:SS`）
- `limit` (可选): 返回记录数，默认100
- `offset` (可选): 偏移量，默认0

**响应示例：**
```json
[
  {
    "id": 1,
    "type_id": 3,
    "type_name": "水位",
    "instrument_id": "上游",
    "measure_time": "2010-07-10 00:00:00",
    "value": 51.4,
    "water_level": null,
    "unit": "m"
  }
]
```

### 5. 统计数据
- `GET /api/statistics` - 获取统计数据
  - 总记录数
  - 按类型统计（数量、平均值）
  - 时间范围
  - 仪器数量

### 6. 数据摘要
- `GET /api/measurements/summary` - 获取数据摘要（按时间间隔分组）

**查询参数：**
- `interval` (可选): 时间间隔（day/week/month/year，默认month）
- `type_id` (可选): 监测类型ID
- `limit` (可选): 返回记录数，默认12

### 7. 数据写入（需要管理员权限）
- `POST /api/measurements` - 创建测量记录
- `PUT /api/measurements/{id}` - 更新测量记录
- `DELETE /api/measurements/{id}` - 删除测量记录

### 8. 用户管理（需要管理员权限）
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建新用户
- `DELETE /api/users/{id}` - 删除用户

## 数据库结构

### measurement表（测量记录）
- `id`: 主键
- `type_id`: 监测类型ID
- `instrument_id`: 仪器ID（如"上游"、"下游"）
- `measure_time`: 测量时间
- `value`: 测量值
- `water_level`: 水位值（仅引张线数据）
- `created_at`: 创建时间
- `updated_at`: 更新时间

### monitoring_type表（监测类型）
- `id`: 主键
- `name`: 类型名称（引张线、静力水准、倒垂线、水位）
- `description`: 描述
- `unit`: 单位

### users表（用户）
- `id`: 主键
- `username`: 用户名
- `password_hash`: 密码哈希
- `name`: 姓名
- `email`: 邮箱
- `role`: 角色（admin/user）
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 前端使用指南

### 1. 水位图表实现
```javascript
// 获取特定年份的上游水位数据
const loadAndRenderWaterLevelChart = async () => {
  const selectedYear = 2024;
  const startTime = `${selectedYear}-01-01 00:00:00`;
  const endTime = `${selectedYear}-12-31 23:59:59`;
  
  const waterLevelData = await getMeasurements({
    type_id: 3, // 水位监测类型
    instrument_id: '上游', // 只获取上游数据
    start_time: startTime,
    end_time: endTime,
    limit: 1000
  });
  
  // 按月份分组计算平均值
  // ...
};
```

### 2. 平均值图表实现（排除水位）
```javascript
// 获取特定年份的数据，排除水位
const loadAndRenderAvgDataChart = async () => {
  const selectedYear = 2024;
  const startTime = `${selectedYear}-01-01 00:00:00`;
  const endTime = `${selectedYear}-12-31 23:59:59`;
  
  const allData = await getMeasurements({
    start_time: startTime,
    end_time: endTime,
    limit: 2000
  });
  
  // 按类型分组，排除水位数据
  const typeData = {};
  allData.forEach(item => {
    if (item.type_name === '水位') return; // 排除水位
    // 计算平均值...
  });
};
```

### 3. 关键注意事项
1. **水位数据单独处理**：水位数据不应包含在仪器平均值计算中
2. **使用时间范围查询**：应使用`start_time`和`end_time`参数，而不是在客户端过滤
3. **区分上下游**：通过`instrument_id`字段区分"上游"和"下游"数据
4. **数据单位**：注意不同监测类型的单位（水位为m，其他为mm）

## 启动和配置
```bash
cd /home/bazzite/exp/cesium/flask_backend
python3 app_with_auth.py
```

服务将在 `http://localhost:5000` 启动。

## 错误处理
- 404: 请求的资源不存在
- 500: 服务器内部错误
- 401: 未授权（需要登录）
- 403: 禁止访问（权限不足）

## 最佳实践
1. 前端应使用`start_time`和`end_time`参数进行时间范围查询
2. 水位数据应单独处理，不包含在仪器平均值中
3. 注意数据单位的差异
4. 合理使用`limit`参数避免返回过多数据
5. 错误处理应包含用户友好的提示信息
