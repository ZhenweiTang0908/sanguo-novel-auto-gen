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
        env_path = os.path.join(script_dir, '.env')
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('DASHSCOPE_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip("'\"")
                        break
    if not api_key:
        print("  错误: 未设置 DASHSCOPE_API_KEY")
        print("  设置方式: 在 .env 文件中配置或 export DASHSCOPE_API_KEY='your-key'")
        return False
    os.environ['DASHSCOPE_API_KEY'] = api_key
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


def show_full_info(story_state):
    """显示完整信息"""
    meta = story_state.meta
    plot_state = story_state.plot_state
    characters = story_state.characters

    print(f"\n  标题: {meta.story_title}")
    print(f"  副标题: {meta.story_subtitle}")
    print(f"  章节: {meta.current_chapter} 章")
    if meta.last_updated:
        print(f"  更新: {meta.last_updated[:19]}")

    if plot_state.get('main_conflict'):
        print(f"\n  主线: {plot_state['main_conflict'][:60]}...")

    print(f"\n  角色 ({len(characters)} 人):")
    for name, char in characters.items():
        role = "主演" if char.role == "main" else "配角"
        print(f"    {name} [{role}] - {char.identity}")

    open_threads = [t for t in plot_state.get('open_threads', []) if isinstance(t, dict) and t.get('status') == 'open']
    if open_threads:
        print(f"\n  伏笔 ({len(open_threads)} 条):")
        for t in open_threads[-5:]:
            print(f"    - {t.get('description', '')[:50]}...")

    arcs = story_state.arc_summaries
    if arcs:
        print(f"\n  分卷 ({len(arcs)} 个):")
        for arc in arcs:
            print(f"    第{arc.arc_id}卷: {arc.chapters}")


