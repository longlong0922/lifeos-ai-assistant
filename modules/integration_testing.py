"""
集成与验收测试计划
LifeOS 完整的集成步骤、测试用例和评估指标

包含：
1. 集成步骤（LLM、存储、日历、提醒）
2. 端到端测试用例
3. 评估指标与基准
4. 部署检查清单
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# 集成步骤
# ============================================================================

INTEGRATION_STEPS = """
# LifeOS 集成步骤

## 阶段1：核心模块集成（第1周）

### 1.1 LLM 集成
**目标**：接入大语言模型 API

**选项A：OpenAI API**
```python
import openai

openai.api_key = "YOUR_API_KEY"

def call_llm(messages, temperature=0.7):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=temperature,
        max_tokens=1000
    )
    return response.choices[0].message.content
```

**选项B：本地模型（llama.cpp / vLLM）**
```python
from llama_cpp import Llama

llm = Llama(model_path="./models/llama-3-8b.gguf")

def call_llm(messages, temperature=0.7):
    prompt = format_messages_to_prompt(messages)
    response = llm(prompt, temperature=temperature)
    return response['choices'][0]['text']
```

**选项C：云端模型（Azure OpenAI / AWS Bedrock）**

**验收标准**：
- ✅ 能成功调用 LLM API
- ✅ 返回格式正确（JSON 可解析）
- ✅ 平均响应时间 < 3 秒
- ✅ 错误处理完善（超时、限流）

### 1.2 数据库集成
**目标**：存储用户记忆和对话历史

**方案A：SQLite（轻量部署）**
```python
from modules.memory import MemoryStore

store = MemoryStore("lifeos_data.db")
```

**方案B：PostgreSQL（生产环境）**
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="lifeos",
    user="user",
    password="password"
)
```

**验收标准**：
- ✅ 记忆读写正常
- ✅ 支持并发访问
- ✅ 数据持久化
- ✅ 备份恢复机制

### 1.3 模块互联
**目标**：连接所有核心模块

```python
# 主控制器
from modules.conversation_flow import ConversationFlowManager
from modules.smart_summary import SmartSummaryParser
from modules.next_action import NextActionParser
from modules.memory import MemoryManager

class LifeOSCore:
    def __init__(self):
        self.flow_manager = ConversationFlowManager()
        self.memory_manager = MemoryManager(store)
        self.summary_parser = SmartSummaryParser()
        self.action_parser = NextActionParser()
    
    def process_user_input(self, user_id, user_input):
        # 1. 意图分类
        mode, classification, _ = self.flow_manager.route(user_input)
        
        # 2. 获取用户画像
        profile = self.memory_manager.get_user_profile(user_id)
        
        # 3. 调用 LLM
        if mode == ConversationMode.ACTION_ASSISTANT:
            # 生成摘要或拆解
            pass
        
        # 4. 解析结果
        # 5. 返回响应
        pass
```

**验收标准**：
- ✅ 所有模块正常导入
- ✅ 端到端流程跑通
- ✅ 错误能被正确捕获


## 阶段2：外部集成（第2周）

### 2.1 日历集成
**目标**：支持添加事件到用户日历

**Google Calendar API**
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def add_to_google_calendar(event_data):
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('calendar', 'v3', credentials=creds)
    
    event = {
        'summary': event_data['title'],
        'start': {'dateTime': event_data['start_time']},
        'end': {'dateTime': event_data['end_time']},
    }
    
    return service.events().insert(calendarId='primary', body=event).execute()
```

**iCal 格式导出**
```python
from icalendar import Calendar, Event

def export_to_ical(events):
    cal = Calendar()
    for event_data in events:
        event = Event()
        event.add('summary', event_data['title'])
        event.add('dtstart', event_data['start_time'])
        cal.add_component(event)
    
    return cal.to_ical()
```

**验收标准**：
- ✅ 能添加事件到日历
- ✅ OAuth 授权流程完整
- ✅ 支持修改和删除事件

### 2.2 提醒/通知集成
**目标**：发送提醒通知给用户

