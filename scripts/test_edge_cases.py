"""
测试各种特殊字符和边界情况
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.settings import get_settings
from app.llm_provider import get_llm_provider

settings = get_settings()
llm_kwargs = {
    "secret_id": settings.TENCENT_SECRET_ID,
    "secret_key": settings.TENCENT_SECRET_KEY,
    "model": settings.HUNYUAN_MODEL
}

llm = get_llm_provider(provider_type=settings.LLM_PROVIDER, **llm_kwargs)

print("="*60)
print("🧪 测试特殊字符处理")
print("="*60)

# 测试用例：包含各种可能导致JSON解析错误的字符
test_cases = [
    {
        "name": "包含引号",
        "message": '我说："今天真好！"'
    },
    {
        "name": "包含单引号",
        "message": "I'm feeling great!"
    },
    {
        "name": "包含换行符",
        "message": "今天完成了：\n1. 跑步\n2. 阅读"
    },
    {
        "name": "包含特殊符号",
        "message": "完成率：100%！🎉🎊"
    },
    {
        "name": "包含列表",
        "message": "我的习惯：['跑步', '阅读', '冥想']"
    },
    {
        "name": "混合中英文",
        "message": "今天running了5km，感觉awesome！"
    },
    {
        "name": "包含反斜杠",
        "message": "路径：C:\\Users\\test\\file.txt"
    },
    {
        "name": "长文本",
        "message": "今天" + "非常" * 50 + "开心！"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n测试 {i}: {test['name']}")
    print(f"消息: {test['message'][:50]}...")
    
    try:
        messages = [
            {"role": "system", "content": "你是友好的助手"},
            {"role": "user", "content": test['message']}
        ]
        
        response = llm.chat(messages, temperature=0.7, max_tokens=50)
        print(f"✅ 成功 - 响应: {response[:50]}...")
    
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("✅ 特殊字符测试完成")
print("="*60)
