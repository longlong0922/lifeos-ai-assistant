"""
完整系统测试 - 测试习惯追踪功能
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.settings import get_settings
from app.llm_provider import get_llm_provider
from app.database import Database
from app.graph import LifeOSGraph

print("="*60)
print("🧪 完整系统测试 - 习惯追踪")
print("="*60)

# 初始化
settings = get_settings()
print(f"\n初始化 {settings.LLM_PROVIDER}...")

llm_kwargs = {
    "secret_id": settings.TENCENT_SECRET_ID,
    "secret_key": settings.TENCENT_SECRET_KEY,
    "model": settings.HUNYUAN_MODEL
}

llm = get_llm_provider(provider_type=settings.LLM_PROVIDER, **llm_kwargs)
db = Database(settings.DB_PATH)
graph = LifeOSGraph(db, llm)

print("✅ 初始化完成\n")

# 测试场景
test_messages = [
    "我今天完成了跑步！跑了5公里，感觉很棒！",
    "今天没去跑步，感觉有点累...",
    "帮我分析一下最近的习惯情况"
]

user_id = 1

for i, message in enumerate(test_messages, 1):
    print(f"\n{'='*60}")
    print(f"测试 {i}/{len(test_messages)}")
    print(f"{'='*60}")
    print(f"用户: {message}")
    print("\nAI 思考中...")
    
    try:
        result = graph.run(user_id=user_id, message=message)
        
        print(f"\n✅ 成功")
        print(f"意图: {result.get('intent', '未知')}")
        print(f"\nAI 响应:")
        print(result['response'])
        
        if result.get('suggestions'):
            print("\n建议:")
            for sug in result['suggestions']:
                print(f"  • {sug}")
    
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        break

print("\n" + "="*60)
print("✅ 测试完成")
print("="*60)
