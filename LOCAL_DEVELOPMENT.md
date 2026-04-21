# 本地开发环境配置指南

## 概述

本项目支持两种数据库运行模式：
1. **模拟数据库模式**（默认）：无需安装MongoDB，数据存储在内存中，重启后数据丢失
2. **本地MongoDB模式**：使用Docker运行MongoDB，数据持久化存储

## 快速开始

### 方式一：使用模拟数据库（无需Docker）

这是默认模式，无需任何额外配置，直接启动后端服务即可：

```bash
cd backend
python app.py
```

**特点**：
- ✅ 无需安装任何数据库软件
- ✅ 启动速度快
- ✅ 适合快速开发和测试
- ❌ 数据存储在内存中，重启后丢失
- ❌ 不支持复杂查询

### 方式二：使用Docker运行本地MongoDB

#### 前提条件

- 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)

#### 启动步骤

1. **启动MongoDB服务**

```bash
# 在项目根目录执行
docker-compose up -d
```

这将启动：
- MongoDB数据库（端口：27017）
- Mongo Express管理界面（端口：8081）

2. **查看MongoDB管理界面**

打开浏览器访问：http://localhost:8081

- 用户名：admin
- 密码：password

3. **配置后端连接本地MongoDB**

编辑 `backend/.env` 文件：

```env
# 本地MongoDB连接（使用Docker）
MONGO_URI=mongodb://skill_user:skill_password@localhost:27017/skill_management

# JWT密钥
SECRET_KEY=your-secret-key-change-in-production
```

4. **启动后端服务**

```bash
cd backend
python app.py
```

**特点**：
- ✅ 数据持久化存储
- ✅ 支持完整MongoDB功能
- ✅ 支持复杂查询和聚合
- ✅ 可迁移到CloudBase等云数据库
- ❌ 需要安装Docker
- ❌ 占用更多系统资源

## 数据库迁移

### 从本地MongoDB迁移到CloudBase

1. **导出本地数据**

```bash
# 导出整个数据库
mongodump --uri="mongodb://skill_user:skill_password@localhost:27017/skill_management" --out=./backup

# 或者导出特定集合
mongodump --uri="mongodb://skill_user:skill_password@localhost:27017/skill_management" --collection=skills --out=./backup
```

2. **导入到CloudBase**

在腾讯云控制台：
- 进入CloudBase数据库管理页面
- 选择"数据导入"功能
- 上传导出的BSON文件

3. **更新后端配置**

编辑 `backend/.env` 文件，修改MONGO_URI为CloudBase连接字符串：

```env
# CloudBase连接字符串（示例）
MONGO_URI=mongodb://username:password@xxx.tencentcloudapi.com:27017/skill_management?ssl=true&authSource=admin
```

## 常用命令

### Docker命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f mongodb

# 重启服务
docker-compose restart

# 删除数据卷（清空数据）
docker-compose down -v
```

### MongoDB命令

```bash
# 进入MongoDB容器
docker exec -it skill-management-mongodb mongosh

# 查看数据库
show dbs

# 切换到skill_management数据库
use skill_management

# 查看集合
show collections

# 查看用户
db.users.find()

# 查看Skill
db.skills.find()
```

## 环境配置对比

| 特性 | 模拟数据库 | 本地MongoDB | CloudBase |
|-----|-----------|------------|-----------|
| 安装难度 | ⭐ 简单 | ⭐⭐ 中等 | ⭐ 简单 |
| 数据持久化 | ❌ 不支持 | ✅ 支持 | ✅ 支持 |
| 功能完整性 | ⭐⭐ 基础 | ⭐⭐⭐⭐⭐ 完整 | ⭐⭐⭐⭐⭐ 完整 |
| 性能 | ⭐⭐⭐ 快 | ⭐⭐⭐⭐ 快 | ⭐⭐⭐ 中等 |
| 成本 | 免费 | 免费 | 按量付费 |
| 适用场景 | 开发测试 | 本地开发 | 生产环境 |

## 推荐工作流

### 开发阶段

1. 使用**模拟数据库**进行快速开发和功能验证
2. 功能稳定后，切换到**本地MongoDB**进行完整测试

### 测试阶段

1. 使用**本地MongoDB**进行集成测试
2. 导出测试数据，准备迁移到生产环境

### 生产阶段

1. 使用**CloudBase**或其他云数据库服务
2. 定期备份数据
3. 监控数据库性能

## 故障排除

### Docker启动失败

```bash
# 检查Docker状态
docker ps

# 查看容器日志
docker-compose logs mongodb

# 重启Docker服务
docker-compose down
docker-compose up -d
```

### 连接MongoDB失败

1. 检查MongoDB是否运行：
```bash
docker ps | grep mongodb
```

2. 检查端口是否被占用：
```bash
netstat -ano | findstr 27017
```

3. 检查连接字符串是否正确

### 权限错误

1. 确认用户已创建：
```bash
docker exec -it skill-management-mongodb mongosh -u admin -p password --authenticationDatabase admin
```

2. 在MongoDB shell中：
```javascript
use skill_management
db.getUsers()
```

## 技术支持

如果遇到问题，请检查：
1. Docker是否正确安装和运行
2. 端口是否被其他程序占用
3. 环境变量配置是否正确
4. 查看后端服务日志获取详细错误信息