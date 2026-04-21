"""
MCP (Model Context Protocol) 服务器
支持多租户策略的MCP服务实现
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from flask import Flask, request, jsonify
from functools import wraps

from .tenant import tenant_manager, Tenant, TenantTier, TenantStatus
from .context import context_manager, Context, Resource, Tool, Prompt, ContextStatus


class MCPServer:
    """
    MCP服务器
    
    功能：
    - 多租户API认证
    - 上下文管理
    - 资源、工具、提示词服务
    - 符合MCP协议规范
    """
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.routes_registered = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """初始化Flask应用"""
        self.app = app
        self._register_routes()
    
    def _register_routes(self):
        """注册API路由"""
        if self.routes_registered:
            return
        
        # ========== 租户管理API ==========
        
        @self.app.route('/api/mcp/tenants', methods=['POST'])
        def create_tenant():
            """创建租户"""
            data = request.get_json()
            
            tenant = tenant_manager.create_tenant(
                name=data.get('name'),
                tier=TenantTier(data.get('tier', 'free')),
                config=data.get('config', {})
            )
            
            return jsonify({
                "id": tenant.id,
                "name": tenant.name,
                "api_key": tenant.api_key,
                "api_secret": tenant.api_secret,
                "tier": tenant.tier.value,
                "status": tenant.status.value,
                "created_at": tenant.created_at.isoformat()
            }), 201
        
        @self.app.route('/api/mcp/tenants/<tenant_id>', methods=['GET'])
        def get_tenant(tenant_id: str):
            """获取租户信息"""
            tenant = tenant_manager.get_tenant(tenant_id)
            if not tenant:
                return jsonify({"error": "Tenant not found"}), 404
            
            return jsonify({
                "id": tenant.id,
                "name": tenant.name,
                "tier": tenant.tier.value,
                "status": tenant.status.value,
                "quota": {
                    "max_contexts": tenant.quota.max_contexts,
                    "max_tools": tenant.quota.max_tools,
                    "max_resources": tenant.quota.max_resources,
                    "max_requests_per_minute": tenant.quota.max_requests_per_minute
                },
                "created_at": tenant.created_at.isoformat()
            })
        
        @self.app.route('/api/mcp/tenants', methods=['GET'])
        def list_tenants():
            """列出租户"""
            tenants = tenant_manager.list_tenants()
            return jsonify([
                {
                    "id": t.id,
                    "name": t.name,
                    "tier": t.tier.value,
                    "status": t.status.value
                }
                for t in tenants
            ])
        
        # ========== 上下文管理API ==========
        
        @self.app.route('/api/mcp/contexts', methods=['POST'])
        def create_context():
            """创建上下文"""
            # 认证
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            
            # 检查配额
            contexts = context_manager.list_contexts(tenant.id)
            if len(contexts) >= tenant.quota.max_contexts:
                return jsonify({"error": "Context quota exceeded"}), 403
            
            context = context_manager.create_context(
                tenant_id=tenant.id,
                name=data.get('name', 'Untitled'),
                metadata=data.get('metadata', {})
            )
            
            return jsonify({
                "id": context.id,
                "tenant_id": context.tenant_id,
                "name": context.name,
                "status": context.status.value,
                "created_at": context.created_at.isoformat()
            }), 201
        
        @self.app.route('/api/mcp/contexts', methods=['GET'])
        def list_contexts():
            """列出租户的上下文"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            contexts = context_manager.list_contexts(tenant.id)
            return jsonify([
                {
                    "id": ctx.id,
                    "name": ctx.name,
                    "status": ctx.status.value,
                    "resource_count": len(ctx.resources),
                    "tool_count": len(ctx.tools),
                    "prompt_count": len(ctx.prompts),
                    "created_at": ctx.created_at.isoformat()
                }
                for ctx in contexts
            ])
        
        @self.app.route('/api/mcp/contexts/<context_id>', methods=['GET'])
        def get_context(context_id: str):
            """获取上下文详情"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            context = context_manager.get_context(context_id, tenant.id)
            if not context:
                return jsonify({"error": "Context not found"}), 404
            
            return jsonify(context_manager.context_to_dict(context))
        
        @self.app.route('/api/mcp/contexts/<context_id>', methods=['DELETE'])
        def delete_context(context_id: str):
            """删除上下文"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            if context_manager.delete_context(context_id, tenant.id):
                return jsonify({"message": "Context deleted"})
            return jsonify({"error": "Context not found"}), 404
        
        # ========== 资源管理API ==========
        
        @self.app.route('/api/mcp/contexts/<context_id>/resources', methods=['POST'])
        def add_resource(context_id: str):
            """添加资源"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            
            resource = Resource(
                uri=data.get('uri'),
                name=data.get('name'),
                description=data.get('description', ''),
                mime_type=data.get('mime_type', 'text/plain'),
                content=data.get('content'),
                metadata=data.get('metadata', {})
            )
            
            if context_manager.add_resource(context_id, tenant.id, resource):
                return jsonify({"message": "Resource added"}), 201
            return jsonify({"error": "Failed to add resource"}), 400
        
        @self.app.route('/api/mcp/contexts/<context_id>/resources', methods=['GET'])
        def list_resources(context_id: str):
            """列出资源"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            context = context_manager.get_context(context_id, tenant.id)
            if not context:
                return jsonify({"error": "Context not found"}), 404
            
            return jsonify([
                {
                    "uri": r.uri,
                    "name": r.name,
                    "description": r.description,
                    "mime_type": r.mime_type,
                    "metadata": r.metadata
                }
                for r in context.resources.values()
            ])
        
        # ========== 工具管理API ==========
        
        @self.app.route('/api/mcp/contexts/<context_id>/tools', methods=['POST'])
        def add_tool(context_id: str):
            """添加工具"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            
            tool = Tool(
                name=data.get('name'),
                description=data.get('description', ''),
                parameters=data.get('parameters', {})
            )
            
            if context_manager.add_tool(context_id, tenant.id, tool):
                return jsonify({"message": "Tool added"}), 201
            return jsonify({"error": "Failed to add tool"}), 400
        
        @self.app.route('/api/mcp/contexts/<context_id>/tools', methods=['GET'])
        def list_tools(context_id: str):
            """列出工具"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            context = context_manager.get_context(context_id, tenant.id)
            if not context:
                return jsonify({"error": "Context not found"}), 404
            
            return jsonify([
                {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters
                }
                for t in context.tools.values()
            ])
        
        # ========== 提示词管理API ==========
        
        @self.app.route('/api/mcp/contexts/<context_id>/prompts', methods=['POST'])
        def add_prompt(context_id: str):
            """添加提示词"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            
            prompt = Prompt(
                name=data.get('name'),
                description=data.get('description', ''),
                template=data.get('template'),
                arguments=data.get('arguments', [])
            )
            
            if context_manager.add_prompt(context_id, tenant.id, prompt):
                return jsonify({"message": "Prompt added"}), 201
            return jsonify({"error": "Failed to add prompt"}), 400
        
        @self.app.route('/api/mcp/contexts/<context_id>/prompts', methods=['GET'])
        def list_prompts(context_id: str):
            """列出提示词"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            context = context_manager.get_context(context_id, tenant.id)
            if not context:
                return jsonify({"error": "Context not found"}), 404
            
            return jsonify([
                {
                    "name": p.name,
                    "description": p.description,
                    "arguments": p.arguments
                }
                for p in context.prompts.values()
            ])
        
        @self.app.route('/api/mcp/contexts/<context_id>/prompts/<prompt_name>', methods=['GET'])
        def get_prompt(context_id: str, prompt_name: str):
            """获取渲染后的提示词"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            args = request.args.to_dict()
            prompt_text = context_manager.get_prompt(
                context_id, tenant.id, prompt_name, args
            )
            
            if prompt_text:
                return jsonify({"prompt": prompt_text})
            return jsonify({"error": "Prompt not found"}), 404
        
        # ========== MCP协议端点 ==========
        
        @self.app.route('/api/mcp/initialize', methods=['POST'])
        def initialize():
            """MCP初始化端点"""
            tenant = self._authenticate()
            if not tenant:
                return jsonify({"error": "Unauthorized"}), 401
            
            return jsonify({
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "skill-management-mcp-server",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "resources": {},
                    "tools": {},
                    "prompts": {}
                }
            })
        
        self.routes_registered = True
    
    def _authenticate(self) -> Optional[Tenant]:
        """
        认证请求
        
        从请求头中获取API密钥进行认证
        """
        api_key = request.headers.get('X-API-Key')
        api_secret = request.headers.get('X-API-Secret')
        
        if not api_key or not api_secret:
            return None
        
        return tenant_manager.authenticate(api_key, api_secret)
    
    def create_default_tenant(self) -> Tenant:
        """创建默认租户（用于测试）"""
        return tenant_manager.create_tenant(
            name="Default Tenant",
            tier=TenantTier.FREE,
            config={"description": "Default tenant for testing"}
        )


# 全局MCP服务器实例
mcp_server = MCPServer()
