"""
数据持久化模块
负责所有 JSON 和 Markdown 文件的读写操作
支持原子写入防止数据损坏
"""

import json
import os
import shutil
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List

from config import config

logger = logging.getLogger(__name__)


class Storage:
    """
    存储管理器
    提供 JSON/Markdown 文件的安全读写，支持多小说
    """
    
    def __init__(self, base_path: Optional[str] = None, novel_id: Optional[str] = None):
        """
        初始化存储管理器
        
        Args:
            base_path: 基础路径，默认为项目根目录
            novel_id: 小说ID，默认为 None（使用 legacy 模式）
        """
        if base_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_path = Path(base_path)
        self.novel_id = novel_id
        self._paths = config.storage.get_novel_paths(novel_id) if novel_id else {}
        self._ensure_data_dirs()
    
    def _ensure_data_dirs(self):
        """确保所有必要目录存在"""
        if self.novel_id:
            dirs = [
                self.base_path / self._paths["chapters_dir"],
                self.base_path / self._paths["chapter_summaries_dir"],
            ]
            for d in dirs:
                d.mkdir(parents=True, exist_ok=True)
                logger.debug(f"确保目录存在: {d}")
    
    def set_novel(self, novel_id: str):
        """切换到指定小说"""
        self.novel_id = novel_id
        self._paths = config.storage.get_novel_paths(novel_id)
        self._ensure_data_dirs()
    
    def _get_novel_file_path(self, key: str) -> Path:
        """获取小说相关文件的完整路径"""
        if not self.novel_id or key not in self._paths:
            raise ValueError(f"未设置小说ID或无效的路径key: {key}")
        return self.base_path / self._paths[key]
    
    def _get_legacy_file_path(self, relative_path: str) -> Path:
        """获取旧版文件路径（兼容模式）"""
        return self.base_path / relative_path
    
    def _get_file_path(self, relative_path: str) -> Path:
        """获取完整文件路径"""
        return self.base_path / relative_path
    
    def read_json(self, relative_path: str, use_novel_paths: bool = False) -> Optional[Dict]:
        """
        读取 JSON 文件
        
        Args:
            relative_path: 相对于 base_path 的路径
            use_novel_paths: 是否使用小说路径（当 novel_id 设置时）
            
        Returns:
            解析后的字典，若文件不存在返回 None
        """
        if use_novel_paths and self.novel_id:
            try:
                file_path = self._get_novel_file_path(relative_path)
            except ValueError:
                file_path = self._get_file_path(relative_path)
        else:
            file_path = self._get_file_path(relative_path)
        if not file_path.exists():
            logger.debug(f"文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"成功读取 JSON: {file_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析错误 {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"读取文件错误 {file_path}: {e}")
            return None
    
    def write_json(self, relative_path: str, data: Dict, atomic: bool = True, use_novel_paths: bool = False) -> bool:
        """
        写入 JSON 文件
        
        Args:
            relative_path: 相对于 base_path 的路径
            data: 要写入的数据
            atomic: 是否使用原子写入（先写 .tmp 再 rename）
            use_novel_paths: 是否使用小说路径（当 novel_id 设置时）
            
        Returns:
            是否写入成功
        """
        if use_novel_paths and self.novel_id:
            try:
                file_path = self._get_novel_file_path(relative_path)
            except ValueError:
                file_path = self._get_file_path(relative_path)
        else:
            file_path = self._get_file_path(relative_path)
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if atomic:
                temp_path = file_path.with_suffix('.tmp')
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                shutil.move(str(temp_path), str(file_path))
                logger.debug(f"原子写入 JSON: {file_path}")
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.debug(f"直接写入 JSON: {file_path}")
            return True
        except Exception as e:
            logger.error(f"写入 JSON 失败 {file_path}: {e}")
            temp_path = file_path.with_suffix('.tmp')
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def read_text(self, relative_path: str) -> Optional[str]:
        """读取文本文件"""
        file_path = self._get_file_path(relative_path)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文本失败 {file_path}: {e}")
            return None
    
    def write_text(self, relative_path: str, content: str, atomic: bool = True) -> bool:
        """
        写入文本文件
        
        Args:
            relative_path: 相对于 base_path 的路径
            content: 要写入的内容
            atomic: 是否使用原子写入
            
        Returns:
            是否写入成功
        """
        file_path = self._get_file_path(relative_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if atomic:
                temp_path = file_path.with_suffix('.tmp')
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                shutil.move(str(temp_path), str(file_path))
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            logger.debug(f"写入文本: {file_path}")
            return True
        except Exception as e:
            logger.error(f"写入文本失败 {file_path}: {e}")
            temp_path = file_path.with_suffix('.tmp')
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def file_exists(self, relative_path: str) -> bool:
        """检查文件是否存在"""
        return self._get_file_path(relative_path).exists()
    
    def get_chapter_path(self, chapter_num: int) -> Path:
        """获取章节文件路径"""
        if self.novel_id:
            return self.base_path / self._paths["chapters_dir"] / f"chapter_{chapter_num:03d}.md"
        return self.base_path / "novel-reader" / "data" / "chapters" / f"chapter_{chapter_num:03d}.md"
    
    def get_chapter_summary_path(self, chapter_num: int) -> Path:
        """获取章节摘要路径"""
        if self.novel_id:
            return self.base_path / self._paths["chapter_summaries_dir"] / f"chapter_{chapter_num:03d}.json"
        return self.base_path / "novel-reader" / "data" / "chapter_summaries" / f"chapter_{chapter_num:03d}.json"
    
    def list_chapters(self) -> List[int]:
        """列出所有已有章节编号"""
        if self.novel_id:
            chapters_dir = self.base_path / self._paths["chapters_dir"]
        else:
            chapters_dir = self.base_path / "novel-reader" / "data" / "chapters"
        chapter_nums = []
        
        if chapters_dir.exists():
            for f in chapters_dir.glob("chapter_*.md"):
                try:
                    num = int(f.stem.split('_')[1])
                    chapter_nums.append(num)
                except (IndexError, ValueError):
                    continue
        
        chapter_nums.sort()
        return chapter_nums
    
    def read_last_chapter_content(self) -> Optional[str]:
        """读取最后一章的完整内容"""
        chapters = self.list_chapters()
        if not chapters:
            return None
        
        last_num = chapters[-1]
        chapter_path = self.get_chapter_path(last_num)
        return self.read_text(str(chapter_path.relative_to(self.base_path)))
    
    def read_last_chapter_ending(self, num_lines: int = 20) -> Optional[str]:
        """
        读取最后一章的结尾部分
        
        Args:
            num_lines: 读取最后几行
            
        Returns:
            章节结尾内容
        """
        content = self.read_last_chapter_content()
        if not content:
            return None
        
        lines = content.split('\n')
        if len(lines) <= num_lines:
            return content
        
        return '\n'.join(lines[-num_lines:])


# 全局存储实例
_storage: Optional[Storage] = None


def get_storage(novel_id: Optional[str] = None) -> Storage:
    """获取存储管理器单例"""
    global _storage
    if _storage is None:
        _storage = Storage(novel_id=novel_id)
    elif novel_id and _storage.novel_id != novel_id:
        _storage.set_novel(novel_id)
    return _storage


def reset_storage():
    """重置存储管理器（用于测试）"""
    global _storage
    _storage = None


class NovelManager:
    """小说管理器 - 管理所有小说"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def list_novels(self) -> List[Dict]:
        """列出所有小说"""
        list_file = self.storage.base_path / config.storage.novel_list_file
        if list_file.exists():
            with open(list_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_novel_list(self, novels: List[Dict]):
        """保存小说列表"""
        list_file = self.storage.base_path / config.storage.novel_list_file
        list_file.parent.mkdir(parents=True, exist_ok=True)
        with open(list_file, 'w', encoding='utf-8') as f:
            json.dump(novels, f, ensure_ascii=False, indent=2)
    
    def get_novel(self, novel_id: str) -> Optional[Dict]:
        """获取指定小说信息"""
        novels = self.list_novels()
        for n in novels:
            if n.get("id") == novel_id:
                return n
        return None
    
    def novel_data_exists(self, novel_id: str) -> bool:
        """检查小说数据是否存在（新位置或旧位置）"""
        # 检查新位置
        novel_meta = self.storage.base_path / config.storage.novels_dir / novel_id / "meta.json"
        if novel_meta.exists():
            return True
        
        # 检查旧位置（legacy）
        if novel_id == "crazy_sanguo":
            legacy_meta = self.storage.base_path / "novel-reader" / "meta.json"
            if legacy_meta.exists():
                return True
        
        return False
    
    def add_novel(self, novel_id: str, title: str, subtitle: str = "") -> Dict:
        """添加新小说"""
        novels = self.list_novels()
        existing = self.get_novel(novel_id)
        if existing:
            return existing
        
        novel = {
            "id": novel_id,
            "title": title,
            "subtitle": subtitle,
            "created_at": "",
        }
        novels.append(novel)
        self.save_novel_list(novels)
        return novel
    
    def remove_novel(self, novel_id: str):
        """删除小说"""
        novels = self.list_novels()
        novels = [n for n in novels if n.get("id") != novel_id]
        self.save_novel_list(novels)
