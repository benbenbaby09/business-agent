from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from datetime import datetime

# 加载环境变量
load_dotenv()

# 尝试连接MongoDB
try:
    # 数据库连接
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/skill_management')
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # 测试连接
    client.server_info()
    db = client.get_database()
    
    # 集合初始化
    users_collection = db.users
    tenants_collection = db.tenants
    skills_collection = db.skills
    skill_files_collection = db.skill_files
    versions_collection = db.versions
    
    # 创建索引
    users_collection.create_index('username', unique=True)
    users_collection.create_index('email', unique=True)
    tenants_collection.create_index('user_id')
    skills_collection.create_index([('user_id', 1), ('status', 1)])
    skills_collection.create_index([('tenant_id', 1), ('status', 1)])
    skills_collection.create_index('type')
    skill_files_collection.create_index('skill_id')
    versions_collection.create_index('skill_id')
    
    print("MongoDB连接成功")
    
except Exception as e:
    print(f"MongoDB连接失败: {e}")
    print("使用JSON本地数据库（数据保存在 backend/data/ 目录）")
    
    # 导入JSON数据库
    from json_database import (
        users_collection,
        tenants_collection,
        skills_collection,
        skill_files_collection,
        versions_collection
    )