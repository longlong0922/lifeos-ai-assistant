#!/usr/bin/env python3
"""
清理多余文件脚本
删除不再使用的旧文件和目录
"""
import os
import shutil
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent

# 要删除的文件和目录
files_to_delete = [
    "main.py",  # 旧的命令行入口，已被 start.py 和 run.py 替代
    "CHANGELOG_REAL_LLM.md",  # 临时的更新日志
    "QUICK_REFERENCE.md",  # 与其他文档重复
]

dirs_to_delete = [
    "lifeos_ai_assistant",  # 旧代码目录，已迁移到 app/
    "demo",  # 旧演示代码，已集成到 scripts/
    "__pycache__",  # Python 缓存
]

# 建议合并但不删除的文档（需要手动检查）
docs_to_review = [
    ("USAGE_GUIDE.md", "USER_GUIDE.md", "内容可能重复，建议合并"),
]


def delete_file(filepath: Path):
    """删除文件"""
    if filepath.exists():
        try:
            filepath.unlink()
            print(f"✅ 已删除文件: {filepath.name}")
            return True
        except Exception as e:
            print(f"❌ 删除文件失败 {filepath.name}: {e}")
            return False
    else:
        print(f"⏭️  文件不存在: {filepath.name}")
        return False


def delete_directory(dirpath: Path):
    """删除目录"""
    if dirpath.exists() and dirpath.is_dir():
        try:
            shutil.rmtree(dirpath)
            print(f"✅ 已删除目录: {dirpath.name}/")
            return True
        except Exception as e:
            print(f"❌ 删除目录失败 {dirpath.name}/: {e}")
            return False
    else:
        print(f"⏭️  目录不存在: {dirpath.name}/")
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("🧹 LifeOS 文件清理工具")
    print("=" * 70)
    
    # 显示将要删除的内容
    print("\n📋 将要删除的文件：")
    for file in files_to_delete:
        filepath = project_root / file
        status = "✓ 存在" if filepath.exists() else "✗ 不存在"
        print(f"  • {file} ({status})")
    
    print("\n📋 将要删除的目录：")
    for dir_name in dirs_to_delete:
        dirpath = project_root / dir_name
        status = "✓ 存在" if dirpath.exists() else "✗ 不存在"
        print(f"  • {dir_name}/ ({status})")
    
    print("\n📋 建议手动检查的文档：")
    for doc1, doc2, reason in docs_to_review:
        print(f"  • {doc1} vs {doc2}")
        print(f"    {reason}")
    
    # 确认
    print("\n" + "=" * 70)
    confirm = input("\n⚠️  确认要删除这些文件吗？(yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\n❌ 已取消清理")
        return
    
    print("\n" + "=" * 70)
    print("开始清理...")
    print("=" * 70)
    
    # 删除文件
    print("\n🗑️  删除文件：")
    deleted_files = 0
    for file in files_to_delete:
        filepath = project_root / file
        if delete_file(filepath):
            deleted_files += 1
    
    # 删除目录
    print("\n🗑️  删除目录：")
    deleted_dirs = 0
    for dir_name in dirs_to_delete:
        dirpath = project_root / dir_name
        if delete_directory(dirpath):
            deleted_dirs += 1
    
    # 总结
    print("\n" + "=" * 70)
    print("✨ 清理完成！")
    print("=" * 70)
    print(f"📊 统计：")
    print(f"  • 删除文件: {deleted_files}/{len(files_to_delete)}")
    print(f"  • 删除目录: {deleted_dirs}/{len(dirs_to_delete)}")
    
    print("\n💡 提示：")
    print("  1. 建议手动检查并合并重复的文档")
    print("  2. 可以运行 git status 查看变更")
    print("  3. 如需恢复，可以使用 git checkout 命令")
    
    print("\n🎯 下一步：")
    print("  • 检查 USAGE_GUIDE.md 和 USER_GUIDE.md 是否有重复内容")
    print("  • 考虑合并到一个文件中")
    print("  • 更新 README.md 中的文档链接")


if __name__ == "__main__":
    main()
