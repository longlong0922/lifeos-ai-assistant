# 🔑 用户ID机制详解

## 问题：系统是怎么知道用户ID的？

简单回答：**目前系统使用硬编码的默认用户ID = 1**

---

## 📍 当前实现方式

### 1. 命令行聊天 (`scripts/chat.py`)

```python
user_id = 1  # 默认用户 ID
```

**硬编码**为 1，所有命令行用户共享这个ID。

---

### 2. Web 界面 (`web/index.html`)

```javascript
const USER_ID = 1;  // 硬编码

// 发送消息时
body: JSON.stringify({
    user_id: USER_ID,  // 固定发送 1
    message: message
})
```

**JavaScript 中硬编码**为 1。

---

### 3. API 接口 (`api/routes_chat.py`)

```python
@router.post("/chat")
async def chat(request: ChatRequest):
    result = graph.run(
        user_id=request.user_id,  # 从请求体获取
        message=request.message
    )
```

从 **HTTP 请求体**中读取 `user_id` 字段。

---

## 🔄 数据流向

### 完整流程

```
1. 前端/脚本设置 user_id = 1
        ↓
2. 发送到 API: POST /api/chat
   { "user_id": 1, "message": "你好" }
        ↓
3. API 读取 request.user_id
        ↓
4. 传递给 LangGraph: graph.run(user_id=1, ...)
        ↓
5. 各个节点使用: state.user_id
        ↓
6. 数据库查询: db.get_user_habits(user_id=1)
```

---

## 📂 各文件中的 user_id

### 命令行脚本

| 文件 | user_id 值 | 说明 |
|------|-----------|------|
| `scripts/chat.py` | `1` | 硬编码默认值 |
| `scripts/demo.py` | `1` | 硬编码默认值 |
| `scripts/demo_all.py` | `1` | 硬编码默认值 |
| `scripts/show_data.py` | `1` | 硬编码默认值 |
| `scripts/test_system.py` | `1` | 硬编码默认值 |

### Web 界面

| 文件 | user_id 值 | 说明 |
|------|-----------|------|
| `web/index.html` | `const USER_ID = 1` | JavaScript 常量 |

### API 路由

| 文件 | user_id 来源 | 说明 |
|------|-------------|------|
| `api/routes_chat.py` | `request.user_id` | 从 HTTP 请求体 |
| `api/routes_habit.py` | `request.user_id` 或路径参数 | 根据接口不同 |

### 核心节点

| 文件 | user_id 来源 | 说明 |
|------|-------------|------|
| `app/nodes/habit_node.py` | `state.user_id` | 从 LangGraph 状态 |
| `app/nodes/coach_node.py` | `state.user_id` | 从 LangGraph 状态 |
| `app/nodes/plan_node.py` | `state.user_id` | 从 LangGraph 状态 |
| `app/nodes/reflect_node.py` | `state.user_id` | 从 LangGraph 状态 |

---

## 🎯 为什么这样设计？

### 当前设计的考虑

1. **简化开发** - MVP 阶段，专注核心功能
2. **快速测试** - 不需要登录系统
3. **单用户场景** - 适合个人使用

### 当前的局限

❌ **无法区分多个用户** - 所有人共享同一个用户数据  
❌ **无用户认证** - 任何人都可以访问  
❌ **无数据隔离** - 数据混在一起  
❌ **无权限控制** - 无法保护隐私  

---

## 🔧 如何修改用户ID？

### 方法 1：修改命令行脚本

编辑 `scripts/chat.py`:
```python
user_id = 2  # 改成你想要的ID
```

### 方法 2：修改 Web 界面

编辑 `web/index.html`:
```javascript
const USER_ID = 2;  // 改成你想要的ID
```