def run_interactive(story_state, chapter_writer):
    """交互模式"""
    print("\n🎮 交互模式")
    print("-" * 50)

    show_status(story_state)

    while True:
        print("\n请选择操作：")
        print("  1. 生成新章节")
        print("  2. 添加新角色")
        print("  3. 修改角色信息")
        print("  4. 设置灵感线索")
        print("  5. 随机角色模式")
        print("  6. 查看更多信息")
        print("  7. 删除章节")
        print("  8. 彻底重置小说")
        print("  9. 退出")

        try:
            choice = input("\n  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！")
            break

        if choice == '1':
            num = input("  章节数: ").strip()
            if not num.isdigit() or int(num) <= 0:
                print("  无效输入")
                continue

            # 检查随机角色模式
            if story_state.is_random_character_mode():
                random_count = story_state.plot_state.get("random_character_count", 5)
                selected = story_state.get_random_characters(random_count)
                print(f"  🎲 随机模式: {', '.join(selected)}")
                story_state.set_active_characters(selected)
            else:
                # 选择角色
                characters = story_state.characters
                if characters:
                    print("  选择角色（主演）或直接回车跳过:")
                    print("  格式: 1,3,4 或 角色名 直接回车跳过")
                    for i, (name, char) in enumerate(characters.items(), 1):
                        role = "主演" if char.role == "main" else "配角"
                        print(f"    {i}. {name} [{role}]")
                    selection = input("  > ").strip()

                    if selection:
                        # 支持数字序号或名字
                        selected = []
                        for item in selection.split(','):
                            item = item.strip()
                            if item.isdigit():
                                idx = int(item) - 1
                                if 0 <= idx < len(characters):
                                    selected.append(list(characters.keys())[idx])
                            elif item in characters:
                                selected.append(item)
                        if selected:
                            story_state.set_active_characters(selected)
                            print(f"  已选择: {', '.join(selected)}")

            run_chapters(int(num), story_state, chapter_writer)

        elif choice == '2':
            try:
                name = input("  角色名: ").strip()
                if not name:
                    print("  已取消")
                    continue
                identity = input("  身份设定: ").strip()
                location = input("  当前位置: ").strip() or "未知"
                goal = input("  当前目标: ").strip() or "待探索"
                print("  角色定位:")
                print("    1. 主演（重要角色）")
                print("    2. 配角（次要角色）")
                role_sel = input("  > ").strip()
                role = "main" if role_sel == "1" else "supporting"
                story_state.add_character(name, identity, location, goal, role=role)
                story_state.save_all()
                print(f"  已添加: {name} ({'主演' if role == 'main' else '配角'})")
            except (EOFError, KeyboardInterrupt):
                print("  已取消")

        elif choice == '3':
            try:
                characters = story_state.characters
                if not characters:
                    print("  暂无角色")
                    continue
                print("  选择要修改的角色:")
                for i, (name, char) in enumerate(characters.items(), 1):
                    role = "主演" if char.role == "main" else "配角"
                    print(f"    {i}. {name} [{role}] - {char.identity}")
                sel = input("  输入编号或角色名: ").strip()
                if not sel:
                    print("  已取消")
                    continue
                # 支持数字序号或名字
                target_name = None
                if sel.isdigit():
                    idx = int(sel) - 1
                    if 0 <= idx < len(characters):
                        target_name = list(characters.keys())[idx]
                elif sel in characters:
                    target_name = sel
                
                if not target_name:
                    print("  无效选择")
                    continue
                
                char = characters[target_name]
                print(f"\n  修改角色: {target_name}")
                print(f"  当前身份: {char.identity}")
                new_identity = input("  新身份设定(直接回车跳过): ").strip()
                print(f"  当前定位: {'主演' if char.role == 'main' else '配角'}")
                print("  角色定位: 1.主演  2.配角  直接回车跳过")
                role_sel = input("  > ").strip()
                
                role = None
                if role_sel == "1":
                    role = "main"
                elif role_sel == "2":
                    role = "supporting"
                
                story_state.update_character(
                    target_name,
                    identity=new_identity if new_identity else None,
                    role=role
                )
                story_state.save_all()
                print("  已更新")
            except (EOFError, KeyboardInterrupt):
                print("  已取消")

        elif choice == '4':
            try:
                inspiration = input("  灵感线索: ").strip()
                if inspiration:
                    story_state.set_user_inspiration(inspiration)
                    story_state.save_all()
                    print("  灵感已设置")
                else:
                    print("  已取消")
            except (EOFError, KeyboardInterrupt):
                print("  已取消")

        elif choice == '5':
            try:
                current_mode = story_state.is_random_character_mode()
                if current_mode:
                    print("  当前状态: 随机角色模式 [开启]")
                    confirm = input("  关闭随机模式? [y/N]: ").strip()
                    if confirm.lower() == 'y':
                        story_state.set_random_character_mode(False)
                        story_state.save_all()
                        print("  已关闭随机模式")
                else:
                    print("  当前状态: 随机角色模式 [关闭]")
                    count = input("  输入随机角色数量(默认5): ").strip()
                    count = int(count) if count.isdigit() else 5
                    story_state.set_random_character_mode(True, count)
                    story_state.save_all()
                    print(f"  已开启随机模式，每次随机选择 {count} 个角色")
            except (EOFError, KeyboardInterrupt):
                print("  已取消")

        elif choice == '6':
            show_full_info(story_state)

        elif choice == '7':
            chapters = story_state.storage.list_chapters()
            if not chapters:
                print("  暂无章节")
                continue
            print("  删除章节:")
            for c in chapters:
                print(f"    {c}. chapter_{c:03d}.md")
            sel = input("  输入编号(多个用逗号分隔): ").strip()
            if not sel:
                print("  已取消")
                continue
            for item in sel.split(','):
                item = item.strip()
                if item.isdigit():
                    idx = int(item) - 1
                    if 0 <= idx < len(chapters):
                        ch = chapters[idx]
                        path = story_state.storage.get_chapter_path(ch)
                        if path.exists():
                            path.unlink()
                            sum_path = story_state.storage.get_chapter_summary_path(ch)
                            if sum_path.exists():
                                sum_path.unlink()
                            print(f"  已删除: chapter_{ch:03d}.md")
            # 更新 meta
            remaining = story_state.storage.list_chapters()
            story_state.meta.current_chapter = len(remaining)
            story_state.save_all()
            story_state.load_all()

        elif choice == '8':
            confirm = input("  ⚠️ 彻底删除所有内容？[y/N]: ").strip()
            if confirm.lower() == 'y':
                confirm2 = input("  再次确认，输入 YES: ").strip()
                if confirm2 == 'YES':
                    import shutil
                    data_dir = story_state.storage.base_path / 'novel-reader' / 'data'
                    for item in ['chapters', 'chapter_summaries']:
                        d = data_dir / item
                        if d.exists():
                            for f in d.iterdir():
                                f.unlink()
                    # 重置 meta
                    story_state.meta.current_chapter = 0
                    story_state.save_all()
                    story_state.load_all()
                    print("  已重置")
                else:
                    print("  已取消")
            else:
                print("  已取消")

        elif choice == '9':
            print("  再见！")
            break

        else:
            print("  无效选项")


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
