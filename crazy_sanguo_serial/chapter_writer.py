"""
章节写作器模块
核心的章节生成逻辑
"""

import json
import logging
import re
import random
from typing import Dict, List, Optional, Any, Tuple

from llm_client import get_llm_client
from prompt_builder import get_prompt_builder
from story_state import get_story_state, CreativeRecord, PlotThread
from storage import get_storage
from summarizer import get_summarizer
from reference_reader import get_reference_reader
from config import config, CreativeTypes

logger = logging.getLogger(__name__)


class ChapterWriter:
    """
    章节写作器
    负责生成单章内容，包括创意选择、上下文构建、正文生成等
    """
    
    def __init__(self):
        self.llm = get_llm_client()
        self.prompt_builder = get_prompt_builder()
        self.storage = get_storage()
        self.story_state = get_story_state()
        self.summarizer = get_summarizer()
    
    def write_chapter(
        self, 
        chapter_num: int, 
        target_length: int = 2000,
        reference_count: int = 0,
        chaos_mode: Optional[bool] = False
    ) -> Tuple[bool, str]:
        """
        写一个章节
        
        Args:
            chapter_num: 章节号
            target_length: 目标字数
            reference_count: 从参考语料中抽取的数量（0=不使用，-1=由AI决定）
            chaos_mode: 混杂模式（True=开启，False=关闭，None=由AI决定）
            
        Returns:
            (是否成功, 章节内容)
        """
        logger.info(f"开始写第{chapter_num}章...")
        if chaos_mode is True:
            logger.info("⚡ 混杂模式：AI将完全自主决定所有配置")
        elif chaos_mode is None:
            logger.info("🎲 AI自主模式：AI将决定具体配置")
        
        try:
            # 1. 抽取参考语料
            reference_texts = []
            use_references = False
            
            if chaos_mode is True:
                # 混杂模式：不使用参考语料
                pass
            elif reference_count > 0:
                # 明确指定数量
                ref_reader = get_reference_reader()
                reference_texts = ref_reader.sample_references(
                    category="joke",
                    count=reference_count,
                    target_length=150
                )
                if reference_texts:
                    logger.info(f"📚 已抽取参考语料: {len(reference_texts)} 条")
            elif reference_count == -1 and chaos_mode is not True:
                # AI决定是否使用参考语料，随机 0-3 条
                import random
                ai_ref_count = random.randint(0, 3)
                if ai_ref_count > 0:
                    ref_reader = get_reference_reader()
                    reference_texts = ref_reader.sample_references(
                        category="joke",
                        count=ai_ref_count,
                        target_length=150
                    )
                    logger.info(f"🎲 AI决定使用 {len(reference_texts)} 条参考语料")
            
            # 2. 生成本章创意（混杂模式下跳过，由AI自行决定）
            if chaos_mode is True:
                selected_creatives = ["（由AI自行决定）"]
                logger.info("混杂模式：跳过创意选择")
            else:
                selected_creatives = self._generate_and_select_creatives(chapter_num)
                logger.info(f"本章创意: {selected_creatives}")
            
            # 3. 获取写作上下文（需要在色彩设计前获取）
            recent_summaries = self.story_state.get_recent_summaries(3)
            recent_summary_text = self.summarizer.format_recent_summaries()
            arc_summary = self.story_state.get_current_arc_summary()
            last_ending = self.storage.read_last_chapter_ending(30)
            
            if last_ending is None:
                last_ending = "（这是第一章，没有上一章）"
            
            # 4. 生成章节色彩设计（混杂模式下跳过）
            if chaos_mode is True:
                chapter_color = None
                logger.info("混杂模式：跳过色彩设计")
            else:
                chapter_color = self._generate_chapter_color(
                    chapter_num=chapter_num,
                    story_bible=self.story_state.story_bible or {},
                    recent_chapters_summary=recent_summary_text,
                    last_chapter_ending=last_ending,
                    selected_creatives=selected_creatives
                )
                logger.info(f"本章色彩设计: {chapter_color.get('writing_guidance', '无')}")
            
            # 5. 构建章节衔接包
            context_anchor = self._build_context_anchor()
            
            # 6. 构建写作 prompt（融入色彩设计）
            prompt = self.prompt_builder.build_chapter_prompt(
                story_bible=self.story_state.story_bible or {},
                characters={
                    name: char.__dict__ 
                    for name, char in self.story_state.characters.items()
                },
                plot_state=self.story_state.plot_state,
                context_anchor=context_anchor,
                selected_creatives=selected_creatives,
                chapter_color=chapter_color,
                recent_summaries=recent_summaries,
                arc_summary=arc_summary.__dict__ if arc_summary else None,
                last_chapter_ending=last_ending,
                chapter_num=chapter_num,
                reference_texts=reference_texts if reference_texts else None,
                chaos_mode=chaos_mode
            )
            
            # 7. 确定 temperature
            if chaos_mode is True:
                temperature = 1.2
            elif chaos_mode is None:
                temperature = 1.0  # AI决定模式，适中温度
            else:
                temperature = 0.9
            
            # 8. 调用 LLM 生成正文
            chapter_content = self.llm.generate_chapter(
                prompt=prompt,
                temperature=temperature
            )
            
            # 8. 清理和格式化内容
            chapter_content = self._clean_chapter_content(chapter_content)
            
            # 8. 保存章节
            self._save_chapter(chapter_num, chapter_content)
            
            # 9. 更新故事状态
            self.story_state.increment_chapter()
            
            # 10. 生成本章摘要
            summary = self.summarizer.generate_chapter_summary(chapter_num, chapter_content)
            
            # 11. 更新伏笔和创意记录
            self._update_plot_state(summary, selected_creatives, chapter_num)
            
            # 12. 检查是否需要生成分卷摘要
            if chapter_num % config.chapter.arc_trigger == 0:
                self.summarizer.generate_arc_summary()
            
            # 13. 保存所有状态
            self.story_state.save_all()

            # 14. 清除已使用的设置
            self.story_state.clear_user_inspiration()
            self.story_state.clear_active_characters()

            logger.info(f"第{chapter_num}章写作完成")
            return True, chapter_content
            
        except Exception as e:
            logger.error(f"写章节失败: {e}")
            return False, ""
    
    def _generate_and_select_creatives(self, chapter_num: int) -> List[str]:
        """
        生成并选择本章创意
        
        Args:
            chapter_num: 章节号
            
        Returns:
            选中的创意列表
        """
        logger.info(f"生成本章创意 (第{chapter_num}章)...")
        
        # 获取未使用的创意类型
        unused_types = self.story_state.get_unused_creative_types(8)
        
        # 如果未使用的不够，从全部类型中补充
        if len(unused_types) < 5:
            all_types = list(CreativeTypes.ALL)
            random.shuffle(all_types)
            unused_types = all_types[:8]
        
        # 获取最近章节摘要作为上下文
        recent_summary = self.summarizer.format_recent_summaries()
        
        # 构建创意生成 prompt
        prompt = self.prompt_builder.build_ideas_prompt(
            story_bible=self.story_state.story_bible or {},
            recent_chapters_summary=recent_summary,
            available_creative_types=unused_types,
            chapter_num=chapter_num
        )
        
        try:
            response = self.llm.generate_ideas(prompt)
            
            # 解析创意
            ideas_data = self._parse_ideas_response(response)
            
            if ideas_data and ideas_data.get('ideas'):
                ideas = ideas_data['ideas']
                # 选择 1-2 个创意
                num_select = min(2, len(ideas))
                selected = random.sample(ideas, num_select)
                
                # 记录创意使用
                for idea in selected:
                    creative_record = CreativeRecord(
                        creative_type=idea.get('creative_type', 'unknown'),
                        used_in_chapter=chapter_num,
                        description=idea.get('title', ''),
                        impact=idea.get('how_to_apply', '')
                    )
                    self.story_state.add_used_creative(creative_record)
                
                return [idea.get('title', idea.get('description', '')) for idea in selected]
            
        except Exception as e:
            logger.warning(f"生成创意失败: {e}")
        
        # 备用创意
        return self._get_fallback_creative(unused_types)
    
    def _parse_ideas_response(self, response: str) -> Optional[Dict]:
        """解析创意响应"""
        import re
        
        # 尝试提取 JSON
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        json_match = re.search(r'\{[\s\S]*?"ideas"[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _get_fallback_creative(self, available_types: List[str]) -> List[str]:
        """获取备用创意"""
        fallback_creatives = [
            "角色之间爆发激烈争吵，揭露出过往的恩怨",
            "意外的访客带来了重要的消息",
            "角色发现被最信任的人背叛",
            "一场密谋已久的计划终于浮出水面",
            "角色面临一个艰难的抉择",
        ]
        
        selected = random.sample(fallback_creatives, min(2, len(fallback_creatives)))
        
        # 也选择一个创意类型
        if available_types:
            type_selected = random.choice(available_types)
            selected.append(f"融入 {type_selected} 元素")
        
        return selected
    
    def _generate_chapter_color(
        self,
        chapter_num: int,
        story_bible: Dict,
        recent_chapters_summary: str,
        last_chapter_ending: str,
        selected_creatives: List[str]
    ) -> Dict:
        """
        生成章节的色彩设计
        
        在正式写作前，让AI深度思考本章的色彩、情感、戏剧张力
        并给出极端色彩建议，使文章更具戏剧性
        
        Args:
            chapter_num: 章节号
            story_bible: 世界观设定
            recent_chapters_summary: 最近几章的摘要
            last_chapter_ending: 上一章结尾
            selected_creatives: 已选中的创意列表
            
        Returns:
            章节色彩设计字典
        """
        logger.info(f"生成章节色彩设计 (第{chapter_num}章)...")
        
        # 构建色彩设计 prompt
        prompt = self.prompt_builder.build_chapter_color_prompt(
            story_bible=story_bible,
            recent_chapters_summary=recent_chapters_summary,
            chapter_num=chapter_num,
            last_chapter_ending=last_chapter_ending,
            selected_creatives=selected_creatives
        )
        
        try:
            response = self.llm.generate_creative_direction(prompt)
            
            # 解析响应
            color_data = self._parse_color_response(response)
            
            if color_data:
                logger.info(f"色彩设计解析成功: {color_data.get('writing_guidance', '无')}")
                return color_data
            
        except Exception as e:
            logger.warning(f"生成章节色彩设计失败: {e}")
        
        # 备用色彩设计
        return self._get_fallback_chapter_color()
    
    def _parse_color_response(self, response: str) -> Optional[Dict]:
        """解析色彩设计响应"""
        import re
        
        # 尝试提取 JSON
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        json_match = re.search(r'\{[\s\S]*?"emotion_palette"[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _get_fallback_chapter_color(self) -> Dict:
        """获取备用色彩设计"""
        return {
            "chapter_num": 0,
            "emotion_palette": {
                "main_tone": "癫狂热血",
                "emotion_contrast": "【紧张】vs【爆发】",
                "emotion_peak": "冲突达到顶峰"
            },
            "dramatic_tension": {
                "core_conflict": "正邪对抗",
                "conflict_escalation": "逐步升级",
                "twist_point": "意外反转",
                "life_death_choice": "生死抉择"
            },
            "extreme_colors": [
                {
                    "name": "血色黄昏",
                    "description": "极端悲壮",
                    "how_to_apply": "在大决战时使用"
                },
                {
                    "name": "荒诞喜剧",
                    "description": "黑色幽默",
                    "how_to_apply": "在紧张时刻穿插"
                },
                {
                    "name": "量子扭曲",
                    "description": "魔幻现实",
                    "how_to_apply": "在设定展示时使用"
                }
            ],
            "mood_shifts": [
                {"from": "紧张", "to": "搞笑", "trigger": "张飞登场"},
                {"from": "搞笑", "to": "危机", "trigger": "敌人出现"}
            ],
            "character_highlights": [
                {"character": "刘备", "highlight_moment": "关键抉择"}
            ],
            "writing_guidance": "癫狂热血，节奏紧凑！"
        }
    
    def _build_context_anchor(self) -> Dict:
        """
        构建章节衔接包
        
        Returns:
            包含衔接信息的字典
        """
        return self.summarizer.get_context_for_writing()
    
    def _clean_chapter_content(self, content: str) -> str:
        """
        清理章节内容
        
        Args:
            content: 原始内容
            
        Returns:
            清理后的内容
        """
        # 移除可能的 markdown 代码块标记
        content = content.strip()
        
        # 如果以 ``` 开头，移除它
        if content.startswith('```'):
            lines = content.split('\n')
            if len(lines) > 2:
                content = '\n'.join(lines[1:-1])
        
        # 移除可能的 "json" 或其他语言标记
        content = re.sub(r'^```\w*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n```$', '', content)
        
        # 确保有标题
        if not re.match(r'^#\s*第', content):
            # 在开头添加一个通用标题
            content = "# 第X章 新的冒险\n\n" + content
        
        return content.strip()
    
    def _save_chapter(self, chapter_num: int, content: str):
        """保存章节到文件"""
        chapter_path = self.storage.get_chapter_path(chapter_num)
        
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"章节已保存: {chapter_path}")
    
    def _update_plot_state(
        self, 
        summary: Dict, 
        selected_creatives: List[str],
        chapter_num: int
    ):
        """
        更新剧情状态
        
        Args:
            summary: 章节摘要
            selected_creatives: 本章使用的创意
            chapter_num: 章节号
        """
        # 更新主线（如果摘要中有）
        if summary.get('next_chapter_teaser'):
            # 可以根据需要更新主线
            pass
        
        # 添加新伏笔
        new_hooks = summary.get('new_hooks', [])
        for i, hook in enumerate(new_hooks):
            thread = PlotThread(
                thread_id=f"hook_{chapter_num}_{i}",
                description=hook,
                status="open",
                introduced_chapter=chapter_num
            )
            self.story_state.add_plot_thread(thread)
        
        # 延续的伏笔可以在这里标记
        continued_hooks = summary.get('continued_hooks', [])
        
        # 更新角色状态
        character_changes = summary.get('character_changes', [])
        for change in character_changes:
            name = change.get('name')
            if name:
                self.story_state.update_character_state(
                    name,
                    # 可以添加更多更新字段
                )
    
    def initialize_story(self, keywords: str = "") -> bool:
        """
        初始化故事宇宙
        
        Args:
            keywords: 用户输入的关键词，用于引导世界观生成
            
        Returns:
            是否初始化成功
        """
        logger.info("开始初始化故事宇宙...")
        if keywords:
            logger.info(f"用户关键词: {keywords}")
        
        try:
            # 生成世界观
            prompt = self.prompt_builder.build_init_world_prompt(keywords)
            response = self.llm.generate(prompt, temperature=0.9)
            
            # 解析响应
            story_data = self._parse_story_data(response)
            
            if not story_data:
                logger.error("解析世界观数据失败")
                return False
            
            # 提取数据
            story_bible = story_data
            characters = self._extract_characters(story_data)
            plot_state = {
                "main_conflict": story_data.get("main_conflict", "未知"),
                "sub_conflicts": [],
                "open_threads": [],
                "used_creatives": [],
                "active_creative_types": story_data.get("creative_types_used", [])
            }
            
            # 初始化故事状态
            self.story_state.initialize(story_bible, characters, plot_state)
            
            logger.info("故事宇宙初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化故事失败: {e}")
            return False
    
    def _parse_story_data(self, response: str) -> Optional[Dict]:
        """解析故事数据响应"""
        import re
        
        # 尝试提取 JSON
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        json_match = re.search(r'\{[\s\S]*?"world_overview"[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _extract_characters(self, story_data: Dict) -> Dict:
        """从故事数据中提取角色信息"""
        characters = {}
        
        main_chars = story_data.get('main_characters', [])
        
        for char_data in main_chars:
            name = char_data.get('name', '')
            if not name:
                continue
            
            characters[name] = {
                "name": name,
                "identity": char_data.get('new_identity', char_data.get('original_identity', '未知')),
                "current_location": "初始地点",
                "goal": "待探索",
                "status": "alive",
                "relationship_changes": [],
                "new_traits": []
            }
        
        return characters

    def generate_character(self, count: int = 1) -> List[Dict]:
        """
        随机生成新角色

        Args:
            count: 生成角色数量

        Returns:
            生成的角色列表
        """
        logger.info(f"开始生成 {count} 个角色...")

        world_info = ""
        if self.story_state.story_bible:
            world_info = self.story_state.story_bible.get('world_overview', '')
            factions = self.story_state.story_bible.get('factions', [])
            if factions:
                faction_info = "\n".join([
                    f"- {f.get('name', '未知')}: {f.get('ideology', '')}"
                    for f in factions[:3]
                ])
                world_info += f"\n\n## 势力信息\n{faction_info}"
            core_rules = self.story_state.story_bible.get('core_rules', [])
            if core_rules:
                world_info += f"\n\n## 核心规则\n" + "\n".join([f"- {r}" for r in core_rules[:3]])

        main_conflict = self.story_state.plot_state.get('main_conflict', '')

        prompt = self.prompt_builder.build_generate_character_prompt(
            world_overview=world_info,
            main_conflict=main_conflict,
            existing_characters=self.story_state.characters,
            count=count
        )

        response = self.llm.generate(prompt, temperature=0.9)

        # 解析响应
        characters = self._parse_characters_response(response)
        if not characters:
            logger.error("解析角色数据失败")
            return []

        return characters

    def _parse_characters_response(self, response: str) -> List[Dict]:
        """解析角色生成响应"""
        import re

        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'characters' in data:
                    return data['characters']
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\[[\s\S]*?"name"[\s\S]*?\]', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return []

    def expand_character(self, name: str, description: str) -> Optional[Dict]:
        """
        根据用户提供的名字和一句话描述，AI扩写为完整角色设定

        Args:
            name: 用户提供的角色名
            description: 用户提供的一句话描述

        Returns:
            扩写后的角色数据
        """
        logger.info(f"开始扩写角色: {name}")

        world_overview = ""
        if self.story_state.story_bible:
            world_overview = self.story_state.story_bible.get('world_overview', '')

        main_conflict = self.story_state.plot_state.get('main_conflict', '')

        prompt = self.prompt_builder.build_expand_character_prompt(
            name=name,
            description=description,
            world_overview=world_overview,
            main_conflict=main_conflict,
            existing_characters=self.story_state.characters
        )

        response = self.llm.generate(prompt, temperature=0.8)

        # 解析响应
        char_data = self._parse_single_character_response(response)
        if not char_data:
            logger.error("解析角色数据失败")
            return None

        return char_data

    def _parse_single_character_response(self, response: str) -> Optional[Dict]:
        """解析单个角色响应"""
        import re
        import json

        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if isinstance(data, dict) and 'name' in data:
                    return data
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[\s\S]*?"name"[\s\S]*?\}', response)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                if isinstance(data, dict) and 'name' in data:
                    return data
            except json.JSONDecodeError:
                pass

        return None

    def generate_chapters_continuous(
        self,
        num_chapters: int,
        target_length: int = 2000
    ) -> Dict[str, Any]:
        """
        连续生成多个章节
        
        Args:
            num_chapters: 要生成的章节数
            target_length: 每章目标字数
            
        Returns:
            生成结果统计
        """
        import random
        
        logger.info(f"开始连续生成 {num_chapters} 章...")
        
        results = {
            "total": num_chapters,
            "success": 0,
            "failed": 0,
            "new_characters": [],
            "world_changes": [],
            "chapters": []
        }
        
        start_chapter = self.story_state.get_next_chapter_num()
        
        for i in range(num_chapters):
            chapter_num = start_chapter + i
            logger.info(f"\n{'='*50}")
            logger.info(f"开始生成第 {chapter_num} 章 ({i+1}/{num_chapters})")
            logger.info(f"{'='*50}")
            
            try:
                # 1. AI生成本章灵感（色彩、叙事风格）
                chapter_inspiration = self._generate_chapter_inspiration(chapter_num)
                if chapter_inspiration:
                    results["chapters"].append({
                        "chapter": chapter_num,
                        "inspiration": chapter_inspiration.get("theme", ""),
                        "color": chapter_inspiration.get("color", "")
                    })
                
                # 2. 8%概率添加新角色
                if random.random() < 0.08:
                    logger.info("🎲 触发添加新角色 (8%概率)")
                    new_chars = self.generate_character(1)
                    if new_chars:
                        for char_data in new_chars:
                            name = char_data.get('name', '')
                            if name and name not in self.story_state.characters:
                                self.story_state.add_character(
                                    name=name,
                                    identity=char_data.get('identity', '未知'),
                                    location=char_data.get('current_location', '未知'),
                                    goal=char_data.get('goal', '待探索'),
                                    role=char_data.get('role', 'supporting')
                                )
                                results["new_characters"].append(name)
                                logger.info(f"  ✅ 添加新角色: {name}")
                
                # 3. 3%概率修改世界观
                if random.random() < 0.03:
                    logger.info("🎲 触发修改世界观 (3%概率)")
                    world_change = self._modify_world_view()
                    if world_change:
                        results["world_changes"].append(world_change)
                        logger.info(f"  ✅ 世界观更新: {world_change[:50]}...")
                
                # 4. 随机抽取参考语料（每章0-2条）
                ref_reader = get_reference_reader()
                ref_count = random.randint(0, 2)
                reference_texts = []
                if ref_count > 0:
                    reference_texts = ref_reader.sample_references(
                        category="joke",
                        count=ref_count,
                        target_length=150
                    )
                    if reference_texts:
                        logger.info(f"📚 使用 {len(reference_texts)} 条参考语料")
                
                # 5. 生成章节
                success, content = self.write_chapter(
                    chapter_num=chapter_num,
                    target_length=target_length,
                    reference_count=-1,  # AI决定
                    chaos_mode=None
                )
                
                if success:
                    results["success"] += 1
                    import re
                    title_match = re.search(r'#\s*第[一二三四五六七八九十百\d]+章\s*(.+)', content)
                    if title_match:
                        title = title_match.group(1).strip()
                        logger.info(f"  ✅ 第{chapter_num}章完成: {title}")
                    else:
                        logger.info(f"  ✅ 第{chapter_num}章完成")
                else:
                    results["failed"] += 1
                    logger.error(f"  ❌ 第{chapter_num}章生成失败")
                
                # 每章之间稍作停顿
                if i < num_chapters - 1:
                    import time
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"第{chapter_num}章生成异常: {e}")
                results["failed"] += 1
                import traceback
                traceback.print_exc()
        
        # 保存状态
        self.story_state.save_all()
        
        logger.info(f"\n{'='*50}")
        logger.info(f"连续生成完成: 成功 {results['success']} 章, 失败 {results['failed']} 章")
        if results["new_characters"]:
            logger.info(f"新增角色: {', '.join(results['new_characters'])}")
        if results["world_changes"]:
            logger.info(f"世界观更新次数: {len(results['world_changes'])}")
        logger.info(f"{'='*50}")
        
        return results

    def _generate_chapter_inspiration(self, chapter_num: int) -> Optional[Dict]:
        """AI生成本章的灵感和色彩"""
        try:
            recent_summaries = self.story_state.get_recent_summaries(2)
            chars_info = "\n".join([
                f"- {name}: {char.identity} (位置:{char.current_location}, 目标:{char.goal})"
                for name, char in list(self.story_state.characters.items())[:5]
            ])
            
            world_overview = ""
            if self.story_state.story_bible:
                world_overview = self.story_state.story_bible.get('world_overview', '')
            
            prompt = f"""# 任务：为本章生成创作灵感

## 基本信息
- 章节号：第{chapter_num}章
- 世界观：{world_overview[:200] if world_overview else '未知'}

## 当前角色状态
{chars_info}

## 近期剧情摘要
{recent_summaries if recent_summaries else '（暂无）'}

## 要求

请为本章确定：
1. **主题色彩**：如"权谋暗战"、"情感爆发"、"势力对决"等
2. **叙事风格**：如"紧张悬疑"、"轻松诙谐"、"悲壮史诗"等  
3. **核心事件指引**：本章应该围绕什么事件展开

请生成简洁的JSON格式：
```json
{{
  "color": "色彩主题",
  "style": "叙事风格", 
  "theme": "核心事件指引"
}}
```
"""
            response = self.llm.generate(prompt, temperature=0.8)
            
            # 解析JSON
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_match:
                import json
                return json.loads(json_match.group(1))
            
            json_match = re.search(r'\{"[^"]*":\s*"[^"]*"[^}]*\}', response)
            if json_match:
                import json
                return json.loads(json_match.group(0))
                
        except Exception as e:
            logger.error(f"生成章节灵感失败: {e}")
        
        return None

    def _modify_world_view(self) -> Optional[str]:
        """AI修改世界观（小幅调整）"""
        try:
            current_world = ""
            if self.story_state.story_bible:
                current_world = self.story_state.story_bible.get('world_overview', '')
            
            factions = self.story_state.story_bible.get('factions', [])
            factions_text = "\n".join([f"- {f.get('name', '未知')}" for f in factions]) if factions else "无"
            
            chars_count = len(self.story_state.characters)
            main_chars = [name for name, c in self.story_state.characters.items() if c.role == 'main']
            
            prompt = f"""# 任务：对世界观进行小幅调整

## 当前世界观
{current_world[:300] if current_world else '未知'}

## 当前势力
{factions_text}

## 角色情况
- 总角色数：{chars_count}
- 主演：{', '.join(main_chars) if main_chars else '暂无'}

## 要求

根据最近剧情发展，对世界观进行**小幅调整**（不要大幅改动）：
- 可以添加新的势力动态
- 可以添加新的社会规则
- 可以添加新的势力关系
- 不要删除已有设定
- 不要做颠覆性修改

请生成小幅的世界观更新描述（50字以内）：

```json
{{
  "update": "更新的描述"
}}
```
"""
            response = self.llm.generate(prompt, temperature=0.7)
            
            # 解析JSON
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_match:
                import json
                data = json.loads(json_match.group(1))
                update_text = data.get('update', '')
                
                if update_text and self.story_state.story_bible:
                    # 追加到现有世界观
                    current_overview = self.story_state.story_bible.get('world_overview', '')
                    new_overview = current_overview + "\n" + update_text
                    self.story_state.story_bible['world_overview'] = new_overview
                    return update_text
                    
        except Exception as e:
            logger.error(f"修改世界观失败: {e}")
        
        return None


# 全局实例
_chapter_writer: Optional[ChapterWriter] = None


def get_chapter_writer() -> ChapterWriter:
    """获取章节写作器实例"""
    global _chapter_writer
    if _chapter_writer is None:
        _chapter_writer = ChapterWriter()
    return _chapter_writer
