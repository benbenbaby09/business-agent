from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from bson.objectid import ObjectId
import os
import tempfile
from database import skill_files_collection, skills_collection
from middleware import auth_required

bp = Blueprint('files', __name__)

# 上传Skill文件
@bp.route('/<skill_id>/files', methods=['POST'])
def upload_file(skill_id):
    try:
        # 检查Skill是否存在
        skill = skills_collection.find_one({'_id': ObjectId(skill_id)})
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # 生成文件路径
        filename = file.filename
        file_path = f"skills/{skill_id}/files/{filename}"
        
        # 这里应该实现文件上传到对象存储的逻辑
        # 暂时保存到本地临时目录
        temp_dir = tempfile.gettempdir()
        local_file_path = os.path.join(temp_dir, filename)
        file.save(local_file_path)
        
        # 保存文件信息到数据库
        skill_file = {
            'skill_id': ObjectId(skill_id),
            'filename': filename,
            'file_path': file_path,
            'file_type': file.content_type,
            'version': skill.get('version', '1.0.0'),
            'created_at': datetime.utcnow()
        }
        
        result = skill_files_collection.insert_one(skill_file)
        skill_file['_id'] = str(result.inserted_id)
        skill_file['skill_id'] = str(skill_file['skill_id'])
        
        return jsonify(skill_file), 201
    except Exception as e:
        return jsonify({'error': 'Invalid skill ID'}), 400

# 获取Skill文件列表
@bp.route('/<skill_id>/files', methods=['GET'])
@auth_required
def get_files(user_id, skill_id):
    try:
        # 检查Skill是否存在且属于当前用户
        skill = skills_collection.find_one({
            '_id': ObjectId(skill_id),
            'user_id': ObjectId(user_id)
        })
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        # 查询文件列表
        files = list(skill_files_collection.find({'skill_id': ObjectId(skill_id)}))
        
        # 格式化数据
        for file in files:
            file['_id'] = str(file['_id'])
            file['skill_id'] = str(file['skill_id'])
        
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': 'Invalid skill ID'}), 400

# 下载Skill文件
@bp.route('/<skill_id>/files/<file_id>', methods=['GET'])
@auth_required
def download_file(user_id, skill_id, file_id):
    try:
        # 检查Skill是否存在且属于当前用户
        skill = skills_collection.find_one({
            '_id': ObjectId(skill_id),
            'user_id': ObjectId(user_id)
        })
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        # 查找文件
        skill_file = skill_files_collection.find_one({
            '_id': ObjectId(file_id),
            'skill_id': ObjectId(skill_id)
        })
        if not skill_file:
            return jsonify({'error': 'File not found'}), 404
        
        # 这里应该实现从对象存储下载文件的逻辑
        # 暂时返回本地临时文件
        temp_dir = tempfile.gettempdir()
        local_file_path = os.path.join(temp_dir, skill_file['filename'])
        
        if not os.path.exists(local_file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(local_file_path, as_attachment=True, download_name=skill_file['filename'])
    except Exception as e:
        return jsonify({'error': 'Invalid ID'}), 400

# 删除Skill文件
@bp.route('/<skill_id>/files/<file_id>', methods=['DELETE'])
@auth_required
def delete_file(user_id, skill_id, file_id):
    try:
        # 检查Skill是否存在且属于当前用户
        skill = skills_collection.find_one({
            '_id': ObjectId(skill_id),
            'user_id': ObjectId(user_id)
        })
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        # 删除文件
        result = skill_files_collection.delete_one({
            '_id': ObjectId(file_id),
            'skill_id': ObjectId(skill_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'File not found'}), 404
        
        # 这里应该实现从对象存储删除文件的逻辑
        
        return jsonify({'message': 'File deleted successfully'})
    except Exception as e:
        return jsonify({'error': 'Invalid ID'}), 400
