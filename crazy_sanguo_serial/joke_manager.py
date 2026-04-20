"""
笑话集管理器模块
核心的笑话生成和管理逻辑
"""

import logging
import re
import json
from typing import Dict, List, Optional, Tuple, Any

from llm_client import get_llm_client
from joke_storage import get_joke_storage

logger = logging.getLogger(__name__)


class JokeManager:
    """
    笑话集管理器
    负责创建笑话集、生成笑话、管理收藏等功能
    """
    
    def __init__(self):
        self.llm = get_llm_client()
        self.storage = get_joke_storage()
    
    def create_collection(
        self, 
        title: str, 
        keywords: List[str], 
        creative_direction: str
    ) -> Tuple[bool, str]:
        """
        创建新笑话集
        
        Args:
            title: 笑话集标题
            keywords: 关键词列表
            creative_direction: 创意方向
            
        Returns:
            (是否成功, 消息/笑话集ID)
        """
        # 生成笑话集ID（使用拼音或英文）
        collection_id = self._generate_collection_id(title)
        
        # 检查是否已存在
        if self.storage.collection_exists(collection_id):
            return False, f"笑话集 '{title}' 已存在"
        
        # 创建笑话集
        self.storage.add_collection(
            collection_id=collection_id,
            title=title,
            keywords=keywords,
            creative_direction=creative_direction
        )
        
        logger.info(f"创建笑话集: {title} (ID: {collection_id})")
        return True, collection_id
    
    def _generate_collection_id(self, title: str) -> str:
        """从标题生成ID"""
        # 移除非字母数字字符，转为小写
        import re
        clean = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', title)
        # 取前10个字符
        return clean[:10] or f"joke_{len(self.storage.list_collections())}"
    
    def generate_keywords(self, user_input: str = "") -> List[str]:
        """
        AI生成关键词
        
        Args:
            user_input: 用户输入的引导词（可选）
            
        Returns:
            生成的关键词列表
        """
        if user_input:
            prompt = f"""用户希望创建一个笑话集，主题方向是：{user_input}

请生成8-12个相关的关键词，用于后续笑话创作。
这些关键词应该涵盖不同的角度和风格。

要求：
1. 关键词要具体、有代表性
2. 覆盖不同的话题（人物、场景、情感等）
3. 适合用于生成笑话

请以JSON格式输出：
```json
{{"keywords": ["关键词1", "关键词2", ...]}}
```"""
        else:
            prompt = """请生成10-15个幽默笑话创作的常用关键词。

要求：
1. 涵盖多个领域：职场、社交、技术、日常生活等
2. 关键词要有趣、有创意
3. 能激发笑话灵感

请以JSON格式输出：
```json
{{"keywords": ["关键词1", "关键词2", ...]}}
```"""
        
        try:
            response = self.llm.generate(prompt, temperature=0.9, max_tokens=800)
            data = self._parse_json_response(response)
            if data and 'keywords' in data:
                return data['keywords']
        except Exception as e:
            logger.error(f"生成关键词失败: {e}")
        
        # 备用关键词
        return ["职场", "程序员", "日常生活", "社交", "情感", "搞笑", "讽刺", "吐槽"]
    
    def generate_creative_direction(
        self, 
        keywords: List[str],
        user_direction_hint: str = ""
    ) -> str:
        """
        AI生成创意方向
        
        Args:
            keywords: 关键词列表
            user_direction_hint: 用户给的方向提示（可选）
            
        Returns:
            创意方向描述
        """
        keywords_str = ", ".join(keywords)
        
        hint_section = f"""
## 用户期望的方向
{user_direction_hint}
""" if user_direction_hint else ""
        
        prompt = f"""# 任务：为笑话集确定创作方向

## 已有关键词
{keywords_str}

{hint_section}
## 要求

请确定这个笑话集的创作方向，包括：
1. **整体风格**：如轻松幽默、黑色幽默、讽刺辛辣等
2. **主题方向**：如职场吐槽、日常搞笑、情感纠葛等
3. **禁忌话题**：如政治、敏感事件等（可选）
4. **语言特点**：如口语化、文艺风、网络用语等

请用50-100字简洁描述这个笑话集的创作方向。

请以JSON格式输出：
```json
{{"direction": "创作方向描述（50-100字）"}}
```"""
        
        try:
            response = self.llm.generate(prompt, temperature=0.9, max_tokens=500)
            data = self._parse_json_response(response)
            if data and 'direction' in data:
                return data['direction']
        except Exception as e:
            logger.error(f"生成创意方向失败: {e}")
        
        return "轻松幽默，适合日常阅读的搞笑风格"
    
    def generate_jokes(
        self, 
        collection_id: str, 
        count: int = 10,
        temperature: float = 1.0
    ) -> Tuple[bool, str, Dict]:
        """
        生成一组笑话（10个）
        
        Args:
            collection_id: 笑话集ID
            count: 生成数量（默认10）
            temperature: 生成温度
            
        Returns:
            (是否成功, 笑话内容, 摘要信息)
        """
        # 获取笑话集元数据
        meta = self.storage.get_collection_meta_path(collection_id)
        if not meta.exists():
            return False, "笑话集不存在", {}
        
        with open(meta, 'r', encoding='utf-8') as f:
            collection_meta = json.load(f)
        
        keywords = collection_meta.get('keywords', [])
        creative_direction = collection_meta.get('creative_direction', '轻松幽默')
        
        # 确定当前组号
        current_groups = self.storage.list_joke_groups(collection_id)
        next_group = (max(current_groups) + 1) if current_groups else 1
        
        # 构建 prompt
        prompt = self._build_joke_prompt(
            keywords=keywords,
            creative_direction=creative_direction,
            count=count
        )
        
        try:
            response = self.llm.generate(prompt, temperature=temperature, max_tokens=3000)
            
            # 解析笑话内容
            jokes_content = self._parse_jokes_response(response)
            
            if not jokes_content:
                return False, "解析笑话内容失败", {}
            
            # 构建摘要
            summary = {
                "joke_group": next_group,
                "keywords_used": keywords[:5],
                "themes": self._extract_themes(jokes_content),
                "joke_titles": self._extract_titles(jokes_content),
                "generated_at": self._get_timestamp()
            }
            
            # 保存
            self.storage.save_joke_group(
                collection_id=collection_id,
                joke_group=next_group,
                content=jokes_content,
                summary=summary
            )
            
            return True, jokes_content, summary
            
        except Exception as e:
            logger.error(f"生成笑话失败: {e}")
            return False, str(e), {}
    
    def _build_joke_prompt(
        self, 
        keywords: List[str],
        creative_direction: str,
        count: int = 10
    ) -> str:
        """构建笑话生成 prompt"""
        keywords_str = ", ".join(keywords)
        
        return f"""# 任务：生成{count}个独立笑话

## 创作要求

### 关键词
{keywords_str}

### 风格方向
{creative_direction}

### 格式要求
1. 每个笑话必须有**标题**（用 `## 笑话标题` 格式）
2. 每个笑话50-150字
3. 笑话必须**独立完整**，各笑话之间无关联
4. 结尾要有**笑点**（出人意料、反转、夸张等）
5. 语言口语化，易读性强

### 禁忌
- 禁止抄袭已有笑话
- 禁止低俗、敏感内容
- 禁止涉及政治、宗教

### 输出格式
```markdown
## 笑话1：（标题）
正文内容，笑点要强...

## 笑话2：（标题）
正文内容...

（以此类推，共{count}个笑话）
```

请立即生成{count}个笑话！"""

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """解析JSON响应"""
        # 尝试提取JSON代码块
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试直接解析
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _parse_jokes_response(self, response: str) -> str:
        """解析笑话内容响应"""
        content = response.strip()
        
        # 移除可能的 markdown 代码块标记
        if content.startswith('```'):
            lines = content.split('\n')
            if len(lines) > 2:
                content = '\n'.join(lines[1:-1])
        
        content = re.sub(r'^```\w*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n```$', '', content)
        
        # 确保有标题格式
        if not content.startswith('## '):
            # 可能是纯文本格式，尝试转换
            lines = content.split('\n\n')
            new_content = []
            for i, line in enumerate(lines, 1):
                if line.strip() and not line.startswith('##'):
                    new_content.append(f"## 笑话{i}\n{line.strip()}")
                elif line.strip():
                    new_content.append(line)
            content = '\n\n'.join(new_content)
        
        return content
    
    def _extract_themes(self, jokes_content: str) -> List[str]:
        """从笑话内容中提取主题"""
        # 简单实现：按段落分割，提取可能的关键词
        themes = []
        lines = jokes_content.split('\n')
        for line in lines:
            if line.startswith('## '):
                themes.append(line.replace('## ', '').strip())
            if len(themes) >= 5:
                break
        return themes[:5]
    
    def _extract_titles(self, jokes_content: str) -> List[str]:
        """提取所有笑话标题"""
        titles = []
        for line in jokes_content.split('\n'):
            if line.startswith('## '):
                titles.append(line.replace('## ', '').strip())
        return titles
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def list_collections(self) -> List[Dict]:
        """列出所有笑话集"""
        return self.storage.list_collections()
    
    def get_collection_info(self, collection_id: str) -> Optional[Dict]:
        """获取笑话集详细信息"""
        if not self.storage.collection_exists(collection_id):
            return None
        
        # 读取元数据
        meta_path = self.storage.get_collection_meta_path(collection_id)
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # 获取统计信息
        groups = self.storage.list_joke_groups(collection_id)
        meta['group_count'] = len(groups)
        meta['total_jokes'] = len(groups) * 10
        
        return meta
    
    def switch_collection(self, collection_id: str) -> bool:
        """切换当前笑话集"""
        return self.storage.collection_exists(collection_id)
    
    def delete_collection(self, collection_id: str) -> bool:
        """删除笑话集"""
        return self.storage.remove_collection(collection_id)
    
    def get_current_progress(self, collection_id: str) -> Dict[str, int]:
        """获取当前笑话集进度"""
        groups = self.storage.list_joke_groups(collection_id)
        return {
            "group_count": len(groups),
            "total_jokes": len(groups) * 10,
            "next_group": (max(groups) + 1) if groups else 1
        }


# 全局实例
_joke_manager: Optional[JokeManager] = None


def get_joke_manager() -> JokeManager:
    """获取笑话管理器实例"""
    global _joke_manager
    if _joke_manager is None:
        _joke_manager = JokeManager()
    return _joke_manager


def reset_joke_manager():
    """重置笑话管理器（用于测试）"""
    global _joke_manager
    _joke_manager = None