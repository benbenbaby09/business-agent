"""
MCP服务管理路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from bson.objectid import ObjectId
from database import tenants_collection
from json_database import tenants_collection as json_tenants_collection
from middleware import auth_required
import sys
import os

bp = Blueprint('mcp_services', __name__)


def get_collection():
    """获取MCP服务集合"""
    try:
        from database import db
        return db.mcp_services
    except:
        # 使用JSON数据库
        from json_database import JSONCollection
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        return JSONCollection(os.path.join(data_dir, 'mcp_services.json'))


def get_tools_collection():
    """获取MCP工具集合"""
    try:
        from database import db
        return db.mcp_tools
    except:
        # 使用JSON数据库
        from json_database import JSONCollection
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        return JSONCollection(os.path.join(data_dir, 'mcp_tools.json'))


# 获取租户的MCP服务
@bp.route('/tenants/<tenant_id>/mcp/service', methods=['GET'])
@auth_required
def get_mcp_service(user_id, tenant_id):
    """获取租户的MCP服务"""
    try:
        services_collection = get_collection()
        
        # 查询该租户的MCP服务
        service = services_collection.find_one({
            'tenant_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        
        if not service:
            return jsonify({'error': 'MCP service not found'}), 404
        
        # 格式化数据
        service['_id'] = str(service['_id'])
        service['tenant_id'] = str(service['tenant_id'])
        service['user_id'] = str(service['user_id'])
        
        return jsonify(service)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 创建MCP服务
@bp.route('/tenants/<tenant_id>/mcp/service', methods=['POST'])
@auth_required
def create_mcp_service(user_id, tenant_id):
    """为租户创建MCP服务"""
    try:
        services_collection = get_collection()
        
        # 检查是否已存在
        existing = services_collection.find_one({
            'tenant_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        
        if existing:
            return jsonify({'error': 'MCP service already exists'}), 400
        
        # 获取租户信息
        tenant = json_tenants_collection.find_one({
            '_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # 创建MCP服务
        service = {
            'user_id': ObjectId(user_id),
            'tenant_id': ObjectId(tenant_id),
            'name': f"{tenant.get('name', 'Unknown')}的MCP服务",
            'status': 'active',
            'version': '1.0.0',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = services_collection.insert_one(service)
        service['_id'] = str(result.inserted_id)
        service['user_id'] = str(service['user_id'])
        service['tenant_id'] = str(service['tenant_id'])
        
        return jsonify(service), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 获取MCP工具列表
@bp.route('/tenants/<tenant_id>/mcp/tools', methods=['GET'])
@auth_required
def get_mcp_tools(user_id, tenant_id):
    """获取租户MCP服务的工具列表"""
    try:
        tools_collection = get_tools_collection()
        
        # 查询该租户的所有工具
        tools = list(tools_collection.find({
            'tenant_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        }))
        
        # 格式化数据
        for tool in tools:
            tool['_id'] = str(tool['_id'])
            tool['tenant_id'] = str(tool['tenant_id'])
            tool['user_id'] = str(tool['user_id'])
        
        return jsonify(tools)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 创建MCP工具
@bp.route('/tenants/<tenant_id>/mcp/tools', methods=['POST'])
@auth_required
def create_mcp_tool(user_id, tenant_id):
    """为租户MCP服务创建工具"""
    try:
        tools_collection = get_tools_collection()
        
        data = request.get_json()
        
        # 创建工具
        tool = {
            'user_id': ObjectId(user_id),
            'tenant_id': ObjectId(tenant_id),
            'name': data.get('name'),
            'title': data.get('title'),
            'type': data.get('type'),
            'description': data.get('description', ''),
            'config': data.get('config', {}),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = tools_collection.insert_one(tool)
        tool['_id'] = str(result.inserted_id)
        tool['user_id'] = str(tool['user_id'])
        tool['tenant_id'] = str(tool['tenant_id'])
        
        return jsonify(tool), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 更新MCP工具
@bp.route('/tenants/<tenant_id>/mcp/tools/<tool_id>', methods=['PUT'])
@auth_required
def update_mcp_tool(user_id, tenant_id, tool_id):
    """更新MCP工具"""
    try:
        tools_collection = get_tools_collection()
        
        data = request.get_json()
        
        # 构建更新数据
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'config' in data:
            update_data['config'] = data['config']
        
        result = tools_collection.update_one(
            {
                '_id': ObjectId(tool_id),
                'tenant_id': ObjectId(tenant_id),
                'user_id': ObjectId(user_id)
            },
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Tool not found'}), 404
        
        # 获取更新后的工具
        tool = tools_collection.find_one({
            '_id': ObjectId(tool_id),
            'tenant_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        
        tool['_id'] = str(tool['_id'])
        tool['tenant_id'] = str(tool['tenant_id'])
        tool['user_id'] = str(tool['user_id'])
        
        return jsonify(tool)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 删除MCP工具
@bp.route('/tenants/<tenant_id>/mcp/tools/<tool_id>', methods=['DELETE'])
@auth_required
def delete_mcp_tool(user_id, tenant_id, tool_id):
    """删除MCP工具"""
    try:
        tools_collection = get_tools_collection()
        
        result = tools_collection.delete_one({
            '_id': ObjectId(tool_id),
            'tenant_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Tool not found'}), 404
        
        return jsonify({'message': 'Tool deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