### 方法 3：直接使用 API

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2, "message": "你好"}'
```

---

## 🚀 如何支持多用户？

### 方案 1：添加登录系统（推荐）

#### 步骤概览

1. **添加用户注册/登录接口**
   ```python
   @router.post("/register")
   async def register(username: str, password: str):
       # 创建用户，返回 token
   
   @router.post("/login")
   async def login(username: str, password: str):
       # 验证用户，返回 token
   ```

2. **使用 JWT Token 认证**
   ```python
   from fastapi import Depends, HTTPException
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   def get_current_user(token: str = Depends(security)):
       # 解析 token，返回 user_id
       user_id = verify_token(token)
       return user_id
   ```

3. **修改聊天接口**
   ```python
   @router.post("/chat")
   async def chat(
       request: ChatRequest,
       user_id: int = Depends(get_current_user)  # 自动获取
   ):
       result = graph.run(user_id=user_id, message=request.message)
   ```

4. **修改 Web 界面**
   ```javascript
   // 登录后保存 token
   localStorage.setItem('token', response.token);
   
   // 发送请求时携带 token
   headers: {
       'Authorization': `Bearer ${localStorage.getItem('token')}`
   }
   ```

---

### 方案 2：使用会话Cookie

#### 步骤概览

1. **添加会话管理**
   ```python
   from fastapi import Cookie
   from starlette.middleware.sessions import SessionMiddleware
   
   app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
   ```

2. **登录时设置会话**
   ```python
   @router.post("/login")
   async def login(request: Request, username: str, password: str):
       user = authenticate(username, password)
       request.session["user_id"] = user.id
   ```

3. **从会话获取用户**
   ```python
   @router.post("/chat")
   async def chat(request: Request, chat_request: ChatRequest):
       user_id = request.session.get("user_id")
       if not user_id:
           raise HTTPException(401, "未登录")
   ```

---

### 方案 3：URL 参数（简单但不安全）

适合测试，不适合生产：

```python
@router.post("/chat/{user_id}")
async def chat(user_id: int, request: ChatRequest):
    result = graph.run(user_id=user_id, message=request.message)
```

Web 界面：
```javascript
const USER_ID = prompt("请输入你的用户 ID:");
fetch(`${API_BASE}/chat/${USER_ID}`, ...)
```

---

## 💡 推荐的完整用户系统

### 数据库表设计

```sql
-- 用户表（已有）
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,  -- 新增：密码哈希
    email TEXT UNIQUE,             -- 新增：邮箱
    created_at TIMESTAMP,
    last_login TIMESTAMP           -- 新增：最后登录
);

-- 会话表（新增）
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 认证流程

```
1. 用户注册
   ↓
2. 创建 users 记录（密码加密）
   ↓
3. 用户登录
   ↓
4. 验证密码
   ↓
5. 生成 JWT token
   ↓
6. 返回 token 给前端
   ↓
7. 前端保存 token（localStorage）
   ↓
8. 后续请求携带 token
   ↓
9. 后端验证 token
   ↓
10. 提取 user_id
```

---

## 🔐 安全考虑

### 密码存储
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 注册时
hashed = pwd_context.hash(password)

# 登录时
pwd_context.verify(password, hashed)
```

### Token 生成
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

def create_token(user_id: int):
    expire = datetime.utcnow() + timedelta(days=7)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
```

---

## 📝 示例：快速添加多用户支持

### 1. 安装依赖
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

### 2. 创建 auth.py
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()
SECRET_KEY = "your-secret-key"

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: int = int(payload.get("sub"))
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
```

### 3. 修改聊天接口
```python
from app.auth import get_current_user_id

@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id)  # 自动获取
):
    result = graph.run(
        user_id=user_id,  # 使用认证后的真实 user_id
        message=request.message
    )
    return ChatResponse(response=result['response'])
```

### 4. 添加登录接口
```python
@router.post("/login")
async def login(username: str, password: str):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(401, "用户名或密码错误")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
```

---

## 🎯 总结

### 当前状态
- ✅ 系统使用硬编码 `user_id = 1`
- ✅ 适合单用户/测试场景
- ❌ 不支持多用户
- ❌ 没有认证系统

### 如何改进
1. **短期**：手动修改 user_id 常量
2. **中期**：添加简单的用户选择
3. **长期**：实现完整的认证系统

### 关键文件
- `scripts/chat.py` - 命令行 user_id
- `web/index.html` - Web 前端 user_id
- `api/routes_chat.py` - API 接口处理

---

**需要帮助实现多用户系统？我可以提供完整的代码！** 🚀
