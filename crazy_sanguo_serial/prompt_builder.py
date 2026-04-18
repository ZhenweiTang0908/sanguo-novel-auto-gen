"""
Prompt 构建器模块
模块化组织所有 prompt 模板
"""

from typing import Dict, List, Optional, Any


class PromptBuilder:
    """
    Prompt 构建器
    负责构建各类 LLM 调用所需的 prompt
    """
    
    # ==================== 初始化相关 Prompt ====================
    
    @staticmethod
    def build_init_world_prompt() -> str:
        """
        构建初始化世界观的 Prompt

        Returns:
            用于生成初始世界观设定的 prompt
        """
        return """# 任务：创建一个魔改三国世界观

你是这个疯狂宇宙的造物主。现在要为一本三国同人小说创建基础设定。

## 核心要求

### 1. 基础设定（保持原样）
- 时代：东汉末年，黄巾起义之后
- 地理：九州框架
- 人物：三国主要人物（刘备、关羽、张飞、曹操、孙权、诸葛亮等）
- 势力：魏/蜀/吴三国

### 2. 世界观（保持简洁正常）
- 不需要复杂的修炼体系
- 不需要上古神族、外星文明
- 不需要科幻元素
- 保持历史小说的基本框架

### 3. 魔改点在【剧情和人物关系】上！

举例魔改手法（全部要体现在伏笔和人物设定中）：
- 人物身份颠倒：刘备其实是曹操的亲兄弟 / 诸葛亮是女性卧底
- 隐藏血脉：某人其实是前朝皇室遗孤 / 孙权是龙的化身
- 背叛与反转：最信任的人其实是卧底 / 敌人其实在保护你
- 历史事件重塑：赤壁之战其实是因为一场赌约 / 夷陵之战是诸葛亮设的局
- 阴谋论：董卓之死是王允和吕布联手策划的 / 黄巾起义背后有人操控
- 身份秘密：华雄其实没死 / 貂蝉是间谍
- 命运纠缠：某些人物之间有"宿命"绑定

### 4. 必须包含的内容

请生成以下 JSON 格式的世界观设定：

```json
{
  "world_overview": "世界观简述（100字）",
  "core_rules": [
    "规则1：某种基础设定",
    "规则2：某种基础设定"
  ],
  "factions": [
    {
      "name": "势力名",
      "leader": "领袖",
      "special_power": "势力特长",
      "ideology": "势力理念"
    }
  ],
  "main_characters": [
    {
      "name": "角色名",
      "original_identity": "原本身份",
      "new_identity": "真实身份或隐藏身份",
      "core_trait": "核心特质",
      "secret": "隐藏秘密或阴谋"
    }
  ],
  "main_conflict": "当前主线冲突",
  "sustainable_hooks": [
    "伏笔1：某个阴谋或秘密",
    "伏笔2：某个身份反转",
    "伏笔3：某个命运纠缠"
  ],
  "creative_types_used": [
    "betrayal_reveal",
    "identity_swap"
  ]
}
```

## 风格要求

- 世界观简洁正常，魔改点在剧情和人物秘密、人物关系上
- 每个角色都要有隐藏的秘密
- 部分角色包含恶趣味
- 大部分角色都庸俗化和带有市井气味，没有那种英雄感
- 允许同性恋、恋物癖、三角恋等元素出现
- 允许角色有反派行为
- 每个伏笔都要能持续挖坑

请立即生成！"""

    # ==================== 章节续写 Prompt ====================
    
    @staticmethod
    def build_chapter_prompt(
        story_bible: Dict,
        characters: Dict[str, Any],
        plot_state: Dict,
        context_anchor: Dict,
        selected_creatives: List[str],
        recent_summaries: List[Dict],
        arc_summary: Optional[Dict],
        last_chapter_ending: str,
        chapter_num: int,
        chapter_color: Optional[Dict] = None
    ) -> str:
        """
        构建章节续写 Prompt
        
        Args:
            story_bible: 世界观设定
            characters: 角色状态
            plot_state: 当前剧情状态
            context_anchor: 章节衔接包
            selected_creatives: 本章要使用的创意
            recent_summaries: 最近章节摘要
            arc_summary: 当前分卷摘要
            last_chapter_ending: 上一章结尾
            chapter_num: 当前章节号
            chapter_color: 章节色彩设计（可选）
        """
        prompt = f"""# 疯狂三国·第{chapter_num}章 续写任务

## ⚠️ 重要指令

这是一本**极度反原著、脑洞离谱、设定癫狂**的魔改三国长篇连载小说。
你必须：
1. 严格遵循下面提供的世界观和角色设定
2. 必须先回应上一章结尾的钩子
3. 注入本章的创意元素
4. 章节结尾必须留下强钩子

**禁止**：
- 不要重新介绍世界观
- 不要像写独立短篇
- 不要忽略刚发生的大事件
- 不要让所有角色说一样的话

"""

        # 如果有色彩设计，添加到 prompt 中
        if chapter_color:
            prompt += f"""
---

## 🎨 章节色彩设计（必须遵循！）

### 情感基调
- **主色调**: {chapter_color.get('emotion_palette', {}).get('main_tone', '癫狂热血')}
- **情感对比**: {chapter_color.get('emotion_palette', {}).get('emotion_contrast', '【紧张】vs【爆发】')}
- **情感峰值**: {chapter_color.get('emotion_palette', {}).get('emotion_peak', '冲突达到顶峰')}

### 戏剧张力
- **核心冲突**: {chapter_color.get('dramatic_tension', {}).get('core_conflict', '正邪对抗')}
- **冲突升级**: {chapter_color.get('dramatic_tension', {}).get('conflict_escalation', '逐步升级')}
- **转折点**: {chapter_color.get('dramatic_tension', {}).get('twist_point', '意外反转')}
- **生死抉择**: {chapter_color.get('dramatic_tension', {}).get('life_death_choice', '生死抉择')}

### 🚨 极端色彩（必须实现！）
"""
            for i, color in enumerate(chapter_color.get('extreme_colors', [])[:3], 1):
                prompt += f"""
**极端色彩{i}: {color.get('name', '未知')}**
- 描述: {color.get('description', '无')}
- 如何呈现: {color.get('how_to_apply', '无')}
"""
            
            prompt += f"""
### 氛围切换
"""
            for shift in chapter_color.get('mood_shifts', [])[:3]:
                prompt += f"- {shift.get('from', 'A')} → {shift.get('to', 'B')}（触发: {shift.get('trigger', '事件')}）\n"
            
            prompt += f"""
### 角色高光
"""
            for highlight in chapter_color.get('character_highlights', [])[:2]:
                prompt += f"- **{highlight.get('character', '未知')}**: {highlight.get('highlight_moment', '高光时刻')}\n"
            
            writing_guidance = chapter_color.get('writing_guidance', '癫狂热血，节奏紧凑！')
            prompt += f"""
### 写手指导语
> **{writing_guidance}**"

"""
        
        prompt += f"""---

## 📖 世界观设定（必须遵守）

```json
{story_bible}
```

---

## 👥 当前活跃角色状态

"""
        
        # 添加角色状态（如果用户指定了角色，优先显示）
        active_chars = plot_state.get('active_characters')
        if active_chars:
            # 按用户指定的顺序排列
            chars_to_show = []
            for name in active_chars:
                if name in characters:
                    chars_to_show.append((name, characters[name]))
            # 添加其他角色
            for name, char in characters.items():
                if name not in active_chars:
                    chars_to_show.append((name, char))
        else:
            # 默认：main 角色优先
            chars_sorted = sorted(characters.items(), key=lambda x: x[1].get('role', 'supporting') != 'main', reverse=True)
            chars_to_show = chars_sorted[:8]

        for name, char in chars_to_show:
            role_label = "【主演】" if char.get('role') == 'main' else "【配角】"
            prompt += f"""### {name} {role_label}
- 身份：{char.get('identity', '未知')}
- 当前位置：{char.get('current_location', '未知')}
- 当前目标：{char.get('goal', '未知')}
- 状态：{char.get('status', '未知')}

"""
        
        prompt += f"""---

## 🔗 章节衔接包（必须优先处理）

### 上一章结尾发生了什么
```
{last_chapter_ending}
```

### 当前场景
{context_anchor.get('current_location', '未知')}

### 主要视角角色
{context_anchor.get('main_pov_character', '未知')}

### 角色的即时目标
{context_anchor.get('immediate_goal', '未知')}

### 当前最大的紧张点
{context_anchor.get('tension_point', '未知')}

### 这一章必须回应的钩子
{context_anchor.get('hook_to_resolve', '未知')}

---

## 🎯 本章创意注入

本章必须包含以下创意（全部实现，越离谱越好！）：

"""
        
        for i, creative in enumerate(selected_creatives, 1):
            prompt += f"{i}. {creative}\n"

        user_inspiration = plot_state.get('user_inspiration')
        if user_inspiration:
            prompt += f"""
---

## 💡 用户指定灵感（必须融入本章！）
**{user_inspiration}**
"""

        prompt += """
---

## 📜 最近剧情摘要

"""
        
        if recent_summaries:
            prompt += "### 近期章节回顾\n"
            for summary in recent_summaries[-3:]:
                prompt += f"- {summary.get('chapter_title', '未知')}: {summary.get('events', ['无'])[0] if summary.get('events') else '无'}\n"
        
        if arc_summary:
            prompt += f"""
### 当前分卷概览
{arc_summary.get('summary', '无')}
"""
        
        prompt += f"""
---

## 📍 当前主线
{plot_state.get('main_conflict', '未知')}

## 🔮 未解决的伏笔
"""
        
        open_threads = plot_state.get('open_threads', [])
        if open_threads:
            for thread in open_threads[-5:]:
                if isinstance(thread, dict) and thread.get('status') == 'open':
                    prompt += f"- {thread.get('description', '未知伏笔')}\n"
        else:
            prompt += "暂无已知伏笔\n"
        
        prompt += """
---

## ✍️ 写作要求

### 风格
- 荒诞史诗 + 热血邪典 + 黑色幽默
- 网文节奏：快节奏、高潮迭起
- 每章必须有推进、有爆点、有结尾钩子

### 长度
- 1500-3000 字
- 章节标题要吸引眼球

### 格式
使用 Markdown 格式：
- # 第X章 章节标题
- 正文分段清晰
- 章节结尾留钩子（可以用"..."或问句）

### 章节结构建议
1. 开篇：回应上章钩子（200字）
2. 发展：推进剧情 + 注入创意（1500字）
3. 高潮：冲突爆发
4. 结尾：留下强钩子

---

## 🚀 开始创作

请立即开始创作第{chapter_num}章！
"""
        
        return prompt
    
    # ==================== 摘要生成 Prompt ====================
    
    @staticmethod
    def build_summary_prompt(chapter_num: int, chapter_content: str) -> str:
        """
        构建章节摘要 Prompt
        
        Args:
            chapter_num: 章节号
            chapter_content: 章节正文
        """
        return f"""# 任务：为第{chapter_num}章生成结构化摘要

你是故事分析师。请仔细阅读以下章节内容，生成详细的结构化摘要。

## 章节内容

{chapter_content}

---

## 输出要求

请生成以下 JSON 格式的摘要：

```json
{{
  "chapter_num": {chapter_num},
  "chapter_title": "从章节中提取的标题",
  "events": [
    "事件1描述",
    "事件2描述",
    "事件3描述"
  ],
  "new_settings": [
    "本章新引入的设定或世界观元素"
  ],
  "character_changes": [
    {{
      "name": "角色名",
      "change": "发生了什么变化"
    }}
  ],
  "faction_changes": [
    "势力关系或力量对比的变化"
  ],
  "new_hooks": [
    "本章埋下的新伏笔"
  ],
  "continued_hooks": [
    "本章延续的伏笔"
  ],
  "style_highlights": [
    "本章的风格亮点"
  ],
  "next_chapter_teaser": "下一章应该从哪个方向展开",
  "word_count": 字数统计
}}
```

请立即生成摘要！
"""

    @staticmethod
    def build_arc_summary_prompt(
        arc_id: int,
        chapter_summaries: List[Dict]
    ) -> str:
        """
        构建分卷摘要 Prompt
        
        Args:
            arc_id: 分卷编号
            chapter_summaries: 要合并的章节摘要列表
        """
        summaries_text = "\n\n".join([
            f"### 第{summary.get('chapter_num', '?')}章: {summary.get('chapter_title', '无标题')}\n"
            f"事件: {', '.join(summary.get('events', []))}\n"
            f"角色变化: {', '.join([c.get('change', '') for c in summary.get('character_changes', [])])}\n"
            f"伏笔: {', '.join(summary.get('new_hooks', []))}"
            for summary in chapter_summaries
        ])
        
        return f"""# 任务：生成分卷摘要

将多个章节摘要合并为一个精炼的分卷摘要。

## 要合并的章节摘要

{summaries_text}

---

## 输出要求

生成以下 JSON 格式的分卷摘要：

```json
{{
  "arc_id": {arc_id},
  "chapters": "1-X",
  "summary": "分卷整体摘要（300字）",
  "key_events": [
    "关键事件1",
    "关键事件2",
    "关键事件3"
  ],
  "main_conflicts": [
    "主要冲突1",
    "主要冲突2"
  ],
  "resolved_hooks": [
    "本卷解决的伏笔"
  ],
  "continuing_hooks": [
    "延续到下一卷的伏笔"
  ],
  "character_developments": [
    "角色发展总结"
  ]
}}
```

请立即生成分卷摘要！
"""

    # ==================== 创意生成 Prompt ====================
    
    @staticmethod
    def build_ideas_prompt(
        story_bible: Dict,
        recent_chapters_summary: str,
        available_creative_types: List[str],
        chapter_num: int
    ) -> str:
        """
        构建创意生成 Prompt
        
        Args:
            story_bible: 世界观设定
            recent_chapters_summary: 最近几章的摘要
            available_creative_types: 可用的创意类型
            chapter_num: 当前章节号
        """
        creative_types_str = "\n".join([f"- {ct}" for ct in available_creative_types])
        
        return f"""# 任务：为第{chapter_num}章生成创意候选

你是创意大师。请为下一章生成3-5个癫狂但合理的创意。

## 当前世界观摘要
{story_bible.get('world_overview', '未知')}

## 最近章节回顾
{recent_chapters_summary}

## 可用的创意类型
{creative_types_str}

---

## 要求

每个创意必须：
1. 比前文更离谱
2. 不能完全脱离已建立的设定
3. 能制造新冲突/新笑点/新反转
4. 有1-2句话的简短描述

## 输出格式

```json
{{
  "ideas": [
    {{
      "creative_type": "使用的创意类型",
      "title": "创意名称",
      "description": "具体描述（2-3句话）",
      "how_to_apply": "如何在本章中应用"
    }},
    ...
  ]
}}
```

请生成3-5个创意！
"""

    @staticmethod
    def build_chapter_color_prompt(
        story_bible: Dict,
        recent_chapters_summary: str,
        chapter_num: int,
        last_chapter_ending: str,
        selected_creatives: List[str]
    ) -> str:
        """
        构建章节创意方向/色彩 Prompt
        
        在正式写作前，让AI深度思考本章的色彩、情感、戏剧张力
        并给出极端色彩建议，使文章更具戏剧性
        
        Args:
            story_bible: 世界观设定
            recent_chapters_summary: 最近几章的摘要
            chapter_num: 当前章节号
            last_chapter_ending: 上一章结尾
            selected_creatives: 已选中的创意列表
        """
        creatives_str = "\n".join([f"- {c}" for c in selected_creatives])
        
        return f"""# 🎨 章节色彩设计任务：为第{chapter_num}章注入灵魂

**这是正式写作前的关键一步！**
你需要为这一章设计独特的"色彩配方"，让故事更具戏剧张力和情感冲击力。

---

## 📜 剧情背景

### 上一章结尾
```
{last_chapter_ending}
```

### 最近剧情回顾
{recent_chapters_summary}

### 本章使用的创意
{creatives_str}

### 世界观基调
{story_bible.get('world_overview', '未知')[:500]}...

---

## 🎯 你的任务

请为这一章设计以下元素，并给出**极端化**的建议：

### 1. 情感基调 (Emotion Palette)
- **主色调**: 这一章的主导情感是什么？（悲壮/癫狂/悬疑/热血/黑色幽默/荒诞）
- **情感对比**: 开头和结尾的情感对比（越极端越好）
- **情感峰值**: 本章情感最激烈的那一刻是什么？

### 2. 戏剧张力设计 (Dramatic Tension)
- **核心冲突**: 本章最核心的冲突是什么？
- **冲突升级**: 冲突如何一步步升级？
- **转折点**: 最意想不到的反转是什么？
- **生死抉择**: 角色面临的最艰难选择？

### 3. 极端色彩建议 (Extreme Colors)
请给出3个"极端色彩"建议，这些建议应该：
- **超出常规**：不是普通的剧情发展
- **视觉冲击**：让读者产生强烈的画面感
- **情感极端**：要么极悲、极喜、极荒诞、极恐怖
- **与创意融合**：融合本章的创意元素

### 4. 氛围切换点 (Mood Shifts)
本章应该有几个氛围切换点？每个切换带来什么变化？

### 5. 角色高光时刻 (Character Highlights)
哪个角色在本章有最亮眼的表现？他们的"高光时刻"是什么？

---

## 📊 输出格式

请生成以下JSON格式的章节色彩设计：

```json
{{
  "chapter_num": {chapter_num},
  "emotion_palette": {{
    "main_tone": "主导情感",
    "emotion_contrast": "【开头】vs【结尾】的情感对比",
    "emotion_peak": "情感峰值描述"
  }},
  "dramatic_tension": {{
    "core_conflict": "核心冲突",
    "conflict_escalation": "冲突升级路径",
    "twist_point": "本章最大反转",
    "life_death_choice": "生死抉择"
  }},
  "extreme_colors": [
    {{
      "name": "极端色彩名称",
      "description": "具体描述（为什么极端？）",
      "how_to_apply": "如何在章节中呈现"
    }},
    {{
      "name": "极端色彩名称2",
      "description": "具体描述",
      "how_to_apply": "如何呈现"
    }},
    {{
      "name": "极端色彩名称3",
      "description": "具体描述",
      "how_to_apply": "如何呈现"
    }}
  ],
  "mood_shifts": [
    {{"from": "氛围A", "to": "氛围B", "trigger": "触发事件"}},
    {{"from": "氛围B", "to": "氛围C", "trigger": "触发事件"}}
  ],
  "character_highlights": [
    {{"character": "角色名", "highlight_moment": "高光时刻描述"}}
  ],
  "writing_guidance": "给写手的指导语（50字以内）"
}}
```

---

## ⚡ 重要提醒

1. **越极端越好**！不要保守，要癫狂！
2. 每个极端色彩都应该有**具体的场景描述**
3. 情感对比要**首尾呼应但反差强烈**
4. 这个设计将直接影响章节写作质量！

请立即开始设计！
"""

    # ==================== 角色状态更新 Prompt ====================
    
    @staticmethod
    def build_character_update_prompt(
        characters: Dict[str, Any],
        chapter_summary: Dict
    ) -> str:
        """
        构建角色状态更新 Prompt
        
        Args:
            characters: 当前角色状态
            chapter_summary: 章节摘要
        """
        chars_text = "\n".join([
            f"### {name}\n- 身份: {char.get('identity', '未知')}\n- 位置: {char.get('current_location', '未知')}\n- 目标: {char.get('goal', '未知')}"
            for name, char in characters.items()
        ])
        
        return f"""# 任务：更新角色状态

基于本章发生的事件，更新角色状态。

## 当前角色状态
{chars_text}

## 本章摘要
{chapter_summary.get('events', [])}

## 本章角色变化
{chapter_summary.get('character_changes', [])}

---

## 输出要求

请生成 JSON 格式的角色更新：

```json
{{
  "updates": [
    {{
      "name": "角色名",
      "location_change": "新位置或null",
      "goal_change": "新目标或null",
      "status_change": "alive/dead/missing/transformed或null",
      "relationship_changes": ["关系变化描述"],
      "new_traits": ["新增特质"]
    }}
  ]
}}
```

请立即生成角色更新！
"""


# 全局实例
_prompt_builder: Optional[PromptBuilder] = None


def get_prompt_builder() -> PromptBuilder:
    """获取 Prompt 构建器实例"""
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = PromptBuilder()
    return _prompt_builder
