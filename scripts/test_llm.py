"""
测试 LLM 配置是否正确
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configs.settings import get_settings
from app.llm_provider import get_llm_provider


def test_llm_connection():
    """测试 LLM 连接"""
    print("=" * 60)
    print("🧪 LifeOS LLM 配置测试")
    print("=" * 60)
    
    settings = get_settings()
    
    print(f"\n📋 当前配置:")
    print(f"   LLM 提供者: {settings.LLM_PROVIDER}")
    
    if settings.LLM_PROVIDER == "openai":
        print(f"   模型: {settings.OPENAI_MODEL}")
        print(f"   API Key: {'已设置' if settings.OPENAI_API_KEY else '❌ 未设置'}")
        if settings.OPENAI_BASE_URL:
            print(f"   Base URL: {settings.OPENAI_BASE_URL}")
    elif settings.LLM_PROVIDER == "hunyuan":
        print(f"   模型: {settings.HUNYUAN_MODEL}")
        print(f"   Secret ID: {'已设置' if settings.TENCENT_SECRET_ID else '❌ 未设置'}")
        print(f"   Secret Key: {'已设置' if settings.TENCENT_SECRET_KEY else '❌ 未设置'}")
    
    print("\n🔌 正在初始化 LLM 提供者...")
    
    try:
        # 构建参数
        llm_kwargs = {}
        
        if settings.LLM_PROVIDER == "openai":
            llm_kwargs = {
                "api_key": settings.OPENAI_API_KEY,
                "model": settings.OPENAI_MODEL
            }
            if settings.OPENAI_BASE_URL:
                llm_kwargs["base_url"] = settings.OPENAI_BASE_URL
        elif settings.LLM_PROVIDER == "hunyuan":
            llm_kwargs = {
                "secret_id": settings.TENCENT_SECRET_ID,
                "secret_key": settings.TENCENT_SECRET_KEY,
                "model": settings.HUNYUAN_MODEL
            }
        
        llm = get_llm_provider(
            provider_type=settings.LLM_PROVIDER,
            **llm_kwargs
        )
        
        print("✅ LLM 提供者初始化成功")
        
    except Exception as e:
        print(f"❌ LLM 提供者初始化失败: {e}")
        print("\n💡 请检查:")
        print("   1. .env 文件是否存在")
        print("   2. API Key 是否正确配置")
        print("   3. 相关依赖是否已安装")
        return False
    
    print("\n📤 正在发送测试请求...")
    
    try:
        test_messages = [
            {"role": "system", "content": "你是一个友好的 AI 助手。"},
            {"role": "user", "content": "请用一句话介绍你自己"}
        ]
        
        response = llm.chat(test_messages, temperature=0.7, max_tokens=100)
        
        print("✅ 测试请求成功")
        print(f"\n📝 AI 响应:\n{response}\n")
        
        print("=" * 60)
        print("🎉 所有测试通过！LLM 配置正确。")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 测试请求失败: {e}")
        print("\n💡 可能的原因:")
        print("   1. API Key 无效或已过期")
        print("   2. 账户余额不足")
        print("   3. 网络连接问题")
        print("   4. API 服务暂时不可用")
        return False


def main():
    """主函数"""
    success = test_llm_connection()
    
    if not success:
        print("\n❌ 测试失败。请参考 DEPLOYMENT_GUIDE.md 进行配置。")
        sys.exit(1)
    else:
        print("\n✅ 可以开始使用 LifeOS 了！")
        print("   运行: python run.py")
        sys.exit(0)


if __name__ == "__main__":
    main()
