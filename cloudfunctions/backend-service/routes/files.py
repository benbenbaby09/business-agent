from flask import Blueprint, request, jsonify, send_file
import os
import uuid
from datetime import datetime

# 创建蓝图
bp = Blueprint('files', __name__)

# 文件存储目录
STORAGE_DIR = 'storage/skills'

# 确保存储目录存在
os.makedirs(STORAGE_DIR, exist_ok=True)

@bp.route('/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名不能为空'}), 400
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}{file_ext}"
    
    # 保存文件
    file_path = os.path.join(STORAGE_DIR, file_name)
    file.save(file_path)
    
    return jsonify({
        'file_id': file_id,
        'file_name': file.filename,
        'file_path': file_path,
        'size': os.path.getsize(file_path),
        'upload_time': datetime.now().isoformat()
    })

@bp.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """下载文件"""
    # 查找文件
    for filename in os.listdir(STORAGE_DIR):
        if filename.startswith(file_id):
            file_path = os.path.join(STORAGE_DIR, filename)
            return send_file(file_path, as_attachment=True)
    
    return jsonify({'error': '文件不存在'}), 404

@bp.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """删除文件"""
    # 查找并删除文件
    for filename in os.listdir(STORAGE_DIR):
        if filename.startswith(file_id):
            file_path = os.path.join(STORAGE_DIR, filename)
            os.remove(file_path)
            return jsonify({'message': '文件删除成功'})
    
    return jsonify({'error': '文件不存在'}), 404
