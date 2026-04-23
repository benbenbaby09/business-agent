from flask import Blueprint, request, jsonify
from mcp.server import mcp_server
from mcp.tenant import tenant_manager

# 创建蓝图
bp = Blueprint('mcp', __name__)

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
    
    if not name:
        return jsonify({'error': '租户名称不能为空'}), 400
    
    tenant = tenant_manager.create_tenant(name, tier, config)
    return jsonify({
        'id': tenant.id,
        'name': tenant.name,
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
    
    # 模拟工具列表
    tools = [
        {
            "name": "get_restaurant_info",
            "display_name": "餐厅基本信息",
            "description": "获取餐厅的基本信息，包括名称、地址、营业时间等"
        },
        {
            "name": "get_queue_info",
            "display_name": "堂食排队取号",
            "description": "获取餐厅的排队取号信息"
        },
        {
            "name": "get_delivery_info",
            "display_name": "外卖配送信息",
            "description": "获取餐厅的外卖配送信息"
        },
        {
            "name": "get_raw_dumpling_info",
            "display_name": "生饺子打包与教程",
            "description": "获取生饺子打包信息和煮饺子教程"
        },
        {
            "name": "get_wifi_info",
            "display_name": "店内Wi-Fi",
            "description": "获取店内Wi-Fi信息"
        },
        {
            "name": "get_latest_news",
            "display_name": "最新消息",
            "description": "获取餐厅的最新消息"
        }
    ]
    
    return jsonify({'tools': tools})

@bp.route('/mcp/tools/call', methods=['POST'])
@bp.route('/mcp/<tenant_id>/tools/call', methods=['POST'])
def mcp_call_tool(tenant_id='default'):
    """调用工具"""
    data = request.get_json()
    toolcall = data.get('toolcall')
    
    if not toolcall or not toolcall.get('name'):
        return jsonify({'error': '工具调用参数不完整'}), 400
    
    tool_name = toolcall.get('name')
    params = toolcall.get('params', {})
    
    # 获取租户信息
    tenant = tenant_manager.get_tenant(tenant_id)
    if not tenant:
        return jsonify({'error': '租户不存在'}), 404
    
    # 从租户配置中获取真实数据
    config = getattr(tenant, 'config', {})
    
    # 根据工具名称返回相应的数据
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
        return jsonify({
            "error": f"工具 {tool_name} 不存在",
            "status": "error"
        }), 404
    
    return jsonify({
        "result": result,
        "status": "success"
    })
