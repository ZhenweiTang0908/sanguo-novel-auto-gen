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
    def build_init_world_prompt(keywords: str = "") -> str:
        """
        构建初始化世界观的 Prompt

        Args:
            keywords: 用户输入的关键词，用于引导世界观生成
        """
        keyword_section = f"""
## 用户期望

用户希望的世界观关键词：{keywords}

根据这些关键词，创建相应的世界观。如果用户没有提供关键词，则创建一个三国背景的世界。

""" if keywords else """
## 用户期望

用户没有指定特定关键词，将创建一个三国背景的世界观。

"""
        
        return f"""# 任务：创建小说世界观

你是一个故事世界观的构建者。根据用户的需求，创建一个简洁、有深度的小说世界观。

{keyword_section}
## 核心原则

### 题材限制
- **禁止**：科幻、奇幻、修仙、玄幻、哲学思辨、外星文明、神话传说、魔法异能
- **允许**：历史权谋、宫斗、宅斗、战争策略、商场博弈、黑帮火拼、职场斗争等现实题材
- **基调**：现实主义，故事发生在可信的物理和社会规则下

### 风格要求
- **爽文风格**：主角要威风，配角要打脸、敌人要惨
- **节奏明快**：少描写，多叙述，事件密集反转快
- **金句要多**：让读者觉得"太牛了"的台词或情节
- **不要用力过度**：不要过度堆砌设定，不要每个角色都惊天动地

### 语言风格限制
- **禁止**：文言文、古风措辞、诗词歌赋
- **禁止**：冗长环境描写、复杂心理独白
- **禁止**：过于文学化的比喻修辞
- **必须**：短句为主、口语化对话、易读性强

### 魔改方向（适度即可）
- 人物身份的小秘密、小反转
- 势力之间真实的利益博弈
- 角色之间复杂的情感纠葛
- 历史事件的另一种解读

### 题材示例（仅供参考）

**历史类**：三国、明清、民国、抗战、唐朝等历史背景
**现代类**：都市商战、黑道风云、职场斗争、娱乐圈
**其他**：星际政治（但不涉及科幻，仅是政治权谋）

## 输出格式

请生成以下 JSON 格式的世界观设定：

```json
{{
  "world_overview": "世界观简述（100字以内，通俗易懂）",
  "core_rules": [
    "基础规则1",
    "基础规则2"
  ],
  "factions": [
    {{
      "name": "势力名",
      "leader": "领袖",
      "special_power": "势力特长",
      "ideology": "势力理念"
    }}
  ],
  "main_characters": [
    {{
      "name": "角色名",
      "original_identity": "身份",
      "new_identity": "真实身份（可选）",
      "core_trait": "核心特质",
      "secret": "隐藏秘密（可选，不要太夸张）"
    }}
  ],
  "main_conflict": "当前主线冲突",
  "sustainable_hooks": [
    "钩子1",
    "钩子2"
  ],
  "creative_types_used": [
    "betrayal_reveal",
    "identity_swap"
  ]
}}
```

## 注意事项
- 角色数量控制在6-10人
- 每个角色可以有秘密，但不要每个角色都惊天动地的身世
- 伏笔要有用，不要挖太多坑
- 世界观要服务于故事，不要喧宾夺主

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
        chapter_color: Optional[Dict] = None,
        reference_texts: Optional[List[str]] = None,
        chaos_mode: Optional[bool] = False,
        temp_characters: Optional[List[Dict]] = None
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
            reference_texts: 参考语料列表（可选）
            chaos_mode: 混杂模式（True=开启，False=关闭，None=AI决定）
            temp_characters: 临时人物列表（仅本章出现）
        """
        prompt = f"""# 第{chapter_num}章 续写任务

## ⚠️ 重要指令

这是一本长篇连载网络小说。
你必须：
1. 严格遵循下面提供的世界观和角色设定
2. 必须先回应上一章结尾的钩子
3. 融入本章的创意元素
4. 章节结尾必须留下钩子

**🚫 语言风格禁止**：
- 禁止：文言文、古风措辞、诗词歌赋
- 禁止：冗长环境描写（超过3句）
- 禁止：心理活动独白超过5句
- 禁止：过于文学化的比喻修辞
- 禁止：学术化、政治化的严肃措辞
- 禁止：西方名字、地名
- 禁止：复杂句式（超过3个从句）

**✅ 必须遵循的文风**：
- ✅ 短句为主：每段不超过5句，每句不超过20字
- ✅ 对话自然：像网文一样直白、口语化
- ✅ 节奏明快：事件密集，反转快，不拖沓
- ✅ 金句点缀：让读者觉得"太牛了"的台词或情节
- ✅ 爽点突出：主角威风、配角出彩、敌人惨
- ✅ 易读性强：小学生都能轻松看懂

"""
        
        if chaos_mode is True:
            prompt += """
## ⚡ 混杂模式

**完全由你决定！** 本章的所有配置由AI根据剧情发展自行决定，
请写出你认为最精彩的章节！

"""
        elif chaos_mode is None:
            prompt += """
## 🎲 AI自主模式

以下提供的色彩设计、创意元素仅供参考，
你可以根据剧情发展自行决定是否采用。

"""
        
        if reference_texts:
            prompt += """
## 📚 参考语料（学习其风格）

以下是从笑话集中抽取的参考文本，**学习其幽默风格并融入本章**：
注意：不要直接复制内容，学习其讽刺、幽默、反转的技巧！

"""
            for i, ref in enumerate(reference_texts, 1):
                prompt += f"""### 参考{i}
{ref}

"""

        # 如果有色彩设计，添加到 prompt 中
        if chapter_color:
            palette = chapter_color.get('emotion_palette', {})
            tension = chapter_color.get('dramatic_tension', {})
            prompt += f"""
---

## 🎨 章节设计

### 情感基调
- **主色调**: {palette.get('main_tone', '紧张/热血')}
- **情感对比**: {palette.get('emotion_contrast', '紧张→爆发')}
- **情感峰值**: {palette.get('emotion_peak', '冲突高潮')}

### 戏剧张力
- **核心冲突**: {tension.get('core_conflict', '势力对抗')}
- **冲突升级**: {tension.get('conflict_escalation', '逐步升级')}
- **转折点**: {tension.get('twist_point', '意外反转')}

### 氛围切换
"""
            for shift in chapter_color.get('mood_shifts', [])[:2]:
                prompt += f"- {shift.get('from', 'A')} → {shift.get('to', 'B')}（触发: {shift.get('trigger', '事件')}）\n"
            
            highlights = chapter_color.get('character_highlights', [])
            if highlights:
                prompt += """
### 角色高光
"""
                for highlight in highlights[:2]:
                    prompt += f"- **{highlight.get('character', '未知')}**: {highlight.get('highlight_moment', '高光时刻')}\n"
            
            writing_guidance = chapter_color.get('writing_guidance', '节奏紧凑，事件密集！')
            prompt += f"""
> **指导语**: {writing_guidance}

"""
        
        if chaos_mode is True:
            prompt += """
## ⚡ 混杂模式

**完全由你决定！** 本章的所有配置（情感基调、写作风格、叙事节奏等）
都由AI根据剧情发展自行决定，不受以下色彩设计的约束。
请尽情发挥，写出你认为最精彩的章节！

"""
        elif chaos_mode is None:
            prompt += """
## 🎲 AI自主模式

**由你决定！** 以下提供的色彩设计、创意元素和参考语料仅供参考，
你可以根据剧情发展自行决定是否采用，以及如何调整。
请写出你认为最精彩的章节！

"""
        
        if reference_texts:
            prompt += """
## 📚 参考语料（学习其风格）

以下是从笑话集中抽取的参考文本，**学习其幽默风格并融入本章**：
注意：不要直接复制内容，而是学习其讽刺、幽默、反转的技巧！

"""
            for i, ref in enumerate(reference_texts, 1):
                prompt += f"""### 参考{i}
{ref}

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
        
        # 添加临时人物
        if temp_characters:
            prompt += """---

