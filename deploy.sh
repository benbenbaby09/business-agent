#!/bin/bash

# 部署脚本

echo "开始部署商家智能体Skill管理平台..."

# 1. 构建前端
echo "构建前端应用..."
cd frontend
npm install
npm run build

# 2. 部署前端到静态网站托管服务
# 这里需要根据实际的托管服务进行配置
# 例如：将dist目录上传到腾讯云COS或阿里云OSS

echo "前端构建完成，准备部署后端..."

# 3. 部署后端云函数
cd ../backend

# 安装依赖
pip install -r requirements.txt

# 打包云函数
# 这里需要根据实际的云服务提供商进行配置
# 例如：创建zip包并上传到腾讯云函数或阿里云函数计算

echo "后端部署完成..."

echo "部署完成！"
