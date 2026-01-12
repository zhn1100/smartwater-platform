#!/bin/bash

echo "=== 初始化Git仓库并推送到GitHub ==="
echo ""

# 检查是否在项目根目录
if [ ! -f "app_spec.yaml" ]; then
    echo "错误：请在项目根目录运行此脚本"
    exit 1
fi

# 1. 初始化Git仓库
echo "1. 初始化Git仓库..."
git init

# 2. 添加所有文件
echo "2. 添加文件到Git..."
git add .

# 3. 提交
echo "3. 提交更改..."
git commit -m "初始提交：智慧水利监测平台 v1.0

- 前端：Vue.js + Cesium 3D可视化
- 后端：Flask RESTful API + JWT认证
- 部署：DigitalOcean App Platform配置
- 功能：监测数据展示、图表分析、用户管理"

# 4. 询问GitHub仓库信息
echo ""
echo "4. 配置GitHub远程仓库"
echo "请先到 https://github.com/new 创建仓库："
echo "  仓库名：smartwater-platform"
echo "  描述：智慧水利监测平台"
echo "  不要初始化README.md"
echo ""
read -p "请输入你的GitHub用户名: " github_username

# 5. 添加远程仓库
echo "5. 添加远程仓库..."
git remote add origin "https://github.com/${github_username}/smartwater-platform.git"

# 6. 推送代码
echo "6. 推送到GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "=== 完成！ ==="
echo ""
echo "下一步："
echo "1. 访问 https://cloud.digitalocean.com"
echo "2. 点击 'Create' → 'Apps'"
echo "3. 连接GitHub账户"
echo "4. 选择 smartwater-platform 仓库"
echo "5. 配置环境变量："
echo "   - SECRET_KEY: 随机字符串"
echo "   - JWT_SECRET_KEY: 随机字符串"
echo "6. 点击 'Create App'"
echo ""
echo "部署完成后访问："
echo "前端：https://frontend-smartwater-platform.ondigitalocean.app"
echo "后端API：https://backend-smartwater-platform.ondigitalocean.app/api/health"