**桌面通知（Web）**
```javascript
if ('Notification' in window) {
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            new Notification('LifeOS 提醒', {
                body: '该开始你的任务了！',
                icon: '/icon.png'
            });
        }
    });
}
```

**移动推送（Firebase Cloud Messaging）**
```python
from firebase_admin import messaging

def send_push_notification(user_token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=user_token,
    )
    return messaging.send(message)
```

**邮件提醒**
```python
import smtplib
from email.mime.text import MIMEText

def send_email_reminder(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'lifeos@example.com'
    msg['To'] = to_email
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.send_message(msg)
```

**验收标准**：
- ✅ 通知能准时送达
- ✅ 支持多种通知渠道
- ✅ 用户可以配置通知偏好


## 阶段3：API 与前端集成（第3周）

### 3.1 REST API
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        response = lifeos_core.process_user_input(
            request.user_id, 
            request.message
        )
        return {"success": True, "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{user_id}/profile")
async def get_profile(user_id: str):
    profile = memory_manager.get_user_profile(user_id)
    return {"success": True, "data": profile}
```

### 3.2 WebSocket（流式响应）
```python
from fastapi import WebSocket

@app.websocket("/ws/chat")
async def chat_stream(websocket: WebSocket):
    await websocket.accept()
    
    async for data in websocket.iter_text():
        request = json.loads(data)
        
        # 流式生成响应
        async for chunk in lifeos_core.stream_response(request):
            await websocket.send_json(chunk)
```

**验收标准**：
- ✅ API 文档完整（Swagger）
- ✅ 错误处理规范
- ✅ 性能测试通过（QPS > 100）
- ✅ 前端能正常调用


## 阶段4：部署与监控（第4周）

### 4.1 Docker 容器化
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 监控与日志
```python
import logging
from prometheus_client import Counter, Histogram

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lifeos")

# 指标收集
chat_requests = Counter('lifeos_chat_requests_total', 'Total chat requests')
response_time = Histogram('lifeos_response_time_seconds', 'Response time')

@app.middleware("http")
async def add_metrics(request, call_next):
    chat_requests.inc()
    with response_time.time():
        response = await call_next(request)
    return response
