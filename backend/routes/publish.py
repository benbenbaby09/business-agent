from flask import Blueprint, request, jsonify
from datetime import datetime
from bson.objectid import ObjectId
from database import skills_collection, versions_collection
from middleware import auth_required

bp = Blueprint('publish', __name__)

# 发布Skill
@bp.route('/<skill_id>/publish', methods=['POST'])
@auth_required
def publish_skill(user_id, skill_id):
    try:
        # 检查Skill是否存在且属于当前用户
        skill = skills_collection.find_one({
            '_id': ObjectId(skill_id),
            'user_id': ObjectId(user_id)
        })
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        # 更新Skill状态
        update_data = {
            'status': 'active',
            'updated_at': datetime.utcnow()
        }
        
        result = skills_collection.update_one(
            {'_id': ObjectId(skill_id)},
            {'$set': update_data}
        )
        
        # 记录版本历史
        version = {
            'skill_id': ObjectId(skill_id),
            'version': new_version,
            'changes': request.get_json().get('changes', ''),
            'created_at': datetime.utcnow(),
            'created_by': ObjectId(user_id)
        }
        
        versions_collection.insert_one(version)
        
        # 获取更新后的Skill
        updated_skill = skills_collection.find_one({'_id': ObjectId(skill_id)})
        updated_skill['_id'] = str(updated_skill['_id'])
        updated_skill['user_id'] = str(updated_skill['user_id'])
        
        return jsonify(updated_skill)
    except Exception as e:
        return jsonify({'error': 'Invalid skill ID'}), 400

# 获取Skill版本历史
@bp.route('/<skill_id>/versions', methods=['GET'])
@auth_required
def get_versions(user_id, skill_id):
    try:
        # 检查Skill是否存在且属于当前用户
        skill = skills_collection.find_one({
            '_id': ObjectId(skill_id),
            'user_id': ObjectId(user_id)
        })
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        # 查询版本历史
        versions = list(versions_collection.find(
            {'skill_id': ObjectId(skill_id)}
        ).sort('created_at', -1))
        
        # 格式化数据
        for version in versions:
            version['_id'] = str(version['_id'])
            version['skill_id'] = str(version['skill_id'])
            version['created_by'] = str(version['created_by'])
        
        return jsonify(versions)
    except Exception as e:
        return jsonify({'error': 'Invalid skill ID'}), 400