## 🌿 本章临时人物（仅本章出现）

以下人物是本章故事中的过客，仅在此章节出现，不会出现在后续章节中。
请自然地融入故事，可以让他们与永久角色互动。

"""
            for temp_char in temp_characters:
                prompt += f"""### {temp_char.get('name', '未知')}
- 身份：{temp_char.get('identity', '未知')}
- 本章作用：{temp_char.get('role_in_chapter', '待描述')}

"""
        
        prompt += """---

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

## 🎯 本章创意

本章需要包含以下创意（合理融入）：

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
- **爽文风格**：主角威风、配角打脸、敌人要惨
- **节奏明快**：少描写多叙述，事件密集推进
- **对话推进**：用对话推进剧情，让人物自己说话
- **金句点缀**：适当的精彩台词
- **不要用力过度**：不要每个情节都惊天动地

### 长度
- 1500-2500 字

### 格式
使用 Markdown 格式：
- # 第X章 章节标题
- 正文分段清晰
- 章节结尾留钩子

### 结构
1. 开篇：回应上章钩子，直接进入（100字）
2. 发展：事件+对话+反转，推进剧情
3. 高潮：主角表现，配角打脸
4. 结尾：留下钩子

---

## 🚀 开始创作

请创作第{chapter_num}章！
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

你是一个故事策划。请为下一章生成2-3个合理但有趣的创意。

## 当前世界观摘要
{story_bible.get('world_overview', '未知')}

## 最近章节回顾
{recent_chapters_summary}

## 可用的创意类型
{creative_types_str}

---

## 要求

每个创意要：
1. 符合当前世界观和人物设定
2. 能推进剧情或增加看点
3. 不要太夸张离谱
4. 1-2句话描述即可

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
        
        在正式写作前，让AI思考本章的情感基调和叙事节奏
        
        Args:
            story_bible: 世界观设定
            recent_chapters_summary: 最近几章的摘要
            chapter_num: 当前章节号
            last_chapter_ending: 上一章结尾
            selected_creatives: 已选中的创意列表
        """
        creatives_str = "\n".join([f"- {c}" for c in selected_creatives])
        
        return f"""# 🎨 章节色彩设计：为第{chapter_num}章规划

