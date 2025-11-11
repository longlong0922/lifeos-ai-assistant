"""
快速切换 LLM 提供者
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def show_menu():
    """显示菜单"""
    print("=" * 60)
    print("🔄 LifeOS LLM 提供者切换")
    print("=" * 60)
    print("\n选择 LLM 提供者:")
    print("  1. Mock 模式（测试用，无需 API）")
    print("  2. OpenAI (gpt-3.5-turbo)")
    print("  3. OpenAI (gpt-4)")
    print("  4. 腾讯混元 (hunyuan-lite)")
    print("  5. 腾讯混元 (hunyuan-standard)")
    print("  0. 退出")
    print()


def read_env_file():
    """读取 .env 文件"""
    env_file = project_root / ".env"
    if not env_file.exists():
        return {}
    
    env_vars = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value.strip('"').strip("'")
    
    return env_vars


def write_env_file(env_vars):
    """写入 .env 文件"""
    env_file = project_root / ".env"
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write("# LifeOS AI Assistant 配置文件\n")
        f.write("# 由 switch_provider.py 自动生成\n\n")
        
        # 写入配置
        for key, value in env_vars.items():
            # 如果值包含空格或特殊字符，加引号
            if ' ' in value or any(c in value for c in ['#', '$', '&']):
                f.write(f'{key}="{value}"\n')
            else:
                f.write(f'{key}={value}\n')


def switch_to_mock(env_vars):
    """切换到 Mock 模式"""
    env_vars['LLM_PROVIDER'] = 'mock'
    return env_vars


def switch_to_openai(env_vars, model="gpt-3.5-turbo"):
    """切换到 OpenAI"""
    env_vars['LLM_PROVIDER'] = 'openai'
    env_vars['OPENAI_MODEL'] = model
    
    # 检查 API Key
    if not env_vars.get('OPENAI_API_KEY'):
        print("\n⚠️  警告: OPENAI_API_KEY 未设置")
        api_key = input("请输入 OpenAI API Key (留空跳过): ").strip()
        if api_key:
            env_vars['OPENAI_API_KEY'] = api_key
    
    return env_vars


def switch_to_hunyuan(env_vars, model="hunyuan-lite"):
    """切换到腾讯混元"""
    env_vars['LLM_PROVIDER'] = 'hunyuan'
    env_vars['HUNYUAN_MODEL'] = model
    
    # 检查密钥
    if not env_vars.get('TENCENT_SECRET_ID'):
        print("\n⚠️  警告: TENCENT_SECRET_ID 未设置")
        secret_id = input("请输入 Tencent Secret ID (留空跳过): ").strip()
        if secret_id:
            env_vars['TENCENT_SECRET_ID'] = secret_id
    
    if not env_vars.get('TENCENT_SECRET_KEY'):
        print("\n⚠️  警告: TENCENT_SECRET_KEY 未设置")
        secret_key = input("请输入 Tencent Secret Key (留空跳过): ").strip()
        if secret_key:
            env_vars['TENCENT_SECRET_KEY'] = secret_key
    
    return env_vars


def main():
    """主函数"""
    while True:
        show_menu()
        
        try:
            choice = input("请选择 (0-5): ").strip()
            
            if choice == '0':
                print("\n👋 再见！")
                break
            
            # 读取当前配置
            env_vars = read_env_file()
            
            # 根据选择切换
            if choice == '1':
                env_vars = switch_to_mock(env_vars)
                print("\n✅ 已切换到 Mock 模式")
            
            elif choice == '2':
                env_vars = switch_to_openai(env_vars, "gpt-3.5-turbo")
                print("\n✅ 已切换到 OpenAI (gpt-3.5-turbo)")
            
            elif choice == '3':
                env_vars = switch_to_openai(env_vars, "gpt-4")
                print("\n✅ 已切换到 OpenAI (gpt-4)")
            
            elif choice == '4':
                env_vars = switch_to_hunyuan(env_vars, "hunyuan-lite")
                print("\n✅ 已切换到腾讯混元 (hunyuan-lite)")
            
            elif choice == '5':
                env_vars = switch_to_hunyuan(env_vars, "hunyuan-standard")
                print("\n✅ 已切换到腾讯混元 (hunyuan-standard)")
            
            else:
                print("\n❌ 无效选择，请重试")
                continue
            
            # 保存配置
            write_env_file(env_vars)
            
            print("\n💡 配置已保存到 .env 文件")
            print("   重启服务后生效: python run.py")
            
            # 询问是否测试
            test = input("\n是否测试连接? (y/n): ").strip().lower()
            if test == 'y':
                print("\n运行测试...")
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(project_root / "scripts" / "test_llm.py")],
                    cwd=project_root
                )
            
            input("\n按回车键继续...")
        
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            input("\n按回车键继续...")


if __name__ == "__main__":
    main()
