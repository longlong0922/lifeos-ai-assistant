# 📖 API 文档的用途和使用方法

## 🎯 API 文档是什么？

API 文档（访问 http://localhost:8000/docs）是一个**交互式界面**，让你可以：

1. **查看所有功能** - 了解系统能做什么
2. **测试 API** - 直接在浏览器中测试各个功能
3. **查看参数** - 了解每个接口需要什么输入
4. **学习使用** - 了解如何集成到其他应用

---

## 💡 API 文档的 5 大用途

### 1️⃣ 可视化测试功能（最常用）

**不需要写代码，直接点点点就能测试！**

#### 示例：发送聊天消息

1. 打开 http://localhost:8000/docs
2. 找到 `POST /api/chat` 接口
3. 点击 "Try it out"
4. 填写参数：
   ```json
   {
     "user_id": 1,
     "message": "我今天完成了跑步！"
   }
   ```
5. 点击 "Execute"
6. 立即看到 AI 的响应！

**好处**：
- ✅ 不用写代码
- ✅ 实时看到结果
- ✅ 可以快速试验不同的输入

---

### 2️⃣ 了解系统所有功能

API 文档清楚地展示了 LifeOS 的所有能力：

#### 聊天相关
- `POST /api/chat` - 发送消息，获取 AI 响应
- `GET /api/health` - 检查系统状态
- `GET /api/stats/{user_id}` - 查看用户统计
- `GET /api/history/{user_id}` - 获取聊天历史

#### 习惯管理
- `POST /api/habit` - 创建新习惯
- `GET /api/habit/{user_id}` - 查看所有习惯
- `PUT /api/habit/{habit_id}` - 更新习惯
- `DELETE /api/habit/{habit_id}` - 删除习惯
- `POST /api/habit/{habit_id}/record` - 记录打卡

#### 目标管理
- `POST /api/goal` - 创建目标
- `GET /api/goal/{user_id}` - 查看所有目标
- `PUT /api/goal/{goal_id}` - 更新目标

#### 反思记录
- `POST /api/reflect` - 保存反思
- `GET /api/reflect/{user_id}` - 获取反思历史

#### 每日简报
- `GET /api/brief/{user_id}` - 生成今日简报

---

### 3️⃣ 学习如何集成到其他应用

API 文档展示了如何用各种编程语言调用接口。

#### Python 示例
```python
import requests

# 发送聊天消息
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "user_id": 1,
        "message": "我今天完成了跑步！"
    }
)

result = response.json()
print(result['response'])  # AI 的回复
```

#### JavaScript 示例
```javascript
// 发送聊天消息
fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 1,
    message: '我今天完成了跑步！'
  })
})
.then(response => response.json())
.then(data => console.log(data.response));
```

#### PowerShell 示例
```powershell
# 发送聊天消息
$body = @{
    user_id = 1
    message = "我今天完成了跑步！"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

---

### 4️⃣ 开发自己的应用

有了 API，你可以基于 LifeOS 开发各种应用：

#### 应用场景示例

**场景 A：桌面提醒工具**
```python
# 每天早上 7 点获取简报并显示通知
import requests
import schedule

def show_daily_brief():
    response = requests.get("http://localhost:8000/api/brief/1")
    brief = response.json()
    # 显示桌面通知
    show_notification(brief['content'])

schedule.every().day.at("07:00").do(show_daily_brief)
```

**场景 B：微信机器人**
```python
# 在微信群中回复消息
def on_message(msg):
    response = requests.post(
        "http://localhost:8000/api/chat",
        json={
            "user_id": get_user_id(msg.sender),
            "message": msg.text
        }
    )
    reply_to_wechat(response.json()['response'])
```

**场景 C：网页仪表盘**
```javascript
// React 组件显示习惯统计
function HabitDashboard() {
  const [stats, setStats] = useState({});
  
  useEffect(() => {
    fetch('http://localhost:8000/api/stats/1')
      .then(res => res.json())
      .then(data => setStats(data));
  }, []);
  
  return <div>完成率: {stats.habits.completion_rate}%</div>
}
```

**场景 D：Telegram Bot**
```python
# 在 Telegram 中使用 LifeOS
from telegram import Bot

def telegram_handler(update):
    ai_response = requests.post(
        "http://localhost:8000/api/chat",
        json={
            "user_id": update.user.id,
            "message": update.message.text
        }
    ).json()
    
    bot.send_message(
        chat_id=update.chat_id,
        text=ai_response['response']
    )
```

---

### 5️⃣ 调试和问题排查

API 文档可以帮助你快速定位问题：

#### 测试流程
```
1. 系统出问题
   ↓
2. 打开 API 文档
   ↓
3. 测试相关接口
   ↓
4. 查看返回的错误信息
   ↓
