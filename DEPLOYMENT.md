# 部署指南

本文档详细说明如何将智慧水利监测平台部署到DigitalOcean App Platform。

## 部署前准备

### 1. 账户准备
- [ ] DigitalOcean账户（如果没有，请注册）
- [ ] GitHub账户（用于代码托管）
- [ ] 域名（可选，用于自定义访问地址）

### 2. 本地检查
确保以下文件已正确配置：
- [ ] `.gitignore` - 忽略不必要的文件
- [ ] `app_spec.yaml` - DigitalOcean部署配置
- [ ] `frontend/.env.production` - 前端生产环境变量
- [ ] `flask_backend/app_with_auth.py` - 后端CORS配置已更新

### 3. 环境变量准备
需要准备以下环境变量值：
- `SECRET_KEY`: Flask应用密钥（随机字符串）
- `JWT_SECRET_KEY`: JWT令牌密钥（随机字符串）

生成随机密钥：
```bash
# 在Linux/macOS上生成随机密钥
openssl rand -hex 32
# 或使用Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 部署步骤

### 步骤1：推送代码到GitHub

1. **初始化Git仓库**
```bash
cd /home/bazzite/exp/cesium
git init
git add .
git commit -m "初始提交：智慧水利监测平台 v1.0"
```

2. **创建GitHub仓库**
   - 访问 https://github.com/new
   - 仓库名：`smartwater-platform`
   - 描述：智慧水利监测平台
   - 选择公开或私有
   - 不要初始化README（因为已有）

3. **推送代码**
```bash
git remote add origin https://github.com/YOUR_USERNAME/smartwater-platform.git
git branch -M main
git push -u origin main
```

### 步骤2：在DigitalOcean创建应用

1. **登录DigitalOcean控制台**
   - 访问 https://cloud.digitalocean.com
   - 点击 "Create" → "Apps"

2. **连接GitHub**
   - 点击 "GitHub" 按钮
   - 授权DigitalOcean访问你的GitHub账户
   - 选择仓库：`YOUR_USERNAME/smartwater-platform`

3. **配置应用**
   - App Platform会自动检测 `app_spec.yaml`
   - 检查配置是否正确：
     - 后端服务：`flask_backend`
     - 前端服务：`frontend`
     - 端口配置正确

4. **设置环境变量**
   在环境变量部分添加：
   - `SECRET_KEY`: 你的随机密钥
   - `JWT_SECRET_KEY`: 你的JWT密钥
   - `VITE_API_URL`: `https://backend-smartwater-platform.ondigitalocean.app/api`

5. **创建应用**
   - 点击 "Create App"
   - 等待构建和部署（约5-10分钟）

### 步骤3：验证部署

1. **查看部署状态**
   - 在DigitalOcean控制台查看构建日志
   - 等待所有服务显示 "Running" 状态

2. **测试应用**
   - 前端URL: `https://frontend-smartwater-platform.ondigitalocean.app`
   - 后端API: `https://backend-smartwater-platform.ondigitalocean.app/api/health`
   - 使用默认用户登录测试：
     - 管理员: admin / admin123
     - 普通用户: user / user123

3. **检查功能**
   - [ ] 用户登录/注销
   - [ ] 监测数据展示
   - [ ] 图表渲染
   - [ ] 3D模型加载
   - [ ] 后台管理功能

## 高级配置

### 自定义域名

1. **添加域名**
   - 在App设置中点击 "Settings" → "Domains"
   - 添加你的域名：`smartwater.yourdomain.com`

2. **配置DNS**
   - 在域名注册商处添加CNAME记录：
     ```
     类型: CNAME
     名称: smartwater
     值: smartwater-platform.ondigitalocean.app
     TTL: 3600
     ```

3. **等待生效**
   - DNS变更可能需要几分钟到几小时生效
   - 在DigitalOcean验证域名状态

### 数据库配置

#### 选项A：使用SQLite（简单）
- 数据库文件随应用一起部署
- 注意：重启应用可能导致数据丢失
- 适合测试和小型应用

