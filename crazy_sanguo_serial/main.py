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
from typing import Optional, Dict

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
    
    parser.add_argument(
        '-n', '--novel-id',
        type=str,
        default='crazy_sanguo',
        help='小说ID（默认 crazy_sanguo）'
    )
    
    parser.add_argument(
        '-r', '--reference',
        type=int,
        default=0,
        help='从参考语料中抽取的段落数量（默认0，不使用）'
    )
    
    parser.add_argument(
        '--chaos',
        action='store_true',
        help='混杂模式：完全由AI决定生成配置'
    )
    
    parser.add_argument(
        '--list-novels',
        action='store_true',
        help='列出所有小说'
    )
    
    parser.add_argument(
        '--create-novel',
        type=str,
        metavar='NOVEL_ID',
        help='创建新小说'
    )
    
    parser.add_argument(
        '--keywords',
        type=str,
        default='',
        help='初始化世界观时的关键词（用于引导世界观生成）'
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


def show_status(story_state, novel_info: Optional[Dict] = None):
    """显示当前状态
    
    Args:
        story_state: 故事状态
        novel_info: 小说信息（可选，用于显示小说列表中的标题）
    """
    print("\n📊 当前状态")
    print("=" * 50)
    
    meta = story_state.meta
    
    # 如果提供了小说信息且当前章节为0，使用小说信息中的标题
    if novel_info and meta.current_chapter == 0:
        print(f"📖 标题: {novel_info.get('title', meta.story_title)}")
        print(f"📝 副标题: {novel_info.get('subtitle', meta.story_subtitle)}")
        print(f"📑 已完成章节: 0 章 (新小说，需要初始化)")
    else:
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


def run_interactive(storage, novel_manager, initial_novel_id, default_reference: int = 0, default_chaos: bool = False):
    """交互模式
    
    Args:
        novel_manager: 小说管理器
        initial_novel_id: 初始小说ID
        default_reference: 默认参考语料数量
        default_chaos: 默认混杂模式
    """
    from story_state import get_story_state
    from chapter_writer import get_chapter_writer
    
    # 确定实际使用的 novel_id（legacy 或新位置）
    if initial_novel_id:
        new_meta = storage.base_path / "novels" / initial_novel_id / "meta.json"
        if new_meta.exists():
            actual_novel_id = initial_novel_id
        else:
            actual_novel_id = None  # legacy 模式
    else:
        actual_novel_id = None
    
    current_novel_id = initial_novel_id
    story_state = get_story_state(actual_novel_id)
    story_state.load_all()
    chapter_writer = get_chapter_writer()
    
    ref_count = default_reference
    chaos_mode = default_chaos

    def reload_story_state():
        """重新加载故事状态"""
        nonlocal story_state, chapter_writer
        # 重置全局单例，强制创建新实例
        import chapter_writer as cw_module
        import story_state as ss_module
        cw_module._chapter_writer = None
        ss_module._story_state = None
        
        # 确定实际 novel_id
        if current_novel_id:
            # 检查新位置是否有数据
            new_meta = storage.base_path / "novels" / current_novel_id / "meta.json"
            if new_meta.exists():
                actual = current_novel_id
            else:
                # 新位置没有数据，检查是否是 legacy
                legacy_meta = storage.base_path / "novel-reader" / "meta.json"
                if current_novel_id == "crazy_sanguo" and legacy_meta.exists():
                    actual = None  # legacy 模式
                else:
                    # 新小说，使用其ID创建新数据
                    actual = current_novel_id
                    # 确保目录存在
                    novel_dir = storage.base_path / "novels" / current_novel_id
                    (novel_dir / "chapters").mkdir(parents=True, exist_ok=True)
                    (novel_dir / "chapter_summaries").mkdir(parents=True, exist_ok=True)
        else:
            actual = None
        story_state = get_story_state(actual)
        story_state.load_all()
        chapter_writer = get_chapter_writer()
        novel_info = novel_manager.get_novel(current_novel_id)
        print(f"\n已切换到小说: {novel_info.get('title', current_novel_id) if current_novel_id else '未知'}")
        show_status(story_state, novel_info)

    def switch_novel():
        """切换小说"""
        nonlocal current_novel_id
        novels = novel_manager.list_novels()
        if not novels:
            print("  暂无小说，请先创建")
            return
        
        print("\n选择小说：")
        for i, n in enumerate(novels, 1):
            marker = " [当前]" if n.get("id") == current_novel_id else ""
            print(f"  {i}. {n.get('title', n.get('id'))}{marker}")
        print("  0. 取消")
        
        sel = input("  > ").strip()
        if sel == '0' or not sel:
            print("  已取消")
            return
        
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(novels):
                current_novel_id = novels[idx].get("id")
                reload_story_state()
            else:
                print("  无效选择")
        else:
            # 按 ID 查找
            for n in novels:
                if n.get("id") == sel:
                    current_novel_id = sel
                    reload_story_state()
                    return
            print("  未找到该小说")

    print("\n🎮 交互模式")
    print("-" * 50)
    show_status(story_state, novel_manager.get_novel(current_novel_id))

    while True:
        current_novel = novel_manager.get_novel(current_novel_id)
        novel_title = current_novel.get("title", current_novel_id) if current_novel else "未选择"
        chaos_display = "开启" if chaos_mode is True else ("关闭" if chaos_mode is False else "AI决定")
        ref_display = f"{ref_count}" if ref_count >= 0 else "AI决定"
        
        print(f"\n📖 当前小说: {novel_title}")
        print("\n请选择操作：")
        print("  0. 切换小说")
        print("  1. 创建新小说")
        print("  2. 生成新章节")
        print("  3. 添加新角色")
        print("  4. 修改角色信息")
        print("  5. 设置灵感线索")
        print("  6. 随机角色模式")
        print("  7. 参考语料设置")
        print("  8. 混杂模式设置")
        print("  9. 查看更多信息")
        print("  10. 删除章节")
        print("  11. 重新初始化世界观")
        print("  12. 删除小说")
        print("  13. 退出")

        try:
            choice = input("\n  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！")
            break

        if choice == '0':
            switch_novel()

        elif choice == '1':
            try:
                print("\n🆕 创建新小说")
                new_novel_id = input("  小说ID: ").strip()
                if not new_novel_id:
                    print("  已取消")
                    continue
                if novel_manager.get_novel(new_novel_id):
                    print(f"  小说 '{new_novel_id}' 已存在")
                    continue
                title = input("  小说标题: ").strip() or f"新小说_{new_novel_id}"
                subtitle = input("  小说副标题: ").strip() or ""
                
                import datetime
                novel = novel_manager.add_novel(new_novel_id, title, subtitle)
                novel["created_at"] = datetime.datetime.now().isoformat()
                novel_manager.save_novel_list(novel_manager.list_novels())
                
                # 切换到新小说并创建目录
                current_novel_id = new_novel_id
                
                # 确保目录存在
                novel_dir = storage.base_path / "novels" / current_novel_id
                (novel_dir / "chapters").mkdir(parents=True, exist_ok=True)
                (novel_dir / "chapter_summaries").mkdir(parents=True, exist_ok=True)
                
                # 重新加载状态
                reload_story_state()
                
                # 设置标题到 meta
                story_state.meta.story_title = title
                story_state.meta.story_subtitle = subtitle
                
                # 选择初始化方式
                print("\n选择初始化方式:")
                print("  1. AI初始化（让AI根据标题生成人物和背景）")
                print("  2. 手动初始化（自己输入世界观和人物）")
                print("  3. 跳过（创建空小说，稍后设置）")
                init_choice = input("  > ").strip()
                
                if init_choice == '1':
                    keywords = input("  输入关键词引导（直接回车使用标题）: ").strip()
                    if not keywords:
                        keywords = title
                    print("\n🔧 AI正在生成初始人物和背景...")
                    if chapter_writer.initialize_story(keywords):
                        story_state.load_all()
                        print("✅ AI初始化完成！")
                    else:
                        print("❌ AI初始化失败，将创建空小说")
                        story_state.save_all()
                elif init_choice == '2':
                    print("\n📝 手动初始化世界观")
                    world_overview = input("  世界观概述: ").strip()
                    main_conflict = input("  主线冲突: ").strip()
                    
                    print("\n👥 添加主演角色（输入角色名，直接回车结束）:")
                    main_chars = []
                    while True:
                        name = input("  角色名（直接回车结束）: ").strip()
                        if not name:
                            break
                        identity = input("  身份设定: ").strip()
                        main_chars.append({"name": name, "new_identity": identity})
                    
                    print("\n🔧 构建初始数据...")
                    story_bible = {
                        "world_overview": world_overview,
                        "main_conflict": main_conflict,
                        "main_characters": main_chars
                    }
                    characters = {}
                    for char in main_chars:
                        characters[char["name"]] = {
                            "name": char["name"],
                            "identity": char["new_identity"],
                            "current_location": "初始地点",
                            "goal": "待探索",
                            "status": "alive",
                            "role": "main"
                        }
                    plot_state = {
                        "main_conflict": main_conflict,
                        "sub_conflicts": [],
                        "open_threads": [],
                        "used_creatives": [],
                        "active_creative_types": []
                    }
                    story_state.initialize(story_bible, characters, plot_state)
                    print("✅ 手动初始化完成！")
                else:
                    print("  将创建空小说，可稍后手动添加角色和设定")
                    story_state.save_all()
            except (EOFError, KeyboardInterrupt):
                print("  已取消")

        elif choice == '2':
            num = input("  章节数: ").strip()
            if not num.isdigit() or int(num) <= 0:
                print("  无效输入")
                continue

            # 设置参考语料（空=由AI决定）
            print(f"  参考语料数量 [当前: {ref_count}, 空=AI决定]: ")
            ref_input = input("  > ").strip()
            if ref_input.isdigit():
                ref_count = int(ref_input)
            elif ref_input == '':
                ref_count = -1  # -1 表示由AI决定
            # 空字符串保持 ref_count = -1 让AI决定
            
            # 混杂模式（空=由AI决定）
            print(f"  混杂模式 (y/N/空=AI决定) [当前: {'开启' if chaos_mode else '关闭'}]: ")
            chaos_input = input("  > ").strip().lower()
            if chaos_input == 'y':
                chaos_mode = True
            elif chaos_input == 'n':
                chaos_mode = False
            else:
                chaos_mode = None  # None 表示由AI决定

            # 检查随机角色模式
            if story_state.is_random_character_mode():
                random_count = story_state.plot_state.get("random_character_count", 5)
                selected = story_state.get_random_characters(random_count)
                print(f"  🎲 随机模式: {', '.join(selected)}")
                story_state.set_active_characters(selected)
            else:
                # 选择角色（空=由AI决定）
                characters = story_state.characters
                if characters:
                    print("  选择角色（主演）或直接回车由AI决定:")
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
                    # 空输入则不清空 active_characters，让 AI 决定

            run_chapters(int(num), story_state, chapter_writer, 2000, ref_count, chaos_mode)

        elif choice == '3':
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

        elif choice == '4':
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

        elif choice == '5':
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

        elif choice == '6':
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

        elif choice == '7':
            try:
                ref_display = f"{ref_count}" if ref_count >= 0 else "AI决定"
                print(f"  当前参考语料数量: {ref_display}")
                new_ref = input("  输入新的参考语料数量 (0=不使用, -1=AI决定): ").strip()
                if new_ref.isdigit():
                    ref_count = int(new_ref)
                    print(f"  已设置为: {ref_count if ref_count >= 0 else 'AI决定'}")
                elif new_ref == '-1':
                    ref_count = -1
                    print("  已设置为: AI决定")
            except (EOFError, KeyboardInterrupt):
                print("  已取消")

        elif choice == '8':
            try:
                chaos_display = "开启" if chaos_mode is True else ("关闭" if chaos_mode is False else "AI决定")
                print(f"  当前混杂模式: {chaos_display}")
                confirm = input("  混杂模式? [y=开启, n=关闭, 空=AI决定]: ").strip().lower()
                if confirm == 'y':
                    chaos_mode = True
                    print("  已设置为: 开启")
                elif confirm == 'n':
                    chaos_mode = False
                    print("  已设置为: 关闭")
                else:
                    chaos_mode = None
                    print("  已设置为: AI决定")
            except (EOFError, KeyboardInterrupt):
                print("  已取消")

        elif choice == '9':
            show_full_info(story_state)

        elif choice == '10':
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

        elif choice == '11':
            print("\n🔄 重新初始化世界观")
            print("  提示：此操作将保留章节，但重新生成世界观、人物和主线")
            confirm = input("  确认继续？[y/N]: ").strip()
            if confirm.lower() != 'y':
                print("  已取消")
                continue
            
            print("\n选择初始化方式:")
            print("  1. AI初始化")
            print("  2. 手动初始化")
            init_choice = input("  > ").strip()
            
            if init_choice == '1':
                keywords = input("  输入关键词（直接回车使用标题）: ").strip()
                if not keywords:
                    keywords = story_state.meta.story_title
                print("\n🔧 AI正在重新生成...")
                if chapter_writer.initialize_story(keywords):
                    story_state.load_all()
                    print("✅ 重新初始化完成！")
                else:
                    print("❌ AI初始化失败")
            elif init_choice == '2':
                print("\n📝 手动输入世界观")
                world_overview = input("  世界观概述: ").strip()
                main_conflict = input("  主线冲突: ").strip()
                
                print("\n👥 添加主演角色（输入角色名，直接回车结束）:")
                main_chars = []
                while True:
                    name = input("  角色名（直接回车结束）: ").strip()
                    if not name:
                        break
                    identity = input("  身份设定: ").strip()
                    main_chars.append({"name": name, "new_identity": identity})
                
                story_bible = {
                    "world_overview": world_overview,
                    "main_conflict": main_conflict,
                    "main_characters": main_chars
                }
                characters = {}
                for char in main_chars:
                    characters[char["name"]] = {
                        "name": char["name"],
                        "identity": char["new_identity"],
                        "current_location": "初始地点",
                        "goal": "待探索",
                        "status": "alive",
                        "role": "main"
                    }
                plot_state = {
                    "main_conflict": main_conflict,
                    "sub_conflicts": [],
                    "open_threads": [],
                    "used_creatives": [],
                    "active_creative_types": []
                }
                story_state.initialize(story_bible, characters, plot_state)
                print("✅ 重新初始化完成！")
            else:
                print("  无效选择")

        elif choice == '12':
            novels = novel_manager.list_novels()
            if not novels:
                print("  暂无小说")
                continue
            
            if len(novels) == 1:
                print("  至少需要保留一部小说")
                continue
            
            print("\n删除小说：")
            for i, n in enumerate(novels, 1):
                marker = " [当前]" if n.get("id") == current_novel_id else ""
                print(f"  {i}. {n.get('title', n.get('id'))}{marker}")
            print("  0. 取消")
            
            sel = input("  > ").strip()
            if sel == '0' or not sel:
                print("  已取消")
                continue
            
            target_id = None
            if sel.isdigit():
                idx = int(sel) - 1
                if 0 <= idx < len(novels):
                    target_id = novels[idx].get("id")
            else:
                for n in novels:
                    if n.get("id") == sel:
                        target_id = sel
                        break
            
            if not target_id:
                print("  无效选择")
                continue
            
            if target_id == current_novel_id:
                print("  不能删除当前选中小说，请先切换")
                continue
            
            confirm = input(f"  确认删除 '{target_id}'？[y/N]: ").strip()
            if confirm.lower() != 'y':
                print("  已取消")
                continue
            
            # 删除小说目录
            import shutil as shutil_mod
            novel_dir = storage.base_path / "novels" / target_id
            if novel_dir.exists():
                shutil_mod.rmtree(novel_dir)
            
            # 从列表中移除
            novel_manager.remove_novel(target_id)
            print(f"  已删除: {target_id}")

        elif choice == '13':
            print("  再见！")
            break

        else:
            print("  无效选项")


def run_chapters(
    num_chapters: int, 
    story_state, 
    chapter_writer, 
    chapter_length: int = 2000,
    reference_count: int = 0,
    chaos_mode: Optional[bool] = False
):
    """生成指定数量的章节
    
    Args:
        reference_count: 参考语料数量，-1表示由AI决定
        chaos_mode: 混杂模式，None表示由AI决定
    """
    if num_chapters <= 0:
        print("⚠️ 章节数必须大于 0")
        return
    
    print(f"\n🚀 开始生成 {num_chapters} 章...")
    if chaos_mode is True:
        print("⚡ 混杂模式：AI完全自主决定")
    elif chaos_mode is None:
        print("🎲 混杂模式：由AI决定")
    if reference_count > 0:
        print(f"📚 将混入参考语料（{reference_count}条/章）")
    elif reference_count == -1:
        print("📚 参考语料：由AI决定")
    print("=" * 50)
    
    # 获取起始章节号
    start_chapter = story_state.get_next_chapter_num()
    
    success_count = 0
    fail_count = 0
    
    for i in range(num_chapters):
        chapter_num = start_chapter + i
        print(f"\n📝 正在生成第 {chapter_num} 章 ({i + 1}/{num_chapters})...")
        
        success, content = chapter_writer.write_chapter(
            chapter_num, 
            chapter_length,
            reference_count=reference_count,
            chaos_mode=chaos_mode
        )
        
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
    from storage import NovelManager, get_storage
    
    storage = get_storage()
    novel_manager = NovelManager(storage)
    
    # 处理 list-novels
    if args.list_novels:
        novels = novel_manager.list_novels()
        print("\n📚 所有小说:")
        print("=" * 50)
        if novels:
            for n in novels:
                print(f"  • {n.get('id')}: {n.get('title')} - {n.get('subtitle', '')}")
        else:
            print("  暂无小说")
        print()
        return
    
    # 处理 create-novel
    if args.create_novel:
        new_novel_id = args.create_novel
        print(f"\n🆕 创建新小说: {new_novel_id}")
        title = input("  小说标题: ").strip() or f"新小说_{new_novel_id}"
        subtitle = input("  小说副标题: ").strip() or ""
        
        import datetime
        novel = novel_manager.add_novel(new_novel_id, title, subtitle)
        novel["created_at"] = datetime.datetime.now().isoformat()
        novel_manager.save_novel_list(novel_manager.list_novels())
        
        # 创建小说目录
        storage.set_novel(new_novel_id)
        print(f"✅ 小说已创建: {title}")
        return
    
    # 使用指定的小说 ID
    novel_id = args.novel_id
    
    # 检查小说是否在列表中
    existing_novel = novel_manager.get_novel(novel_id)
    
    # 检查是否有实际数据（旧位置或新位置）
    has_data = novel_manager.novel_data_exists(novel_id)
    is_legacy_data = False
    
    if not existing_novel:
        if has_data:
            # 数据存在但不在列表中，可能是 legacy 数据
            print(f"\n📖 检测到小说 '{novel_id}' 的数据")
            legacy_meta = storage.base_path / "novel-reader" / "meta.json"
            if legacy_meta.exists():
                import json
                meta = json.load(open(legacy_meta, 'r', encoding='utf-8'))
                title = meta.get('story_title', novel_id)
                subtitle = meta.get('story_subtitle', '')
                is_legacy_data = True
                print(f"   位置: novel-reader/ (legacy)")
            else:
                title = novel_id
                subtitle = ''
            
            # 添加到列表
            import datetime
            existing_novel = novel_manager.add_novel(novel_id, title, subtitle)
            existing_novel["created_at"] = datetime.datetime.now().isoformat()
            novel_manager.save_novel_list(novel_manager.list_novels())
            print(f"   已注册为: {title}")
        else:
            print(f"\n⚠️ 小说 '{novel_id}' 不存在")
            print("  使用 --list-novels 查看所有小说")
            print("  使用 --create-novel <id> 创建新小说")
            response = input(f"\n  是否以此ID创建新小说? [y/N]: ").strip()
            if response.lower() == 'y':
                title = input("  小说标题: ").strip() or f"新小说_{novel_id}"
                subtitle = input("  小说副标题: ").strip() or ""
                import datetime
                novel = novel_manager.add_novel(novel_id, title, subtitle)
                novel["created_at"] = datetime.datetime.now().isoformat()
                novel_manager.save_novel_list(novel_manager.list_novels())
                storage.set_novel(novel_id)
                print(f"✅ 小说已创建: {title}")
            else:
                print("已取消")
                return
    
    # 如果是 legacy 数据，使用 legacy 模式（novel_id=None）
    if is_legacy_data:
        actual_novel_id = None
        print(f"   正在以 legacy 模式加载...")
    else:
        # 检查新位置是否有数据
        new_meta = storage.base_path / "novels" / novel_id / "meta.json"
        if new_meta.exists():
            actual_novel_id = novel_id
        else:
            # 新位置没有数据，使用 legacy 模式
            actual_novel_id = None
            print(f"   小说数据位于 legacy 位置")
    
    # 加载故事状态
    story_state = get_story_state(actual_novel_id)
    story_state.load_all()
    
    # 获取章节写作器
    chapter_writer = get_chapter_writer()
    
    # 检查是否需要初始化
    need_init = args.init or story_state.meta.current_chapter == 0
    
    if need_init:
        print("\n🔧 初始化故事宇宙...")
        
        # 关键词优先使用命令行参数
        keywords = args.keywords.strip()
        
        if not keywords:
            # 如果命令行没有提供，询问用户
            print("\n请输入世界观关键词（直接回车跳过）：")
            print("  例如：三国、现代都市商战、民国、黑帮、职场 等")
            print("  不指定则创建默认三国世界观")
            keywords = input("  > ").strip()
        
        if keywords:
            print(f"\n📝 将根据关键词 '{keywords}' 创建世界观...")
        else:
            print("\n📝 将创建默认三国世界观...")
        
        if chapter_writer.initialize_story(keywords):
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
            args.chapter_length,
            reference_count=args.reference,
            chaos_mode=args.chaos
        )
        
    else:
        run_interactive(storage, novel_manager, novel_id, args.reference, args.chaos)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已取消，再见！")
        sys.exit(0)
    except Exception as e:
        logger.exception("程序异常退出")
        sys.exit(1)
