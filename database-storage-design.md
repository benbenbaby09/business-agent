# 数据库和存储方案设计

## 1. MongoDB数据库设计

### 1.1 数据库连接配置
- **连接字符串**：`mongodb://username:password@host:port/database`
- **数据库名称**：`skill_management`
- **连接池配置**：
  - 最大连接数：50
  - 连接超时：30秒
  - 心跳间隔：10秒

### 1.2 集合设计

#### 1.2.1 用户集合 (users)
| 字段名 | 类型 | 描述 | 索引 |
|-------|------|------|------|
| _id | ObjectId | 用户ID | 主键 |
| username | String | 用户名 | 唯一索引 |
| email | String | 邮箱 | 唯一索引 |
| password | String | 密码哈希 | 无 |
| created_at | Date | 创建时间 | 无 |
| updated_at | Date | 更新时间 | 无 |

#### 1.2.2 Skill集合 (skills)
| 字段名 | 类型 | 描述 | 索引 |
|-------|------|------|------|
| _id | ObjectId | Skill ID | 主键 |
| user_id | ObjectId | 所属用户ID | 复合索引 (user_id, status) |
| name | String | Skill名称 | 无 |
| description | String | Skill描述 | 无 |
| type | String | Skill类型 | 索引 |
| status | String | 状态 (draft/published) | 复合索引 (user_id, status) |
| version | String | 版本号 | 无 |
| created_at | Date | 创建时间 | 无 |
| updated_at | Date | 更新时间 | 无 |

#### 1.2.3 Skill文件集合 (skill_files)
| 字段名 | 类型 | 描述 | 索引 |
|-------|------|------|------|
| _id | ObjectId | 文件ID | 主键 |
| skill_id | ObjectId | 所属Skill ID | 索引 |
| filename | String | 文件名 | 无 |
| file_path | String | 文件存储路径 | 无 |
| file_type | String | 文件类型 | 无 |
| version | String | 版本号 | 无 |
| created_at | Date | 创建时间 | 无 |

#### 1.2.4 版本集合 (versions)
| 字段名 | 类型 | 描述 | 索引 |
|-------|------|------|------|
| _id | ObjectId | 版本ID | 主键 |
| skill_id | ObjectId | 所属Skill ID | 索引 |
| version | String | 版本号 | 无 |
| changes | String | 变更描述 | 无 |
| created_at | Date | 创建时间 | 无 |
| created_by | ObjectId | 创建人ID | 无 |

### 1.3 索引设计

#### 1.3.1 用户集合索引
```javascript
// 唯一索引
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });
```

#### 1.3.2 Skill集合索引
```javascript
// 复合索引，用于快速查询用户的Skill列表
db.skills.createIndex({ user_id: 1, status: 1 });

// 类型索引，用于按类型筛选
db.skills.createIndex({ type: 1 });
```

#### 1.3.3 Skill文件集合索引
```javascript
// 索引，用于快速查询Skill的文件列表
db.skill_files.createIndex({ skill_id: 1 });
```

#### 1.3.4 版本集合索引
```javascript
// 索引，用于快速查询Skill的版本历史
db.versions.createIndex({ skill_id: 1 });
```

## 2. 对象存储服务设计

### 2.1 存储服务选择
- **腾讯云COS** 或 **阿里云OSS**
- 选择理由：
  - 高可用性和可靠性
  - 支持文件版本控制
  - 提供CDN加速
  - 按需计费，成本可控

### 2.2 存储桶结构

#### 2.2.1 存储桶命名
- 主存储桶：`skill-management`

#### 2.2.2 目录结构
```
skill-management/
├── users/
│   └── {user_id}/
│       └── skills/
│           └── {skill_id}/
│               ├── files/
│               │   └── {version}/
│               │       └── {filename}
│               └── versions/
│                   └── {version}.json
└── templates/
    └── {template_type}/
        └── {template_name}.json
```

### 2.3 文件命名规范
- **Skill文件**：`{skill_id}_{version}_{timestamp}_{filename}`
- **版本文件**：`{skill_id}_{version}.json`
- **模板文件**：`{template_type}_{template_name}.json`

