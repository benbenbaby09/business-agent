from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime

# 创建蓝图
bp = Blueprint('publish', __name__)

# 技能数据文件路径
SKILLS_FILE = '/data/skills.json'

# 加载技能数据
def load_skills():
    if not os.path.exists(SKILLS_FILE):
        return []
    with open(SKILLS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存技能数据
def save_skills(skills):
    os.makedirs('/data', exist_ok=True)
    with open(SKILLS_FILE, 'w', encoding='utf-8') as f:
        json.dump(skills, f, ensure_ascii=False, indent=2)

@bp.route('/publish/<skill_id>', methods=['POST'])
def publish_skill(skill_id):
    """发布技能"""
    skills = load_skills()
    
    for skill in skills:
        if skill['id'] == skill_id:
            # 更新技能状态为已发布
            skill['status'] = 'published'
            skill['published_at'] = datetime.now().isoformat()
            skill['updated_at'] = datetime.now().isoformat()
            save_skills(skills)
            return jsonify(skill)
    
    return jsonify({'error': '技能不存在'}), 404

@bp.route('/unpublish/<skill_id>', methods=['POST'])
def unpublish_skill(skill_id):
    """取消发布技能"""
    skills = load_skills()
    
    for skill in skills:
        if skill['id'] == skill_id:
            # 更新技能状态为未发布
            skill['status'] = 'active'
            if 'published_at' in skill:
                del skill['published_at']
            skill['updated_at'] = datetime.now().isoformat()
            save_skills(skills)
            return jsonify(skill)
    
    return jsonify({'error': '技能不存在'}), 404