你需要为这一章设计合适的情感基调和叙事节奏。

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
{story_bible.get('world_overview', '未知')[:500]}

---

## 🎯 设计要求

### 1. 情感基调
- **主色调**: 本章的主导情感（紧张/热血/悬疑/搞笑等）
- **情感对比**: 开头和结尾的情感变化
- **情感峰值**: 本章最精彩的那一刻

### 2. 戏剧张力
- **核心冲突**: 本章主要冲突
- **冲突升级**: 冲突如何推进
- **转折点**: 可能的反转
- **生死抉择**: 角色的艰难选择

### 3. 叙事节奏
- **节奏**: 快/中等/慢
- **氛围切换**: 1-2个切换点即可

### 4. 角色高光
- 本章重点表现的角色

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

    @staticmethod
    def build_generate_character_prompt(
        world_overview: str,
        main_conflict: str,
        existing_characters: Dict[str, Any],
        count: int = 1
    ) -> str:
        """
        构建随机生成角色的 Prompt

        Args:
            world_overview: 世界观概述
            main_conflict: 主线冲突
            existing_characters: 已存在的角色
            count: 生成角色数量
        """
        def format_char(name: str, char) -> str:
            if hasattr(char, 'identity'):
                return f"- {name}: {char.identity} [{char.role}]"
            return f"- {name}: {char.get('identity', '未知')} [{char.get('role', 'supporting')}]"
        
        chars_text = "\n".join([
            format_char(name, char) for name, char in existing_characters.items()
        ]) or "（暂无角色）"

        return f"""# 任务：随机生成新角色

根据以下世界观信息，生成符合这个世界的新角色。

## 世界观
{world_overview[:500] if world_overview else '未知'}

## 主线冲突
{main_conflict if main_conflict else '未知'}

## 已存在角色
{chars_text}

## 要求

1. 生成 {count} 个新角色
2. 角色身份要与世界观和主线冲突相符
3. 可以是主演或配角
4. 每个角色需要有：
   - name: 角色名
   - identity: 身份设定
   - current_location: 当前位置
   - goal: 当前目标
   - role: "main" 或 "supporting"
   - core_trait: 核心特质（一句话）

## 输出格式

请生成 JSON 格式的角色列表：

```json
[
  {{
    "name": "角色名",
    "identity": "身份设定",
    "current_location": "当前位置",
    "goal": "当前目标",
    "role": "main/supporting",
    "core_trait": "核心特质"
  }}
]
```

请立即生成角色！
"""

    @staticmethod
    def build_expand_character_prompt(
        name: str,
        description: str,
        world_overview: str,
        main_conflict: str,
        existing_characters: Dict[str, Any]
    ) -> str:
        """
        构建扩写角色设定的 Prompt

        Args:
            name: 用户提供的角色名
            description: 用户提供的一句话描述
            world_overview: 世界观概述
            main_conflict: 主线冲突
            existing_characters: 已存在的角色
        """
        def format_char(n: str, char) -> str:
            if hasattr(char, 'identity'):
                return f"- {n}: {char.identity} [{char.role}]"
            return f"- {n}: {char.get('identity', '未知')} [{char.get('role', 'supporting')}]"
        
        chars_text = "\n".join([
            format_char(n, char) for n, char in existing_characters.items()
        ]) or "（暂无角色）"

        return f"""# 任务：扩写角色设定

用户希望创建一个名为「{name}」的角色，描述是：「{description}」

请根据这个描述，将其扩写为一个完整的角色设定（100字左右）。

## 世界观
{world_overview[:500] if world_overview else '未知'}

## 主线冲突
{main_conflict if main_conflict else '未知'}

## 已存在角色（注意不要与这些角色重复）
{chars_text}

## 要求

1. 保留用户给定的角色名
2. 基于用户描述，合理扩写角色设定
3. 角色身份要与世界观和主线冲突相符
4. 扩写后的角色需要有：
   - name: 角色名（使用用户提供的）
   - identity: 身份设定（扩写到50字左右）
   - current_location: 当前位置
   - goal: 当前目标
   - role: "main" 或 "supporting"（根据角色重要性判断）
   - core_trait: 核心特质（一句话，20字以内）

## 输出格式

请生成 JSON 格式的角色：

```json
{{
  "name": "{name}",
  "identity": "扩写后的身份设定（50字左右）",
  "current_location": "当前位置",
  "goal": "当前目标",
  "role": "main/supporting",
  "core_trait": "核心特质一句话"
}}
```

请立即生成！
"""


# 全局实例
_prompt_builder: Optional[PromptBuilder] = None


def get_prompt_builder() -> PromptBuilder:
    """获取 Prompt 构建器实例"""
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = PromptBuilder()
    return _prompt_builder
