from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime

# 创建蓝图
bp = Blueprint('skills', __name__)

# 技能数据文件路径
SKILLS_FILE = '/data/skills.json'

# 确保数据目录存在
os.makedirs('/data', exist_ok=True)

# 初始化技能数据
if not os.path.exists(SKILLS_FILE):
    with open(SKILLS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# 加载技能数据
def load_skills():
    with open(SKILLS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存技能数据
def save_skills(skills):
    with open(SKILLS_FILE, 'w', encoding='utf-8') as f:
        json.dump(skills, f, ensure_ascii=False, indent=2)

@bp.route('/list', methods=['GET'])
def list_skills():
    """获取技能列表"""
    skills = load_skills()
    return jsonify(skills)

@bp.route('/create', methods=['POST'])
def create_skill():
    """创建技能"""
    data = request.get_json()
    skills = load_skills()
    
    # 生成技能ID
    skill_id = f"skill_{len(skills) + 1}"
    
    # 创建技能对象
    skill = {
        'id': skill_id,
        'name': data.get('name'),
        'type': data.get('type'),
        'description': data.get('description'),
        'version': data.get('version', '1.0.0'),
        'status': data.get('status', 'active'),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    skills.append(skill)
    save_skills(skills)
    
    return jsonify(skill)

@bp.route('/<skill_id>', methods=['GET'])
def get_skill(skill_id):
    """获取技能详情"""
    skills = load_skills()
    for skill in skills:
        if skill['id'] == skill_id:
            return jsonify(skill)
    return jsonify({'error': '技能不存在'}), 404

@bp.route('/<skill_id>', methods=['PUT'])
def update_skill(skill_id):
    """更新技能"""
    data = request.get_json()
    skills = load_skills()
    
    for skill in skills:
        if skill['id'] == skill_id:
            # 更新技能信息
            skill.update(data)
            skill['updated_at'] = datetime.now().isoformat()
            save_skills(skills)
            return jsonify(skill)
    
    return jsonify({'error': '技能不存在'}), 404

@bp.route('/<skill_id>', methods=['DELETE'])
def delete_skill(skill_id):
    """删除技能"""
    skills = load_skills()
    new_skills = [skill for skill in skills if skill['id'] != skill_id]
    
    if len(new_skills) == len(skills):
        return jsonify({'error': '技能不存在'}), 404
    
    save_skills(new_skills)
    return jsonify({'message': '技能删除成功'})
