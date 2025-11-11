"""
测试复杂消息场景
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.settings import get_settings
from app.llm_provider import get_llm_provider

settings = get_settings()
print(f"测试 {settings.LLM_PROVIDER}...")

llm_kwargs = {
    "secret_id": settings.TENCENT_SECRET_ID,
    "secret_key": settings.TENCENT_SECRET_KEY,
    "model": settings.HUNYUAN_MODEL
}

llm = get_llm_provider(provider_type=settings.LLM_PROVIDER, **llm_kwargs)

# 测试包含中文、标点符号、特殊字符的消息
test_cases = [
    {
        "name": "简单中文",
        "messages": [
            {"role": "system", "content": "你是生活助手"},
            {"role": "user", "content": "你好"}
        ]
    },
    {
        "name": "复杂中文和标点",
        "messages": [
            {"role": "system", "content": "你是LifeOS，用户的AI生活助理和教练。"},
            {"role": "user", "content": "我今天完成了跑步！感觉很好，但有点累..."}
        ]
    },
    {
        "name": "多轮对话",
        "messages": [
            {"role": "system", "content": "你是友好的助手"},
            {"role": "user", "content": "我想学Python"},
            {"role": "assistant", "content": "很好的选择！"},
            {"role": "user", "content": "怎么开始？"}
        ]
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*60}")
    print(f"测试 {i}: {test['name']}")
    print(f"{'='*60}")
    
    try:
        response = llm.chat(test['messages'], temperature=0.7, max_tokens=100)
        print(f"✅ 成功")
        print(f"响应: {response[:100]}...")
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("测试完成")
print("="*60)
