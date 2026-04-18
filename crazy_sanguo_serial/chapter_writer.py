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
    
    def write_chapter(self, chapter_num: int, target_length: int = 2000) -> Tuple[bool, str]:
        """
        写一个章节
        
        Args:
            chapter_num: 章节号
            target_length: 目标字数
            
        Returns:
            (是否成功, 章节内容)
        """
        logger.info(f"开始写第{chapter_num}章...")
        
        try:
            # 1. 生成本章创意
            selected_creatives = self._generate_and_select_creatives(chapter_num)
            logger.info(f"本章创意: {selected_creatives}")
            
            # 2. 获取写作上下文（需要在色彩设计前获取）
            recent_summaries = self.story_state.get_recent_summaries(3)
            recent_summary_text = self.summarizer.format_recent_summaries()
            arc_summary = self.story_state.get_current_arc_summary()
            last_ending = self.storage.read_last_chapter_ending(30)
            
            if last_ending is None:
                last_ending = "（这是第一章，没有上一章）"
            
            # 3. 生成章节色彩设计（新增步骤！）
            chapter_color = self._generate_chapter_color(
                chapter_num=chapter_num,
                story_bible=self.story_state.story_bible or {},
                recent_chapters_summary=recent_summary_text,
                last_chapter_ending=last_ending,
                selected_creatives=selected_creatives
            )
            logger.info(f"本章色彩设计: {chapter_color.get('writing_guidance', '无')}")
            
            # 4. 构建章节衔接包
            context_anchor = self._build_context_anchor()
            
            # 5. 构建写作 prompt（融入色彩设计）
            prompt = self.prompt_builder.build_chapter_prompt(
                story_bible=self.story_state.story_bible or {},
                characters={
                    name: char.__dict__ 
                    for name, char in self.story_state.characters.items()
                },
                plot_state=self.story_state.plot_state,
                context_anchor=context_anchor,
                selected_creatives=selected_creatives,
                chapter_color=chapter_color,  # 新增：传递色彩设计
                recent_summaries=recent_summaries,
                arc_summary=arc_summary.__dict__ if arc_summary else None,
                last_chapter_ending=last_ending,
                chapter_num=chapter_num
            )
            
            # 6. 调用 LLM 生成正文
            chapter_content = self.llm.generate_chapter(
                prompt=prompt,
                temperature=0.9  # 提高温度以配合色彩设计
            )
            
            # 7. 清理和格式化内容
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
            "人物身份突然互换，三人发现自己灵魂对调",
            "一场突如其来的量子风暴，所有人的记忆开始错乱",
            "神秘的第三方势力突然介入，打破现有平衡",
            "核心道具突然失效，整个系统开始崩溃",
            "一个被遗忘的角色带着重大秘密回归",
        ]
        
        selected = random.sample(fallback_creatives, min(2, len(fallback_creatives)))
        
        # 也选择一个创意类型
        if available_types:
            type_selected = random.choice(available_types)
            selected.append(f"使用 {type_selected} 类型的创意")
        
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
    
    def initialize_story(self) -> bool:
        """
        初始化故事宇宙
        
        Returns:
            是否初始化成功
        """
        logger.info("开始初始化故事宇宙...")
        
        try:
            # 生成世界观
            prompt = self.prompt_builder.build_init_world_prompt()
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


# 全局实例
_chapter_writer: Optional[ChapterWriter] = None


def get_chapter_writer() -> ChapterWriter:
    """获取章节写作器实例"""
    global _chapter_writer
    if _chapter_writer is None:
        _chapter_writer = ChapterWriter()
    return _chapter_writer
