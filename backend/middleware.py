from functools import wraps
from flask import request, jsonify
import jwt
import os
from bson.objectid import ObjectId

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        
        try:
            # 提取令牌
            token = token.split(' ')[1] if 'Bearer' in token else token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            
            # 将用户ID传递给路由函数
            return f(user_id, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    return decorated_function
