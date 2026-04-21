// MongoDB初始化脚本
// 创建数据库和用户

db = db.getSiblingDB('skill_management');

// 创建应用用户
db.createUser({
  user: 'skill_user',
  pwd: 'skill_password',
  roles: [
    { role: 'readWrite', db: 'skill_management' }
  ]
});

// 创建集合
db.createCollection('users');
db.createCollection('skills');
db.createCollection('skill_files');
db.createCollection('versions');

// 创建索引
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });
db.skills.createIndex({ user_id: 1, status: 1 });
db.skills.createIndex({ type: 1 });
db.skill_files.createIndex({ skill_id: 1 });
db.versions.createIndex({ skill_id: 1 });

print('数据库初始化完成');