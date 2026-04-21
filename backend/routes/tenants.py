from flask import Blueprint, request, jsonify
from datetime import datetime
from bson.objectid import ObjectId
from database import tenants_collection, skills_collection
from middleware import auth_required
import secrets

bp = Blueprint('tenants', __name__)

# 生成API密钥
def generate_api_key():
    return f"mcp_{secrets.token_urlsafe(32)}"

def generate_api_secret():
    return secrets.token_urlsafe(64)

# 获取租户列表
@bp.route('', methods=['GET'])
@auth_required
def get_tenants(user_id):
    try:
        # 获取当前用户的租户
        tenants = list(tenants_collection.find({'user_id': ObjectId(user_id)}))
        
        # 格式化数据
        for tenant in tenants:
            tenant['_id'] = str(tenant['_id'])
            tenant['user_id'] = str(tenant['user_id'])
            # 不返回api_secret
            tenant.pop('api_secret', None)
            # 确保type字段存在
            if 'type' not in tenant:
                tenant['type'] = 'restaurant_entity'
        
        return jsonify(tenants)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取租户详情
@bp.route('/<tenant_id>', methods=['GET'])
@auth_required
def get_tenant(user_id, tenant_id):
    try:
        tenant = tenants_collection.find_one({
            '_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        tenant['_id'] = str(tenant['_id'])
        tenant['user_id'] = str(tenant['user_id'])
        tenant.pop('api_secret', None)
        
        return jsonify(tenant)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 创建租户
@bp.route('', methods=['POST'])
@auth_required
def create_tenant(user_id):
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        tenant_type = data.get('type', 'restaurant_entity')
        
        if not name:
            return jsonify({'error': 'Tenant name is required'}), 400
        
        # 创建租户
        tenant = {
            'user_id': ObjectId(user_id),
            'name': name,
            'description': description,
            'type': tenant_type,
            'api_key': generate_api_key(),
            'api_secret': generate_api_secret(),
            'status': 'active',
            'tier': 'free',
            'quota': {
                'max_skills': 10,
                'max_contexts': 5,
                'max_tools': 10,
                'max_resources': 50
            },
            'config': {},
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = tenants_collection.insert_one(tenant)
        tenant['_id'] = str(result.inserted_id)
        tenant['user_id'] = str(tenant['user_id'])
        
        return jsonify(tenant), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 更新租户
@bp.route('/<tenant_id>', methods=['PUT'])
@auth_required
def update_tenant(user_id, tenant_id):
    try:
        data = request.get_json()
        
        # 构建更新数据
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'type' in data:
            update_data['type'] = data['type']
        if 'status' in data:
            update_data['status'] = data['status']
        if 'config' in data:
            update_data['config'] = data['config']
        
        result = tenants_collection.update_one(
            {
                '_id': ObjectId(tenant_id),
                'user_id': ObjectId(user_id)
            },
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Tenant not found'}), 404
        
        tenant = tenants_collection.find_one({'_id': ObjectId(tenant_id)})
        tenant['_id'] = str(tenant['_id'])
        tenant['user_id'] = str(tenant['user_id'])
        tenant.pop('api_secret', None)
        
        return jsonify(tenant)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 删除租户
@bp.route('/<tenant_id>', methods=['DELETE'])
@auth_required
def delete_tenant(user_id, tenant_id):
    try:
        # 删除租户
        result = tenants_collection.delete_one({
            '_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # 删除租户下的所有Skill
        skills_collection.delete_many({'tenant_id': ObjectId(tenant_id)})
        
        return jsonify({'message': 'Tenant deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 重新生成API密钥
@bp.route('/<tenant_id>/regenerate-api-key', methods=['POST'])
@auth_required
def regenerate_api_key(user_id, tenant_id):
    try:
        new_api_key = generate_api_key()
        new_api_secret = generate_api_secret()
        
        result = tenants_collection.update_one(
            {
                '_id': ObjectId(tenant_id),
                'user_id': ObjectId(user_id)
            },
            {
                '$set': {
                    'api_key': new_api_key,
                    'api_secret': new_api_secret,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Tenant not found'}), 404
        
        return jsonify({
            'api_key': new_api_key,
            'api_secret': new_api_secret
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
