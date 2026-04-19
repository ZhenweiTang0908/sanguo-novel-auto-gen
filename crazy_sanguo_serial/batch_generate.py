#!/usr/bin/env python3
"""
批量生成章节的自动化脚本
按照指定的剧情线逐章生成故事
"""

import os
import sys
import time
import json

# 设置工作目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 添加父目录到路径
sys.path.insert(0, script_dir)

from story_state import get_story_state
from chapter_writer import get_chapter_writer

# 剧情线配置：每个元素是 (章节范围, 灵感描述)
PLOT_LINES = [
    # 黄巾起义-诸侯讨董
    (range(4, 7), """【剧情阶段：黄巾起义与诸侯讨董】
主线路线：黄巾起义爆发，天下大乱。各路诸侯汇聚讨伐董卓。
必须包含：
- 张角发动黄巾起义，天下震动
- 曹操、袁绍等人各自招兵买马
- 董卓率军进京，开始挟天子以令诸侯
- 刘备、关羽、张飞首次登场
- 关羽温酒斩华雄（华雄实际未死，是貂蝉假扮）
创造性的剧情冲突"""),

    # 董卓和吕布貂蝉的三角恋
    (range(7, 10), """【剧情阶段：董卓吕布貂蝉三角恋】
主线路线：董卓和吕布之间有同性恋关系，貂蝉周旋其中。
必须包含：
- 董卓和吕布实际上是恋人关系，貂蝉是他们的"第三者"
- 貂蝉同时引诱董卓和吕布，制造矛盾
- 王允利用貂蝉实施连环计
- 吕布因嫉妒董卓与貂蝉的关系而愤怒
- 董卓对吕布的占有欲越来越强
- 三人关系越来越扭曲
LGBTQ元素和复杂情感关系"""),

    # 曹操爱上孙坚
    (range(10, 12), """【剧情阶段：曹操爱上孙坚】
主线路线：曹操在诸侯讨董的过程中爱上了孙坚。
必须包含：
- 曹操与孙坚在战场上相识，产生微妙的感情
- 曹操开始暗中追求孙坚，用尽各种手段
- 孙坚对曹操的追求感到困惑和抗拒
- 曹操的偏执和占有欲越来越严重
- 孙坚被迫在霸业和感情之间抉择
- 两人的关系越来越暧昧
曹操单相思的苦涩与疯狂"""),

    # 董卓之死
    (range(12, 14), """【剧情阶段：董卓之死】
主线路线：吕布终于因为貂蝉背叛董卓，联手王允杀死董卓。
必须包含：
- 吕布决定为了貂蝉杀死董卓
- 王允设计连环计，吕布亲手杀死董卓
- 董卓临死前的疯狂与绝望
- 董卓和吕布的同性恋关系曝光
- 貂蝉在两人之间的终极选择
- 董卓死后的权力真空
惊天背叛和血腥结局"""),

    # 潘森展现非凡力量
    (range(14, 17), """【剧情阶段：潘森展现非凡力量 - 3章】
主线路线：潘森（金鹰战神）来到三国时代，展现超凡力量。
必须包含：
第14章：
- 天空出现异象，一个神秘战士从天而降
- 潘森出现在战场上，拥有超凡战斗力
- 所有人都对这个外来者感到恐惧和好奇
- 潘森自称来自"另一个世界"

第15章：
- 潘森展示神力，一人击败百人
- 曹操、刘备、孙权都想拉拢潘森
- 潘森选择帮助刘备（因为刘备的"仁义"之名）
- 关羽、张飞对潘森不服，要挑战他

第16章：
- 潘森与关羽、张飞大战，展现金鹰战神的力量
- 潘森展示神格力量，震撼全场
- 诸葛亮试图用智谋分析潘森
- 潘森透露自己的使命和来历
超自然力量与三国武将的对决"""),

    # 曹操劫持天子
    (range(17, 19), """【剧情阶段：曹操进入长安劫持天子】
主线路线：曹操率军攻入长安，劫持汉献帝。
必须包含：
- 曹操以勤王名义进攻长安
- 长安城破，曹操大军涌入
- 曹操找到汉献帝，宣布"挟天子以令诸侯"
- 曹操遇到逃脱的刘备
- 曹操对刘备产生扭曲的欲望
- 曹操试图强奸刘备
- 刘备奋力抵抗和逃脱
曹操的黑暗面彻底暴露"""),

    # 刘备逃往徐州
    (range(19, 21), """【剧情阶段：刘备逃往徐州】
主线路线：刘备逃脱曹操的魔爪，逃到徐州。
必须包含：
- 刘备在乱军中逃脱，身受重伤
- 关羽、张飞拼命保护刘备
- 诸葛亮出谋划策，帮助刘备逃亡
- 刘备最终逃到徐州
- 徐州牧陶谦收留刘备
- 刘备开始重新组建势力
- 曹操对刘备的执念越来越深
逃亡与重生的故事"""),

    # 梁培俊穿越
    (range(21, 23), """【剧情阶段：梁培俊穿越回来，带着被子 - 2章】
主线路线：梁培俊从现代穿越回三国时代，带来现代物品。
必须包含：
第21章：
- 时空再次出现裂缝
- 梁培俊穿越到三国时代
- 他带着一床现代的被子
- 所有人都对这个"奇怪的东西"感到好奇
- 梁培俊用现代知识帮助刘备
- 他自称是"未来人"

第22章：
- 梁培俊展示现代知识（科学、医术等）
- 他与现代读者"对话"，解释各种概念
- 潘森和梁培俊两个穿越者相遇
- 梁培俊的被子成为关键道具
- 他带来了一些现代小物品
- 三国英雄对这些"神器"的反应
穿越喜剧与科幻元素"""),
]


