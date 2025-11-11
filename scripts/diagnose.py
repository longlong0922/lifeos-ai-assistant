"""
系统诊断脚本 - 检查所有配置和依赖
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_environment():
    """检查环境配置"""
    print("=" * 60)
    print("🔍 LifeOS 系统诊断")
    print("=" * 60)
    
    issues = []
    
    # 1. 检查 Python 版本
    print("\n📌 Python 版本:")
    print(f"   {sys.version}")
    if sys.version_info < (3, 8):
        issues.append("Python 版本过低，需要 3.8+")
        print("   ❌ 版本过低")
    else:
        print("   ✅ 版本合适")
    
    # 2. 检查 .env 文件
    print("\n📌 配置文件:")
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"   ✅ .env 文件存在")
        
        # 读取配置
        try:
            from configs.settings import get_settings
            settings = get_settings()
            print(f"   LLM 提供者: {settings.LLM_PROVIDER}")
            
            if settings.LLM_PROVIDER == "openai":
                if not settings.OPENAI_API_KEY:
                    issues.append("OPENAI_API_KEY 未设置")
                    print("   ❌ OPENAI_API_KEY 未配置")
                else:
                    print("   ✅ OPENAI_API_KEY 已配置")
            
            elif settings.LLM_PROVIDER == "hunyuan":
                if not settings.TENCENT_SECRET_ID or not settings.TENCENT_SECRET_KEY:
                    issues.append("腾讯云密钥未完整配置")
                    print("   ❌ 腾讯云密钥未完整配置")
                else:
                    print("   ✅ 腾讯云密钥已配置")
            
        except Exception as e:
            issues.append(f"配置文件读取失败: {e}")
            print(f"   ❌ 读取失败: {e}")
    else:
        issues.append(".env 文件不存在")
        print("   ❌ .env 文件不存在")
    
    # 3. 检查依赖包
    print("\n📌 依赖包检查:")
    
    required_packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "pydantic": "Pydantic",
        "langgraph": "LangGraph",
    }
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {name}")
        except ImportError:
            issues.append(f"缺少依赖: {package}")
            print(f"   ❌ {name} 未安装")
    
    # 检查 LLM 相关包
    print("\n📌 LLM 依赖检查:")
    
    try:
        from configs.settings import get_settings
        settings = get_settings()
        
        if settings.LLM_PROVIDER == "openai":
            try:
                import openai
                print(f"   ✅ OpenAI SDK (版本: {openai.__version__})")
            except ImportError:
                issues.append("openai 包未安装")
                print("   ❌ OpenAI SDK 未安装")
                print("      安装: pip install openai")
        
        elif settings.LLM_PROVIDER == "hunyuan":
            try:
                import tencentcloud
                print("   ✅ 腾讯云 SDK")
            except ImportError:
                issues.append("tencentcloud-sdk-python 未安装")
                print("   ❌ 腾讯云 SDK 未安装")
                print("      安装: pip install tencentcloud-sdk-python")
    
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
    
    # 4. 检查数据库
    print("\n📌 数据库检查:")
    
    try:
        from configs.settings import get_settings
        settings = get_settings()
        db_path = Path(settings.DB_PATH)
        
        if db_path.exists():
            print(f"   ✅ 数据库文件存在: {db_path}")
            print(f"      大小: {db_path.stat().st_size / 1024:.2f} KB")
        else:
            print(f"   ⚠️  数据库文件不存在，首次运行时会自动创建")
            print(f"      路径: {db_path}")
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
    
    # 5. 检查日志目录
    print("\n📌 日志目录:")
    
    try:
        from configs.settings import get_settings
        settings = get_settings()
        log_path = Path(settings.LOG_FILE)
        log_dir = log_path.parent
        
        if log_dir.exists():
            print(f"   ✅ 日志目录存在: {log_dir}")
        else:
            print(f"   ⚠️  日志目录不存在，将自动创建")
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ 已创建日志目录")
            except Exception as e:
                issues.append(f"无法创建日志目录: {e}")
                print(f"   ❌ 创建失败: {e}")
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
    
    # 6. 网络连接测试（可选）
    print("\n📌 网络连接:")
    
    try:
        import socket
        socket.setdefaulttimeout(3)
        
        # 测试常见的 API 端点
        endpoints = []
        
        try:
            from configs.settings import get_settings
            settings = get_settings()
            
            if settings.LLM_PROVIDER == "openai":
                endpoints.append(("api.openai.com", 443, "OpenAI API"))
            elif settings.LLM_PROVIDER == "hunyuan":
                endpoints.append(("hunyuan.tencentcloudapi.com", 443, "腾讯混元 API"))
        except:
            pass
        
        for host, port, name in endpoints:
            try:
                socket.create_connection((host, port), timeout=3)
                print(f"   ✅ {name} 可访问")
            except Exception as e:
                print(f"   ⚠️  {name} 无法访问: {e}")
                print(f"      这可能是网络问题或需要代理")
    
    except Exception as e:
        print(f"   ⚠️  网络检查失败: {e}")
    
    # 总结
    print("\n" + "=" * 60)
    if issues:
        print("❌ 发现以下问题:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print("\n💡 建议:")
        print("   1. 查看 DEPLOYMENT_GUIDE.md 了解配置步骤")
        print("   2. 运行 pip install -r requirements.txt 安装依赖")
        print("   3. 检查 .env 文件中的 API 配置")
    else:
        print("✅ 所有检查通过！系统配置正常。")
        print("\n🚀 可以运行:")
        print("   python run.py")
    print("=" * 60)
    
    return len(issues) == 0


def main():
    """主函数"""
    success = check_environment()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
