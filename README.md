# 商家智能体Skill管理平台

## 项目简介

商家智能体Skill管理平台是一个基于Vue+Python云函数技术栈的系统，旨在帮助商家自定义、管理和发布智能体技能（Skill）。该平台提供了完整的Skill生命周期管理，包括创建、编辑、文件生成、发布和版本管理等功能。

## 技术栈

### 前端
- **框架**：Vue 3 + Vite
- **状态管理**：Pinia
- **路由**：Vue Router
- **UI组件库**：Element Plus
- **HTTP客户端**：Axios
- **文件处理**：FileSaver.js

### 后端
- **云函数**：Python + Flask
- **数据库**：MongoDB
- **文件存储**：对象存储服务（如腾讯云COS或阿里云OSS）
- **认证**：JWT

## 核心功能

### 1. 用户认证
- 登录/注册
- JWT令牌认证
- 用户信息管理

### 2. Skill管理
- 创建/编辑/删除Skill
- 查看Skill详情
- 按状态和类型筛选Skill
- 技能状态管理（草稿/已发布）

### 3. 文件管理
- 上传Skill文件
- 下载Skill文件
- 删除Skill文件
- 文件版本控制

### 4. 文件生成
- 选择模板（客服、销售、运营）
- 配置参数
- 生成文件
- 下载文件

### 5. 版本管理
- 发布Skill
- 查看版本历史
- 版本回滚

## 项目结构

```
business-agent/
├── backend/            # 后端代码
│   ├── routes/         # API路由
│   ├── database.py     # 数据库连接
│   ├── middleware.py   # 认证中间件
│   ├── app.py          # Flask应用入口
│   ├── requirements.txt # 依赖文件
│   └── .env            # 环境变量配置
├── frontend/           # 前端代码
│   ├── src/            # 源代码
│   │   ├── components/ # 组件
│   │   ├── views/      # 页面
│   │   ├── stores/     # 状态管理
│   │   ├── router/     # 路由配置
│   │   ├── utils/      # 工具函数
│   │   └── main.js     # 应用入口
│   ├── package.json    # 依赖文件
│   ├── vite.config.js  # Vite配置
│   └── .env            # 环境变量配置
├── deploy.sh           # 部署脚本
├── DEPLOYMENT.md       # 部署指南
├── database-storage-design.md # 数据库和存储设计
└── system-design.md    # 系统架构设计
```

## 安装和运行

### 前端

1. 安装依赖

```bash
cd frontend
npm install
```

2. 启动开发服务器

```bash
npm run dev
```

前端服务将在 `http://localhost:3000` 运行。

### 后端

1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

2. 启动Flask应用

```bash
python app.py
```

后端服务将在 `http://localhost:8000` 运行。

## 环境配置

### 前端配置
编辑 `frontend/.env` 文件：

```env
# API地址
VITE_API_BASE_URL=http://localhost:8000/api

# 前端配置
VITE_APP_TITLE=商家智能体Skill管理平台
VITE_APP_VERSION=1.0.0
```

### 后端配置
编辑 `backend/.env` 文件：

```env
# 数据库连接信息
MONGO_URI=mongodb://localhost:27017/skill_management

# JWT密钥
SECRET_KEY=your-secret-key-change-in-production

# 云函数配置
FUNCTION_NAME=skill-management-api

# 文件存储配置
STORAGE_BUCKET=skill-management
STORAGE_REGION=ap-beijing
```

## 部署

### 前端部署
1. 构建前端

```bash
cd frontend
npm run build
```

2. 将 `frontend/dist` 目录部署到静态网站托管服务，如：
- 腾讯云COS静态网站
- 阿里云OSS静态网站
- Vercel
- Netlify

### 后端部署
1. 将后端代码部署到云函数服务，如：
- 腾讯云函数
- 阿里云函数计算
- AWS Lambda

2. 配置API网关，将前端的API请求转发到后端云函数。

## 技术支持

如果遇到部署或使用问题，请联系技术支持：
- 邮箱：support@example.com
- 电话：123-456-7890

## 许可证

MIT License
"# business-agent" 
