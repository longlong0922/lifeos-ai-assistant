"""
LifeOS - 用户友好版启动器
让用户轻松选择使用方式
"""
import sys
from pathlib import Path
import subprocess

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def clear_screen():
    """清屏"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def show_welcome():
    """显示欢迎界面"""
    clear_screen()
    print("=" * 60)
    print("🌟  欢迎使用 LifeOS AI 生活助手")
    print("=" * 60)
    print("\nLifeOS 可以帮助你：")
    print("  🏃 追踪习惯，找到成功模式")
    print("  🔮 做出更好的决策")
    print("  🎯 拆解和实现目标")
    print("  💭 深度反思，认识自己")
    print("  📋 智能规划每一天")
    print("\n" + "=" * 60)
    print("💡 新用户？查看「新用户快速上手.md」或选择「帮助文档」")
    print("=" * 60)


def show_menu():
    """显示主菜单"""
    print("\n📱 请选择使用方式：\n")
    print("  1. 💬 聊天模式（最简单，推荐新手）")
    print("     - 直接和 AI 对话")
    print("     - 像聊天一样使用\n")
    
    print("  2. 🌐 Web 服务（功能完整）")
    print("     - 在浏览器中使用")
    print("     - 有完整的 API 文档\n")
    
    print("  3. 🎬 功能演示（快速体验）")
    print("     - 自动展示所有功能")
    print("     - 了解 LifeOS 能做什么\n")
    
    print("  4. 🔧 管理工具")
    print("     - 查看数据")
    print("     - 配置设置\n")
    
    print("  5. 📚 帮助文档")
    print("     - 查看使用指南\n")
    
    print("  0. 退出\n")
    print("=" * 60)


def run_chat_mode():
    """启动聊天模式"""
    clear_screen()
    print("启动聊天模式...\n")
    subprocess.run([sys.executable, str(project_root / "scripts" / "chat.py")])


def run_web_service():
    """启动 Web 服务"""
    clear_screen()
    print("=" * 60)
    print("🌐 启动 Web 服务")
    print("=" * 60)
    print("\n服务将在以下地址运行：")
    print("  • 主页: http://localhost:8000")
    print("  • API 文档: http://localhost:8000/docs")
    print("  • 健康检查: http://localhost:8000/api/health")
    print("\n按 Ctrl+C 停止服务\n")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, str(project_root / "run.py")])
    except KeyboardInterrupt:
        print("\n\n服务已停止")


def run_demo():
    """运行功能演示"""
    clear_screen()
    print("启动功能演示...\n")
    subprocess.run([sys.executable, str(project_root / "scripts" / "demo_all.py")])


def show_management_menu():
    """管理工具菜单"""
    while True:
        clear_screen()
        print("=" * 60)
        print("🔧 管理工具")
        print("=" * 60)
        print("\n  1. 📊 查看所有数据")
        print("  2. 👤 查看用户数据")
        print("  3. 🧪 测试 LLM 连接")
        print("  4. 🔄 切换 LLM 提供者")
        print("  5. 🩺 系统诊断")
        print("  6. 📥 加载示例数据")
        print("  0. 返回主菜单\n")
        print("=" * 60)
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            subprocess.run([sys.executable, str(project_root / "scripts" / "show_data.py")])
            input("\n按回车键继续...")
        elif choice == "2":
            subprocess.run([sys.executable, str(project_root / "scripts" / "view_user_data.py")])
            input("\n按回车键继续...")
        elif choice == "3":
            subprocess.run([sys.executable, str(project_root / "scripts" / "test_llm.py")])
            input("\n按回车键继续...")
        elif choice == "4":
            subprocess.run([sys.executable, str(project_root / "scripts" / "switch_provider.py")])
        elif choice == "5":
            subprocess.run([sys.executable, str(project_root / "scripts" / "diagnose.py")])
            input("\n按回车键继续...")
        elif choice == "6":
            subprocess.run([sys.executable, str(project_root / "scripts" / "load_sample_data.py")])
            input("\n按回车键继续...")
        elif choice == "0":
            break
        else:
            print("\n❌ 无效选择，请重试")
            input("按回车键继续...")


def show_help():
    """显示帮助"""
    clear_screen()
    print("=" * 60)
    print("📚 LifeOS 帮助文档")
    print("=" * 60)
    
    docs = [
        ("🎉 新用户快速上手", "新用户快速上手.md"),
        ("📘 用户界面指南", "USER_GUIDE.md"),
        ("📊 查看用户数据", "docs/VIEW_USER_DATA.md"),
        ("🔧 使用指南", "HOW_TO_USE.md"),
        ("⚙️  工作原理", "HOW_IT_WORKS.md"),
        ("🌐 API 指南", "API_GUIDE.md"),
        ("🚀 部署指南", "DEPLOYMENT_GUIDE.md"),
        ("⚡ 快速开始", "QUICK_START_REAL_LLM.md"),
    ]
    
    print("\n可用文档：\n")
    for i, (name, filename) in enumerate(docs, 1):
        filepath = project_root / filename
        exists = "✅" if filepath.exists() else "❌"
        print(f"  {i}. {exists} {name} ({filename})")
    
    print("\n💡 这些文档都在项目根目录中")
    print("   可以用文本编辑器或浏览器打开")
    
    print("\n" + "=" * 60)
    print("快速提示：")
    print("  • 第一次使用？先选择「功能演示」")
    print("  • 日常使用？选择「聊天模式」")
    print("  • 开发应用？选择「Web 服务」")
    print("=" * 60)
    
    input("\n按回车键继续...")


def main():
    """主函数"""
    while True:
        show_welcome()
        show_menu()
        
        choice = input("请输入选项 (0-5): ").strip()
        
        if choice == "1":
            run_chat_mode()
        elif choice == "2":
            run_web_service()
        elif choice == "3":
            run_demo()
        elif choice == "4":
            show_management_menu()
        elif choice == "5":
            show_help()
        elif choice == "0":
            clear_screen()
            print("\n👋 再见！感谢使用 LifeOS！\n")
            break
        else:
            print("\n❌ 无效选择，请输入 0-5 之间的数字")
            input("按回车键继续...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)
