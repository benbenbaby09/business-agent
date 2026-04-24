from flask import Blueprint, request, jsonify, Response
import os
import json
from mcp.server import mcp_server
from mcp.tenant import tenant_manager

# 创建蓝图
bp = Blueprint('mcp', __name__)

TOOL_TEMPLATES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'tool_templates.json')

def load_tool_templates():
    try:
        with open(TOOL_TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f) or {}
    except Exception:
        return {}

def get_tool_catalog():
    base_schema = {"type": "object", "properties": {}, "additionalProperties": True}
    return {
        "get_restaurant_info": {"description": "获取餐厅的基本信息，包括名称、地址、营业时间等", "inputSchema": base_schema},
        "get_queue_info": {"description": "获取餐厅的排队取号信息", "inputSchema": base_schema},
        "get_delivery_info": {"description": "获取餐厅的外卖配送信息", "inputSchema": base_schema},
        "get_raw_dumpling_info": {"description": "获取生饺子打包信息和煮饺子教程", "inputSchema": base_schema},
        "get_wifi_info": {"description": "获取店内Wi-Fi信息", "inputSchema": base_schema},
        "get_latest_news": {"description": "获取餐厅的最新消息", "inputSchema": base_schema}
    }

def get_tools_list(tenant_id='default'):
    tenant_type = 'restaurant_entity'
    tenant = tenant_manager.get_tenant(tenant_id)
    if tenant:
        tenant_type = getattr(tenant, 'type', None) or tenant_type

    templates = load_tool_templates()
    template_list = templates.get(tenant_type) or templates.get('restaurant_entity') or []
    catalog = get_tool_catalog()

    if not template_list:
        template_list = [{"name": name, "title": name} for name in catalog.keys()]

    tools = []
    for item in template_list:
        name = item.get('name')
        if not name:
            continue
        title = item.get('title') or name
        meta = catalog.get(name, {})
        tools.append({
            "name": name,
            "display_name": title,
            "description": meta.get("description") or "",
            "inputSchema": meta.get("inputSchema") or {"type": "object", "properties": {}, "additionalProperties": True}
        })
    return tools

def call_tool_for_tenant(tenant_id, tool_name, params):
    tenant = tenant_manager.get_tenant(tenant_id)
    if not tenant:
        return None, (jsonify({'error': '租户不存在'}), 404)

    config = getattr(tenant, 'config', {})

    if tool_name == "get_restaurant_info":
        result = {
            "restaurantName": config.get('shopName', '未知餐厅'),
            "restaurantIntro": config.get('specialDishes', '暂无介绍'),
            "businessHours": config.get('businessHours', '营业时间未知'),
            "locations": [
                {
                    "name": config.get('shopName', '未知餐厅'),
                    "address": config.get('address', '地址未知')
                }
            ]
        }
    elif tool_name == "get_queue_info":
        result = {
            "queueDescription": config.get('queueDescription', '暂无排队信息'),
            "queueMethods": config.get('queueMethods', []),
            "queueStores": config.get('queueStores', [])
        }
    elif tool_name == "get_delivery_info":
        result = {
            "deliveryDescription": config.get('deliveryDescription', '暂无外卖信息'),
            "deliveryPlatform": config.get('deliveryPlatform', '未知平台'),
            "deliverySearchKeyword": config.get('deliverySearchKeyword', ''),
            "deliveryStores": config.get('deliveryStores', []),
            "deliveryRange": config.get('deliveryRange', '配送范围未知')
        }
    elif tool_name == "get_raw_dumpling_info":
        result = {
            "rawDumplingDescription": config.get('rawDumplingDescription', '暂无生饺子信息'),
            "rawDumplingOrderMethod": config.get('rawDumplingOrderMethod', '未知下单方式'),
            "rawDumplingStorageTips": config.get('rawDumplingStorageTips', '暂无保存提示'),
            "rawDumplingCookingSteps": config.get('rawDumplingCookingSteps', []),
            "rawDumplingTips": config.get('rawDumplingTips', [])
        }
    elif tool_name == "get_wifi_info":
        result = {
            "wifiName": config.get('wifiName', '未知WiFi名称'),
            "wifiFindMethod": config.get('wifiFindMethod', '查找方式未知'),
            "wifiPassword": config.get('wifiPassword', '密码未知')
        }
    elif tool_name == "get_latest_news":
        result = {
            "latestNewsItems": config.get('latestNewsItems', [])
        }
    else:
        return None, (jsonify({"error": f"工具 {tool_name} 不存在", "status": "error"}), 404)

    return result, None

