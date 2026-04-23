from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保所有必要的目录存在
import os
# 创建主数据目录
os.makedirs('/data', exist_ok=True)
# 创建技能文件存储目录
os.makedirs('/data/skills', exist_ok=True)

# 初始化Flask应用
app = Flask(__name__)
# 启用CORS，允许所有来源
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key", "X-API-Secret"],
        "supports_credentials": False
    }
})

# 导入路由
from routes import auth, skills, files, publish, tenants, mcp, mcp_services

# 注册蓝图
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(tenants.bp, url_prefix='/api/tenants')
app.register_blueprint(skills.bp, url_prefix='/api/skills')
app.register_blueprint(files.bp, url_prefix='/api/skills')
app.register_blueprint(publish.bp, url_prefix='/api/skills')
app.register_blueprint(mcp.bp, url_prefix='/api')
app.register_blueprint(mcp_services.bp, url_prefix='/api')

# 配置静态文件服务
app.static_folder = '/data'
app.static_url_path = '/storage'

# 静态文件服务路由
@app.route('/storage/<path:filename>')
def serve_static(filename):
    """静态文件服务"""
    import os
    file_path = os.path.join(app.static_folder, filename)
    if os.path.exists(file_path):
        from flask import send_file
        return send_file(file_path)
    else:
        from flask import abort
        abort(404)



# 导入并初始化MCP服务
from mcp.server import mcp_server
from mcp.tenant import tenant_manager, TenantTier

# 初始化MCP服务器
mcp_server.init_app(app)

# 创建默认租户（如果不存在）
if not tenant_manager.list_tenants():
    default_tenant = tenant_manager.create_tenant(
        name="Default Tenant",
        tier=TenantTier.FREE,
        config={"description": "Default tenant for testing"}
    )
    print(f"Created default tenant: {default_tenant.name}")
    print(f"API Key: {default_tenant.api_key}")
    print(f"API Secret: {default_tenant.api_secret}")

# 健康检查
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

# MCP信息端点
@app.route('/api/mcp/info', methods=['GET'])
def mcp_info():
    """MCP服务信息"""
    return jsonify({
        "name": "Skill Management MCP Server",
        "version": "1.0.0",
        "protocol_version": "2024-11-05",
        "features": [
            "multi-tenant",
            "context-management",
            "resources",
            "tools",
            "prompts"
        ],
        "endpoints": {
            "initialize": "/api/mcp/initialize",
            "tenants": "/api/mcp/tenants",
            "contexts": "/api/mcp/contexts",
            "resources": "/api/mcp/contexts/{context_id}/resources",
            "tools": "/api/mcp/contexts/{context_id}/tools",
            "prompts": "/api/mcp/contexts/{context_id}/prompts"
        }
    })

# 云函数入口
def main(event, context):
    # 处理HTTP请求
    from flask import request
    # 确保处理OPTIONS请求
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key, X-API-Secret',
                'Access-Control-Allow-Credentials': 'true'
            },
            'body': ''
        }
    return app(event, context)

# 本地运行
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
