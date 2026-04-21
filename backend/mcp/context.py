"""
MCP上下文管理模块
支持多租户上下文隔离和管理
"""

import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading


class ContextStatus(Enum):
    """上下文状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ERROR = "error"


@dataclass
class Resource:
    """MCP资源"""
    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tool:
    """MCP工具"""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    handler: Optional[Callable] = None


@dataclass
class Prompt:
    """MCP提示词"""
    name: str
    description: str
    template: str
    arguments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Context:
    """
    MCP上下文
    
    一个上下文代表一个独立的会话环境，包含：
    - 资源（Resources）
    - 工具（Tools）
    - 提示词（Prompts）
    - 状态信息
    """
    id: str
    tenant_id: str
    name: str
    status: ContextStatus = ContextStatus.ACTIVE
    resources: Dict[str, Resource] = field(default_factory=dict)
    tools: Dict[str, Tool] = field(default_factory=dict)
    prompts: Dict[str, Prompt] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0


class ContextManager:
    """
    上下文管理器
    
    功能：
    - 多租户上下文隔离
    - 上下文CRUD操作
    - 资源、工具、提示词管理
    - 上下文生命周期管理
    """
    
    def __init__(self):
        self._contexts: Dict[str, Context] = {}
        self._tenant_contexts: Dict[str, List[str]] = {}  # tenant_id -> [context_ids]
        self._lock = threading.RLock()
    
    def create_context(
        self,
        tenant_id: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Context:
        """
        创建新上下文
        
        Args:
            tenant_id: 租户ID
            name: 上下文名称
            metadata: 元数据
            
        Returns:
            Context: 创建的上下文对象
        """
        with self._lock:
            context_id = str(uuid.uuid4())
            
            context = Context(
                id=context_id,
                tenant_id=tenant_id,
                name=name,
                metadata=metadata or {}
            )
            
            # 保存上下文
            self._contexts[context_id] = context
            
            # 更新租户上下文索引
            if tenant_id not in self._tenant_contexts:
                self._tenant_contexts[tenant_id] = []
            self._tenant_contexts[tenant_id].append(context_id)
            
            return context
    
    def get_context(self, context_id: str, tenant_id: Optional[str] = None) -> Optional[Context]:
        """
        获取上下文
        
        Args:
            context_id: 上下文ID
            tenant_id: 租户ID（用于验证权限）
            
        Returns:
            Context: 上下文对象，无权限时返回None
        """
        with self._lock:
            context = self._contexts.get(context_id)
            if not context:
                return None
            
            # 验证租户权限
            if tenant_id and context.tenant_id != tenant_id:
                return None
            
            # 更新访问信息
            context.last_accessed_at = datetime.utcnow()
            context.access_count += 1
            
            return context
    
    def list_contexts(self, tenant_id: str) -> List[Context]:
        """
        列出租户的所有上下文
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            List[Context]: 上下文列表
        """
        with self._lock:
            context_ids = self._tenant_contexts.get(tenant_id, [])
            return [self._contexts[cid] for cid in context_ids if cid in self._contexts]
    
    def update_context(
        self,
        context_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: Optional[ContextStatus] = None
    ) -> Optional[Context]:
        """更新上下文"""
        with self._lock:
            context = self.get_context(context_id, tenant_id)
            if not context:
                return None
            
            if name:
                context.name = name
            if metadata:
                context.metadata.update(metadata)
            if status:
                context.status = status
            
            context.updated_at = datetime.utcnow()
            return context
    
    def delete_context(self, context_id: str, tenant_id: str) -> bool:
        """删除上下文"""
        with self._lock:
            context = self.get_context(context_id, tenant_id)
            if not context:
                return False
            
            del self._contexts[context_id]
            
            # 更新租户上下文索引
            if tenant_id in self._tenant_contexts:
                self._tenant_contexts[tenant_id] = [
                    cid for cid in self._tenant_contexts[tenant_id]
                    if cid != context_id
                ]
            
            return True
    
    # ========== 资源管理 ==========
    
    def add_resource(
        self,
        context_id: str,
        tenant_id: str,
        resource: Resource
    ) -> bool:
        """添加资源到上下文"""
        with self._lock:
            context = self.get_context(context_id, tenant_id)
            if not context:
                return False
            
            context.resources[resource.uri] = resource
            context.updated_at = datetime.utcnow()
            return True
    
    def get_resource(
        self,
        context_id: str,
        tenant_id: str,
        uri: str
    ) -> Optional[Resource]:
        """获取资源"""
        with self._lock:
            context = self.get_context(context_id, tenant_id)
            if not context:
                return None
            
            return context.resources.get(uri)
    
    def remove_resource(
        self,
        context_id: str,
        tenant_id: str,
        uri: str
    ) -> bool:
        """从上下文移除资源"""
        with self._lock:
            context = self.get_context(context_id, tenant_id)
            if not context or uri not in context.resources:
                return False
            
            del context.resources[uri]
            context.updated_at = datetime.utcnow()
            return True
    
    # ========== 工具管理 ==========
    
    def add_tool(
        self,
        context_id: str,
        tenant_id: str,
        tool: Tool
    ) -> bool:
        """添加工具到上下文"""
        with self._lock:
            context = self.get_context(context_id, tenant_id)
            if not context:
                return False
            
            context.tools[tool.name] = tool
            context.updated_at = datetime.utcnow()
            return True
    
    def get_tool(
        self,
        context_id: str,
        tenant_id: str,
        name: str
    ) -> Optional[Tool]:
        """获取工具"""
        with self._lock:
            context = self.get_context(context_id, tenant_id)
            if not context:
                return None
            
            return context.tools.get(name)
    
    def call_tool(
        self,
        context_id: str,
        tenant_id: str,
        name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        调用工具
        
        Args:
            context_id: 上下文ID
            tenant_id: 租户ID
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            Any: 工具执行结果
        """
        with self._lock:
            tool = self.get_tool(context_id, tenant_id, name)
            if not tool or not tool.handler:
                raise ValueError(f"Tool '{name}' not found or no handler")
            
            return tool.handler(arguments)
    
    # ========== 提示词管理 ==========
    
    def add_prompt(
        self,
        context_id: str,
        tenant_id: str,
        prompt: Prompt
    ) -> bool:
        """添加提示词到上下文"""
        with self._lock:
            context = self.get_context(context_id, tenant_id)
            if not context:
                return False
            
            context.prompts[prompt.name] = prompt
            context.updated_at = datetime.utcnow()
            return True
    
    def get_prompt(
        self,
        context_id: str,
        tenant_id: str,
        name: str,
        arguments: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        获取提示词（支持模板渲染）
        
        Args:
            context_id: 上下文ID
            tenant_id: 租户ID
            name: 提示词名称
            arguments: 模板参数
            
        Returns:
            str: 渲染后的提示词
        """
        with self._lock:
            context = self.get_context(context_id, tenant_id)
            if not context:
                return None
            
            prompt = context.prompts.get(name)
            if not prompt:
                return None
            
            # 简单的模板渲染
            template = prompt.template
            if arguments:
                for key, value in arguments.items():
                    template = template.replace(f"{{{key}}}", str(value))
            
            return template
    
    # ========== 序列化 ==========
    
    def context_to_dict(self, context: Context) -> Dict[str, Any]:
        """将上下文转换为字典"""
        return {
            "id": context.id,
            "tenant_id": context.tenant_id,
            "name": context.name,
            "status": context.status.value,
            "resources": {
                uri: asdict(resource)
                for uri, resource in context.resources.items()
            },
            "tools": {
                name: {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
                for name, tool in context.tools.items()
            },
            "prompts": {
                name: asdict(prompt)
                for name, prompt in context.prompts.items()
            },
            "metadata": context.metadata,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "last_accessed_at": context.last_accessed_at.isoformat(),
            "access_count": context.access_count
        }


# 全局上下文管理器实例
context_manager = ContextManager()