def jsonrpc_result(id_value, result):
    return jsonify({"jsonrpc": "2.0", "id": id_value, "result": result})

def jsonrpc_error(id_value, code, message, data=None):
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return jsonify({"jsonrpc": "2.0", "id": id_value, "error": err})

@bp.route('/mcp', methods=['GET', 'POST'])
@bp.route('/mcp/<tenant_id>', methods=['GET', 'POST'])
def mcp_entry(tenant_id='default'):
    if request.method == 'GET':
        tenant = tenant_manager.get_tenant(tenant_id)
        if tenant_id != 'default' and not tenant:
            return jsonify({'error': '租户不存在'}), 404
        return jsonify({
            'status': 'ok',
            'tenant_id': tenant_id,
            'tenant_name': tenant.name if tenant else 'Default Tenant',
            'endpoints': {
                'initialize': f'/api/mcp/{tenant_id}/initialize',
                'tools_list': f'/api/mcp/{tenant_id}/tools/list',
                'tools_call': f'/api/mcp/{tenant_id}/tools/call'
            }
        })

    data = request.get_json(silent=True) or {}
    if data.get('jsonrpc') == '2.0' and isinstance(data.get('method'), str):
        method = data.get('method')
        params = data.get('params') or {}
        id_value = data.get('id')
        method_l = method.strip().lower().replace('.', '/')

        if method_l.startswith('notifications/'):
            return Response(status=200)

        if method_l == 'initialize':
            context_id = mcp_server.create_context(tenant_id, {'name': 'MCP Context', 'tenant_id': tenant_id})
            tenant = tenant_manager.get_tenant(tenant_id)
            if tenant_id != 'default' and not tenant:
                return jsonrpc_error(id_value, -32000, '租户不存在'), 404
            protocol_version = params.get('protocolVersion') if isinstance(params, dict) else None
            protocol_version = protocol_version or '2024-11-05'
            return jsonrpc_result(id_value, {
                "protocolVersion": protocol_version,
                "serverInfo": {"name": "Skill Management MCP Server", "version": "1.0.0"},
                "capabilities": {"tools": {}},
                "context_id": context_id,
                "tenant": {"id": tenant_id, "name": tenant.name if tenant else 'Default Tenant', "tier": "free"}
            })

        if method_l == 'tools/list':
            tenant = tenant_manager.get_tenant(tenant_id)
            if tenant_id != 'default' and not tenant:
                return jsonrpc_error(id_value, -32000, '租户不存在'), 404
            return jsonrpc_result(id_value, {"tools": get_tools_list(tenant_id)})

        if method_l == 'tools/call':
            if not isinstance(params, dict):
                return jsonrpc_error(id_value, -32602, 'params 必须是对象'), 400
            tool_name = params.get('name')
            arguments = params.get('arguments') or {}
            if not tool_name:
                return jsonrpc_error(id_value, -32602, '缺少工具名称'), 400
            result, error_response = call_tool_for_tenant(tenant_id, tool_name, arguments)
            if error_response:
                resp, status = error_response
                body = resp.get_json(silent=True) or {}
                return jsonrpc_error(id_value, -32000, body.get('error') or '工具调用失败'), status
            return jsonrpc_result(id_value, {
                "content": [{"type": "text", "text": jsonify(result).get_data(as_text=True)}],
                "structuredContent": result,
                "isError": False
            })

        return jsonrpc_error(id_value, -32601, f'不支持的方法: {method}'), 404

    method = data.get('method') or data.get('type')

    if isinstance(method, str):
        method_l = method.strip().lower()
        if 'initialize' in method_l:
            return mcp_initialize(tenant_id)
        if 'tools/list' in method_l or method_l in ('tools.list', 'tools_list'):
            return mcp_list_tools(tenant_id)
        if 'tools/call' in method_l or method_l in ('tools.call', 'tools_call', 'call_tool'):
            return mcp_call_tool(tenant_id)

    if 'toolcall' in data:
        return mcp_call_tool(tenant_id)
    if 'protocolVersion' in data or 'clientInfo' in data or 'capabilities' in data:
        return mcp_initialize(tenant_id)

    return mcp_list_tools(tenant_id)