### 2.4 访问控制
- **存储桶权限**：私有
- **访问方式**：
  - 后端通过API密钥访问
  - 前端通过临时访问凭证访问
- **文件访问URL**：使用预签名URL，设置合理的过期时间

### 2.5 文件版本控制
- **启用存储桶版本控制**
- **保留策略**：
  - 保留最近5个版本
  - 自动清理超过30天的旧版本

### 2.6 存储优化
- **文件压缩**：对文本文件进行压缩存储
- **CDN加速**：启用CDN加速，提高文件访问速度
- **缓存策略**：设置合理的缓存头，减少重复请求

## 3. 数据备份与恢复

### 3.1 数据库备份
- **备份策略**：
  - 每日自动备份
  - 保留最近7天的备份
  - 每月手动备份，保留1年
- **备份方式**：
  - 使用MongoDB Atlas的自动备份功能
  - 或使用云服务商提供的数据库备份服务

### 3.2 文件备份
- **备份策略**：
  - 存储桶跨区域复制
  - 定期快照
- **恢复机制**：
  - 从备份中恢复数据库
  - 从存储桶中恢复文件

### 3.3 灾难恢复
- **多区域部署**：
  - 数据库多区域复制
  - 存储桶跨区域复制
- **故障转移**：
  - 数据库自动故障转移
  - 存储服务冗余

## 4. 性能优化

### 4.1 数据库性能优化
- **查询优化**：
  - 使用索引覆盖查询
  - 避免全表扫描
  - 合理使用投影，减少返回数据量
- **写入优化**：
  - 使用批量写入
  - 合理设置写入关注点
- **连接池管理**：
  - 使用连接池复用连接
  - 设置合理的连接超时时间

### 4.2 存储性能优化
- **文件上传优化**：
  - 支持分块上传
  - 支持断点续传
- **文件下载优化**：
  - 使用CDN加速
  - 支持范围请求
- **缓存策略**：
  - 前端缓存静态资源
  - 后端缓存热点数据

## 5. 安全考虑

### 5.1 数据库安全
- **访问控制**：
  - 使用最小权限原则
  - 定期轮换数据库凭证
- **数据加密**：
  - 传输加密 (TLS/SSL)
  - 静态加密 (可选)
- **审计日志**：
  - 启用数据库审计日志
  - 定期检查异常操作

### 5.2 存储安全
- **访问控制**：
  - 使用临时访问凭证
  - 限制IP访问范围
- **数据加密**：
  - 传输加密 (HTTPS)
  - 静态加密
- **防DDoS**：
  - 启用存储服务的DDoS防护
  - 设置合理的访问限速

### 5.3 数据保护
- **敏感数据处理**：
  - 密码哈希存储
  - 敏感信息脱敏
- **数据泄露防护**：
  - 定期安全扫描
  - 数据访问监控

## 6. 监控与告警

### 6.1 数据库监控
- **监控指标**：
  - 查询性能
  - 连接数
  - 存储空间
  - 操作延迟
- **告警策略**：
  - 性能异常告警
  - 存储空间告警
  - 连接数告警

### 6.2 存储监控
- **监控指标**：
  - 文件上传/下载速度
  - 存储使用量
  - API调用次数
  - 错误率
- **告警策略**：
  - 存储容量告警
  - 访问异常告警
  - 错误率告警

## 7. 部署与维护

### 7.1 部署步骤
1. **创建MongoDB数据库**
   - 配置数据库实例
   - 创建用户和权限
   - 设置备份策略

2. **创建对象存储桶**
   - 配置存储桶
   - 设置访问权限
   - 启用版本控制

3. **配置连接信息**
   - 数据库连接字符串
   - 存储服务API密钥
   - 环境变量配置

### 7.2 维护计划
- **定期检查**：
  - 数据库性能
  - 存储使用情况
  - 安全配置

- **定期优化**：
  - 数据库索引
  - 存储结构
  - 缓存策略

- **定期更新**：
  - 数据库版本
  - 存储服务配置
  - 安全补丁