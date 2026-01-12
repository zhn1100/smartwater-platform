# 智慧水利监测数据API

基于Flask的后端API服务，提供水利监测数据的RESTful接口。

## 功能特性

- 提供四种监测类型的数据访问：引张线、静力水准、水位、倒垂线
- 支持按时间范围、仪器ID、监测类型查询数据
- 提供数据统计和摘要信息
- 支持跨域请求（CORS）
- 健康检查端点

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行服务

```bash
python app.py
```

服务将在 http://localhost:5000 启动。

### 3. 验证安装

访问 http://localhost:5000/api/health 检查服务状态。

## API接口文档

### 基础信息

- `GET /` - 获取API基本信息
- `GET /api/health` - 健康检查

### 监测类型

- `GET /api/types` - 获取所有监测类型

**响应示例：**
```json
[
  {
    "id": 1,
    "name": "引张线",
    "description": "引张线监测数据",
    "unit": "mm"
  },
  {
    "id": 2,
    "name": "静力水准",
    "description": "静力水准监测数据",
    "unit": "mm"
  }
]
```

### 仪器列表

- `GET /api/instruments` - 获取所有仪器列表

**响应示例：**
```json
[
  {
    "instrument_id": "IP1",
    "type_id": 1,
    "type_name": "引张线"
  },
  {
    "instrument_id": "上游",
    "type_id": 3,
    "type_name": "水位"
  }
]
```

### 测量数据

- `GET /api/measurements` - 获取测量数据

**查询参数：**
- `type_id` (可选): 监测类型ID
- `instrument_id` (可选): 仪器ID
- `start_time` (可选): 开始时间 (格式: YYYY-MM-DD HH:MM:SS)
- `end_time` (可选): 结束时间 (格式: YYYY-MM-DD HH:MM:SS)
- `limit` (可选): 返回记录数，默认100

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

### 统计数据

- `GET /api/statistics` - 获取总体统计数据

**响应示例：**
```json
{
  "total_measurements": 44460,
  "type_statistics": [
    {
      "name": "水位",
      "count": 10096,
      "min_value": 0.0,
      "max_value": 100.5,
      "avg_value": 52.3
    }
  ],
  "time_range": {
    "first": "2010-07-10 00:00:00",
    "last": "2025-12-31 23:59:59"
  },
  "generated_at": "2026-01-12T01:30:00"
}
```

### 数据摘要

- `GET /api/measurements/summary` - 获取按时间分组的摘要数据

**查询参数：**
- `interval` (可选): 时间间隔，可选值: day, month, year，默认day

**响应示例：**
```json
[
  {
    "period": "2023-01-01",
    "count": 120,
    "avg_value": 25.6,
    "min_value": 20.1,
    "max_value": 30.5
  }
]
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

## 部署说明

### 生产环境部署

1. 使用Gunicorn作为WSGI服务器：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. 使用Nginx作为反向代理（可选）

### 环境变量

- `FLASK_ENV`: 环境模式 (development/production)
- `DATABASE_URL`: 数据库连接URL

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库文件路径是否正确
   - 确保有读写权限

2. **导入数据失败**
   - 检查Excel文件路径
   - 确保openpyxl已安装

3. **API返回空数据**
   - 检查查询参数是否正确
   - 验证数据库是否有数据

### 日志查看

Flask默认在控制台输出日志，生产环境建议配置日志文件。

## 开发说明

### 添加新的API端点

1. 在`app.py`中添加新的路由函数
2. 更新API文档
3. 测试新端点

### 数据更新

要更新监测数据，运行数据导入脚本：
```bash
python data_import.py
```

## 许可证

MIT License
