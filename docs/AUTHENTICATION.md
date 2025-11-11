# 用户认证系统使用指南

## 概述

LifeOS AI 现在支持完整的用户认证系统,每个用户都有独立的账号和数据。新用户注册后会自动进入新手引导流程。

## 功能特点

### 1. 用户注册与登录
- **注册**: 需要用户名、邮箱、密码和时区
- **登录**: 使用用户名和密码登录
- **JWT Token**: 使用 JSON Web Token 进行身份验证,有效期 30 天
- **安全性**: 密码使用 bcrypt 加密存储

### 2. 新手引导流程
- 新注册用户会自动进入新手引导页面
- 引导内容包括:
  - 介绍 LifeOS AI 的 6 大功能
  - 引导创建第一个习惯
  - 完成后标记为老用户
- 可以跳过创建习惯步骤

### 3. 用户数据隔离
- 每个用户拥有独立的:
  - 习惯记录
  - 聊天历史
  - 目标和计划
  - 反思日记
- 数据完全隔离,互不干扰

## 使用流程

### 首次使用

1. **访问应用**
   ```
   http://localhost:8000
   ```
   自动跳转到登录/注册页面

2. **注册账号**
   - 点击"注册"标签
   - 填写用户名(3-20字符)
   - 填写邮箱(用于找回密码)
   - 设置密码(至少6位)
   - 选择时区(默认中国 UTC+8)
   - 点击"注册"按钮

3. **完成新手引导**
   - 了解 6 大功能介绍
   - 创建第一个习惯(可跳过)
   - 进入主界面

### 日常使用

1. **登录**
   ```
   http://localhost:8000
   ```
   - 输入用户名和密码
   - 点击"登录"按钮
   - 自动进入主界面

2. **使用功能**
   - 和 AI 聊天
   - 记录习惯
   - 制定计划
   - 设定目标
   - 写反思日记

3. **退出登录**
   - 点击右上角"退出"按钮
   - 确认退出

## 技术架构

### 认证流程

```
用户 → 注册/登录 → 服务器验证 → 返回 JWT Token → 存储在浏览器
     ↓
每次 API 请求 → 携带 Token → 服务器验证 → 执行操作
```

### API 端点

#### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/complete-onboarding` - 完成新手引导
- `POST /api/auth/logout` - 退出登录(客户端处理)

#### 业务功能(需要认证)
- `POST /api/chat` - 聊天对话
- `POST /api/habit/create` - 创建习惯
- `GET /api/habit/{user_id}` - 获取习惯列表
- 其他业务接口...

### 数据库结构

更新后的 `users` 表:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT,           -- 新增: 密码哈希
    email TEXT UNIQUE,            -- 新增: 邮箱
    timezone TEXT DEFAULT 'Asia/Shanghai',
    is_new_user BOOLEAN DEFAULT 1,         -- 新增: 是否新用户
    onboarding_completed BOOLEAN DEFAULT 0, -- 新增: 是否完成引导
    last_login TIMESTAMP,         -- 新增: 最后登录时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 安全说明

### 密码安全
- 使用 bcrypt 算法加密,不可逆
- 加密强度: 12 轮哈希
- 数据库中只存储密码哈希值

### Token 安全
- 使用 HS256 算法签名
- 有效期: 30 天
- 存储在浏览器 localStorage 中
- 每次请求通过 Authorization Header 发送

### 生产环境注意事项

⚠️ **重要**: 在生产环境使用前,必须修改以下配置:

1. **修改密钥**: `app/auth.py` 中的 `SECRET_KEY`
   ```python
   # 当前(不安全):
   SECRET_KEY = "your-secret-key-change-in-production-use-random-string"
   
   # 应改为(随机生成):
   import secrets
   SECRET_KEY = secrets.token_urlsafe(32)
   ```

2. **启用 HTTPS**: 生产环境必须使用 HTTPS
   - Token 通过 HTTPS 传输
   - 防止中间人攻击

3. **配置 CORS**: 限制允许的域名
   ```python
   # configs/settings.py
   CORS_ORIGINS = ["https://yourdomain.com"]  # 不要用 "*"
   ```

4. **Token 有效期**: 根据需求调整
   ```python
   # app/auth.py
   ACCESS_TOKEN_EXPIRE_DAYS = 7  # 改为 7 天更安全
   ```

## 迁移现有数据

如果你之前使用的是 `user_id=1` 的单用户模式,需要迁移数据:

### 方法 1: 为现有数据创建用户

```python
# 运行此脚本
from app.database import Database
from app.auth import hash_password

db = Database()

# 为现有数据创建一个用户
password_hash = hash_password("your_password")
user_id = db.create_user_with_password(
    username="admin",
    password_hash=password_hash,
    email="admin@example.com",
    timezone="Asia/Shanghai"
)

print(f"创建用户成功,user_id={user_id}")
print("现有数据已关联到此用户")
```

### 方法 2: 使用 SQL 直接更新

```sql
-- 1. 创建用户
INSERT INTO users (username, password_hash, email, is_new_user, onboarding_completed)
VALUES ('admin', '$2b$12$...', 'admin@example.com', 0, 1);

-- 2. 确认 user_id(应该是 1)
SELECT id FROM users WHERE username = 'admin';
```

## 故障排查

### 问题 1: 无法登录

**症状**: 输入正确密码仍提示"用户名或密码错误"

**解决**:
```python
# 检查密码哈希是否正确
from app.database import Database
from app.auth import verify_password

db = Database()
user = db.get_user_by_username("your_username")
if user:
    print(f"用户存在,密码哈希: {user['password_hash'][:20]}...")
    is_valid = verify_password("your_password", user['password_hash'])
    print(f"密码验证: {is_valid}")
```

### 问题 2: Token 失效

**症状**: 已登录但页面自动跳转到登录页

**解决**:
1. 检查 Token 是否过期(F12 → Application → Local Storage)
2. 清除浏览器缓存和 localStorage
3. 重新登录

### 问题 3: 新用户看不到引导页

**症状**: 注册后直接进入主界面

**解决**:
```sql
-- 检查用户状态
SELECT username, is_new_user, onboarding_completed FROM users;

-- 重置为新用户
UPDATE users SET is_new_user = 1, onboarding_completed = 0 
WHERE username = 'your_username';
```

## 开发测试

### 创建测试用户

```bash
# 使用 API 创建
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "test123",
    "timezone": "Asia/Shanghai"
  }'
```

### 获取 Token

```bash
# 登录获取 Token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "test123"
  }'
```

### 使用 Token 调用 API

```bash
# 获取用户信息
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 发送聊天消息
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "user_id": 1,
    "message": "你好"
  }'
```

## 相关文档

- [Agent 工作原理说明](AGENT_EXPLAINED.md) - 了解 AI 如何处理你的消息
- [用户 ID 机制说明](USER_ID_MECHANISM.md) - 旧版单用户系统说明(已废弃)
- [新用户快速上手](../新用户快速上手.md) - 功能使用指南
- [项目结构说明](../PROJECT_STRUCTURE.md) - 代码组织结构

## 更新日志

### v1.1.0 (当前版本)
- ✅ 添加完整用户认证系统
- ✅ 支持用户注册和登录
- ✅ JWT Token 身份验证
- ✅ 新手引导流程
- ✅ 用户数据隔离
- ✅ 密码加密存储
- ✅ 精美的登录/注册界面
- ✅ 响应式引导页面

### v1.0.0 (旧版本)
- 单用户模式(user_id=1)
- 无认证系统
- 所有用户共享数据
