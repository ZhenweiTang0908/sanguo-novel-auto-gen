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
    """存储路径配置 - 支持多小说"""
    base_dir: str = "novel-reader"
    novels_dir: str = "novel-reader/novels"
    novel_list_file: str = "novel-reader/novel-list.json"
    
    def get_novel_paths(self, novel_id: str) -> dict:
        """获取指定小说的路径配置"""
        return {
            "meta_file": f"{self.novels_dir}/{novel_id}/meta.json",
            "story_bible_file": f"{self.novels_dir}/{novel_id}/story_bible.json",
            "characters_file": f"{self.novels_dir}/{novel_id}/characters.json",
            "plot_state_file": f"{self.novels_dir}/{novel_id}/plot_state.json",
            "arc_summaries_file": f"{self.novels_dir}/{novel_id}/arc_summaries.json",
            "chapters_dir": f"{self.novels_dir}/{novel_id}/chapters",
            "chapter_summaries_dir": f"{self.novels_dir}/{novel_id}/chapter_summaries",
        }


@dataclass
class CreativeTypes:
    """创意类型枚举（保持现实克制风格）"""
    IDENTITY_REVEAL = "identity_reveal"  # 身份揭露
    SECRET_ALLIANCE = "secret_alliance"  # 秘密联盟
    POWER_STRUGGLE = "power_struggle"  # 权力斗争
    BETRAYAL = "betrayal"  # 背叛
    REVENGE = "revenge"  # 复仇
    LOVE_TRIANGLE = "love_triangle"  # 情感纠葛
    SCHEMING = "scheming"  # 阴谋算计
    WAR_STRATEGY = "war_strategy"  # 战争策略
    POLITICAL_MARRIAGE = "political_marriage"  # 政治联姻
    HIDDEN_HEIR = "hidden_heir"  # 隐藏的继承人
    PAST_SECRET = "past_secret"  # 过往秘密
    FACTION_CONFLICT = "faction_conflict"  # 势力冲突
    ASSASSINATION_PLAN = "assassination_plan"  # 刺杀计划
    UNEXPECTED_ALLY = "unexpected_ally"  # 意外盟友
    
    ALL = [
        IDENTITY_REVEAL,
        SECRET_ALLIANCE,
        POWER_STRUGGLE,
        BETRAYAL,
        REVENGE,
        LOVE_TRIANGLE,
        SCHEMING,
        WAR_STRATEGY,
        POLITICAL_MARRIAGE,
        HIDDEN_HEIR,
        PAST_SECRET,
        FACTION_CONFLICT,
        ASSASSINATION_PLAN,
        UNEXPECTED_ALLY,
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
