from flask import Blueprint, request, jsonify
from datetime import datetime
from bson.objectid import ObjectId
from database import skills_collection
from middleware import auth_required

bp = Blueprint('skills', __name__)

# 获取Skill列表
@bp.route('', methods=['GET'])
@auth_required
def get_skills(user_id):
    # 分页参数
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit
    
    # 筛选参数
    status = request.args.get('status')
    type = request.args.get('type')
    tenant_id = request.args.get('tenant_id')
    
    # 构建查询
    query = {'user_id': ObjectId(user_id)}
    if tenant_id:
        query['tenant_id'] = ObjectId(tenant_id)
    if status:
        query['status'] = status
    if type:
        query['type'] = type
    
    # 查询数据
    total = skills_collection.count_documents(query)
    skills = list(skills_collection.find(query).skip(skip).limit(limit))
    
    # 格式化数据
    for skill in skills:
        skill['_id'] = str(skill['_id'])
        skill['user_id'] = str(skill['user_id'])
        if 'tenant_id' in skill:
            skill['tenant_id'] = str(skill['tenant_id'])
    
    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'skills': skills
    })

# 获取Skill详情
@bp.route('/<skill_id>', methods=['GET'])
@auth_required
def get_skill(user_id, skill_id):
    try:
        skill = skills_collection.find_one({
            '_id': ObjectId(skill_id),
            'user_id': ObjectId(user_id)
        })
        
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        skill['_id'] = str(skill['_id'])
        skill['user_id'] = str(skill['user_id'])
        
        return jsonify(skill)
    except Exception as e:
        return jsonify({'error': 'Invalid skill ID'}), 400

# 创建Skill
@bp.route('', methods=['POST'])
@auth_required
def create_skill(user_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    type = data.get('type')
    tenant_id = data.get('tenant_id')
    
    if not name or not type:
        return jsonify({'error': 'Name and type are required'}), 400
    
    if not tenant_id:
        return jsonify({'error': 'Tenant ID is required'}), 400
    
    # 创建Skill
    skill = {
        'user_id': ObjectId(user_id),
        'tenant_id': ObjectId(tenant_id),
        'name': name,
        'description': description or '',
        'type': type,
        'status': 'active',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = skills_collection.insert_one(skill)
    skill['_id'] = str(result.inserted_id)
    skill['user_id'] = str(skill['user_id'])
    skill['tenant_id'] = str(skill['tenant_id'])
    
    return jsonify(skill), 201

# 更新Skill
@bp.route('/<skill_id>', methods=['PUT'])
@auth_required
def update_skill(user_id, skill_id):
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
        if 'version' in data:
            update_data['version'] = data['version']
        if 'config' in data:
            update_data['config'] = data['config']
        
        # 更新Skill
        result = skills_collection.update_one(
            {
                '_id': ObjectId(skill_id),
                'user_id': ObjectId(user_id)
            },
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Skill not found'}), 404
        
        # 获取更新后的Skill
        skill = skills_collection.find_one({'_id': ObjectId(skill_id)})
        skill['_id'] = str(skill['_id'])
        skill['user_id'] = str(skill['user_id'])
        if 'tenant_id' in skill:
            skill['tenant_id'] = str(skill['tenant_id'])
        
        return jsonify(skill)
    except Exception as e:
        return jsonify({'error': 'Invalid skill ID'}), 400

# 删除Skill
@bp.route('/<skill_id>', methods=['DELETE'])
@auth_required
def delete_skill(user_id, skill_id):
    try:
        result = skills_collection.delete_one({
            '_id': ObjectId(skill_id),
            'user_id': ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Skill not found'}), 404
        
        return jsonify({'message': 'Skill deleted successfully'})
    except Exception as e:
        return jsonify({'error': 'Invalid skill ID'}), 400
