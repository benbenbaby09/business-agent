from flask import Blueprint, request, jsonify
import hashlib
import uuid

# 创建蓝图
bp = Blueprint('auth', __name__)

# 模拟用户数据
users = {
    'admin': {
        'password': hashlib.sha256('password123'.encode()).hexdigest(),
        'name': 'Admin User',
        'role': 'admin'
    }
}

@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    print(f"Login request data: {data}")  # 调试日志
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        print(f"Missing fields - username: {username}, password: {password}")
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    if username not in users:
        return jsonify({'error': '用户不存在'}), 401
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if hashed_password != users[username]['password']:
        return jsonify({'error': '密码错误'}), 401
    
    # 生成token
    token = str(uuid.uuid4())
    
    return jsonify({
        'token': token,
        'user': {
            'username': username,
            'name': users[username]['name'],
            'role': users[username]['role']
        }
    })

@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username') or data.get('email')  # 支持username或email
    password = data.get('password')
    name = data.get('name', username)
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    if username in users:
        return jsonify({'error': '用户名已存在'}), 409
    
    # 创建新用户
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users[username] = {
        'password': hashed_password,
        'name': name,
        'role': 'user'
    }
    
    # 生成token
    token = str(uuid.uuid4())
    
    return jsonify({
        'token': token,
        'user': {
            'username': username,
            'name': name,
            'role': 'user'
        }
    })

@bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    # 实际项目中需要清除token
    return jsonify({'message': '登出成功'})