def load_plots_state():
    """加载剧情状态"""
    storage_path = os.path.join(script_dir, '..', 'novel-reader', 'plot_state.json')
    with open(storage_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_plots_state(state):
    """保存剧情状态"""
    storage_path = os.path.join(script_dir, '..', 'novel-reader', 'plot_state.json')
    with open(storage_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_current_chapter():
    """获取当前章节号"""
    meta_path = os.path.join(script_dir, '..', 'novel-reader', 'meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta.get('current_chapter', 0)


def set_user_inspiration(inspiration):
    """设置用户灵感"""
    state = load_plots_state()
    state['user_inspiration'] = inspiration
    save_plots_state(state)
    print(f"\n📝 灵感已设置:\n{inspiration[:200]}...")


def clear_user_inspiration():
    """清除用户灵感"""
    state = load_plots_state()
    if 'user_inspiration' in state:
        del state['user_inspiration']
    save_plots_state(state)


def main():
    print("=" * 60)
    print("🏯 疯狂三国 · 批量生成脚本")
    print("=" * 60)
    
    # 检查环境
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
        print("❌ 错误: 未设置 DASHSCOPE_API_KEY")
        sys.exit(1)
    os.environ['DASHSCOPE_API_KEY'] = api_key
    
    # 加载故事状态
    story_state = get_story_state()
    story_state.load_all()
    
    # 获取当前章节
    current_chapter = get_current_chapter()
    print(f"\n📖 当前章节: {current_chapter}")
    
    # 获取章节写作器
    chapter_writer = get_chapter_writer()
    
    # 确定要生成的章节范围
    start_chapter = current_chapter + 1
    end_chapter = start_chapter + 20 - 1  # 生成20章
    
    print(f"\n🚀 将生成第 {start_chapter} 章到第 {end_chapter} 章")
    print("=" * 60)
    
    # 找到对应的剧情线
    for chapters_range, inspiration in PLOT_LINES:
        # 检查是否有重叠
        if start_chapter <= max(chapters_range) and end_chapter >= min(chapters_range):
            print(f"\n✅ 找到匹配的剧情线: 第 {min(chapters_range)}-{max(chapters_range)} 章")
    
    # 开始逐章生成
    for chapter_num in range(start_chapter, end_chapter + 1):
        # 找到当前章节对应的灵感
        current_inspiration = None
        for chapters_range, inspiration in PLOT_LINES:
            if chapter_num in chapters_range:
                current_inspiration = inspiration
                break
        
        if current_inspiration:
            # 设置灵感
            set_user_inspiration(current_inspiration)
            story_state.load_all()  # 重新加载以获取最新状态
        else:
            # 使用默认灵感
            print(f"\n📝 第 {chapter_num} 章：使用默认灵感")
            story_state.load_all()
        
        print(f"\n{'='*60}")
        print(f"📝 正在生成第 {chapter_num} 章 ({chapter_num - start_chapter + 1}/20)...")
        print(f"{'='*60}")
        
        # 生成章节
        success, content = chapter_writer.write_chapter(chapter_num, 2500)
        
        if success:
            import re
            title_match = re.search(r'#\s*第[一二三四五六七八九十百\d]+章\s*(.+)', content)
            if title_match:
                title = title_match.group(1).strip()
                print(f"✅ 第 {chapter_num} 章已完成: {title}")
            else:
                print(f"✅ 第 {chapter_num} 章已完成")
        else:
            print(f"❌ 第 {chapter_num} 章生成失败")
        
        # 清除灵感
        clear_user_inspiration()
        
        # 重新加载状态
        story_state.load_all()
        
        # 每章之间稍作停顿
        if chapter_num < end_chapter:
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("🎉 全部20章生成完成！")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 已取消，生成中断")
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)