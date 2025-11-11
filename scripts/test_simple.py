"""
简单测试 - 直接调用 LLM
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("开始测试...")

from configs.settings import get_settings
from app.llm_provider import get_llm_provider

settings = get_settings()
print(f"LLM 提供者: {settings.LLM_PROVIDER}")
print(f"模型: {settings.HUNYUAN_MODEL}")

# 初始化 LLM
llm_kwargs = {
    "secret_id": settings.TENCENT_SECRET_ID,
    "secret_key": settings.TENCENT_SECRET_KEY,
    "model": settings.HUNYUAN_MODEL
}

llm = get_llm_provider(provider_type=settings.LLM_PROVIDER, **llm_kwargs)
print("LLM 初始化成功")

# 测试对话
messages = [
    {"role": "system", "content": "你是一个友好的生活助手。"},
    {"role": "user", "content": "我今天完成了跑步，感觉很好！你能鼓励我一下吗？"}
]

print("\n发送消息...")
response = llm.chat(messages, temperature=0.7, max_tokens=200)

print("\n" + "="*60)
print("AI 响应:")
print(response)
print("="*60)

print("\n✅ 测试成功！")
