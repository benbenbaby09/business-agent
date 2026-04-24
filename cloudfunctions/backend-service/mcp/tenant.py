from enum import Enum
import os
import json
import uuid
from datetime import datetime

class TenantTier(Enum):
    FREE = 'free'
    BASIC = 'basic'
    PROFESSIONAL = 'professional'
    ENTERPRISE = 'enterprise'

class Tenant:
    def __init__(self, id, name, tier, config=None, type='restaurant_entity', status='active', created_at=None, api_key=None, api_secret=None):
        self.id = id
        self.name = name
        self.tier = TenantTier(tier) if isinstance(tier, str) else tier
        self.config = config or {}
        self.type = type or 'restaurant_entity'
        self.status = status
        self.created_at = created_at or datetime.now()
        self.api_key = api_key or f'mcp_{str(uuid.uuid4())[:8]}'
        self.api_secret = api_secret or str(uuid.uuid4())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tier': self.tier.value,
            'config': self.config,
            'type': self.type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'api_key': self.api_key,
            'api_secret': self.api_secret
        }

class TenantManager:
    def __init__(self, data_file='/data/tenants.json'):
        self.data_file = data_file
        self.tenants = []
        self.load_tenants()

    def reload_tenants(self):
        self.tenants = []
        self.load_tenants()

    def load_tenants(self):
        """加载租户数据"""
        os.makedirs('/data', exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        with open(self.data_file, 'r', encoding='utf-8') as f:
            tenants_data = json.load(f)
            for data in tenants_data:
                api_key = data.get('api_key')
                api_secret = data.get('api_secret')
                if not api_key and 'mcp_service' in data:
                    api_key = data['mcp_service'].get('api_key')
                    api_secret = data['mcp_service'].get('api_secret')
                tenant = Tenant(
                    id=data['id'],
                    name=data['name'],
                    tier=data['tier'],
                    config=data.get('config', {}),
                    type=data.get('type', 'restaurant_entity'),
                    status=data.get('status', 'active'),
                    created_at=datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at'],
                    api_key=api_key,
                    api_secret=api_secret
                )
                self.tenants.append(tenant)

    def _save_tenants(self):
        """保存租户数据"""
        tenants_data = [tenant.to_dict() for tenant in self.tenants]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(tenants_data, f, ensure_ascii=False, indent=2)

    def create_tenant(self, name, tier, config=None, type='restaurant_entity'):
        """创建租户"""
        tenant_id = f"tenant_{len(self.tenants) + 1}"
        tenant = Tenant(tenant_id, name, tier, config, type=type)
        self.tenants.append(tenant)
        self._save_tenants()
        return tenant

    def list_tenants(self):
        """列出租户"""
        return self.tenants

    def get_tenant(self, tenant_id):
        """获取租户"""
        for tenant in self.tenants:
            if tenant.id == tenant_id:
                return tenant
        return None

    def get_tenant_by_api_key(self, api_key):
        """通过API Key获取租户"""
        for tenant in self.tenants:
            if tenant.api_key == api_key:
                return tenant
        return None

    def update_tenant(self, tenant_id, updates):
        """更新租户"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return None
        
        # 如果 updates 包含完整的租户数据（从 routes/tenants.py 传来）
        # 则更新所有字段
        if 'id' in updates and 'name' in updates and 'tier' in updates:
            tenant.name = updates.get('name', tenant.name)
            tenant.tier = TenantTier(updates['tier']) if isinstance(updates['tier'], str) else updates['tier']
            tenant.config = updates.get('config', tenant.config)
            tenant.type = updates.get('type', tenant.type) or tenant.type
            tenant.status = updates.get('status', tenant.status)
        else:
            # 部分更新（兼容旧逻辑）
            if 'name' in updates:
                tenant.name = updates['name']
            if 'tier' in updates:
                tenant.tier = TenantTier(updates['tier'])
            if 'config' in updates:
                tenant.config = updates['config']
            if 'type' in updates:
                tenant.type = updates['type'] or tenant.type
            if 'status' in updates:
                tenant.status = updates['status']
        
        self._save_tenants()
        return tenant

    def delete_tenant(self, tenant_id):
        """删除租户"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        self.tenants = [t for t in self.tenants if t.id != tenant_id]
        self._save_tenants()
        return True

# 创建租户管理器实例
tenant_manager = TenantManager()
