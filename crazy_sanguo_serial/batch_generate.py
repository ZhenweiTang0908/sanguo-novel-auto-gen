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

# 诸葛亮与刘备的狗血恋爱 - 50章（真实历史风格，无玄幻）
PLOT_LINES = [
    # 暗恋萌芽 (29-32)
    (range(29, 33), """【剧情阶段：诸葛亮的暗恋萌芽】
主线路线：诸葛亮发现自己对刘备产生了超越君臣的感情，深陷自我挣扎。
必须包含：
- 诸葛亮作为刘备的军师，日夜为其出谋划策
- 在频繁的相处中，诸葛亮渐渐被刘备的"仁义"外表吸引
- 诸葛亮发现自己在刘备面前会变得紧张、语无伦次
- 深夜独处时，诸葛亮不自觉地想起刘备的一举一动
- 关羽张飞察觉诸葛亮对刘备的态度有些异常
- 诸葛亮试图用工作麻痹自己，却适得其反
风格：细腻的心理描写，压抑的情感，符合历史背景
禁止：玄幻、穿越、神话元素"""),

    # 刘备的察觉与试探 (33-36)
    (range(33, 37), """【剧情阶段：刘备察觉端倪，开始试探】
主线路线：刘备发现诸葛亮对自己态度有异，故意试探。
必须包含：
- 刘备故意在诸葛亮面前与其他谋士亲近，观察反应
- 诸葛亮努力压抑情绪，但偶尔流露出的醋意让刘备心中暗喜
- 刘备开始有意无意地对诸葛亮进行身体接触（整理衣冠、拍肩等）
- 诸葛亮每次被触碰都脸红心跳，只能借口逃离
- 刘备心中生出一种奇异的满足感
- 两人之间的气氛越来越微妙
风格：暧昧试探，心跳加速，符合古人含蓄的表达方式
禁止：玄幻、穿越、神话元素"""),

    # 情敌出现 (37-40)
    (range(37, 41), """【剧情阶段：曹操加入争夺，醋海翻涌】
主线路线：曹操对诸葛亮也产生了兴趣，刘备醋意大发。
必须包含：
- 曹操率军攻打荆州，意图招降诸葛亮
- 曹操对诸葛亮大献殷勤，送礼、写诗、亲自拜访
- 刘备看到曹操对诸葛亮如此热情，内心极度不适
- 刘备开始对诸葛亮寸步不离，像是在宣示主权
- 诸葛亮夹在两人之间，左右为难
- 曹操故意在刘备面前称赞诸葛亮"世间奇男子"
风格：政治博弈与情感纠葛交织，刘备占有欲爆发
禁止：玄幻、穿越、神话元素"""),

    # 表白与拒绝 (41-44)
    (range(41, 45), """【剧情阶段：诸葛亮终于鼓起勇气表白，却遭刘备拒绝】
主线路线：诸葛亮无法再压抑情感，主动表白却被刘备拒绝。
必须包含：
- 一个月夜，诸葛亮终于鼓起勇气向刘备倾诉衷肠
- 刘备沉默良久，最后说"你我君臣相称，怎可如此"
- 诸葛亮心碎欲裂，誓言此生不再提此事
- 刘备转身离去，但步伐踉跄，眼眶泛红
- 那一夜，诸葛亮独自在草堂借酒浇愁
- 关羽张飞在门外守着，不知如何安慰
风格：细腻的感情描写，古人的压抑与挣扎
禁止：玄幻、穿越、神话元素"""),

    # 冷战与疏离 (45-48)
    (range(45, 49), """【剧情阶段：两人冷战，关系降至冰点】
主线路线：表白被拒后，诸葛亮刻意与刘备保持距离。
必须包含：
- 诸葛亮开始刻意回避刘备，所有军务都通过关羽张飞传达
- 刘备感觉自己被抛弃，脾气变得暴躁
- 每次擦肩而过，诸葛亮都装作视而不见
- 刘备在深夜独自饮酒，喃喃自语"我错了吗"
- 关羽张飞急得团团转，试图缓和两人关系
- 军议时两人面对面却无言以对，气氛尴尬至极
风格：冷战中体现思念，符合古代君臣礼节
禁止：玄幻、穿越、神话元素"""),

    # 危机时刻 (49-52)
    (range(49, 53), """【剧情阶段：曹操大军压境，两人被迫合作】
主线路线：曹操南下攻打荆州，刘备诸葛亮被迫并肩作战。
必须包含：
- 曹操率十万大军南下，刘备危在旦夕
- 诸葛亮强忍个人情感，誓言要为主公效力
- 刘备亲自到诸葛亮草堂请他出山
- 两人相对无言，却胜过千言万语
- 最终诸葛亮答应再次为刘备出谋划策
- 战事紧张期间，两人在地图前彻夜商讨
风格：国难当前的情感压抑，战争与感情交织
禁止：玄幻、穿越、神话元素"""),

    # 并肩作战 (53-56)
    (range(53, 57), """【剧情阶段：赤壁之战中的生死与共】
主线路线：赤壁之战中，两人并肩作战，情感逐渐回温。
必须包含：
- 周瑜诸葛亮联手设计火攻之计
- 深夜偏厅，两人在地图前商讨军情
- 刘备不自觉地握住诸葛亮的手，说"有你在，孤心安"
- 诸葛亮心跳如雷，却努力保持镇定
- 战事激烈，刘备为救诸葛亮身陷险境
- 诸葛亮冒死救出刘备，两人相拥而泣
风格：战火中的真情流露，符合历史战争描写
禁止：玄幻、穿越、神话元素"""),

    # 战后的暧昧 (57-60)
    (range(57, 61), """【剧情阶段：赤壁大捷后的独处时光】
主线路线：赤壁之战胜利后，刘备与诸葛亮独处，感情急剧升温。
必须包含：
- 庆功宴后，刘备"醉意朦胧"地要诸葛亮送他回房
- 两人在月下独行，刘备突然说"其实那天拒绝你，孤后悔了"
- 诸葛亮愣住，刘备趁机拉住他的手
- 两人在长廊尽头接吻，被路过的张飞撞见
- 张飞惊得酒杯摔碎，大喊"大哥你们..."
- 刘备淡定地说"三弟，孤与军师有要事相商"
风格：含蓄又直接的情感表达，符合古代礼教下的突破
禁止：玄幻、穿越、神话元素"""),

    # 周瑜的心事 (61-64)
    (range(61, 65), """【剧情阶段：周瑜对诸葛亮的惺惺相惜】
主线路线：周瑜对诸葛亮有惺惺相惜之情，但发现诸葛亮心中只有刘备。
必须包含：
- 周瑜一直对诸葛亮有惺惺相惜之感
- 发现诸葛亮选择刘备后，周瑜愤怒又不甘
- 周瑜故意设计离间计，试图让诸葛亮离开刘备
- 诸葛亮一眼看穿周瑜的计策，却心痛于他的执念
- 周瑜质问诸葛亮"我哪里不如刘备"
- 诸葛亮说"公瑾，你是我此生最好的知己，但我心里只有主公"
风格：两个聪明人之间的较量，情感的微妙变化
禁止：玄幻、穿越、神话元素"""),

    # 刘备的决定 (65-68)
    (range(68, 72), """【剧情阶段：刘备决定正式与诸葛亮在一起】
主线路线：刘备决定打破世俗，与诸葛亮正式在一起。
必须包含：
- 刘备召集关羽张飞，宣布要与诸葛亮"相守一生"
- 关羽沉默，张飞跳脚大喊"这成何体统"
- 刘备说"我与孔明之情，超越男女，超越世俗，何须他人理解"
- 诸葛亮在屏风后听到，泪流满面
- 刘备亲自到诸葛亮房中，问他"你愿意吗"
- 诸葛亮点头，两人相拥
风格：打破世俗的勇气，符合古代人对情感的执着
禁止：玄幻、穿越、神话元素"""),

    # 舆论风波 (69-72)
    (range(69, 73), """【剧情阶段：蜀汉内部的反应与舆论】
主线路线：刘备与诸葛亮的关系在蜀汉内部引发各种反应。
必须包含：
- 关羽态度复杂，但最终选择支持大哥
- 张飞从反对到接受，成为"最强助攻"
- 糜芳等旧臣窃窃私语，觉得"主公与军师过于亲密"
- 刘备在朝堂上公开为诸葛亮辩护
- 诸葛亮感动得说不出话
- 最终蜀汉内部渐渐接受了两人的关系
风格：古代政治与人伦的冲突，友情与爱情的平衡
禁止：玄幻、穿越、神话元素"""),

    # 婚后日常 (73-76)
    (range(73, 77), """【剧情阶段：新婚后的甜蜜生活】
主线路线：刘备与诸葛亮婚后的甜蜜生活。
必须包含：
- 每天清晨，刘备亲自为诸葛亮整理衣冠
- 军议时两人眉来眼去，关羽张飞看不下去
- 诸葛亮开始学会对刘备撒娇，刘备受用无穷
- 但处理政务时，诸葛亮依然铁面无私
- 夜里，两人秉烛夜谈，谈论天下大势
- 刘备说"孤有今日，全因有孔明"
风格：甜蜜温馨，符合古人含蓄表达
禁止：玄幻、穿越、神话元素"""),

    # 孙权的试探 (77-80)
    (range(77, 81), """【剧情阶段：东吴对蜀汉内部关系的试探】
主线路线：孙权不甘心蜀吴联盟，派鲁肃前往刺探。
必须包含：
- 鲁肃受孙权之命前往荆州，名义上是加强联盟
- 鲁肃发现刘备诸葛亮形影不离，回报孙权
- 孙权大笑，说"原来如此，难怪诸葛亮如此忠心"
- 周瑜听闻此事，心中更加不是滋味
- 孙权故意在信中调侃刘备"听说玄德与军师情同手足？"
- 刘备回信说"孤与孔明，名为君臣，实为..."
风格：外交场合的试探与调侃，符合历史政治斗争
禁止：玄幻、穿越、神话元素"""),
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
    num_chapters = 50  # 生成50章
    end_chapter = start_chapter + num_chapters - 1
    
    print(f"\n🚀 将生成第 {start_chapter} 章到第 {end_chapter} 章（共{num_chapters}章）")
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
        print(f"📝 正在生成第 {chapter_num} 章 ({chapter_num - start_chapter + 1}/{num_chapters})...")
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
    print("🎉 全部50章生成完成！")
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