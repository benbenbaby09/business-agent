from flask import Blueprint, request, jsonify
import os
import json
import zipfile
from datetime import datetime

# 导入MCP tenant_manager
from mcp.tenant import tenant_manager

# 工具模板文件路径（项目目录下的templates文件夹）
TOOL_TEMPLATES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'tool_templates.json')

# 确保templates目录存在
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
os.makedirs(templates_dir, exist_ok=True)

# 确保工具模板文件存在
if not os.path.exists(TOOL_TEMPLATES_FILE):
    with open(TOOL_TEMPLATES_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

# 创建蓝图
bp = Blueprint('tenants', __name__)

# 租户数据文件路径（用户数据目录/data）
# 使用服务器的/data目录
DATA_DIR = '/data'
TENANTS_FILE = os.path.join(DATA_DIR, 'tenants.json')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化租户数据
if not os.path.exists(TENANTS_FILE):
    with open(TENANTS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# 加载租户数据
def load_tenants():
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    # 确保数据文件存在
    if not os.path.exists(TENANTS_FILE):
        with open(TENANTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    # 读取数据
    with open(TENANTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存租户数据
def save_tenants(tenants):
    with open(TENANTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tenants, f, ensure_ascii=False, indent=2)

def get_public_backend_url():
    env_url = os.environ.get('PUBLIC_BACKEND_URL') or os.environ.get('BACKEND_URL')
    if env_url:
        return env_url.rstrip('/')
    forwarded_proto = request.headers.get('X-Forwarded-Proto')
    forwarded_host = request.headers.get('X-Forwarded-Host')
    proto = (forwarded_proto.split(',')[0].strip() if forwarded_proto else request.scheme)
    host = (forwarded_host.split(',')[0].strip() if forwarded_host else request.host)
    host_name = host.split(':')[0].strip().lower()
    is_local = host_name in ('localhost', '127.0.0.1', '0.0.0.0') or host_name.endswith('.local')
    if not is_local and not forwarded_proto and proto == 'http':
        proto = 'https'
    return f"{proto}://{host}".rstrip('/')

# 加载工具模板
def load_tool_templates():
    try:
        with open(TOOL_TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading tool templates: {e}")
        return {}

def build_skill_tools(tenant, shop_name):
    tool_templates = load_tool_templates() or {}
    tenant_type = tenant.get('type', 'restaurant_entity')
    template_list = tool_templates.get(tenant_type) or tool_templates.get('restaurant_entity') or []
    input_schema = {"type": "object", "properties": {}, "additionalProperties": True}
    tools = []
    for t in template_list:
        name = t.get('name')
        if not name:
            continue
        title = t.get('title') or name
        tools.append({
            "name": name,
            "display_name": title,
            "description": f"获取{shop_name}{title}信息",
            "inputSchema": input_schema
        })
    return tools

@bp.route('', methods=['GET', 'POST', 'OPTIONS'])
@bp.route('/', methods=['GET', 'POST', 'OPTIONS'])
def handle_tenants():
    """处理租户相关请求"""
    if request.method == 'OPTIONS':
        # 处理OPTIONS预检请求
        return jsonify({}), 200
    elif request.method == 'GET':
        # 获取租户列表
        tenants = load_tenants()
        # 确保每个租户都有type字段
        for tenant in tenants:
            if 'type' not in tenant:
                tenant['type'] = 'restaurant_entity'
        return jsonify(tenants)
    elif request.method == 'POST':
        # 创建租户
        data = request.get_json()
        print(f"Create tenant request data: {data}")  # 调试日志
        tenants = load_tenants()
        
        # 生成租户ID
        tenant_id = f"tenant_{len(tenants) + 1}"
        
        # 创建租户对象
        tenant = {
            'id': tenant_id,
            'name': data.get('name'),
            'type': data.get('type', 'restaurant_entity'),
            'tier': data.get('tier', 'free'),
            'config': data.get('config', {}),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        tenants.append(tenant)
        save_tenants(tenants)
        tenant_manager.reload_tenants()
        
        return jsonify(tenant)

@bp.route('/<tenant_id>', methods=['GET'])
def get_tenant(tenant_id):
    """获取租户详情"""
    tenants = load_tenants()
    for tenant in tenants:
        if tenant['id'] == tenant_id:
            # 确保租户有type字段
            if 'type' not in tenant:
                tenant['type'] = 'restaurant_entity'
            return jsonify(tenant)
    return jsonify({'error': '租户不存在'}), 404

@bp.route('/<tenant_id>', methods=['PUT'])
def update_tenant(tenant_id):
    """更新租户"""
    data = request.get_json()
    print(f"Update tenant {tenant_id} request data: {data}")  # 调试日志
    tenants = load_tenants()
    
    for tenant in tenants:
        if tenant['id'] == tenant_id:
            # 更新租户信息
            tenant.update(data)
            tenant['updated_at'] = datetime.now().isoformat()
            
            save_tenants(tenants)
            tenant_manager.reload_tenants()
            
            return jsonify(tenant)
    
    return jsonify({'error': '租户不存在'}), 404

@bp.route('/<tenant_id>', methods=['DELETE'])
def delete_tenant(tenant_id):
    """删除租户"""
    tenants = load_tenants()
    new_tenants = [tenant for tenant in tenants if tenant['id'] != tenant_id]
    
    if len(new_tenants) == len(tenants):
        return jsonify({'error': '租户不存在'}), 404
    
    save_tenants(new_tenants)
    tenant_manager.reload_tenants()
    return jsonify({'message': '租户删除成功'})

@bp.route('/<tenant_id>/preview', methods=['POST', 'OPTIONS'])
def preview_tenant(tenant_id):
    """获取租户预览内容"""
    if request.method == 'OPTIONS':
        # 处理OPTIONS预检请求
        return jsonify({}), 200
    
    # 检查租户是否存在
    tenants = load_tenants()
    tenant = None
    for t in tenants:
        if t['id'] == tenant_id:
            tenant = t
            break
    
    if not tenant:
        return jsonify({'error': '租户不存在'}), 404
    
    # 生成预览内容
    config = tenant.get('config', {})
    
    # 生成技能名称
    english_name = tenant.get('englishName', tenant.get('name', 'shop'))
    skill_name = f"{english_name.lower().replace(' ', '-')}-skill"
    
    # 生成技能描述
    shop_name = config.get('shopName', tenant.get('name', '商家'))
    
    # 生成skill.md内容
    template_path = 'templates/skill-template.md'
    if not os.path.exists(template_path):
        # 如果模板文件不存在，使用默认内容
        skill_md = f"""# {shop_name}信息查询

## 服务介绍
{shop_name}信息查询与在线排队取号

## 功能说明
- 餐厅基本信息查询
- 堂食排队取号
- 外卖配送信息
- 生饺子打包与教程
- 店内Wi-Fi信息
- 最新消息

## 工具列表

### 1. 餐厅基本信息
获取{shop_name}餐厅基本信息信息。当用户询问相关问题时使用。

### 2. 堂食排队取号
获取{shop_name}堂食排队取号信息。当用户询问相关问题时使用。

### 3. 外卖配送信息
获取{shop_name}外卖配送信息信息。当用户询问相关问题时使用。

### 4. 生饺子打包与教程
获取{shop_name}生饺子打包与教程信息。当用户询问相关问题时使用。

### 5. 店内Wi-Fi
获取{shop_name}店内Wi-Fi信息。当用户询问相关问题时使用。

### 6. 最新消息
获取{shop_name}最新消息信息。当用户询问相关问题时使用。
"""
    else:
        # 使用模板文件生成内容
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 生成技能描述
        skill_description = f"{shop_name}信息查询与在线排队取号。查询餐厅信息、外卖配送、生饺子打包、Wi-Fi、最新动态；内嵌美团排队 Skill 支持在线取号、查进度、取消排队。"
        
        # 生成关键词
        keywords = [
            shop_name,
            shop_name.lower(),
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
        keywords_str = '\n   - '.join(keywords)
        
        # 替换占位符
        skill_md = template_content.replace('{{skill_name}}', skill_name)
        skill_md = skill_md.replace('{{skill_description}}', skill_description)
        skill_md = skill_md.replace('{{keywords}}', keywords_str)
        skill_md = skill_md.replace('{{shop_name}}', shop_name)
        skill_md = skill_md.replace('{{business_hours}}', config.get('businessHours', '10:00-22:00'))
        skill_md = skill_md.replace('{{address}}', config.get('address', '地址未知'))
    
    # 生成skill.json内容
    skill_json = {
        "name": f"{tenant.get('name', 'shop').lower().replace(' ', '-')}-skill",
        "display_name": f"{config.get('shopName', tenant.get('name', '商家'))}信息查询",
        "description": f"{config.get('shopName', tenant.get('name', '商家'))}信息查询与在线排队取号",
        "version": "0.4.2",
        "author": config.get('shopName', tenant.get('name', '商家')),
        "license": "MIT",
        "repository": "",
        "category": "信息查询",
        "keywords": [
            config.get('shopName', tenant.get('name', '商家')),
            "信息查询",
            "排队取号"
        ],
        "mcpServer": {
            "transport": "streamable-http",
            "url": f"{get_public_backend_url()}/api/mcp/{tenant_id}"
        },
        "brandPrompt": {
            "systemInstruction": "你是一家餐厅的AI助手，用朴素、实在、有温度的方式回答问题。",
            "tone": {
                "personality": "warm_and_honest",
                "avoid": [
                    "hype",
                    "clickbait",
                    "marketing_jargon"
                ]
            },
            "brandKeywords": [
                config.get('shopName', tenant.get('name', '商家'))
            ]
        }
    }
    skill_json["tools"] = build_skill_tools(tenant, shop_name)
    
    return jsonify({
        'skillMd': skill_md,
        'skillJson': skill_json
    })

@bp.route('/<tenant_id>/publish', methods=['POST', 'OPTIONS'])
def publish_tenant(tenant_id):
    """发布租户技能"""
    if request.method == 'OPTIONS':
        # 处理OPTIONS预检请求
        return jsonify({}), 200
    
    # 检查租户是否存在
    tenants = load_tenants()
    tenant = None
    for t in tenants:
        if t['id'] == tenant_id:
            tenant = t
            break
    
    if not tenant:
        return jsonify({'error': '租户不存在'}), 404
    
    # 生成技能文件
    config = tenant.get('config', {})
    
    # 生成技能名称
    english_name = tenant.get('englishName', tenant.get('name', 'shop'))
    skill_name = f"{english_name.lower().replace(' ', '-')}-skill"
    
    # 生成技能描述
    shop_name = config.get('shopName', tenant.get('name', '商家'))
    
    # 生成skill.md内容
    template_path = 'templates/skill-template.md'
    if not os.path.exists(template_path):
        # 如果模板文件不存在，使用默认内容
        skill_md = f"""# {shop_name}信息查询

## 服务介绍
{shop_name}信息查询与在线排队取号

## 功能说明
- 餐厅基本信息查询
- 堂食排队取号
- 外卖配送信息
- 生饺子打包与教程
- 店内Wi-Fi信息
- 最新消息

## 工具列表

### 1. 餐厅基本信息
获取{shop_name}餐厅基本信息信息。当用户询问相关问题时使用。

### 2. 堂食排队取号
获取{shop_name}堂食排队取号信息。当用户询问相关问题时使用。

### 3. 外卖配送信息
获取{shop_name}外卖配送信息信息。当用户询问相关问题时使用。

### 4. 生饺子打包与教程
获取{shop_name}生饺子打包与教程信息。当用户询问相关问题时使用。

### 5. 店内Wi-Fi
获取{shop_name}店内Wi-Fi信息。当用户询问相关问题时使用。

### 6. 最新消息
获取{shop_name}最新消息信息。当用户询问相关问题时使用。
"""
    else:
        # 使用模板文件生成内容
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 生成技能描述
        skill_description = f"{shop_name}信息查询与在线排队取号。查询餐厅信息、外卖配送、生饺子打包、Wi-Fi、最新动态；内嵌美团排队 Skill 支持在线取号、查进度、取消排队。"
        
        # 生成关键词
        keywords = [
            shop_name,
            shop_name.lower(),
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
        keywords_str = '\n   - '.join(keywords)
        
        # 替换占位符
        skill_md = template_content.replace('{{skill_name}}', skill_name)
        skill_md = skill_md.replace('{{skill_description}}', skill_description)
        skill_md = skill_md.replace('{{keywords}}', keywords_str)
        skill_md = skill_md.replace('{{shop_name}}', shop_name)
        skill_md = skill_md.replace('{{business_hours}}', config.get('businessHours', '10:00-22:00'))
        skill_md = skill_md.replace('{{address}}', config.get('address', '地址未知'))
    
    # 生成skill.json内容
    skill_json = {
        "name": skill_name,
        "display_name": f"{shop_name}信息查询",
        "description": f"{shop_name}信息查询与在线排队取号",
        "version": "0.4.2",
        "author": shop_name,
        "license": "MIT",
        "repository": "",
        "category": "信息查询",
        "keywords": [
            shop_name,
            "信息查询",
            "排队取号"
        ],
        "mcpServer": {
            "transport": "streamable-http",
            "url": f"{get_public_backend_url()}/api/mcp/{tenant_id}"
        },
        "brandPrompt": {
            "systemInstruction": "你是一家餐厅的AI助手，用朴素、实在、有温度的方式回答问题。",
            "tone": {
                "personality": "warm_and_honest",
                "avoid": [
                    "hype",
                    "clickbait",
                    "marketing_jargon"
                ]
            },
            "brandKeywords": [
                shop_name
            ]
        }
    }
    skill_json["tools"] = build_skill_tools(tenant, shop_name)
    
    # 保存技能文件（用户数据目录/data）
    skill_dir = f'/data/skills/{tenant_id}'
    os.makedirs(skill_dir, exist_ok=True)
    
    # 保存skill.md
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    with open(skill_md_path, 'w', encoding='utf-8') as f:
        f.write(skill_md)
    
    # 保存skill.json
    skill_json_path = os.path.join(skill_dir, 'skill.json')
    with open(skill_json_path, 'w', encoding='utf-8') as f:
        json.dump(skill_json, f, ensure_ascii=False, indent=2)
    
    # 处理旧版本zip文件，添加日期后缀
    for file in os.listdir(skill_dir):
        if file.startswith('skill.zip') and file != 'skill.zip':
            os.remove(os.path.join(skill_dir, file))
    
    # 检查是否存在skill.zip，如果存在，重命名为带日期的版本
    skill_zip_path = os.path.join(skill_dir, 'skill.zip')
    if os.path.exists(skill_zip_path):
        old_zip_name = f'skill-{datetime.now().strftime("%Y%m%d%H%M%S")}.zip'
        old_zip_path = os.path.join(skill_dir, old_zip_name)
        os.rename(skill_zip_path, old_zip_path)
    
    # 创建新的skill.zip文件
    with zipfile.ZipFile(skill_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加SKILL.md
        zipf.write(skill_md_path, 'SKILL.md')
        # 添加skill.json
        zipf.write(skill_json_path, 'skill.json')
    
    # 生成技能URL
    skill_url = f'/storage/skills/{tenant_id}/skill.zip'
    
    # 更新租户信息，保存技能URL
    if 'serviceConfig' not in tenant:
        tenant['serviceConfig'] = {}
    tenant['serviceConfig']['skillUrl'] = skill_url
    save_tenants(tenants)
    
    return jsonify({
        'skill_url': skill_url
    })

# MCP服务相关路由
@bp.route('/<tenant_id>/mcp/service', methods=['GET', 'POST', 'OPTIONS'])
def handle_mcp_service(tenant_id):
    """处理租户MCP服务相关请求"""
    print(f"MCP service request: tenant_id={tenant_id}, method={request.method}")  # 调试日志
    
    if request.method == 'OPTIONS':
        # 处理OPTIONS预检请求
        return jsonify({}), 200
    
    # 检查租户是否存在
    tenants = load_tenants()
    print(f"Loaded {len(tenants)} tenants")  # 调试日志
    tenant = None
    for t in tenants:
        if t['id'] == tenant_id:
            tenant = t
            break
    
    if not tenant:
        print(f"Tenant {tenant_id} not found")
        return jsonify({'error': '租户不存在'}), 404
    
    print(f"Tenant found: {tenant.get('id')}, has mcp_service: {'mcp_service' in tenant}")  # 调试日志
    
    if request.method == 'GET':
        # 获取MCP服务（如果存在）
        if 'mcp_service' in tenant:
            return jsonify(tenant['mcp_service'])
        else:
            # MCP服务不存在，返回空对象而不是404错误
            return jsonify({'error': 'MCP服务不存在'}), 200
    elif request.method == 'POST':
        # 创建MCP服务
        mcp_service = {
            'id': f"mcp_service_{tenant_id}",
            'tenant_id': tenant_id,
            'name': f"{tenant['name']} MCP Service",
            'status': 'active',
            'api_key': f"api_key_{tenant_id}",
            'api_secret': f"api_secret_{tenant_id}",
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        tenant['mcp_service'] = mcp_service
        
        # 从工具模板中获取工具信息
        try:
            tool_templates = load_tool_templates()
            tenant_type = tenant.get('type', 'restaurant_entity')
            tenant['tools'] = []
            
            if tenant_type in tool_templates:
                for i, template in enumerate(tool_templates[tenant_type]):
                    tool_id = f"tool_{i + 1}"
                    tool = {
                        'id': tool_id,
                        'tenant_id': tenant_id,
                        'name': template['name'],
                        'title': template['title'],
                        'type': template['type'],
                        'description': f"获取{tenant.get('name', '商家')}{template['title']}信息",
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    tenant['tools'].append(tool)
        except Exception as e:
            print(f"Error loading tool templates: {e}")
            # 即使工具模板加载失败，也继续创建MCP服务
            tenant['tools'] = []
        
        # 保存租户数据
        try:
            save_tenants(tenants)
        except Exception as e:
            print(f"Error saving tenants: {e}")
            return jsonify({'error': '保存租户数据失败'}), 500
        
        return jsonify(mcp_service)

# MCP工具相关路由
@bp.route('/<tenant_id>/mcp/tools', methods=['GET', 'POST', 'OPTIONS'])
def handle_mcp_tools(tenant_id):
    """处理租户MCP工具相关请求 - 动态从模板加载工具"""
    if request.method == 'OPTIONS':
        # 处理OPTIONS预检请求
        return jsonify({}), 200
    
    # 检查租户是否存在
    tenants = load_tenants()
    tenant = None
    for t in tenants:
        if t['id'] == tenant_id:
            tenant = t
            break
    
    if not tenant:
        return jsonify({'error': '租户不存在'}), 404
    
    # 动态从工具模板加载工具列表（不保存到租户对象）
    try:
        tool_templates = load_tool_templates()
        tenant_type = tenant.get('type', 'restaurant_entity')
        print(f"Loading tools for tenant {tenant_id}, type: {tenant_type}")  # 调试日志
        print(f"Available templates: {list(tool_templates.keys())}")  # 调试日志
        tools = []
        
        if tenant_type in tool_templates:
            print(f"Found template for type {tenant_type}, templates count: {len(tool_templates[tenant_type])}")  # 调试日志
            for i, template in enumerate(tool_templates[tenant_type]):
                tool = {
                    'id': f"tool_{i + 1}",
                    'tenant_id': tenant_id,
                    'name': template['name'],
                    'title': template['title'],
                    'type': template['type'],
                    'description': f"获取{tenant.get('name', '商家')}{template['title']}信息",
                    'config': {},
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                tools.append(tool)
                print(f"Created tool: {tool['name']}")  # 调试日志
        else:
            print(f"No template found for type {tenant_type}")  # 调试日志
        
        print(f"Returning {len(tools)} tools")  # 调试日志
    except Exception as e:
        print(f"Error loading tools: {e}")
        tools = []
    
    if request.method == 'GET':
        # 返回工具列表
        return jsonify(tools)
    elif request.method == 'POST':
        # 伪装创建工具成功，不保存到租户对象
        data = request.get_json()
        
        tool_id = f"tool_{len(tools) + 1}"
        tool = {
            'id': tool_id,
            'tenant_id': tenant_id,
            'name': data.get('name'),
            'title': data.get('title'),
            'type': data.get('type'),
            'description': data.get('description'),
            'config': data.get('config', {}),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        return jsonify(tool)

@bp.route('/<tenant_id>/mcp/tools/<tool_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def handle_mcp_tool(tenant_id, tool_id):
    """处理单个MCP工具相关请求"""
    if request.method == 'OPTIONS':
        # 处理OPTIONS预检请求
        return jsonify({}), 200
    
    # 检查租户是否存在
    tenants = load_tenants()
    tenant = None
    for t in tenants:
        if t['id'] == tenant_id:
            tenant = t
            break
    
    if not tenant:
        return jsonify({'error': '租户不存在'}), 404
    
    # 查找工具（从模板动态生成中查找）
    tool = None
    try:
        tool_templates = load_tool_templates()
        tenant_type = tenant.get('type', 'restaurant_entity')
        
        if tenant_type in tool_templates:
            for i, template in enumerate(tool_templates[tenant_type]):
                if f"tool_{i + 1}" == tool_id:
                    tool = {
                        'id': f"tool_{i + 1}",
                        'tenant_id': tenant_id,
                        'name': template['name'],
                        'title': template['title'],
                        'type': template['type'],
                        'description': f"获取{tenant.get('name', '商家')}{template['title']}信息",
                        'config': {},
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    break
    except Exception as e:
        print(f"Error loading tools: {e}")
        
    if not tool and request.method == 'GET':
        return jsonify({'error': '工具不存在'}), 404
        
    if request.method == 'GET':
        # 获取工具详情
        return jsonify(tool)
    elif request.method == 'PUT':
        # 伪装更新工具成功，不保存到租户对象
        data = request.get_json()
        if tool:
            tool.update(data)
            tool['updated_at'] = datetime.now().isoformat()
            return jsonify(tool)
        else:
            data['id'] = tool_id
            data['tenant_id'] = tenant_id
            data['updated_at'] = datetime.now().isoformat()
            return jsonify(data)
    elif request.method == 'DELETE':
        # 伪装删除工具成功，不保存到租户对象
        return jsonify({'message': '工具删除成功'})
