"""
LLM 客户端封装
使用 OpenAI SDK 调用阿里云百炼 qwen-turbo
"""

import time
import logging
from typing import Optional

from openai import OpenAI, APIError, RateLimitError, APITimeoutError
from config import config

logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM 客户端，统一封装 API 调用
    支持指数退避重试机制
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 LLM 客户端
        
        Args:
            api_key: API密钥，若不传则从环境变量读取
        """
        if api_key is None:
            api_key = config.get_api_key()
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=config.llm.base_url,
            timeout=config.llm.request_timeout
        )
        self.model = config.llm.model
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.8,
        top_p: float = 0.9,
        retry_count: int = 3,
        retry_delay: float = 2.0
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大生成长度
            temperature: 温度参数
            top_p: top_p 参数
            retry_count: 重试次数
            retry_delay: 初始重试延迟（秒），会指数增长
            
        Returns:
            生成的文本
        """
        last_error = None
        
        for attempt in range(retry_count + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一位才华横溢的网络小说作家。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens
                )
                
                content = response.choices[0].message.content
                
                # 记录 token 使用情况
                if hasattr(response, 'usage') and response.usage:
                    logger.info(
                        f"API 调用成功 | "
                        f"prompt_tokens: {response.usage.prompt_tokens} | "
                        f"completion_tokens: {response.usage.completion_tokens} | "
                        f"total_tokens: {response.usage.total_tokens}"
                    )
                
                return content
                
            except RateLimitError as e:
                last_error = e
                logger.warning(f"API 限流 (attempt {attempt + 1}/{retry_count + 1}): {e}")
                
            except APITimeoutError as e:
                last_error = e
                logger.warning(f"API 超时 (attempt {attempt + 1}/{retry_count + 1}): {e}")
                
            except APIError as e:
                status_code = getattr(e, 'status_code', None)
                
                if status_code == 401:
                    # 认证错误，不重试
                    logger.error(f"API 认证失败: {e}")
                    raise
                
                elif status_code in (500, 502, 503, 504):
                    last_error = e
                    logger.warning(f"API 服务器错误 {status_code} (attempt {attempt + 1}/{retry_count + 1}): {e}")
                
                elif status_code == 429:
                    last_error = e
                    logger.warning(f"API 请求过多 (attempt {attempt + 1}/{retry_count + 1}): {e}")
                
                else:
                    last_error = e
                    logger.warning(f"API 错误 (attempt {attempt + 1}/{retry_count + 1}): {e}")
            
            # 指数退避等待
            if attempt < retry_count:
                wait_time = retry_delay * (2 ** attempt)
                logger.info(f"等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)
        
        # 所有重试都失败
        error_msg = f"LLM API 调用失败，已重试 {retry_count} 次: {last_error}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    def generate_chapter(self, prompt: str, temperature: float = 0.8) -> str:
        """生成章节正文"""
        return self.generate(
            prompt=prompt,
            max_tokens=config.llm.max_tokens_chapter,
            temperature=temperature
        )
    
    def generate_summary(self, prompt: str) -> str:
        """生成摘要"""
        return self.generate(
            prompt=prompt,
            max_tokens=config.llm.max_tokens_summary,
            temperature=0.3  # 摘要用低温保证准确性
        )
    
    def generate_ideas(self, prompt: str) -> str:
        """生成创意"""
        return self.generate(
            prompt=prompt,
            max_tokens=config.llm.max_tokens_ideas,
            temperature=1.0  # 创意用高温增加多样性
        )
    
    def generate_creative_direction(self, prompt: str) -> str:
        """
        生成章节创意方向和色彩建议
        包括情感基调、戏剧张力、极端色彩等
        """
        return self.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=1.2  # 极高温度以获得更有戏剧性的建议
        )


# 全局客户端实例（延迟初始化）
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取 LLM 客户端单例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def reset_llm_client():
    """重置 LLM 客户端（用于测试或更换 API Key）"""
    global _llm_client
    _llm_client = None
