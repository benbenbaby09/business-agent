# 商家智能体Skill管理平台部署指南

## 系统架构

- **前端**：Vue 3 + Vite + Element Plus
- **后端**：Python + Flask + MongoDB
- **文件存储**：对象存储服务（如腾讯云COS或阿里云OSS）

## 环境要求

### 前端环境
- Node.js 16.0+ 
- npm 7.0+

### 后端环境
- Python 3.8+ 
- MongoDB 4.0+

## 部署步骤

### 1. 克隆代码库

```bash
git clone <repository-url>
cd business-agent
```

### 2. 配置环境变量

#### 后端配置
编辑 `backend/.env` 文件：

```env
# 数据库连接信息
MONGO_URI=mongodb://username:password@host:port/skill_management

# JWT密钥
SECRET_KEY=your-secret-key-change-in-production

# 云函数配置
FUNCTION_NAME=skill-management-api

# 文件存储配置
STORAGE_BUCKET=skill-management
STORAGE_REGION=ap-beijing
```

#### 前端配置
编辑 `frontend/.env` 文件：

```env
# API地址
VITE_API_BASE_URL=http://localhost:8000/api

# 前端配置
VITE_APP_TITLE=商家智能体Skill管理平台
VITE_APP_VERSION=1.0.0
```

### 3. 安装依赖

#### 前端依赖

```bash
cd frontend
npm install
```

#### 后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 运行开发服务器

#### 启动后端服务

```bash
cd backend
python app.py
```

后端服务将在 `http://localhost:8000` 运行。

#### 启动前端服务

```bash
cd frontend
npm run dev
```

前端服务将在 `http://localhost:3000` 运行。

### 5. 构建生产版本

#### 构建前端

```bash
cd frontend
npm run build
```

构建产物将生成在 `frontend/dist` 目录。

### 6. 部署到生产环境

#### 前端部署
将 `frontend/dist` 目录部署到静态网站托管服务，如：
- 腾讯云COS静态网站
- 阿里云OSS静态网站
- Vercel
- Netlify

#### 后端部署
将后端代码部署到云函数服务，如：
- 腾讯云函数
- 阿里云函数计算
- AWS Lambda

### 7. 配置API网关

配置API网关，将前端的API请求转发到后端云函数。

## 系统功能

### 1. 用户认证
- 登录/注册
- JWT令牌认证

### 2. Skill管理
- 创建/编辑/删除Skill
- 查看Skill详情
- 按状态和类型筛选Skill

### 3. 文件管理
- 上传Skill文件
- 下载Skill文件
- 删除Skill文件

### 4. 文件生成
- 选择模板
- 配置参数
- 生成文件
- 下载文件

### 5. 版本管理
- 发布Skill
- 查看版本历史
- 版本回滚

## 技术支持

如果遇到部署或使用问题，请联系技术支持：
- 邮箱：support@example.com
- 电话：123-456-7890

## 常见问题

### 1. 数据库连接失败

检查 `MONGO_URI` 配置是否正确，确保MongoDB服务正在运行。

### 2. 前端无法连接后端API

检查 `VITE_API_BASE_URL` 配置是否正确，确保后端服务正在运行。

### 3. 文件上传失败

检查文件存储配置是否正确，确保有足够的存储权限。

### 4. 部署后前端出现404错误

确保前端路由配置正确，对于SPA应用，需要配置服务器返回index.html。