#### 选项B：使用DigitalOcean Managed Database（推荐生产环境）

1. **创建数据库**
   - 在DigitalOcean控制台创建Managed Database
   - 选择PostgreSQL或MySQL
   - 区域与App相同

2. **更新配置**
   修改 `app_spec.yaml`：
   ```yaml
   databases:
   - engine: PG
     name: smartwater-db
     production: true
     version: "15"
   ```

3. **更新环境变量**
   - `DATABASE_URL`: `${smartwater-db.DATABASE_URL}`

### 监控和日志

1. **查看日志**
   - 在DigitalOcean控制台：Apps → 你的应用 → "Monitoring" → "Logs"
   - 可以查看实时日志和搜索历史日志

2. **设置告警**
   - 在 "Monitoring" → "Alerts" 中设置
   - 建议设置：
     - CPU使用率 > 80%
     - 内存使用率 > 80%
     - 5分钟内错误率 > 5%

3. **性能监控**
   - 查看 "Metrics" 标签页
   - 监控CPU、内存、请求数等指标

## 维护和更新

### 代码更新
1. **本地修改代码**
2. **提交到GitHub**
```bash
git add .
git commit -m "更新说明"
git push origin main
```
3. **自动部署**
   - DigitalOcean会自动检测并部署新版本

### 手动重新部署
如果需要手动触发部署：
1. 在DigitalOcean控制台进入应用
2. 点击 "Deploy" 按钮
3. 选择 "Deploy from GitHub"

### 回滚部署
如果新版本有问题：
1. 进入 "Deployments" 标签页
2. 找到之前的稳定版本
3. 点击 "Redeploy"

## 故障排除

### 常见问题

#### 1. 构建失败
**症状**：部署状态显示 "Failed"
**解决**：
- 查看构建日志，找到错误信息
- 常见原因：
  - 依赖安装失败：检查requirements.txt和package.json
  - 内存不足：升级实例规格
  - 配置错误：检查app_spec.yaml语法

#### 2. 应用启动失败
**症状**：服务状态不是 "Running"
**解决**：
- 查看运行时日志
- 检查环境变量配置
- 验证数据库连接

#### 3. API连接失败
**症状**：前端无法访问后端API
**解决**：
- 检查CORS配置
- 验证VITE_API_URL环境变量
- 检查网络连通性

#### 4. 数据库连接失败
**症状**：API返回数据库错误
**解决**：
- 检查DATABASE_URL环境变量
- 验证数据库权限
- 检查数据库服务状态

### 调试命令

通过DigitalOcean控制台可以：
1. **查看实时日志**
2. **进入容器终端**（需要专业版）
3. **查看资源使用情况**

## 成本估算

### 基础配置（每月约$10）
- 后端：Basic XS ($5)
- 前端：Basic XS ($5)

### 含数据库配置（每月约$25）
- 基础配置：$10
- Basic DB：$15

### 生产配置（每月约$50+）
- 后端：Basic S ($10)
- 前端：Basic S ($10)
- Basic DB：$15
- 自定义域名：$0（仅域名注册费）

## 安全建议

1. **定期更新密钥**
   - 定期更换SECRET_KEY和JWT_SECRET_KEY
   - 更新后需要重新部署

2. **启用HTTPS**
   - DigitalOcean自动提供SSL证书
   - 确保所有流量使用HTTPS

3. **限制访问**
   - 考虑添加IP白名单（如果需要）
   - 使用强密码策略

4. **数据备份**
   - 定期备份数据库
   - 使用DigitalOcean备份功能或手动导出

## 支持

如果遇到问题：
1. 查看本文档的故障排除部分
2. 检查DigitalOcean文档
3. 查看GitHub Issues
4. 联系技术支持

## 更新日志

### v1.0 (2026-01-12)
- 初始版本发布
- 支持基本监测数据展示
- 3D模型可视化
- 用户认证系统
- DigitalOcean App Platform部署支持