```

**验收标准**：
- ✅ 能通过 Docker 部署
- ✅ 日志收集完整
- ✅ 监控指标可查询
- ✅ 告警机制正常
"""


# ============================================================================
# 端到端测试用例
# ============================================================================

@dataclass
class TestCase:
    """测试用例"""
    id: str
    name: str
    scenario: str
    user_input: str
    expected_mode: str
    expected_output_type: str
    success_criteria: List[str]


E2E_TEST_CASES = [
    TestCase(
        id="E2E-001",
        name="情绪支持基础场景",
        scenario="用户表达疲惫",
        user_input="我好累啊，不想动",
        expected_mode="emotion_support",
        expected_output_type="text_with_options",
        success_criteria=[
            "回复包含同理心表达",
            "回复长度 < 100 字",
            "提供 1-2 个选项",
            "不包含长篇说教"
        ]
    ),
    
    TestCase(
        id="E2E-002",
        name="任务摘要场景",
        scenario="用户列出多个任务",
        user_input="今天要写报告、开会、买菜、付房租",
        expected_mode="action_assistant",
        expected_output_type="summary_card",
        success_criteria=[
            "返回结构化 JSON",
            "包含优先级排序",
            "包含建议的下一步",
            "响应时间 < 5 秒"
        ]
    ),
    
    TestCase(
        id="E2E-003",
        name="任务拆解场景",
        scenario="用户需要拆解复杂任务",
        user_input="我要学习 Python 数据分析",
        expected_mode="action_assistant",
        expected_output_type="action_cards",
        success_criteria=[
            "返回 3-5 个具体步骤",
            "第一步预计时间 <= 5 分钟",
            "每个步骤可执行",
            "包含时间估算"
        ]
    ),
    
    TestCase(
        id="E2E-004",
        name="混合模式场景",
        scenario="用户同时表达情绪和任务",
        user_input="我感觉好累，今天还有好多事做不完",
        expected_mode="mixed",
        expected_output_type="text_with_action_invite",
        success_criteria=[
            "先安抚情绪（≤20字）",
            "提供转行动的选项",
            "不立即列任务清单",
            "给用户选择权"
        ]
    ),
    
    TestCase(
        id="E2E-005",
        name="决策咨询场景",
        scenario="用户需要帮助做决策",
        user_input="我不知道要不要接受这个加班任务",
        expected_mode="action_assistant",
        expected_output_type="decision_analysis",
        success_criteria=[
            "列出利弊分析",
            "给出建议",
            "考虑用户偏好",
            "不做绝对判断"
        ]
    ),
    
    TestCase(
        id="E2E-006",
        name="记忆引用场景",
        scenario="系统引用用户偏好",
        user_input="帮我安排明天的学习时间",
        expected_mode="action_assistant",
        expected_output_type="text_with_calendar",
        success_criteria=[
            "根据用户时间偏好建议",
            "自然引用记忆（如'你说过早上效率高'）",
            "提供加入日历选项",
            "时间建议合理"
        ]
    ),
    
    TestCase(
        id="E2E-007",
        name="模式切换场景",
        scenario="从情绪模式切换到行动模式",
        user_input="【第1轮】我好焦虑\n【第2轮】帮我做点什么缓解一下",
        expected_mode="action_assistant",
        expected_output_type="action_cards",
        success_criteria=[
            "第1轮返回情绪支持",
            "第2轮切换到行动模式",
            "提供具体缓解动作",
            "切换流畅"
        ]
    ),
    
    TestCase(
        id="E2E-008",
        name="边缘情况：空输入",
        scenario="用户发送空消息",
        user_input="",
        expected_mode="unknown",
        expected_output_type="clarification",
        success_criteria=[
            "友好提示用户",
            "提供示例输入",
            "不报错",
            "响应迅速"
        ]
    ),
    
    TestCase(
        id="E2E-009",
        name="边缘情况：过长输入",
        scenario="用户输入超长文本",
        user_input="今天要做" + "、做事" * 100,
        expected_mode="action_assistant",
        expected_output_type="summary_card",
        success_criteria=[
            "能正常处理",
            "返回摘要而非全部",
            "不超时",
            "提示用户输入过长"
        ]
    ),
    
    TestCase(
        id="E2E-010",
        name="完整工作流",
        scenario="从输入到完成任务的完整流程",
        user_input="【1】我今天要写报告\n【2】开始执行\n【3】完成了",
        expected_mode="multiple",
        expected_output_type="workflow",
        success_criteria=[
            "第1轮：拆解任务",
            "第2轮：确认开始",
            "第3轮：庆祝完成",
            "全流程 < 30 秒"
        ]
    )
]


# ============================================================================
# 评估指标
# ============================================================================

EVALUATION_METRICS = {
    "功能指标": {
        "意图分类准确率": {
            "目标": "> 90%",
            "计算方法": "正确分类数 / 总测试样本数",
            "测试集大小": "≥ 500 条标注样本"
        },
        "模式切换准确率": {
            "目标": "> 85%",
            "计算方法": "正确切换数 / 需要切换的场景数",
            "测试集大小": "≥ 200 条场景"
        },
        "JSON 输出正确率": {
            "目标": "> 95%",
            "计算方法": "可解析的 JSON / 总输出数",
            "测试集大小": "≥ 1000 次调用"
        },
        "任务拆解合理性": {
            "目标": "> 80%",
            "计算方法": "人工评分 ≥ 4 分（满分5分）的比例",
            "评估人数": "≥ 3 人"
        }
    },
    
    "性能指标": {
        "平均响应时间": {
            "目标": "< 3 秒（P95 < 5 秒）",
            "测量工具": "Prometheus + Grafana",
            "负载条件": "QPS = 50"
        },
        "并发处理能力": {
            "目标": "≥ 100 QPS",
            "测试工具": "Apache Bench / Locust",
            "成功率要求": "> 99%"
        },
        "内存占用": {
            "目标": "< 2GB（含模型）",
            "测量方式": "Docker stats",
            "持续时间": "24 小时稳定运行"
        }
    },
    
    "用户体验指标": {
        "建议接受率": {
            "目标": "> 40%",
            "定义": "用户实际执行推荐动作的比例",
            "跟踪周期": "7 天"
        },
        "任务完成率": {
            "目标": "> 60%",
            "定义": "被推荐的任务最终被完成的比例",
            "跟踪周期": "30 天"
        },
        "用户满意度": {
            "目标": "> 4.0 / 5.0",
            "收集方式": "每次对话后可选评分",
            "最小样本": "≥ 100 条反馈"
        },
        "日活跃用户留存": {
            "目标": "次日留存 > 60%，7日留存 > 40%",
            "计算方式": "活跃用户数 / 新用户数",
            "跟踪工具": "Google Analytics / Mixpanel"
        }
    },
    
    "质量指标": {
        "同理心得分": {
            "目标": "> 4.0 / 5.0",
            "适用场景": "情绪支持模式",
            "评估方式": "人工盲测"
        },
        "可执行性得分": {
            "目标": "> 4.0 / 5.0",
            "适用场景": "行动助理模式",
            "评估方式": "用户能否理解并执行"
        },
        "记忆准确率": {
            "目标": "> 90%",
            "定义": "正确引用记忆 / 总引用次数",
            "跟踪周期": "持续"
        }
    }
}


# ============================================================================
# 部署检查清单
# ============================================================================

DEPLOYMENT_CHECKLIST = """
# LifeOS 部署检查清单

## 部署前（Pre-deployment）

### 代码质量
- [ ] 所有单元测试通过（覆盖率 > 80%）
- [ ] 集成测试通过（全部10个E2E用例）
- [ ] 代码审查完成
- [ ] 无已知的 P0/P1 Bug
- [ ] 依赖项安全扫描通过

### 配置检查
- [ ] 环境变量正确配置
- [ ] API 密钥安全存储
- [ ] 数据库连接测试通过
- [ ] 日志级别适当（生产环境 INFO）
- [ ] 错误监控已配置（Sentry/Rollbar）

### 性能测试
- [ ] 压力测试通过（100 QPS 持续 10 分钟）
- [ ] 内存泄漏检测通过
- [ ] 响应时间达标（P95 < 5秒）
- [ ] 数据库索引优化完成

### 安全检查
- [ ] SQL 注入防护
- [ ] XSS 防护
- [ ] CSRF Token 启用
- [ ] HTTPS 证书有效
- [ ] 敏感数据加密（用户记忆）
- [ ] 权限控制测试通过


## 部署中（During Deployment）

### 基础设施
- [ ] 服务器资源充足（CPU/内存/磁盘）
- [ ] 数据库备份完成
- [ ] 负载均衡器配置
- [ ] CDN 缓存配置
- [ ] DNS 记录更新

### 容器/服务
- [ ] Docker 镜像构建成功
- [ ] 容器健康检查配置
- [ ] 自动重启策略设置
- [ ] 环境变量注入成功
- [ ] 端口映射正确


## 部署后（Post-deployment）

### 冒烟测试
- [ ] 健康检查端点响应正常
- [ ] 基本聊天功能正常
- [ ] 数据库连接正常
- [ ] LLM API 调用正常
- [ ] 前端页面加载正常

### 监控验证
- [ ] 日志正常输出
- [ ] 指标正常上报（Prometheus）
- [ ] 告警规则生效
- [ ] Dashboard 显示正常
- [ ] 错误追踪正常（Sentry）

### 业务验证
- [ ] 10个E2E测试用例全部通过
- [ ] 用户注册/登录正常
- [ ] 记忆存储和读取正常
- [ ] 日历集成正常（如启用）
- [ ] 通知推送正常（如启用）

### 回滚准备
- [ ] 回滚脚本准备完成
- [ ] 上一版本镜像保留
- [ ] 数据库回滚方案明确
- [ ] 回滚决策阈值定义（如错误率 > 5%）


## 发布后（Post-release）

### 7天观察期
- [ ] 每日检查核心指标
- [ ] 收集用户反馈
- [ ] 监控错误率和响应时间
- [ ] 检查资源使用情况
- [ ] 准备热修复（如需要）

### 持续优化
- [ ] A/B 测试新 prompt
- [ ] 收集训练数据（用户授权）
- [ ] 定期重训练模型
- [ ] 更新文档和 FAQ
- [ ] 优化慢查询


## 应急响应

### 紧急情况联系人
- 技术负责人：[姓名] [电话]
- 运维负责人：[姓名] [电话]
- 产品负责人：[姓名] [电话]

### 常见问题快速修复
1. **LLM API 超时**：切换到备用 API 或降级到规则响应
2. **数据库连接失败**：检查连接池，重启服务
3. **内存溢出**：增加资源限制，重启容器
4. **响应时间过长**：启用缓存，优化查询

### 回滚流程
```bash
# 1. 停止当前版本
docker stop lifeos_app

