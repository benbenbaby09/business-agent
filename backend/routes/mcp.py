"""
MCP (Model Context Protocol) 路由
为租户提供MCP服务管理功能
一个租户只有一个MCP服务
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from bson.objectid import ObjectId
from database import tenants_collection
from json_database import tenants_collection as json_tenants_collection
from middleware import auth_required
import sys
import os

# 添加mcp模块到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp.tenant import tenant_manager, TenantTier, TenantStatus
from mcp.context import context_manager

bp = Blueprint('mcp', __name__)


def get_tenant_by_user_and_id(user_id, tenant_id):
    """获取用户拥有的租户"""
    try:
        # 尝试从JSON数据库获取
        tenant = json_tenants_collection.find_one({
            '_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        if tenant:
            return tenant
    except:
        pass
    
    # 尝试从MongoDB获取
    try:
        tenant = tenants_collection.find_one({
            '_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        return tenant
    except:
        return None


# 获取租户的MCP服务信息
@bp.route('/tenants/<tenant_id>/mcp', methods=['GET'])
@auth_required
def get_mcp_service(user_id, tenant_id):
    """获取租户的MCP服务信息"""
    tenant = get_tenant_by_user_and_id(user_id, tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    # 获取或创建MCP租户
    mcp_tenant = tenant_manager.get_tenant(tenant_id)
    if not mcp_tenant:
        # 创建MCP租户
        tier = TenantTier(tenant.get('tier', 'free'))
        mcp_tenant = tenant_manager.create_tenant(
            name=tenant.get('name', 'Unknown'),
            tier=tier,
            config={
                'original_tenant_id': tenant_id,
                'user_id': str(user_id)
            }
        )
    
    return jsonify({
        'tenant_id': tenant_id,
        'mcp_tenant_id': mcp_tenant.id,
        'api_key': mcp_tenant.api_key,
        'api_secret': mcp_tenant.api_secret,
        'tier': mcp_tenant.tier.value,
        'status': mcp_tenant.status.value,
        'quota': {
            'max_contexts': mcp_tenant.quota.max_contexts,
            'max_tools': mcp_tenant.quota.max_tools,
            'max_resources': mcp_tenant.quota.max_resources
        },
        'created_at': mcp_tenant.created_at.isoformat()
    })


# 重新生成MCP API密钥
@bp.route('/tenants/<tenant_id>/mcp/regenerate-keys', methods=['POST'])
@auth_required
def regenerate_mcp_keys(user_id, tenant_id):
    """重新生成MCP服务的API密钥"""
    tenant = get_tenant_by_user_and_id(user_id, tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    # 获取MCP租户
    mcp_tenant = tenant_manager.get_tenant(tenant_id)
    if not mcp_tenant:
        return jsonify({'error': 'MCP service not found'}), 404
    
    # 重新生成密钥
    updated_tenant = tenant_manager.regenerate_api_key(mcp_tenant.id)
    if not updated_tenant:
        return jsonify({'error': 'Failed to regenerate keys'}), 500
    
    return jsonify({
        'tenant_id': tenant_id,
        'api_key': updated_tenant.api_key,
        'api_secret': updated_tenant.api_secret,
        'message': 'API keys regenerated successfully'
    })


# 获取MCP上下文列表
@bp.route('/tenants/<tenant_id>/mcp/contexts', methods=['GET'])
@auth_required
def list_mcp_contexts(user_id, tenant_id):
    """获取租户MCP服务的上下文列表"""
    tenant = get_tenant_by_user_and_id(user_id, tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    # 获取MCP租户
    mcp_tenant = tenant_manager.get_tenant(tenant_id)
    if not mcp_tenant:
        return jsonify({'contexts': []})
    
    contexts = context_manager.list_contexts(mcp_tenant.id)
    
    return jsonify({
        'contexts': [
            {
                'id': ctx.id,
                'name': ctx.name,
                'status': ctx.status.value,
                'resource_count': len(ctx.resources),
                'tool_count': len(ctx.tools),
                'prompt_count': len(ctx.prompts),
                'created_at': ctx.created_at.isoformat()
            }
            for ctx in contexts
        ]
    })


# 创建MCP上下文
@bp.route('/tenants/<tenant_id>/mcp/contexts', methods=['POST'])
@auth_required
def create_mcp_context(user_id, tenant_id):
    """为租户MCP服务创建上下文"""
    tenant = get_tenant_by_user_and_id(user_id, tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    # 获取或创建MCP租户
    mcp_tenant = tenant_manager.get_tenant(tenant_id)
    if not mcp_tenant:
        tier = TenantTier(tenant.get('tier', 'free'))
        mcp_tenant = tenant_manager.create_tenant(
            name=tenant.get('name', 'Unknown'),
            tier=tier,
            config={'original_tenant_id': tenant_id}
        )
    
    # 检查配额
    contexts = context_manager.list_contexts(mcp_tenant.id)
    if len(contexts) >= mcp_tenant.quota.max_contexts:
        return jsonify({'error': 'Context quota exceeded'}), 403
    
    data = request.get_json()
    
    # 创建上下文
    context = context_manager.create_context(
        tenant_id=mcp_tenant.id,
        name=data.get('name', 'Untitled'),
        metadata=data.get('metadata', {})
    )
    
    return jsonify({
        'id': context.id,
        'tenant_id': tenant_id,
        'name': context.name,
        'status': context.status.value,
        'created_at': context.created_at.isoformat()
    }), 201


# 删除MCP上下文
@bp.route('/tenants/<tenant_id>/mcp/contexts/<context_id>', methods=['DELETE'])
@auth_required
def delete_mcp_context(user_id, tenant_id, context_id):
    """删除租户MCP服务的上下文"""
    tenant = get_tenant_by_user_and_id(user_id, tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    mcp_tenant = tenant_manager.get_tenant(tenant_id)
    if not mcp_tenant:
        return jsonify({'error': 'MCP service not found'}), 404
    
    if context_manager.delete_context(context_id, mcp_tenant.id):
        return jsonify({'message': 'Context deleted'})
    
    return jsonify({'error': 'Context not found'}), 404


# 获取MCP服务统计信息
@bp.route('/tenants/<tenant_id>/mcp/stats', methods=['GET'])
@auth_required
def get_mcp_stats(user_id, tenant_id):
    """获取租户MCP服务统计信息"""
    tenant = get_tenant_by_user_and_id(user_id, tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    mcp_tenant = tenant_manager.get_tenant(tenant_id)
    if not mcp_tenant:
        return jsonify({
            'contexts_count': 0,
            'resources_count': 0,
            'tools_count': 0,
            'prompts_count': 0,
            'quota': {
                'max_contexts': 5,
                'max_tools': 10,
                'max_resources': 50
            }
        })
    
    contexts = context_manager.list_contexts(mcp_tenant.id)
    
    total_resources = sum(len(ctx.resources) for ctx in contexts)
    total_tools = sum(len(ctx.tools) for ctx in contexts)
    total_prompts = sum(len(ctx.prompts) for ctx in contexts)
    
    return jsonify({
        'contexts_count': len(contexts),
        'resources_count': total_resources,
        'tools_count': total_tools,
        'prompts_count': total_prompts,
        'quota': {
            'max_contexts': mcp_tenant.quota.max_contexts,
            'max_tools': mcp_tenant.quota.max_tools,
            'max_resources': mcp_tenant.quota.max_resources
        }
    })
