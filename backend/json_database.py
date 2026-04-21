import json
import os
from datetime import datetime
from bson.objectid import ObjectId

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
TENANTS_FILE = os.path.join(DATA_DIR, 'tenants.json')
SKILLS_FILE = os.path.join(DATA_DIR, 'skills.json')
FILES_FILE = os.path.join(DATA_DIR, 'files.json')
VERSIONS_FILE = os.path.join(DATA_DIR, 'versions.json')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

class JSONCollection:
    """基于JSON文件的集合"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = []
        self._load()
    
    def _load(self):
        """从JSON文件加载数据"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                    # 将字符串_id转换回ObjectId
                    for item in self.data:
                        if '_id' in item:
                            item['_id'] = ObjectId(item['_id'])
                        if 'user_id' in item:
                            item['user_id'] = ObjectId(item['user_id'])
                        if 'skill_id' in item:
                            item['skill_id'] = ObjectId(item['skill_id'])
                        if 'tenant_id' in item:
                            item['tenant_id'] = ObjectId(item['tenant_id'])
            except Exception as e:
                print(f"加载数据失败 {self.file_path}: {e}")
                self.data = []
        else:
            self.data = []
    
    def _save(self):
        """保存数据到JSON文件"""
        try:
            # 将ObjectId转换为字符串
            save_data = []
            for item in self.data:
                save_item = item.copy()
                if '_id' in save_item:
                    save_item['_id'] = str(save_item['_id'])
                if 'user_id' in save_item:
                    save_item['user_id'] = str(save_item['user_id'])
                if 'skill_id' in save_item:
                    save_item['skill_id'] = str(save_item['skill_id'])
                if 'tenant_id' in save_item:
                    save_item['tenant_id'] = str(save_item['tenant_id'])
                save_data.append(save_item)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"保存数据失败 {self.file_path}: {e}")
    
    def find_one(self, query):
        """查找单个文档"""
        for item in self.data:
            if self._match(item, query):
                return item
        return None
    
    def find(self, query=None):
        """查找多个文档"""
        if query is None:
            query = {}
        
        results = []
        for item in self.data:
            if self._match(item, query):
                results.append(item)
        
        return JSONCursor(results)
    
    def insert_one(self, document):
        """插入单个文档"""
        if '_id' not in document:
            document['_id'] = ObjectId()
        if 'created_at' not in document:
            document['created_at'] = datetime.utcnow()
        if 'updated_at' not in document:
            document['updated_at'] = datetime.utcnow()
        
        self.data.append(document)
        self._save()
        
        return type('obj', (object,), {'inserted_id': document['_id']})()
    
    def update_one(self, filter_query, update):
        """更新单个文档"""
        for item in self.data:
            if self._match(item, filter_query):
                for key, value in update.get('$set', {}).items():
                    item[key] = value
                item['updated_at'] = datetime.utcnow()
                self._save()
                return type('obj', (object,), {'matched_count': 1})()
        return type('obj', (object,), {'matched_count': 0})()
    
    def delete_one(self, query):
        """删除单个文档"""
        for i, item in enumerate(self.data):
            if self._match(item, query):
                del self.data[i]
                self._save()
                return type('obj', (object,), {'deleted_count': 1})()
        return type('obj', (object,), {'deleted_count': 0})()
    
    def count_documents(self, query):
        """统计文档数量"""
        count = 0
        for item in self.data:
            if self._match(item, query):
                count += 1
        return count
    
    def create_index(self, keys, **kwargs):
        """创建索引（模拟）"""
        pass
    
    def _match(self, item, query):
        """检查文档是否匹配查询条件"""
        for key, value in query.items():
            item_value = item.get(key)
            
            # 处理ObjectId比较
            if isinstance(value, ObjectId):
                if str(item_value) != str(value):
                    return False
            # 处理字符串和ObjectId的混合比较
            elif isinstance(item_value, ObjectId):
                if str(item_value) != str(value):
                    return False
            elif item_value != value:
                return False
        
        return True


class JSONCursor:
    """JSON查询游标"""
    
    def __init__(self, data):
        self.data = data
        self._skip = 0
        self._limit = 0
    
    def skip(self, n):
        self._skip = n
        return self
    
    def limit(self, n):
        self._limit = n
        return self
    
    def __iter__(self):
        result = self.data
        if self._skip > 0:
            result = result[self._skip:]
        if self._limit > 0:
            result = result[:self._limit]
        return iter(result)
    
    def __len__(self):
        result = self.data
        if self._skip > 0:
            result = result[self._skip:]
        if self._limit > 0:
            result = result[:self._limit]
        return len(result)


# 初始化集合
users_collection = JSONCollection(USERS_FILE)
tenants_collection = JSONCollection(TENANTS_FILE)
skills_collection = JSONCollection(SKILLS_FILE)
skill_files_collection = JSONCollection(FILES_FILE)
versions_collection = JSONCollection(VERSIONS_FILE)

# 添加默认测试数据
if not users_collection.find_one({'email': 'test@example.com'}):
    test_user = {
        '_id': ObjectId('5f9f1b9b9b9b9b9b9b9b9b9b'),
        'username': 'test',
        'email': 'test@example.com',
        'password': b'$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    users_collection.insert_one(test_user)
    print("已创建测试用户: test@example.com")

if not skills_collection.find_one({'name': '测试Skill'}):
    test_skill = {
        '_id': ObjectId('5f9f1b9b9b9b9b9b9b9b9b9c'),
        'user_id': ObjectId('5f9f1b9b9b9b9b9b9b9b9b9b'),
        'name': '测试Skill',
        'description': '这是一个测试Skill',
        'type': 'restaurant_entity',
        'status': 'active',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    skills_collection.insert_one(test_skill)
    print("已创建测试Skill")

print(f"JSON数据库初始化完成，数据保存在: {DATA_DIR}")