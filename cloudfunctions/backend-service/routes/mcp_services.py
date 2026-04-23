from flask import Blueprint, request, jsonify
import os
import json

# 创建蓝图
bp = Blueprint('mcp_services', __name__)

# 服务数据文件路径
SERVICES_FILE = 'data/mcp_services.json'

# 确保数据目录存在
os.makedirs('data', exist_ok=True)

# 初始化服务数据
if not os.path.exists(SERVICES_FILE):
    with open(SERVICES_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# 加载服务数据
def load_services():
    with open(SERVICES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存服务数据
def save_services(services):
    with open(SERVICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(services, f, ensure_ascii=False, indent=2)

@bp.route('/mcp/services', methods=['GET'])
def list_services():
    """获取服务列表"""
    services = load_services()
    return jsonify(services)

@bp.route('/mcp/services', methods=['POST'])
def create_service():
    """创建服务"""
    data = request.get_json()
    services = load_services()
    
    # 生成服务ID
    service_id = f"service_{len(services) + 1}"
    
    # 创建服务对象
    service = {
        'id': service_id,
        'name': data.get('name'),
        'type': data.get('type'),
        'description': data.get('description'),
        'config': data.get('config', {}),
        'status': 'active',
        'created_at': data.get('created_at', '2026-04-23T00:00:00Z')
    }
    
    services.append(service)
    save_services(services)
    
    return jsonify(service)

@bp.route('/mcp/services/<service_id>', methods=['GET'])
def get_service(service_id):
    """获取服务详情"""
    services = load_services()
    for service in services:
        if service['id'] == service_id:
            return jsonify(service)
    return jsonify({'error': '服务不存在'}), 404

@bp.route('/mcp/services/<service_id>', methods=['PUT'])
def update_service(service_id):
    """更新服务"""
    data = request.get_json()
    services = load_services()
    
    for service in services:
        if service['id'] == service_id:
            # 更新服务信息
            service.update(data)
            save_services(services)
            return jsonify(service)
    
    return jsonify({'error': '服务不存在'}), 404

@bp.route('/mcp/services/<service_id>', methods=['DELETE'])
def delete_service(service_id):
    """删除服务"""
    services = load_services()
    new_services = [service for service in services if service['id'] != service_id]
    
    if len(new_services) == len(services):
        return jsonify({'error': '服务不存在'}), 404
    
    save_services(new_services)
    return jsonify({'message': '服务删除成功'})
