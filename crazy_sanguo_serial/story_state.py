"""
故事状态管理模块
管理小说世界观、角色、剧情状态、伏笔等
"""

import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

from config import config, CreativeTypes
from storage import get_storage

logger = logging.getLogger(__name__)


@dataclass
class MetaInfo:
    """元信息"""
    current_chapter: int = 0
    created_at: str = ""
    last_updated: str = ""
    story_title: str = "疯狂三国：魔改演义"
    story_subtitle: str = "当罗贯中棺材板压不住的时候"


@dataclass
class CharacterState:
    """角色状态"""
    name: str
    identity: str
    current_location: str
    goal: str
    status: str = "alive"  # alive, dead, missing, transformed
    role: str = "supporting"  # main, supporting
    relationship_changes: List[str] = field(default_factory=list)
    new_traits: List[str] = field(default_factory=list)


@dataclass
class PlotThread:
    """伏笔/剧情线"""
    thread_id: str
    description: str
    status: str = "open"  # open, resolved, abandoned
    introduced_chapter: int = 0
    resolved_chapter: Optional[int] = None
    notes: str = ""


@dataclass
class CreativeRecord:
    """已使用创意记录"""
    creative_type: str
    used_in_chapter: int
    description: str
    impact: str = ""


@dataclass 
class ArcSummary:
    """分卷摘要"""
    arc_id: int
    chapters: str  # "1-5"
    summary: str
    key_events: List[str] = field(default_factory=list)
    main_conflicts: List[str] = field(default_factory=list)


