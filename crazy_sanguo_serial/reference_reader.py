"""
参考语料读取模块
从 reference 文件夹中随机抽取参考文本
"""

import os
import re
import random
import logging
from pathlib import Path
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class ReferenceReader:
    """
    参考语料读取器
    从 reference 文件夹中读取并抽取参考文本
    """
    
    def __init__(self, reference_dir: Optional[str] = None):
        """
        初始化参考语料读取器
        
        Args:
            reference_dir: 参考语料目录，默认为当前目录/reference
        """
        if reference_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            reference_dir = os.path.join(script_dir, "reference")
        self.reference_dir = Path(reference_dir)
    
    def get_available_categories(self) -> List[str]:
        """获取可用的参考类别（如 joke）"""
        if not self.reference_dir.exists():
            return []
        return [d.name for d in self.reference_dir.iterdir() if d.is_dir()]
    
    def get_files_in_category(self, category: str) -> List[Path]:
        """获取指定类别下的所有文件"""
        category_dir = self.reference_dir / category
        if not category_dir.exists():
            return []
        return [f for f in category_dir.iterdir() if f.is_file() and f.suffix == '.txt']
    
    def extract_paragraphs(self, file_path: Path, min_length: int = 30, max_length: int = 500) -> List[str]:
        """
        从文件中提取段落
        
        Args:
            file_path: 文件路径
            min_length: 最小段落长度（字符，默认30）
            max_length: 最大段落长度（字符，默认500）
            
        Returns:
            段落列表
        """
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 清理内容：移除版权信息、空白行等
            content = self._clean_content(content)
            
            # 按空行分割成段落
            paragraphs = []
            current_para = []
            
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    if current_para:
                        para_text = ' '.join(current_para)
                        if min_length <= len(para_text) <= max_length:
                            paragraphs.append(para_text)
                        current_para = []
                else:
                    # 移除编号（如 "1）"、"1."、"1、" 等）
                    cleaned_line = re.sub(r'^\d+[）\.、:]\s*', '', line)
                    current_para.append(cleaned_line)
            
            # 处理最后一个段落
            if current_para:
                para_text = ' '.join(current_para)
                if min_length <= len(para_text) <= max_length:
                    paragraphs.append(para_text)
            
            return paragraphs
            
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return []
    
    def _clean_content(self, content: str) -> str:
        """
        清理内容
        移除版权页、空白页等无关内容，保留段落分隔的空行
        """
        lines = content.split('\n')
        cleaned_lines = []
        skip_mode = False
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # 跳过版权信息相关行
            if any(keyword in line for keyword in ['版权', '版权所有', 'ISBN', ' CIP ', '图书在版编目']):
                skip_mode = True
                continue
            
            # 跳过前言/目录相关行
            if line in ['前言', '目录', '序言', '后记', '内容提要']:
                skip_mode = True
                continue
            
            # 保留空行作为段落分隔
            if not line:
                if skip_mode and len(cleaned_lines) > 0:
                    skip_mode = False
                cleaned_lines.append('')  # 保留空行
                continue
            
            # 重置跳过模式
            if skip_mode and len(line) > 20:
                skip_mode = False
            
            if not skip_mode:
                cleaned_lines.append(line)
        
        # 移除开头和结尾的空行
        while cleaned_lines and cleaned_lines[0] == '':
            cleaned_lines.pop(0)
        while cleaned_lines and cleaned_lines[-1] == '':
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def sample_references(
        self, 
        category: str = "joke",
        count: int = 3,
        min_length: int = 30,
        max_length: int = 500,
        target_length: int = 150
    ) -> List[str]:
        """
        随机抽取参考文本
        
        Args:
            category: 参考类别（默认 joke）
            count: 抽取数量（默认 3）
            min_length: 最小长度（默认30，用于笑话等短文本）
            max_length: 最大长度（默认500）
            target_length: 目标长度（约150字）
            
        Returns:
            抽取的参考文本列表
        """
        files = self.get_files_in_category(category)
        if not files:
            logger.warning(f"未找到类别 {category} 的文件")
            return []
        
        all_paragraphs = []
        
        # 从所有文件中收集段落
        for file_path in files:
            paragraphs = self.extract_paragraphs(file_path, min_length, max_length)
            all_paragraphs.extend(paragraphs)
        
        if not all_paragraphs:
            logger.warning(f"类别 {category} 中未找到有效段落")
            return []
        
        # 随机选择指定数量的段落
        sample_size = min(count, len(all_paragraphs))
        sampled = random.sample(all_paragraphs, sample_size)
        
        # 确保每个段落约150字
        result = []
        for para in sampled:
            if len(para) > target_length:
                para = para[:target_length * 2]
                for i in range(len(para) - 1, target_length, -1):
                    if para[i] in '，。！？、；：':
                        para = para[:i + 1]
                        break
            result.append(para)
        
        logger.info(f"从 {category} 中抽取了 {len(result)} 条参考文本")
        return result
    
    def sample_multi_category_references(
        self,
        count_per_category: int = 2,
        categories: Optional[List[str]] = None,
        target_length: int = 150
    ) -> Dict[str, List[str]]:
        """
        从多个类别中抽取参考文本
        
        Args:
            count_per_category: 每个类别抽取的数量
            categories: 类别列表，默认为所有可用类别
            target_length: 目标长度
            
        Returns:
            {类别: [参考文本列表]}
        """
        if categories is None:
            categories = self.get_available_categories()
        
        result = {}
        for category in categories:
            refs = self.sample_references(
                category=category,
                count=count_per_category,
                target_length=target_length
            )
            if refs:
                result[category] = refs
        
        return result


# 全局实例
_reference_reader: Optional[ReferenceReader] = None


def get_reference_reader() -> ReferenceReader:
    """获取参考语料读取器实例"""
    global _reference_reader
    if _reference_reader is None:
        _reference_reader = ReferenceReader()
    return _reference_reader