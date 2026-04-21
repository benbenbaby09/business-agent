# MCP (Model Context Protocol) 服务模块

## 概述

MCP服务模块是一个支持多租户策略的Model Context Protocol实现，提供以下功能：

- **多租户管理**：租户隔离、API密钥认证、配额管理
- **上下文管理**：创建和管理独立的会话环境
- **资源管理**：管理文档、文件等资源
- **工具管理**：注册和调用工具
- **提示词管理**：管理提示词模板

## 架构设计

### 多租户策略

```
Tenant (租户)
  ├── API Key / Secret (认证)
  ├── Quota (配额管理)
  │   ├── max_contexts: 最大上下文数
  │   ├── max_tools: 最大工具数
  │   ├── max_resources: 最大资源数
  │   └── max_requests_per_minute: 每分钟最大请求数
  └── Contexts (上下文列表)
       ├── Resources (资源)
       ├── Tools (工具)
       └── Prompts (提示词)
```

### 租户等级

| 等级 | 上下文数 | 工具数 | 资源数 | 请求/分钟 |
|-----|---------|--------|--------|----------|
| FREE | 5 | 10 | 50 | 30 |
| BASIC | 20 | 50 | 200 | 120 |
| PROFESSIONAL | 50 | 100 | 500 | 300 |
| ENTERPRISE | 200 | 500 | 2000 | 1000 |

## API端点

### 租户管理

```
POST   /api/mcp/tenants          # 创建租户
GET    /api/mcp/tenants          # 列出租户
GET    /api/mcp/tenants/{id}     # 获取租户信息
```

### 上下文管理

```
POST   /api/mcp/contexts                    # 创建上下文
GET    /api/mcp/contexts                    # 列出上下文
GET    /api/mcp/contexts/{id}               # 获取上下文
DELETE /api/mcp/contexts/{id}               # 删除上下文
```

### 资源管理

```
POST   /api/mcp/contexts/{id}/resources      # 添加资源
GET    /api/mcp/contexts/{id}/resources      # 列出资源
```

### 工具管理

```
POST   /api/mcp/contexts/{id}/tools          # 添加工具
GET    /api/mcp/contexts/{id}/tools          # 列出工具
```

### 提示词管理

```
POST   /api/mcp/contexts/{id}/prompts        # 添加提示词
GET    /api/mcp/contexts/{id}/prompts        # 列出提示词
GET    /api/mcp/contexts/{id}/prompts/{name} # 获取提示词
```

### MCP协议

```
POST   /api/mcp/initialize                   # MCP初始化
GET    /api/mcp/info                         # MCP服务信息
```

## 认证方式

所有MCP API（除创建租户外）需要在请求头中提供：

```
X-API-Key: your-api-key
X-API-Secret: your-api-secret
```

## 使用示例

### 1. 创建租户

```bash
curl -X POST http://localhost:8000/api/mcp/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Tenant",
    "tier": "basic",
    "config": {
      "description": "My first tenant"
    }
  }'
```

响应：
```json
{
  "id": "uuid",
  "name": "My Tenant",
  "api_key": "mcp_...",
  "api_secret": "...",
  "tier": "basic",
  "status": "active",
  "created_at": "2024-01-01T00:00:00"
}
```

### 2. 创建上下文

```bash
curl -X POST http://localhost:8000/api/mcp/contexts \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "X-API-Secret: your-api-secret" \
  -d '{
    "name": "My Context",
    "metadata": {
      "description": "A test context"
    }
  }'
```

### 3. 添加资源

```bash
curl -X POST http://localhost:8000/api/mcp/contexts/{context_id}/resources \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "X-API-Secret: your-api-secret" \
  -d '{
    "uri": "file:///docs/readme.md",
    "name": "README",
    "description": "Project README",
    "mime_type": "text/markdown",
    "content": "# Hello World"
  }'
```

### 4. 添加工具

```bash
curl -X POST http://localhost:8000/api/mcp/contexts/{context_id}/tools \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "X-API-Secret: your-api-secret" \
  -d '{
    "name": "calculator",
    "description": "A simple calculator",
    "parameters": {
      "operation": {
        "type": "string",
        "enum": ["add", "subtract", "multiply", "divide"]
      },
      "a": {"type": "number"},
      "b": {"type": "number"}
    }
  }'
```

### 5. 添加提示词

```bash
curl -X POST http://localhost:8000/api/mcp/contexts/{context_id}/prompts \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "X-API-Secret: your-api-secret" \
  -d '{
    "name": "greeting",
    "description": "A greeting prompt",
    "template": "Hello, {name}! Welcome to {place}.",
    "arguments": [
      {"name": "name", "description": "User name", "required": true},
      {"name": "place", "description": "Place name", "required": true}
    ]
  }'
```

### 6. 获取渲染后的提示词

```bash
curl "http://localhost:8000/api/mcp/contexts/{context_id}/prompts/greeting?name=Alice&place=Wonderland" \
  -H "X-API-Key: your-api-key" \
  -H "X-API-Secret: your-api-secret"
```

响应：
```json
{
  "prompt": "Hello, Alice! Welcome to Wonderland."
}
```

## 默认租户

系统启动时会自动创建一个默认租户：

- **名称**: Default Tenant
- **等级**: FREE
- **API Key**: 启动时打印在控制台
- **API Secret**: 启动时打印在控制台

## 模块结构

```
backend/mcp/
├── __init__.py      # 模块导出
├── server.py        # MCP服务器实现
├── tenant.py        # 多租户管理
└── context.py       # 上下文管理
```

## 集成说明

MCP服务已集成到主应用中，启动后端服务后自动可用：

```bash
cd backend
python app.py
```

访问 http://localhost:8000/api/mcp/info 查看MCP服务信息。

## 与Skill管理系统的集成

MCP服务可以与Skill管理系统结合使用：

1. 每个Skill可以关联一个MCP上下文
2. 通过MCP上下文管理Skill的资源、工具和提示词
3. 多租户支持确保不同商家的Skill数据隔离

## 后续扩展

- [ ] WebSocket支持实时通信
- [ ] 工具执行器实现
- [ ] 资源内容存储优化
- [ ] 租户计费系统
- [ ] 使用统计和监控
