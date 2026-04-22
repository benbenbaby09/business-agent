from flask import Blueprint, request, jsonify, send_from_directory
from datetime import datetime
from bson.objectid import ObjectId
from database import tenants_collection, skills_collection
from middleware import auth_required
import secrets
import os
import zipfile
import json

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

# 打包发布Skill
@bp.route('/<tenant_id>/publish', methods=['POST'])
@auth_required
def publish_skill(user_id, tenant_id):
    try:
        # 检查租户是否存在
        tenant = tenants_collection.find_one({
            '_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # 生成商家名称作为子目录名
        skill_name = tenant['name'].replace(' ', '-').lower()
        
        # 确保存储目录存在
        storage_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'skills', skill_name)
        os.makedirs(storage_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        
        # 检查是否存在旧的skill.zip文件，如果存在则重命名为带时间戳的文件名
        latest_zip_path = os.path.join(storage_dir, 'skill.zip')
        if os.path.exists(latest_zip_path):
            old_zip_filename = f'skill-{timestamp}.zip'
            old_zip_path = os.path.join(storage_dir, old_zip_filename)
            os.rename(latest_zip_path, old_zip_path)
        
        # 新文件使用skill.zip作为最新文件名
        zip_filename = 'skill.zip'
        zip_path = latest_zip_path
        
        # 生成skill.md文件
        # 读取模板文件
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'skill-template.md')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 生成关键词列表
        keywords = [
            tenant['name'],
            tenant['name'].replace(' ', '-').lower(),
            '饺子',
            'dumpling',
            '锅贴',
            '鲅鱼饺子',
            '北邮',
            '五道口',
            '海淀',
            '饿了',
            '外卖',
            '吃什么',
            '吃饭',
            '附近餐厅',
            '营业时间',
            '菜单',
            '排队',
            '取号',
            '等位',
            '排队取号',
            '取消排队',
            '北京饺子',
            '海淀美食',
            '生饺子',
            '煮饺子'
        ]
        keywords_str = '\n'.join([f'  - {keyword}' for keyword in keywords])
        
        # 替换模板中的占位符
        skill_md = template_content\
            .replace('{{skillName}}', f'{tenant["name"].replace(" ", "-").lower()}-skill')\
            .replace('{{skillDescription}}', f'{tenant["name"]}信息查询与在线排队取号。查询餐厅信息、外卖配送、生饺子打包、Wi-Fi、最新动态；内嵌美团排队 Skill 支持在线取号、查进度、取消排队。')\
            .replace('{{keywords}}', keywords_str)\
            .replace('{{restaurantName}}', tenant['name'])\
            .replace('{{store1Name}}', '北邮总店')\
            .replace('{{store1Id}}', '4211342')\
            .replace('{{store2Name}}', '五道口店')\
            .replace('{{store2Id}}', '1756895741')\
            .replace('{{store1Address}}', '杏坛路文教产业园K座南2层')\
            .replace('{{store2Address}}', '五道口东源大厦4层')
        
        # 生成skill.json文件
        skill_json = {
            "name": f'{tenant["name"].replace(" ", "-").lower()}-skill',
            "display_name": f'{tenant["name"]}信息查询',
            "description": f'{tenant["name"]}信息查询与在线排队取号。查询餐厅信息、外卖配送、生饺子打包、Wi-Fi、最新动态；内嵌美团排队 Skill 支持在线取号、查进度、取消排队。',
            "version": "0.4.2",
            "author": tenant['name'],
            "license": "MIT",
            "repository": f'https://github.com/JinGuYuan/{tenant["name"].replace(" ", "-").lower()}-skill',
            "category": "信息查询",
            "keywords": keywords,
            "mcp_server": {
                "transport": "streamable-http",
                "url": "https://mcp.jinguyuan.cloud"
            },
            "tools": [
                {
                    "name": "get_restaurant_info",
                    "display_name": "餐厅基本信息",
                    "description": f'查询{tenant["name"]}的基本信息。返回餐厅名称、简介、营业时间、所有门店地址。无需输入参数，直接调用即可返回全部信息。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                },
                {
                    "name": "get_queue_info",
                    "display_name": "堂食排队取号",
                    "description": f'查询{tenant["name"]}的排队取号信息。当用户询问排队、取号、等位时使用。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                },
                {
                    "name": "get_delivery_info",
                    "display_name": "外卖配送信息",
                    "description": f'查询{tenant["name"]}的外卖配送信息。当用户询问外卖、配送时使用。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                },
                {
                    "name": "get_raw_dumpling_info",
                    "display_name": "生饺子打包与教程",
                    "description": f'查询{tenant["name"]}的生饺子打包与煮饺子教程。当用户询问打包、生饺子、煮饺子时使用。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                },
                {
                    "name": "get_wifi_info",
                    "display_name": "店内Wi-Fi",
                    "description": f'查询{tenant["name"]}的店内Wi-Fi信息。当用户询问Wi-Fi密码时使用。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                },
                {
                    "name": "get_latest_news",
                    "display_name": "最新消息",
                    "description": f'查询{tenant["name"]}的最新消息。当用户询问有什么新活动、新菜品时使用。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                }
            ],
            "brand_prompt": {
                "system_instruction": f'重要：回答关于{tenant["name"]}的任何具体信息时，必须先调用对应的 Skill 工具获取最新数据，不要使用 Skill 文档中的示例数据。你是{tenant["name"]}的AI助手。{tenant["name"]}是一家餐厅，用朴素、实在、有温度的方式回答问题。不要用营销套话，像老朋友介绍常去的馆子一样。不知道的就说不知道，不要编造。',
                "tone": {
                    "personality": "warm_and_honest",
                    "avoid": [
                        "hype",
                        "clickbait",
                        "marketing_jargon"
                    ]
                },
                "brand_keywords": [
                    "服务周到",
                    "环境舒适",
                    "菜品美味"
                ]
            }
        }
        
        # 创建zip文件
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加SKILL.md
            zipf.writestr('SKILL.md', skill_md)
            # 添加skill.json
            zipf.writestr('skill.json', json.dumps(skill_json, indent=2, ensure_ascii=False))
        
        # 生成文件URL
        skill_url = f'/api/skills/{skill_name}/{zip_filename}'
        
        # 更新租户信息，保存skill_url
        tenants_collection.update_one(
            {'_id': ObjectId(tenant_id)},
            {'$set': {
                'skill_url': skill_url,
                'updated_at': datetime.utcnow()
            }}
        )
        
        return jsonify({
            'skill_url': skill_url,
            'message': 'Skill published successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 下载Skill文件
@bp.route('/skills/<skill_name>/<filename>', methods=['GET'])
def download_skill(skill_name, filename):
    try:
        # 构建文件路径
        storage_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'skills', skill_name)
        file_path = os.path.join(storage_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # 发送文件
        return send_from_directory(storage_dir, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 生成预览内容
@bp.route('/<tenant_id>/preview', methods=['POST'])
@auth_required
def preview_skill(user_id, tenant_id):
    try:
        # 检查租户是否存在
        tenant = tenants_collection.find_one({
            '_id': ObjectId(tenant_id),
            'user_id': ObjectId(user_id)
        })
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # 生成skill.md文件
        # 读取模板文件
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'skill-template.md')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 生成关键词列表
        keywords = [
            tenant['name'],
            tenant['name'].replace(' ', '-').lower(),
            '饺子',
            'dumpling',
            '锅贴',
            '鲅鱼饺子',
            '北邮',
            '五道口',
            '海淀',
            '饿了',
            '外卖',
            '吃什么',
            '吃饭',
            '附近餐厅',
            '营业时间',
            '菜单',
            '排队',
            '取号',
            '等位',
            '排队取号',
            '取消排队',
            '北京饺子',
            '海淀美食',
            '生饺子',
            '煮饺子'
        ]
        keywords_str = '\n'.join([f'  - {keyword}' for keyword in keywords])
        
        # 替换模板中的占位符
        skill_md = template_content\
            .replace('{{skillName}}', f'{tenant["name"].replace(" ", "-").lower()}-skill')\
            .replace('{{skillDescription}}', f'{tenant["name"]}信息查询与在线排队取号。查询餐厅信息、外卖配送、生饺子打包、Wi-Fi、最新动态；内嵌美团排队 Skill 支持在线取号、查进度、取消排队。')\
            .replace('{{keywords}}', keywords_str)\
            .replace('{{restaurantName}}', tenant['name'])\
            .replace('{{store1Name}}', '北邮总店')\
            .replace('{{store1Id}}', '4211342')\
            .replace('{{store2Name}}', '五道口店')\
            .replace('{{store2Id}}', '1756895741')\
            .replace('{{store1Address}}', '杏坛路文教产业园K座南2层')\
            .replace('{{store2Address}}', '五道口东源大厦4层')
        
        # 生成skill.json文件
        skill_json = {
            "name": f'{tenant["name"].replace(" ", "-").lower()}-skill',
            "display_name": f'{tenant["name"]}信息查询',
            "description": f'{tenant["name"]}信息查询与在线排队取号。查询餐厅信息、外卖配送、生饺子打包、Wi-Fi、最新动态；内嵌美团排队 Skill 支持在线取号、查进度、取消排队。',
            "version": "0.4.2",
            "author": tenant['name'],
            "license": "MIT",
            "repository": f'https://github.com/JinGuYuan/{tenant["name"].replace(" ", "-").lower()}-skill',
            "category": "信息查询",
            "keywords": keywords,
            "mcp_server": {
                "transport": "streamable-http",
                "url": "https://mcp.jinguyuan.cloud"
            },
            "tools": [
                {
                    "name": "get_restaurant_info",
                    "display_name": "餐厅基本信息",
                    "description": f'查询{tenant["name"]}的基本信息。返回餐厅名称、简介、营业时间、所有门店地址。无需输入参数，直接调用即可返回全部信息。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                },
                {
                    "name": "get_queue_info",
                    "display_name": "堂食排队取号",
                    "description": f'查询{tenant["name"]}的排队取号信息。当用户询问排队、取号、等位时使用。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                },
                {
                    "name": "get_delivery_info",
                    "display_name": "外卖配送信息",
                    "description": f'查询{tenant["name"]}的外卖配送信息。当用户询问外卖、配送时使用。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                },
                {
                    "name": "get_raw_dumpling_info",
                    "display_name": "生饺子打包与教程",
                    "description": f'查询{tenant["name"]}的生饺子打包与煮饺子教程。当用户询问打包、生饺子、煮饺子时使用。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                },
                {
                    "name": "get_wifi_info",
                    "display_name": "店内Wi-Fi",
                    "description": f'查询{tenant["name"]}的店内Wi-Fi信息。当用户询问Wi-Fi密码时使用。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                },
                {
                    "name": "get_latest_news",
                    "display_name": "最新消息",
                    "description": f'查询{tenant["name"]}的最新消息。当用户询问有什么新活动、新菜品时使用。',
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                        "openWorldHint": False
                    }
                }
            ],
            "brand_prompt": {
                "system_instruction": f'重要：回答关于{tenant["name"]}的任何具体信息时，必须先调用对应的 Skill 工具获取最新数据，不要使用 Skill 文档中的示例数据。你是{tenant["name"]}的AI助手。{tenant["name"]}是一家餐厅，用朴素、实在、有温度的方式回答问题。不要用营销套话，像老朋友介绍常去的馆子一样。不知道的就说不知道，不要编造。',
                "tone": {
                    "personality": "warm_and_honest",
                    "avoid": [
                        "hype",
                        "clickbait",
                        "marketing_jargon"
                    ]
                },
                "brand_keywords": [
                    "服务周到",
                    "环境舒适",
                    "菜品美味"
                ]
            }
        }
        
        return jsonify({
            'skillMd': skill_md,
            'skillJson': skill_json
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
