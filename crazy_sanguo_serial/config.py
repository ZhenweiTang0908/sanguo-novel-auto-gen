"""
配置管理模块
管理所有可配置的常量和环境变量
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# 加载 .env 文件
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    with open(_env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


@dataclass
class LLMConfig:
    """LLM 模型配置"""
    model: str = "qwen-turbo"
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key_env: str = "DASHSCOPE_API_KEY"
    temperature: float = 0.8
    top_p: float = 0.9
    max_tokens_chapter: int = 3500  # 章节正文生成
    max_tokens_summary: int = 800   # 摘要生成
    max_tokens_ideas: int = 600     # 创意生成
    request_timeout: int = 120


@dataclass
class ChapterConfig:
    """章节配置"""
    default_length: int = 2000          # 默认章节字数
    min_length: int = 1500
    max_length: int = 3000
    arc_trigger: int = 5                # 多少章触发分卷摘要
    recent_summaries_keep: int = 3      # 保留最近几章摘要


@dataclass
class StorageConfig:
    """存储路径配置"""
    data_dir: str = "data"
    meta_file: str = "meta.json"
    story_bible_file: str = "story_bible.json"
    characters_file: str = "characters.json"
    plot_state_file: str = "plot_state.json"
    arc_summaries_file: str = "arc_summaries.json"
    chapters_dir: str = "data/chapters"
    chapter_summaries_dir: str = "data/chapter_summaries"


@dataclass
class CreativeTypes:
    """创意类型枚举"""
    CHARACTER_IDENTITY_SWAP = "character_identity_swap"
    REVERSE_HISTORY = "reverse_history"
    TECH_DISASTER = "tech_disaster"
    FACTION_SHUFFLE = "faction_shuffle"
    MEMORY_MANIPULATION = "memory_manipulation"
    MULTIVERSE_COLLISION = "multiverse_collision"
    BUREAUCRACY_CHAOS = "bureaucracy_chaos"
    BETRAYAL_REVEAL = "betrayal_reveal"
    POWER_SYSTEM_BROKEN = "power_system_broken"
    PROPHECY_SUBVERTED = "prophecy_subverted"
    TIME_LOOP = "time_loop"
    ZOMBIE_OUTBREAK = "zombie_outbreak"
    AI_TAKEOVER = "ai_takeover"
    CULT_DOCTRINE = "cult_doctrine"
    
    ALL = [
        CHARACTER_IDENTITY_SWAP,
        REVERSE_HISTORY,
        TECH_DISASTER,
        FACTION_SHUFFLE,
        MEMORY_MANIPULATION,
        MULTIVERSE_COLLISION,
        BUREAUCRACY_CHAOS,
        BETRAYAL_REVEAL,
        POWER_SYSTEM_BROKEN,
        PROPHECY_SUBVERTED,
        TIME_LOOP,
        ZOMBIE_OUTBREAK,
        AI_TAKEOVER,
        CULT_DOCTRINE,
    ]


@dataclass
class AppConfig:
    """应用总配置"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    chapter: ChapterConfig = field(default_factory=ChapterConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    def get_api_key(self) -> str:
        """从环境变量获取 API Key"""
        api_key = os.getenv(self.llm.api_key_env)
        if not api_key:
            raise ValueError(
                f"未找到环境变量 {self.llm.api_key_env}，"
                "请设置: export DASHSCOPE_API_KEY='your-api-key'"
            )
        return api_key


# 全局配置实例
config = AppConfig()
