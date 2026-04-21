from flask import Blueprint, request, jsonify
import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from database import users_collection

bp = Blueprint('auth', __name__)

# JWT密钥
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

# 登录
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # 查找用户
    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # 验证密码
    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # 生成JWT令牌
    payload = {
        'user_id': str(user['_id']),
        'email': user['email'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    return jsonify({'token': token, 'user': {
        'id': str(user['_id']),
        'username': user['username'],
        'email': user['email']
    }})

# 注册
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # 检查用户是否已存在
    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'Email already exists'}), 400
    
    if users_collection.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400
    
    # 哈希密码
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # 创建用户
    user = {
        'username': username,
        'email': email,
        'password': hashed_password,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = users_collection.insert_one(user)
    user['_id'] = str(result.inserted_id)
    
    # 生成JWT令牌
    payload = {
        'user_id': str(user['_id']),
        'email': user['email'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    return jsonify({'token': token, 'user': {
        'id': user['_id'],
        'username': user['username'],
        'email': user['email']
    }}), 201

# 获取当前用户信息
@bp.route('/me', methods=['GET'])
def get_me():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token required'}), 401
    
    try:
        # 提取令牌
        token = token.split(' ')[1] if 'Bearer' in token else token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        
        # 查找用户
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email']
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
