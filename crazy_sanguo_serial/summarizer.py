"""
摘要生成器模块
负责生成章节摘要、分卷摘要等
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any

from llm_client import get_llm_client
from prompt_builder import get_prompt_builder
from story_state import get_story_state, ArcSummary
from storage import get_storage
from config import config

logger = logging.getLogger(__name__)


class Summarizer:
    """
    摘要生成器
    负责从章节内容中提取摘要信息
    """
    
    def __init__(self):
        self.llm = get_llm_client()
        self.prompt_builder = get_prompt_builder()
        self.storage = get_storage()
        self.story_state = get_story_state()
    
    def generate_chapter_summary(self, chapter_num: int, chapter_content: str) -> Dict:
        """
        生成本章摘要
        
        Args:
            chapter_num: 章节号
            chapter_content: 章节正文
            
        Returns:
            解析后的摘要字典
        """
        logger.info(f"生成第{chapter_num}章摘要...")
        
        prompt = self.prompt_builder.build_summary_prompt(chapter_num, chapter_content)
        
        try:
            response = self.llm.generate_summary(prompt)
            
            # 尝试解析 JSON
            summary = self._parse_json_response(response)
            
            if summary:
                # 保存摘要到文件
                self._save_chapter_summary(chapter_num, summary)
                # 更新故事状态
                self.story_state.add_chapter_summary(chapter_num, summary)
                logger.info(f"第{chapter_num}章摘要生成成功")
                return summary
            else:
                # 返回基础摘要
                return self._generate_fallback_summary(chapter_num, chapter_content)
                
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return self._generate_fallback_summary(chapter_num, chapter_content)
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """尝试从响应中解析 JSON"""
        # 尝试提取 ```json ... ``` 块
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试直接解析整个响应
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取 JSON 对象（即使前后有其他文本）
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _generate_fallback_summary(self, chapter_num: int, chapter_content: str) -> Dict:
        """生成备用摘要（当 JSON 解析失败时）"""
        # 简单提取标题
        title_match = re.search(r'#\s*第[一二三四五六七八九十百\d]+章\s*(.+)', chapter_content)
        title = title_match.group(1).strip() if title_match else f"第{chapter_num}章"
        
        # 统计字数
        word_count = len(chapter_content.replace(' ', '').replace('\n', ''))
        
        return {
            "chapter_num": chapter_num,
            "chapter_title": title,
            "events": ["内容摘要生成失败，请查看正文"],
            "new_settings": [],
            "character_changes": [],
            "faction_changes": [],
            "new_hooks": [],
            "continued_hooks": [],
            "style_highlights": [],
            "next_chapter_teaser": "未知",
            "word_count": word_count
        }
    
    def _save_chapter_summary(self, chapter_num: int, summary: Dict):
        """保存章节摘要到文件"""
        summary_path = self.storage.get_chapter_summary_path(chapter_num)
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        logger.debug(f"保存摘要到 {summary_path}")
    
    def generate_arc_summary(self) -> Optional[ArcSummary]:
        """
        生成分卷摘要
        当达到分卷阈值时调用
        
        Returns:
            生成分卷摘要，若不满足条件返回 None
        """
        current_chapter = self.story_state.meta.current_chapter
        
        # 检查是否达到触发阈值
        if current_chapter % config.chapter.arc_trigger != 0:
            return None
        
        logger.info(f"生成分卷摘要 (前 {current_chapter} 章)...")
        
        # 获取要合并的章节摘要
        chapter_summaries = []
        for i in range(1, current_chapter + 1):
            if i in self.story_state.chapter_summaries:
                chapter_summaries.append(self.story_state.chapter_summaries[i])
        
        if len(chapter_summaries) < 3:
            logger.warning("章节摘要不足，无法生成分卷摘要")
            return None
        
        # 只取最近一个分卷后的章节
        last_arc_end = (current_chapter // config.chapter.arc_trigger - 1) * config.chapter.arc_trigger
        if last_arc_end > 0:
            chapter_summaries = [
                s for s in chapter_summaries 
                if s.get('chapter_num', 0) > last_arc_end
            ]
        
        arc_id = current_chapter // config.chapter.arc_trigger
        prompt = self.prompt_builder.build_arc_summary_prompt(arc_id, chapter_summaries)
        
        try:
            response = self.llm.generate_summary(prompt)
            arc_data = self._parse_json_response(response)
            
            if arc_data:
                arc_summary = ArcSummary(
                    arc_id=arc_data.get('arc_id', arc_id),
                    chapters=f"{last_arc_end + 1}-{current_chapter}",
                    summary=arc_data.get('summary', ''),
                    key_events=arc_data.get('key_events', []),
                    main_conflicts=arc_data.get('main_conflicts', [])
                )
                
                # 保存分卷摘要
                self.story_state.arc_summaries.append(arc_summary)
                self.story_state.save_all()
                
                logger.info(f"分卷 {arc_id} 摘要生成成功")
                return arc_summary
            
        except Exception as e:
            logger.error(f"生成分卷摘要失败: {e}")
        
        return None
    
    def get_context_for_writing(self) -> Dict:
        """
        获取写作所需的上下文信息
        用于构建章节衔接包
        
        Returns:
            包含上下文信息的字典
        """
        context = {
            "last_chapter_ending": "",
            "current_location": "未知",
            "main_pov_character": "未知",
            "immediate_goal": "未知",
            "tension_point": "未知",
            "hook_to_resolve": "未知"
        }
        
        # 获取最后一章摘要
        recent = self.story_state.get_recent_summaries(1)
        if recent:
            last_summary = recent[0]
            context["hook_to_resolve"] = last_summary.get(
                'next_chapter_teaser', 
                '继续上一章的剧情'
            )
        
        # 获取最后一章结尾
        last_ending = self.storage.read_last_chapter_ending(30)
        if last_ending:
            context["last_chapter_ending"] = last_ending
        
        # 尝试从角色状态推断当前场景
        characters = self.story_state.characters
        if characters:
            # 找到最近有位置更新的角色
            for name, char in list(characters.items())[:5]:
                if char.current_location and char.current_location != "未知":
                    context["current_location"] = char.current_location
                    context["main_pov_character"] = name
                    context["immediate_goal"] = char.goal
                    break
        
        # 获取当前紧张点
        plot_state = self.story_state.plot_state
        if plot_state.get("main_conflict"):
            context["tension_point"] = plot_state["main_conflict"]
        
        open_threads = plot_state.get("open_threads", [])
        if open_threads:
            for thread in open_threads:
                if isinstance(thread, dict) and thread.get('status') == 'open':
                    context["tension_point"] = thread.get('description', context["tension_point"])
                    break
        
        return context
    
    def format_recent_summaries(self) -> str:
        """
        格式化最近章节摘要为文本
        
        Returns:
            格式化的摘要文本
        """
        recent = self.story_state.get_recent_summaries(3)
        
        if not recent:
            return "暂无历史章节"
        
        lines = []
        for summary in recent:
            lines.append(f"第{summary.get('chapter_num', '?')}章《{summary.get('chapter_title', '无标题')}》")
            events = summary.get('events', [])
            if events:
                lines.append(f"  事件: {events[0]}")
        
        return "\n".join(lines)


# 全局实例
_summarizer: Optional[Summarizer] = None


def get_summarizer() -> Summarizer:
    """获取摘要生成器实例"""
    global _summarizer
    if _summarizer is None:
        _summarizer = Summarizer()
    return _summarizer
