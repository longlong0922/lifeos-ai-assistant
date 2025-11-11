# 🚀 真实 LLM 版本部署指南

本文档帮助你从 Mock 模式切换到真实的 LLM 提供者（OpenAI 或腾讯混元）。

## 📋 前置要求

### 选项 1: 使用 OpenAI
- OpenAI API 账号
- API Key（从 [OpenAI Platform](https://platform.openai.com/api-keys) 获取）
- 账户余额（需要充值）

### 选项 2: 使用腾讯混元
- 腾讯云账号
- Secret ID 和 Secret Key（从 [腾讯云控制台](https://console.cloud.tencent.com/cam/capi) 获取）
- 开通混元服务

## 🔧 配置步骤

### 1. 安装依赖

```bash
# 如果使用 OpenAI
pip install openai

# 如果使用腾讯混元
pip install tencentcloud-sdk-python
```

### 2. 配置环境变量

编辑项目根目录下的 `.env` 文件：

#### 使用 OpenAI 的配置：

```env
LLM_PROVIDER="openai"
OPENAI_API_KEY="sk-your-actual-api-key-here"
OPENAI_MODEL="gpt-3.5-turbo"

# 可选：如果使用代理或第三方 API
# OPENAI_BASE_URL="https://api.openai.com/v1"
```

#### 使用腾讯混元的配置：

```env
LLM_PROVIDER="hunyuan"
TENCENT_SECRET_ID="your-secret-id"
TENCENT_SECRET_KEY="your-secret-key"
HUNYUAN_MODEL="hunyuan-lite"
```

### 3. 验证配置

运行以下脚本验证 API 配置是否正确：

```bash
python scripts/test_llm.py
```

### 4. 启动服务

```bash
python run.py
```

服务将在 `http://localhost:8000` 启动。

## 📊 模型选择

### OpenAI 模型推荐

| 模型 | 特点 | 成本 | 适用场景 |
|------|------|------|----------|
| gpt-3.5-turbo | 快速、便宜 | ¥0.002/1K tokens | 日常对话 |
| gpt-4 | 高质量、慢 | ¥0.03/1K tokens | 复杂推理 |
| gpt-4-turbo | 平衡性能 | ¥0.01/1K tokens | 推荐使用 |

### 腾讯混元模型推荐

| 模型 | 特点 | 成本 | 适用场景 |
|------|------|------|----------|
| hunyuan-lite | 轻量快速 | 低 | 日常对话 |
| hunyuan-standard | 标准性能 | 中 | 一般使用 |
| hunyuan-pro | 高性能 | 高 | 复杂任务 |

## 🧪 测试 API

### 使用 curl 测试

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "你好，帮我分析一下我的习惯数据"
  }'
```

### 使用 Python 测试

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "user_id": 1,
        "message": "今天跑步完成了！"
    }
)

print(response.json())
```

## ⚠️ 常见问题

### 1. API Key 无效

**问题**: `Invalid API Key` 或 `Unauthorized`

**解决**:
- 检查 `.env` 文件中的 API Key 是否正确
- 确认 API Key 没有被引号包裹
- 检查账户是否有余额

### 2. 请求超时

**问题**: `Request timeout` 或响应很慢

**解决**:
- 检查网络连接
- 如果在中国，可能需要配置代理
- 考虑使用国内的 API 代理服务

### 3. 回退到 Mock 模式

如果 LLM 初始化失败，系统会自动回退到 Mock 模式。检查日志：

```bash
tail -f logs/lifeos.log
```

### 4. 中文支持问题

**OpenAI**: gpt-3.5-turbo 和 gpt-4 都支持中文
**混元**: 原生支持中文，效果更好

## 💰 成本优化建议

1. **使用轻量模型**: 日常对话用 gpt-3.5-turbo 或 hunyuan-lite
2. **控制 token 数**: 设置合理的 `max_tokens` 参数
3. **缓存响应**: 对常见问题使用缓存
4. **限制历史记录**: 只传递必要的对话历史

## 🔒 安全建议

1. **保护 API Key**: 
   - ❌ 不要提交 `.env` 到 Git
   - ✅ 使用 `.gitignore` 排除
   - ✅ 定期轮换 API Key

2. **访问控制**:
   - 使用防火墙限制访问
   - 添加身份验证
   - 监控 API 使用量

3. **错误处理**:
   - 不要在错误消息中暴露 API Key
   - 记录错误日志用于调试

## 📈 监控与日志

查看实时日志：

```bash
tail -f logs/lifeos.log
```

检查 API 调用统计：

```bash
# 访问健康检查端点
curl http://localhost:8000/api/health
```

## 🎯 下一步

配置完成后，你可以：

1. 访问 API 文档: `http://localhost:8000/docs`
2. 运行完整测试: `pytest tests/`
3. 查看使用指南: `USAGE_GUIDE.md`

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件 `logs/lifeos.log`
2. 运行诊断脚本 `python scripts/diagnose.py`
3. 查看 [项目文档](README.md)

---

**注意**: 首次使用真实 LLM 时，建议先用小量数据测试，确认一切正常后再大规模使用。
