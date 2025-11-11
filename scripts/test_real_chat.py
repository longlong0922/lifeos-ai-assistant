"""
快速测试真实 API 调用
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.settings import get_settings
from app.llm_provider import get_llm_provider
from app.database import Database
from app.graph import LifeOSGraph

def test_real_conversation():
    """测试真实对话"""
    print("=" * 60)
    print("🎯 测试真实 LLM 对话")
    print("=" * 60)
    
    # 初始化
    settings = get_settings()
    print(f"\n📋 使用 {settings.LLM_PROVIDER} ({settings.HUNYUAN_MODEL})")
    
    # 构建参数
    llm_kwargs = {
        "secret_id": settings.TENCENT_SECRET_ID,
        "secret_key": settings.TENCENT_SECRET_KEY,
        "model": settings.HUNYUAN_MODEL
    }
    
    llm = get_llm_provider(
        provider_type=settings.LLM_PROVIDER,
        **llm_kwargs
    )
    
    db = Database(settings.DB_PATH)
    graph = LifeOSGraph(db, llm)
    
    # 测试对话
    test_cases = [
        {
            "user_id": 1,
            "message": "你好！我今天完成了跑步习惯！",
            "expected_intent": "habit"
        },
        {
            "user_id": 1,
            "message": "帮我分析一下最近的习惯完成情况",
            "expected_intent": "habit"
        },
        {
            "user_id": 1,
            "message": "今天要不要去健身房？",
            "expected_intent": "coach"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {test_case['message']}")
        print(f"{'='*60}")
        
        try:
            result = graph.run(
                user_id=test_case["user_id"],
                message=test_case["message"]
            )
            
            print(f"\n✅ 意图识别: {result.get('intent', '未知')}")
            print(f"\n🤖 AI 响应:")
            print(f"   {result['response']}")
            
            if result.get('suggestions'):
                print(f"\n💡 建议:")
                for suggestion in result['suggestions']:
                    print(f"   - {suggestion}")
        
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_real_conversation()
