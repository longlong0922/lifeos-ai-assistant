# 🚀 从 Mock 模式切换到真实 LLM

## 快速步骤

### 1️⃣ 选择 LLM 提供者

#### 选项 A: OpenAI (推荐)
- **优点**: 质量高、稳定、中英文都好
- **缺点**: 需要翻墙、按量付费
- **成本**: gpt-3.5-turbo ~¥0.002/1K tokens

#### 选项 B: 腾讯混元
- **优点**: 国内访问、中文优化
- **缺点**: 功能相对有限
- **成本**: hunyuan-lite 较便宜

### 2️⃣ 获取 API 密钥

**OpenAI:**
1. 访问 https://platform.openai.com/api-keys
2. 注册并创建 API Key
3. 账户充值（最低 $5）

**腾讯混元:**
1. 访问 https://console.cloud.tencent.com/cam/capi
2. 创建 Secret ID 和 Secret Key
3. 开通混元服务

### 3️⃣ 配置项目

**方法 1: 使用切换脚本（推荐）**
```powershell
python scripts\switch_provider.py
```
按提示选择提供者并输入 API 密钥。

**方法 2: 手动编辑 .env**
```env
# 使用 OpenAI
LLM_PROVIDER="openai"
OPENAI_API_KEY="sk-your-api-key-here"
OPENAI_MODEL="gpt-3.5-turbo"

# 或使用腾讯混元
LLM_PROVIDER="hunyuan"
TENCENT_SECRET_ID="your-secret-id"
TENCENT_SECRET_KEY="your-secret-key"
HUNYUAN_MODEL="hunyuan-lite"
```

### 4️⃣ 测试配置

```powershell
# 测试 LLM 连接
python scripts\test_llm.py

# 系统诊断
python scripts\diagnose.py
```

### 5️⃣ 启动服务

```powershell
python run.py
```

访问 http://localhost:8000/docs 开始使用！

## 常见问题

### Q: API Key 在哪里填写？
A: 在项目根目录的 `.env` 文件中，或运行 `python scripts\switch_provider.py`。

### Q: 提示 API Key 无效？
A: 
1. 检查 Key 是否正确复制（没有多余空格）
2. OpenAI 账户是否有余额
3. 网络是否能访问 API（可能需要代理）

### Q: 成本如何？
A: 
- Mock 模式：免费
- OpenAI gpt-3.5-turbo: 一次对话约 ¥0.01-0.05
- 腾讯混元: 更便宜，具体看腾讯云定价

### Q: 可以混合使用吗？
A: 当前只能选择一个提供者，但可以随时用 `switch_provider.py` 切换。

### Q: 出错了怎么办？
A: 
1. 运行 `python scripts\diagnose.py` 诊断
2. 查看 `logs/lifeos.log` 日志
3. 参考 `DEPLOYMENT_GUIDE.md` 详细文档

## 下一步

配置完成后，建议：
1. 阅读 [使用指南](USAGE_GUIDE.md)
2. 尝试不同的对话场景
3. 调整 prompt 模板（在 `app/llm_provider.py` 中）

---

**💡 提示**: 刚开始可以用 Mock 模式测试功能，确认无误后再配置真实 LLM。