# 2. 启动上一版本
docker run -d --name lifeos_app lifeos:v1.0.0

# 3. 验证健康检查
curl http://localhost:8000/health

# 4. 数据库回滚（如需要）
psql -U user -d lifeos < backup_v1.0.0.sql
```
"""


# ============================================================================
# 测试脚本示例
# ============================================================================

TEST_SCRIPT = '''
"""
自动化测试脚本
运行所有 E2E 测试用例
"""

import asyncio
import requests
from typing import Dict, List

API_BASE_URL = "http://localhost:8000"

async def run_test_case(test_case: TestCase) -> Dict:
    """运行单个测试用例"""
    print(f"\\n[{test_case.id}] {test_case.name}")
    print(f"场景: {test_case.scenario}")
    print(f"输入: {test_case.user_input}")
    
    # 发送请求
    response = requests.post(
        f"{API_BASE_URL}/api/chat",
        json={"user_id": "test_user", "message": test_case.user_input},
        timeout=10
    )
    
    # 验证
    passed = True
    results = []
    
    for criteria in test_case.success_criteria:
        # 这里需要实现具体的验证逻辑
        check_passed = True  # placeholder
        results.append({"criteria": criteria, "passed": check_passed})
        if not check_passed:
            passed = False
    
    print(f"结果: {'✅ PASSED' if passed else '❌ FAILED'}")
    
    return {
        "test_id": test_case.id,
        "passed": passed,
        "details": results,
        "response_time": response.elapsed.total_seconds()
    }


async def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("LifeOS E2E 测试套件")
    print("="*60)
    
    results = []
    for test_case in E2E_TEST_CASES:
        result = await run_test_case(test_case)
        results.append(result)
    
    # 统计
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    
    print("\\n" + "="*60)
    print(f"测试完成: {passed}/{total} 通过")
    print("="*60)
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
'''


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    'INTEGRATION_STEPS',
    'E2E_TEST_CASES',
    'EVALUATION_METRICS',
    'DEPLOYMENT_CHECKLIST',
    'TEST_SCRIPT'
]


if __name__ == "__main__":
    print("=" * 60)
    print("LifeOS 集成与测试计划")
    print("=" * 60)
    
    print("\n📋 E2E 测试用例总数:", len(E2E_TEST_CASES))
    print("\n前 3 个测试用例:")
    for tc in E2E_TEST_CASES[:3]:
        print(f"\n  [{tc.id}] {tc.name}")
        print(f"  输入: {tc.user_input}")
        print(f"  期望模式: {tc.expected_mode}")
        print(f"  成功标准: {len(tc.success_criteria)} 条")
    
    print("\n" + "=" * 60)
    print("\n📊 评估指标类别:")
    for category in EVALUATION_METRICS:
        metrics = EVALUATION_METRICS[category]
        print(f"\n  {category}: {len(metrics)} 个指标")
        for name in list(metrics.keys())[:2]:
            print(f"    - {name}: {metrics[name]['目标']}")