@bp.route('/mcp/initialize', methods=['POST'])
@bp.route('/mcp/<tenant_id>/initialize', methods=['POST'])
def mcp_initialize(tenant_id='default'):
    """MCP初始化"""
    data = request.get_json()
    
    # 初始化MCP上下文
    context_id = mcp_server.create_context(tenant_id, {
        'name': 'MCP Context',
        'tenant_id': tenant_id
    })
    
    # 获取租户信息
    tenant = tenant_manager.get_tenant(tenant_id)
    tenant_name = tenant.name if tenant else 'Default Tenant'
    
    return jsonify({
        'context_id': context_id,
        'tenant': {
            'id': tenant_id,
            'name': tenant_name,
            'tier': 'free'
        },
        'protocolVersion': '1.0'
    })

@bp.route('/mcp/tenants', methods=['GET'])
def mcp_list_tenants():
    """列出所有租户"""
    tenants = tenant_manager.list_tenants()
    return jsonify([
        {
            'id': tenant.id,
            'name': tenant.name,
            'type': getattr(tenant, 'type', 'restaurant_entity'),
            'tier': tenant.tier.value,
            'status': tenant.status,
            'created_at': tenant.created_at.isoformat()
        }
        for tenant in tenants
    ])

@bp.route('/mcp/tenants', methods=['POST'])
def mcp_create_tenant():
    """创建租户"""
    data = request.get_json()
    name = data.get('name')
    tier = data.get('tier', 'free')
    config = data.get('config', {})
    tenant_type = data.get('type', 'restaurant_entity')
    
    if not name:
        return jsonify({'error': '租户名称不能为空'}), 400
    
    tenant = tenant_manager.create_tenant(name, tier, config, type=tenant_type)
    return jsonify({
        'id': tenant.id,
        'name': tenant.name,
        'type': getattr(tenant, 'type', 'restaurant_entity'),
        'api_key': tenant.api_key,
        'api_secret': tenant.api_secret,
        'tier': tenant.tier.value,
        'status': tenant.status,
        'created_at': tenant.created_at.isoformat()
    })

@bp.route('/mcp/tenants/<tenant_id>', methods=['GET'])
def mcp_get_tenant(tenant_id):
    """获取租户信息"""
    tenant = tenant_manager.get_tenant(tenant_id)
    if not tenant:
        return jsonify({'error': '租户不存在'}), 404
    
    return jsonify({
        'id': tenant.id,
        'name': tenant.name,
        'type': getattr(tenant, 'type', 'restaurant_entity'),
        'tier': tenant.tier.value,
        'status': tenant.status,
        'config': tenant.config,
        'created_at': tenant.created_at.isoformat()
    })

@bp.route('/mcp/tools/list', methods=['POST'])
@bp.route('/mcp/<tenant_id>/tools/list', methods=['POST'])
def mcp_list_tools(tenant_id='default'):
    """获取工具列表"""
    data = request.get_json()

    tenant = tenant_manager.get_tenant(tenant_id)
    if tenant_id != 'default' and not tenant:
        return jsonify({'error': '租户不存在'}), 404

    tools = get_tools_list(tenant_id)
    
    return jsonify({'tools': tools})

@bp.route('/mcp/tools/call', methods=['POST'])
@bp.route('/mcp/<tenant_id>/tools/call', methods=['POST'])
def mcp_call_tool(tenant_id='default'):
    """调用工具"""
    print(f"MCP call tool: tenant_id={tenant_id}")  # 调试日志
    data = request.get_json()
    print(f"Request data: {data}")  # 调试日志
    toolcall = data.get('toolcall')
    
    if not toolcall or not toolcall.get('name'):
        return jsonify({'error': '工具调用参数不完整'}), 400
    
    tool_name = toolcall.get('name')
    params = toolcall.get('params', {})

    result, error_response = call_tool_for_tenant(tenant_id, tool_name, params)
    if error_response:
        return error_response
    
    return jsonify({
        "result": result,
        "status": "success"
    })