5. 找到问题原因
```

#### 示例：习惯记录不成功

1. 打开 API 文档
2. 测试 `GET /api/habit/1` - 查看习惯是否存在
3. 测试 `POST /api/habit/{habit_id}/record` - 尝试记录
4. 查看返回的错误信息（如 habit_id 不存在）
5. 定位问题并修复

---

## 🎮 实战演练

### 练习 1：创建习惯并记录

1. **启动服务**
   ```powershell
   python run.py
   ```

2. **打开 API 文档**
   - 浏览器访问：http://localhost:8000/docs

3. **创建习惯**
   - 找到 `POST /api/habit`
   - 点击 "Try it out"
   - 填写：
     ```json
     {
       "user_id": 1,
       "name": "每天学习编程",
       "description": "学习 30 分钟 Python",
       "target_frequency": "daily"
     }
     ```
   - 点击 "Execute"
   - 记下返回的 `habit_id`

4. **记录打卡**
   - 找到 `POST /api/habit/{habit_id}/record`
   - 填写 habit_id
   - 填写：
     ```json
     {
       "user_id": 1,
       "status": "completed",
       "context": "今天学习了函数和类"
     }
     ```
   - 点击 "Execute"

5. **查看统计**
   - 找到 `GET /api/stats/1`
   - 点击 "Try it out"
   - 点击 "Execute"
   - 看到新习惯的统计数据

### 练习 2：聊天测试

1. **发送消息**
   - 找到 `POST /api/chat`
   - 填写：
     ```json
     {
       "user_id": 1,
       "message": "帮我分析一下我的学习习惯"
     }
     ```
   - 查看 AI 响应

2. **查看历史**
   - 找到 `GET /api/history/1`
   - 查看所有对话记录

---

## 🔧 高级用法

### 自动化脚本

创建一个每日打卡脚本：

```python
# daily_checkin.py
import requests
from datetime import datetime

def daily_checkin():
    # 获取用户输入
    print("今天完成了哪些习惯？")
    
    # 获取所有习惯
    habits = requests.get("http://localhost:8000/api/habit/1").json()
    
    for i, habit in enumerate(habits, 1):
        print(f"{i}. {habit['name']}")
        status = input(f"完成了吗？(y/n): ")
        
        if status.lower() == 'y':
            # 记录完成
            requests.post(
                f"http://localhost:8000/api/habit/{habit['id']}/record",
                json={
                    "user_id": 1,
                    "status": "completed",
                    "context": f"打卡于 {datetime.now()}"
                }
            )
            print("✅ 已记录")
        else:
            print("⏭️  跳过")
    
    # 获取今日简报
    brief = requests.get("http://localhost:8000/api/brief/1").json()
    print("\n📋 今日简报:")
    print(brief['content'])

if __name__ == "__main__":
    daily_checkin()
```

### 批量操作

```python
# batch_operations.py
import requests

# 批量创建习惯
habits_to_create = [
    {"name": "跑步", "description": "每天 30 分钟"},
    {"name": "阅读", "description": "每天 20 页"},
    {"name": "冥想", "description": "每天 10 分钟"}
]

for habit in habits_to_create:
    response = requests.post(
        "http://localhost:8000/api/habit",
        json={
            "user_id": 1,
            **habit,
            "target_frequency": "daily"
        }
    )
    print(f"✅ 创建习惯: {habit['name']}")
```

---

## 📊 API 文档 vs 其他使用方式

| 方式 | 优点 | 适用场景 |
|------|------|----------|
| **API 文档** | 可视化、交互式、适合测试 | 快速测试、学习接口 |
| **命令行聊天** | 简单直接、对话式 | 日常使用、快速交互 |
| **编程调用** | 灵活、可集成、自动化 | 开发应用、批量操作 |
| **Web 界面** | 友好、美观（需开发） | 普通用户使用 |

---

## 🎯 总结

### API 文档的核心价值

1. **学习工具** 📚
   - 了解系统能做什么
   - 学习如何使用每个功能

2. **测试工具** 🧪
   - 快速测试功能
   - 验证参数和返回值

3. **开发参考** 💻
   - 集成到其他应用
   - 自动化脚本开发

4. **调试工具** 🔍
   - 问题排查
   - 接口验证

### 下一步

1. **现在就试试**：http://localhost:8000/docs
2. **创建一个习惯**：用 API 文档测试
3. **发送聊天消息**：看看 AI 如何响应
4. **查看统计数据**：了解你的数据

---

## 💡 实用技巧

### 技巧 1：保存常用请求

在 API 文档中测试成功后，点击 "Copy" 按钮，可以复制为 curl 命令：

```bash
curl -X 'POST' \
  'http://localhost:8000/api/chat' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 1,
  "message": "你好"
}'
```

### 技巧 2：使用 Postman

将 API 文档导出为 OpenAPI 规范，导入到 Postman 中使用：
- 访问：http://localhost:8000/openapi.json
- 在 Postman 中导入此文件

### 技巧 3：查看响应格式

点击 "Schemas" 部分，查看每个对象的详细结构。

---

**现在打开浏览器试试吧！** 🚀

http://localhost:8000/docs