class StoryState:
    """
    故事状态管理器
    负责加载、保存和管理所有故事状态数据
    """
    
    def __init__(self, novel_id: Optional[str] = None):
        self.storage = get_storage(novel_id)
        self.novel_id = novel_id
        self._meta: Optional[MetaInfo] = None
        self._story_bible: Optional[Dict] = None
        self._characters: Optional[Dict[str, CharacterState]] = None
        self._plot_state: Optional[Dict] = None
        self._arc_summaries: List[ArcSummary] = []
        self._chapter_summaries: Dict[int, Dict] = {}
    
    def set_novel(self, novel_id: str):
        """切换到指定小说"""
        self.novel_id = novel_id
        self.storage.set_novel(novel_id)
        self.load_all()
    
    # ==================== 加载方法 ====================
    
    def load_all(self) -> bool:
        """
        加载所有故事状态
        
        Returns:
            是否加载成功（即使没有数据也会返回 True）
        """
        logger.info("加载故事状态...")
        
        # 加载元信息
        self._meta = self._load_meta()
        
        # 加载世界观
        self._story_bible = self._load_story_bible()
        
        # 加载角色
        self._load_characters()
        
        # 加载剧情状态
        self._plot_state = self._load_plot_state()
        
        # 加载分卷摘要
        self._arc_summaries = self._load_arc_summaries()
        
        # 加载章节摘要
        self._load_chapter_summaries()
        
        if self._meta.current_chapter > 0:
            logger.info(f"已加载故事状态：共 {self._meta.current_chapter} 章")
        else:
            logger.info("未找到已有故事，将创建新故事")
        
        return True
    
    def _load_meta(self) -> MetaInfo:
        """加载元信息"""
        if self.novel_id:
            data = self.storage.read_json("meta_file", use_novel_paths=True)
        else:
            data = self.storage.read_json("novel-reader/meta.json")
        if data:
            return MetaInfo(**data)
        return MetaInfo()
    
    def _load_story_bible(self) -> Optional[Dict]:
        """加载世界观设定"""
        if self.novel_id:
            return self.storage.read_json("story_bible_file", use_novel_paths=True)
        return self.storage.read_json("novel-reader/story_bible.json")
    
    def _load_characters(self):
        """加载角色数据"""
        if self.novel_id:
            data = self.storage.read_json("characters_file", use_novel_paths=True)
        else:
            data = self.storage.read_json("novel-reader/characters.json")
        self._characters = {}
        if data:
            for name, char_data in data.items():
                self._characters[name] = CharacterState(**char_data)
    
    def _load_plot_state(self) -> Dict:
        """加载剧情状态"""
        default_state = {
            "main_conflict": "待设定",
            "sub_conflicts": [],
            "open_threads": [],
            "used_creatives": [],
            "active_creative_types": [],
        }
        if self.novel_id:
            data = self.storage.read_json("plot_state_file", use_novel_paths=True)
        else:
            data = self.storage.read_json("novel-reader/plot_state.json")
        return data if data else default_state
    
    def _load_arc_summaries(self) -> List[ArcSummary]:
        """加载分卷摘要"""
        if self.novel_id:
            data = self.storage.read_json("arc_summaries_file", use_novel_paths=True)
        else:
            data = self.storage.read_json("novel-reader/arc_summaries.json")
        if data:
            return [ArcSummary(**a) for a in data]
        return []
    
    def _load_chapter_summaries(self):
        """加载所有章节摘要"""
        self._chapter_summaries = {}
        chapters = self.storage.list_chapters()
        for num in chapters:
            path = self.storage.get_chapter_summary_path(num)
            if path.exists():
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    self._chapter_summaries[num] = json.load(f)
    
    # ==================== 保存方法 ====================
    
    def save_all(self):
        """保存所有故事状态"""
        logger.info("保存故事状态...")
        self._save_meta()
        self._save_story_bible()
        self._save_characters()
        self._save_plot_state()
        self._save_arc_summaries()
        logger.info("故事状态保存完成")
    
    def _save_meta(self):
        """保存元信息"""
        if self._meta:
            if self.novel_id:
                self.storage.write_json("meta_file", asdict(self._meta), use_novel_paths=True)
            else:
                self.storage.write_json("novel-reader/meta.json", asdict(self._meta))
    
    def _save_story_bible(self):
        """保存世界观"""
        if self._story_bible:
            if self.novel_id:
                self.storage.write_json("story_bible_file", self._story_bible, use_novel_paths=True)
            else:
                self.storage.write_json("novel-reader/story_bible.json", self._story_bible)
    
    def _save_characters(self):
        """保存角色数据"""
        if self._characters:
            data = {name: asdict(char) for name, char in self._characters.items()}
            if self.novel_id:
                self.storage.write_json("characters_file", data, use_novel_paths=True)
            else:
                self.storage.write_json("novel-reader/characters.json", data)
    
    def _save_plot_state(self):
        """保存剧情状态"""
        if self._plot_state:
            if self.novel_id:
                self.storage.write_json("plot_state_file", self._plot_state, use_novel_paths=True)
            else:
                self.storage.write_json("novel-reader/plot_state.json", self._plot_state)
    
    def _save_arc_summaries(self):
        """保存分卷摘要"""
        data = [asdict(arc) for arc in self._arc_summaries]
        if self.novel_id:
            self.storage.write_json("arc_summaries_file", data, use_novel_paths=True)
        else:
            self.storage.write_json("novel-reader/arc_summaries.json", data)
    
    # ==================== 初始化方法 ====================
    
    def initialize(self, story_bible: Dict, characters: Dict, plot_state: Dict):
        """
        初始化故事状态
        
        Args:
            story_bible: 世界观设定
            characters: 角色数据
            plot_state: 初始剧情状态
        """
        import datetime
        
        self._meta = MetaInfo(
            current_chapter=0,
            created_at=datetime.datetime.now().isoformat(),
            last_updated=datetime.datetime.now().isoformat()
        )
        self._story_bible = story_bible
        self._characters = {
            name: CharacterState(**char_data) 
            for name, char_data in characters.items()
        }
        self._plot_state = plot_state
        self._arc_summaries = []
        self._chapter_summaries = {}
        
        self.save_all()
        logger.info("故事状态初始化完成")
    
    # ==================== 章节相关方法 ====================
    
    def get_next_chapter_num(self) -> int:
        """获取下一章编号"""
        return (self._meta.current_chapter if self._meta else 0) + 1
    
    def increment_chapter(self):
        """章节编号 +1"""
        if self._meta:
            self._meta.current_chapter += 1
            import datetime
            self._meta.last_updated = datetime.datetime.now().isoformat()
    
    def get_current_arc_summary(self) -> Optional[ArcSummary]:
        """获取当前分卷摘要"""
        if self._arc_summaries:
            return self._arc_summaries[-1]
        return None
    
    def get_recent_summaries(self, count: int = 3) -> List[Dict]:
        """获取最近 N 章摘要"""
        sorted_nums = sorted(self._chapter_summaries.keys(), reverse=True)
        return [
            self._chapter_summaries[num] 
            for num in sorted_nums[:count]
        ]
    
    # ==================== 剧情状态更新 ====================
    
    def add_chapter_summary(self, chapter_num: int, summary: Dict):
        """添加章节摘要"""
        self._chapter_summaries[chapter_num] = summary
    
    def add_plot_thread(self, thread: PlotThread):
        """添加伏笔"""
        self._plot_state["open_threads"].append(asdict(thread))
    
    def resolve_thread(self, thread_id: str, chapter_num: int):
        """标记伏笔已解决"""
        for thread in self._plot_state["open_threads"]:
            if thread.get("thread_id") == thread_id:
                thread["status"] = "resolved"
                thread["resolved_chapter"] = chapter_num
                break
    
    def add_used_creative(self, creative: CreativeRecord):
        """记录已使用的创意"""
        self._plot_state["used_creatives"].append(asdict(creative))
        
        # 更新活跃创意类型（最近 3 章）
        active = self._plot_state.get("active_creative_types", [])
        active.append(creative.creative_type)
        # 只保留最近 9 个（3 章 x 3 个/章）
        self._plot_state["active_creative_types"] = active[-9:]
    
    def get_unused_creative_types(self, count: int = 5) -> List[str]:
        """获取最近未使用的创意类型"""
        active = set(self._plot_state.get("active_creative_types", []))
        all_types = set(CreativeTypes.ALL)
        unused = list(all_types - active)
        # 随机打乱
        import random
        random.shuffle(unused)
        return unused[:count]
    
    def update_character_state(self, name: str, **kwargs):
        """更新角色状态"""
        if name in self._characters:
            char = self._characters[name]
            for key, value in kwargs.items():
                if hasattr(char, key):
                    setattr(char, key, value)
    
    def update_main_conflict(self, conflict: str):
        """更新主线冲突"""
        self._plot_state["main_conflict"] = conflict

    def add_character(self, name: str, identity: str, current_location: str = "未知", goal: str = "待探索", status: str = "alive", role: str = "supporting"):
        """添加新角色"""
        if self._characters is None:
            self._characters = {}
        self._characters[name] = CharacterState(
            name=name,
            identity=identity,
            current_location=current_location,
            goal=goal,
            status=status,
            role=role,
            relationship_changes=[],
            new_traits=[]
        )
        logger.info(f"添加角色: {name} - {identity} ({role})")

    def get_main_characters(self) -> Dict[str, CharacterState]:
        """获取主要人物"""
        return {n: c for n, c in self.characters.items() if c.role == "main"}

    def get_supporting_characters(self) -> Dict[str, CharacterState]:
        """获取配角"""
        return {n: c for n, c in self.characters.items() if c.role == "supporting"}

    def update_character(self, name: str, identity: Optional[str] = None, role: Optional[str] = None, current_location: Optional[str] = None, goal: Optional[str] = None):
        """修改角色信息"""
        if name not in self._characters:
            logger.warning(f"角色不存在: {name}")
            return False
        char = self._characters[name]
        if identity is not None:
            char.identity = identity
        if role is not None:
            char.role = role
        if current_location is not None:
            char.current_location = current_location
        if goal is not None:
            char.goal = goal
        logger.info(f"更新角色: {name}")
        return True

    def set_random_character_mode(self, enabled: bool, count: int = 5):
        """设置随机角色模式"""
        self._plot_state["random_character_mode"] = enabled
        self._plot_state["random_character_count"] = count
        if enabled:
            self.clear_active_characters()
        logger.info(f"随机角色模式: {'开启' if enabled else '关闭'}, 数量: {count}")

    def is_random_character_mode(self) -> bool:
        """是否启用随机角色模式"""
        return self._plot_state.get("random_character_mode", False)

    def get_random_characters(self, count: int = 5) -> List[str]:
        """获取随机角色列表"""
        import random
        all_chars = list(self._characters.keys())
        if len(all_chars) <= count:
            return all_chars
        return random.sample(all_chars, count)

    def set_active_characters(self, names: List[str]):
        """设置下一章需要出现的角色（优先级最高）"""
        self._plot_state["active_characters"] = names

    def get_active_characters(self) -> Optional[List[str]]:
        """获取下一章需要出现的角色"""
        return self._plot_state.get("active_characters")

    def clear_active_characters(self):
        """清除活动角色设置"""
        if "active_characters" in self._plot_state:
            del self._plot_state["active_characters"]

    def set_user_inspiration(self, inspiration: str):
        """设置用户输入的灵感线索，下一章必须融入"""
        self._plot_state["user_inspiration"] = inspiration

    def get_user_inspiration(self) -> Optional[str]:
        """获取用户灵感线索"""
        return self._plot_state.get("user_inspiration")

    def clear_user_inspiration(self):
        """清除用户灵感线索（使用后）"""
        if "user_inspiration" in self._plot_state:
            del self._plot_state["user_inspiration"]

    # ==================== 状态查询 ====================
    
    @property
    def meta(self) -> MetaInfo:
        return self._meta
    
    @property
    def story_bible(self) -> Optional[Dict]:
        return self._story_bible
    
    @property
    def characters(self) -> Dict[str, CharacterState]:
        return self._characters or {}
    
    @property
    def plot_state(self) -> Dict:
        return self._plot_state or {}
    
    @property
    def arc_summaries(self) -> List[ArcSummary]:
        return self._arc_summaries
    
    @property
    def chapter_summaries(self) -> Dict[int, Dict]:
        return self._chapter_summaries
    
    def get_summary_text(self) -> str:
        """获取状态摘要文本"""
        if not self._meta or self._meta.current_chapter == 0:
            return "尚未开始创作"
        
        lines = [
            f"📖 《{self._meta.story_title}》",
            f"   副标题：{self._meta.story_subtitle}",
            f"   已创作：第 {self._meta.current_chapter} 章",
            ""
        ]
        
        if self._story_bible:
            lines.append(f"📍 当前主线：{self._plot_state.get('main_conflict', '未知')}")
        
        if self._characters:
            main_chars = list(self._characters.keys())[:5]
            lines.append(f"👥 主要角色：{', '.join(main_chars)}...")
        
        if self._plot_state.get("open_threads"):
            open_count = len([t for t in self._plot_state["open_threads"] 
                            if t.get("status") == "open"])
            lines.append(f"🔮 未解伏笔：{open_count} 条")
        
        return "\n".join(lines)


# 全局状态实例
_story_state: Optional[StoryState] = None


def get_story_state(novel_id: Optional[str] = None) -> StoryState:
    """获取故事状态管理器单例"""
    global _story_state
    if _story_state is None:
        _story_state = StoryState(novel_id)
    elif novel_id and _story_state.novel_id != novel_id:
        _story_state.set_novel(novel_id)
    return _story_state


def reset_story_state():
    """重置故事状态（用于测试）"""
    global _story_state
    _story_state = None
