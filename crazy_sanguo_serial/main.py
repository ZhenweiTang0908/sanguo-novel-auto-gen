#!/usr/bin/env python3
"""
疯狂三国连载器 - 主入口
Crazy Sanguo Serial Writer

用法:
    python main.py                    # 交互模式
    python main.py --chapters 3       # 直接生成3章
    python main.py --init              # 重新初始化故事
    python main.py --status           # 查看当前状态
"""

import os
import sys
import argparse
import logging
from typing import Optional

# 设置工作目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="疯狂三国连载器 - 自动生成魔改三国小说",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                    # 交互模式
  python main.py --chapters 3       # 生成3章
  python main.py --chapters 5 --temperature 1.1  # 高温模式生成5章
  python main.py --init             # 重新初始化
  python main.py --status           # 查看状态

环境变量:
  DASHSCOPE_API_KEY    阿里云百炼 API Key（必须设置）
"""
    )
    
    parser.add_argument(
        '-c', '--chapters',
        type=int,
        default=0,
        help='要生成的章节数（默认进入交互模式）'
    )
    
    parser.add_argument(
        '-l', '--chapter-length',
        type=int,
        default=2000,
        help='每章目标字数（默认2000）'
    )
    
    parser.add_argument(
        '-t', '--temperature',
        type=float,
        default=0.85,
        help='生成温度（默认0.85，范围0-1.5）'
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='强制重新初始化故事'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='仅显示当前状态'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    return parser.parse_args()


def check_environment():
    """检查环境变量"""
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 错误：未设置 DASHSCOPE_API_KEY 环境变量")
        print()
        print("请执行以下命令设置 API Key：")
        print("  export DASHSCOPE_API_KEY='your-api-key-here'")
        print()
        print("或者在命令行直接运行：")
        print("  DASHSCOPE_API_KEY='your-key' python main.py")
        return False
    return True


def show_banner():
    """显示横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🏯  疯 狂 三 国 · 魔 改 演 义  🏯                      ║
║                                                           ║
║     当罗贯中的棺材板压不住的时候...                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def show_status(story_state):
    """显示当前状态"""
    print("\n📊 当前状态")
    print("=" * 50)
    
    meta = story_state.meta
    print(f"📖 标题: {meta.story_title}")
    print(f"📝 副标题: {meta.story_subtitle}")
    print(f"📑 已完成章节: {meta.current_chapter} 章")
    
    if meta.current_chapter > 0:
        print(f"🕐 最后更新: {meta.last_updated}")
    
    # 显示当前主线
    plot_state = story_state.plot_state
    if plot_state.get('main_conflict'):
        print(f"\n📍 当前主线: {plot_state['main_conflict']}")
    
    # 显示角色
    characters = story_state.characters
    if characters:
        print(f"\n👥 主要角色 ({len(characters)} 人):")
        for name in list(characters.keys())[:5]:
            char = characters[name]
            print(f"   • {name} - {char.identity}")
    
    # 显示伏笔
    open_threads = [
        t for t in plot_state.get('open_threads', [])
        if isinstance(t, dict) and t.get('status') == 'open'
    ]
    if open_threads:
        print(f"\n🔮 未解伏笔 ({len(open_threads)} 条):")
        for thread in open_threads[-3:]:
            print(f"   → {thread.get('description', '未知')[:50]}...")
    
    # 显示分卷
    arcs = story_state.arc_summaries
    if arcs:
        print(f"\n📚 分卷 ({len(arcs)} 个):")
        for arc in arcs[-2:]:
            print(f"   • 第{arc.arc_id}卷: {arc.chapters} - {arc.summary[:30]}...")
    
    print("\n" + "=" * 50)


def run_interactive(story_state, chapter_writer):
    """交互模式"""
    print("\n🎮 交互模式")
    print("-" * 50)
    
    # 显示状态
    show_status(story_state)
    
    while True:
        print("\n请选择操作：")
        print("  1. 生成新章节")
        print("  2. 重新初始化故事（慎用！）")
        print("  3. 退出")
        
        try:
            choice = input("\n请输入选项 [1-3]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！")
            break
        
        if choice == '1':
            try:
                num = input("请输入要生成的章节数: ").strip()
                if num.isdigit():
                    run_chapters(int(num), story_state, chapter_writer)
                else:
                    print("⚠️ 请输入有效数字")
            except (EOFError, KeyboardInterrupt):
                print("\n已取消")
                
        elif choice == '2':
            confirm = input("⚠️ 确定要重新初始化故事吗？这将清空所有章节和设定！[y/N]: ")
            if confirm.lower() == 'y':
                if chapter_writer.initialize_story():
                    story_state.load_all()
                    print("✅ 故事已重新初始化")
                else:
                    print("❌ 初始化失败")
            else:
                print("已取消")
                
        elif choice == '3':
            print("\n👋 再见！")
            break
            
        else:
            print("⚠️ 无效选项")


def run_chapters(num_chapters: int, story_state, chapter_writer, chapter_length: int = 2000):
    """生成指定数量的章节"""
    if num_chapters <= 0:
        print("⚠️ 章节数必须大于 0")
        return
    
    print(f"\n🚀 开始生成 {num_chapters} 章...")
    print("=" * 50)
    
    # 获取起始章节号
    start_chapter = story_state.get_next_chapter_num()
    
    success_count = 0
    fail_count = 0
    
    for i in range(num_chapters):
        chapter_num = start_chapter + i
        print(f"\n📝 正在生成第 {chapter_num} 章 ({i + 1}/{num_chapters})...")
        
        success, content = chapter_writer.write_chapter(chapter_num, chapter_length)
        
        if success:
            success_count += 1
            # 显示章节标题
            import re
            title_match = re.search(r'#\s*第[一二三四五六七八九十百\d]+章\s*(.+)', content)
            if title_match:
                title = title_match.group(1).strip()
                print(f"   ✅ 已保存: 第{chapter_num}章 - {title}")
            else:
                print(f"   ✅ 第{chapter_num}章已完成")
        else:
            fail_count += 1
            print(f"   ❌ 第{chapter_num}章生成失败")
        
        # 每章之间稍作停顿，避免 API 限流
        if i < num_chapters - 1:
            import time
            time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"📊 生成完成: 成功 {success_count} 章, 失败 {fail_count} 章")
    
    # 重新加载状态
    story_state.load_all()
    show_status(story_state)


def main():
    """主函数"""
    args = parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 显示横幅
    show_banner()
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 延迟导入，避免环境检查失败时报错
    from story_state import get_story_state
    from chapter_writer import get_chapter_writer
    
    # 加载故事状态
    story_state = get_story_state()
    story_state.load_all()
    
    # 获取章节写作器
    chapter_writer = get_chapter_writer()
    
    # 检查是否需要初始化
    need_init = args.init or story_state.meta.current_chapter == 0
    
    if need_init:
        print("\n🔧 初始化故事宇宙...")
        if chapter_writer.initialize_story():
            story_state.load_all()
            print("✅ 故事宇宙初始化完成！")
        else:
            print("❌ 初始化失败")
            sys.exit(1)
    
    # 根据参数决定运行模式
    if args.status:
        show_status(story_state)
        
    elif args.chapters > 0:
        run_chapters(
            args.chapters, 
            story_state, 
            chapter_writer,
            args.chapter_length
        )
        
    else:
        run_interactive(story_state, chapter_writer)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已取消，再见！")
        sys.exit(0)
    except Exception as e:
        logger.exception("程序异常退出")
        sys.exit(1)
