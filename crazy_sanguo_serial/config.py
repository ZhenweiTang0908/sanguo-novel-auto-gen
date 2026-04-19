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
    """创意类型枚举 - 强调多样性和自由度"""
    
    # 核心剧情创意
    IDENTITY_REVEAL = "identity_reveal"
    SECRET_ALLIANCE = "secret_alliance"
    POWER_STRUGGLE = "power_struggle"
    BETRAYAL = "betrayal"
    REVENGE = "revenge"
    LOVE_TRIANGLE = "love_triangle"
    SCHEMING = "scheming"
    WAR_STRATEGY = "war_strategy"
    POLITICAL_MARRIAGE = "political_marriage"
    HIDDEN_HEIR = "hidden_heir"
    PAST_SECRET = "past_secret"
    FACTION_CONFLICT = "faction_conflict"
    ASSASSINATION_PLAN = "assassination_plan"
    UNEXPECTED_ALLY = "unexpected_ally"
    
    # 风格与节奏创意（新增）
    COMIC_RELIEF = "comic_relief"
    DARK_TURN = "dark_turn"
    TIME_SKIP = "time_skip"
    FLASHBACK = "flashback"
    PARALLEL_EDITING = "parallel_editing"
    UNRELIABLE_NARRATOR = "unreliable_narrator"
    
    # 事件创意（新增）
    ACCIDENT = "accident"
    NATURAL_DISASTER = "natural_disaster"
    PUBBLIC_HUMILIATION = "public_humiliation"
    THIRD_PARTY_INTERVENTION = "third_party_intervention"
    ITEM_DISCOVERY = "item_discovery"
    BODY_DISCOVERY = "body_discovery"
    BETTING_GAME = "betting_game"
    COOKING_BATTLE = "cooking_battle"
    DRUNK_CONFESSION = "drunk_confession"
    
    # 角色互动创意（新增）
    BODY_SWAP = "body_swap"
    AMNESIA = "amnesia"
    IMPOSTER = "imposter"
    MISTAKE_IDENTITY = "mistake_identity"
    ROLE_REVERSAL = "role_reversal"
    ENEMIES_ALLIES_SWAP = "enemies_allies_swap"
    
    # 世界观扩展（新增）
    NEW_FACTION_INTRO = "new_faction_intro"
    FORGOTTEN_PROPHECY = "forgotten_prophecy"
    ANCIENT_WEAPON = "ancient_weapon"
    SECRET_TECHNIQUE = "secret_technique"
    FORBIDDEN_KNOWLEDGE = "forbidden_knowledge"
    
    # 极端创意（让剧情炸裂）
    MASS_CASUALTY = "mass_casualty"
    SCANDAL_EXPOSURE = "scandal_exposure"
    DEAL_WITH_DEVIL = "deal_with_devil"
    SACRIFICE = "sacrifice"
    HERO_TURN_VILLAIN = "hero_turn_villain"
    VILLAIN_TURN_HERO = "villain_turn_hero"
    
    # 完全随机（真正让AI自由发挥）
    WILD_CARD = "wild_card"
    
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
        COMIC_RELIEF,
        DARK_TURN,
        TIME_SKIP,
        FLASHBACK,
        PARALLEL_EDITING,
        UNRELIABLE_NARRATOR,
        ACCIDENT,
        NATURAL_DISASTER,
        PUBBLIC_HUMILIATION,
        THIRD_PARTY_INTERVENTION,
        ITEM_DISCOVERY,
        BODY_DISCOVERY,
        BETTING_GAME,
        COOKING_BATTLE,
        DRUNK_CONFESSION,
        BODY_SWAP,
        AMNESIA,
        IMPOSTER,
        MISTAKE_IDENTITY,
        ROLE_REVERSAL,
        ENEMIES_ALLIES_SWAP,
        NEW_FACTION_INTRO,
        FORGOTTEN_PROPHECY,
        ANCIENT_WEAPON,
        SECRET_TECHNIQUE,
        FORBIDDEN_KNOWLEDGE,
        MASS_CASUALTY,
        SCANDAL_EXPOSURE,
        DEAL_WITH_DEVIL,
        SACRIFICE,
        HERO_TURN_VILLAIN,
        VILLAIN_TURN_HERO,
        WILD_CARD,
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
