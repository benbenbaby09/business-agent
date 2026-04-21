"""
多租户管理模块
支持租户隔离、权限管理和资源分配
"""

import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import threading


class TenantStatus(Enum):
    """租户状态"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    PENDING = "pending"


class TenantTier(Enum):
    """租户等级/套餐"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class TenantQuota:
    """租户资源配额"""
    max_contexts: int = 10
    max_tools: int = 20
    max_resources: int = 100
    max_requests_per_minute: int = 60
    max_storage_mb: int = 100
    max_concurrent_connections: int = 5


@dataclass
class Tenant:
    """租户实体"""
    id: str
    name: str
    api_key: str
    api_secret: str
    status: TenantStatus = TenantStatus.ACTIVE
    tier: TenantTier = TenantTier.FREE
    quota: TenantQuota = field(default_factory=TenantQuota)
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TenantManager:
    """
    多租户管理器
    
    功能：
    - 租户CRUD操作
    - API密钥管理
    - 配额管理
    - 租户隔离
    """
    
    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}
        self._api_key_index: Dict[str, str] = {}  # api_key -> tenant_id
        self._lock = threading.RLock()
        
    def create_tenant(
        self,
        name: str,
        tier: TenantTier = TenantTier.FREE,
        quota: Optional[TenantQuota] = None,
        config: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None
    ) -> Tenant:
        """
        创建新租户
        
        Args:
            name: 租户名称
            tier: 租户等级
            quota: 资源配额
            config: 租户配置
            expires_at: 过期时间
            
        Returns:
            Tenant: 创建的租户对象
        """
        with self._lock:
            # 生成租户ID
            tenant_id = str(uuid.uuid4())
            
            # 生成API密钥
            api_key = self._generate_api_key()
            api_secret = self._generate_api_secret()
            
            # 创建租户
            tenant = Tenant(
                id=tenant_id,
                name=name,
                api_key=api_key,
                api_secret=api_secret,
                tier=tier,
                quota=quota or self._get_default_quota(tier),
                config=config or {},
                expires_at=expires_at
            )
            
            # 保存租户
            self._tenants[tenant_id] = tenant
            self._api_key_index[api_key] = tenant_id
            
            return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """根据ID获取租户"""
        with self._lock:
            return self._tenants.get(tenant_id)
    
    def get_tenant_by_api_key(self, api_key: str) -> Optional[Tenant]:
        """根据API密钥获取租户"""
        with self._lock:
            tenant_id = self._api_key_index.get(api_key)
            if tenant_id:
                return self._tenants.get(tenant_id)
            return None
    
    def authenticate(self, api_key: str, api_secret: str) -> Optional[Tenant]:
        """
        验证租户API密钥
        
        Args:
            api_key: API密钥
            api_secret: API密钥
            
        Returns:
            Tenant: 验证成功返回租户对象，失败返回None
        """
        with self._lock:
            tenant = self.get_tenant_by_api_key(api_key)
            if tenant and tenant.api_secret == api_secret:
                # 检查租户状态
                if tenant.status == TenantStatus.ACTIVE:
                    # 检查是否过期
                    if tenant.expires_at and datetime.utcnow() > tenant.expires_at:
                        tenant.status = TenantStatus.EXPIRED
                        return None
                    return tenant
            return None
    
    def update_tenant(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        tier: Optional[TenantTier] = None,
        quota: Optional[TenantQuota] = None,
        config: Optional[Dict[str, Any]] = None,
        status: Optional[TenantStatus] = None
    ) -> Optional[Tenant]:
        """更新租户信息"""
        with self._lock:
            tenant = self._tenants.get(tenant_id)
            if not tenant:
                return None
            
            if name:
                tenant.name = name
            if tier:
                tenant.tier = tier
                # 更新配额
                if not quota:
                    tenant.quota = self._get_default_quota(tier)
            if quota:
                tenant.quota = quota
            if config:
                tenant.config.update(config)
            if status:
                tenant.status = status
            
            tenant.updated_at = datetime.utcnow()
            return tenant
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """删除租户"""
        with self._lock:
            tenant = self._tenants.get(tenant_id)
            if not tenant:
                return False
            
            del self._tenants[tenant_id]
            del self._api_key_index[tenant.api_key]
            return True
    
    def regenerate_api_key(self, tenant_id: str) -> Optional[Tenant]:
        """重新生成API密钥"""
        with self._lock:
            tenant = self._tenants.get(tenant_id)
            if not tenant:
                return None
            
            # 删除旧的API密钥索引
            del self._api_key_index[tenant.api_key]
            
            # 生成新的API密钥
            tenant.api_key = self._generate_api_key()
            tenant.api_secret = self._generate_api_secret()
            tenant.updated_at = datetime.utcnow()
            
            # 添加新的API密钥索引
            self._api_key_index[tenant.api_key] = tenant_id
            
            return tenant
    
    def list_tenants(
        self,
        status: Optional[TenantStatus] = None,
        tier: Optional[TenantTier] = None
    ) -> List[Tenant]:
        """列出租户"""
        with self._lock:
            tenants = list(self._tenants.values())
            
            if status:
                tenants = [t for t in tenants if t.status == status]
            if tier:
                tenants = [t for t in tenants if t.tier == tier]
            
            return tenants
    
    def check_quota(self, tenant_id: str, resource_type: str) -> bool:
        """
        检查租户配额
        
        Args:
            tenant_id: 租户ID
            resource_type: 资源类型 (contexts, tools, resources, requests)
            
        Returns:
            bool: 是否在配额内
        """
        with self._lock:
            tenant = self._tenants.get(tenant_id)
            if not tenant:
                return False
            
            # 这里应该实现实际的配额检查逻辑
            # 例如查询当前使用量并与配额比较
            return True
    
    def _generate_api_key(self) -> str:
        """生成API密钥"""
        return f"mcp_{secrets.token_urlsafe(32)}"
    
    def _generate_api_secret(self) -> str:
        """生成API密钥"""
        return secrets.token_urlsafe(64)
    
    def _get_default_quota(self, tier: TenantTier) -> TenantQuota:
        """获取默认配额"""
        quotas = {
            TenantTier.FREE: TenantQuota(
                max_contexts=5,
                max_tools=10,
                max_resources=50,
                max_requests_per_minute=30,
                max_storage_mb=50,
                max_concurrent_connections=2
            ),
            TenantTier.BASIC: TenantQuota(
                max_contexts=20,
                max_tools=50,
                max_resources=200,
                max_requests_per_minute=120,
                max_storage_mb=500,
                max_concurrent_connections=10
            ),
            TenantTier.PROFESSIONAL: TenantQuota(
                max_contexts=50,
                max_tools=100,
                max_resources=500,
                max_requests_per_minute=300,
                max_storage_mb=2000,
                max_concurrent_connections=25
            ),
            TenantTier.ENTERPRISE: TenantQuota(
                max_contexts=200,
                max_tools=500,
                max_resources=2000,
                max_requests_per_minute=1000,
                max_storage_mb=10000,
                max_concurrent_connections=100
            )
        }
        return quotas.get(tier, quotas[TenantTier.FREE])


# 全局租户管理器实例
tenant_manager = TenantManager()
