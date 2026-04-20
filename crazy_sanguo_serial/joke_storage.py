"""
笑话集存储模块
负责笑话集数据的持久化
"""

import json
import os
import shutil
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class JokeStorage:
    """
    笑话集存储管理器
    负责所有笑话集相关文件的读写
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        初始化存储管理器
        
        Args:
            base_path: 基础路径，默认为项目根目录
        """
        if base_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_path = Path(base_path)
        self.jokes_dir = self.base_path / "jokes"
        self._ensure_data_dirs()
    
    def _ensure_data_dirs(self):
        """确保基础目录存在"""
        self.jokes_dir.mkdir(parents=True, exist_ok=True)
        meta_file = self.jokes_dir / "meta.json"
        if not meta_file.exists():
            self.write_json("meta.json", [])
    
    # ==================== 笑话集列表操作 ====================
    
    def list_collections(self) -> List[Dict]:
        """列出所有笑话集"""
        return self.read_json("meta.json") or []
    
    def save_collection_list(self, collections: List[Dict]) -> bool:
        """保存笑话集列表"""
        return self.write_json("meta.json", collections)
    
    def get_collection_meta_path(self, collection_id: str) -> Path:
        """获取笑话集元数据路径"""
        return self.jokes_dir / collection_id / "meta.json"
    
    def get_collection_jokes_dir(self, collection_id: str) -> Path:
        """获取笑话存储目录路径"""
        return self.jokes_dir / collection_id / "jokes"
    
    def get_collection_summaries_dir(self, collection_id: str) -> Path:
        """获取摘要存储目录路径"""
        return self.jokes_dir / collection_id / "joke_summaries"
    
    def get_joke_path(self, collection_id: str, joke_group: int) -> Path:
        """获取单组笑话文件路径"""
        return self.get_collection_jokes_dir(collection_id) / f"joke_{joke_group:03d}.md"
    
    def get_joke_summary_path(self, collection_id: str, joke_group: int) -> Path:
        """获取单组摘要文件路径"""
        return self.get_collection_summaries_dir(collection_id) / f"joke_{joke_group:03d}.json"
    
    # ==================== 单个笑话集操作 ====================
    
    def get_collection(self, collection_id: str) -> Optional[Dict]:
        """获取指定笑话集"""
        collections = self.list_collections()
        for c in collections:
            if c.get("id") == collection_id:
                return c
        return None
    
    def add_collection(self, collection_id: str, title: str, 
                       keywords: List[str], creative_direction: str) -> Dict:
        """
        添加新笑话集
        
        Args:
            collection_id: 笑话集ID
            title: 标题
            keywords: 关键词列表
            creative_direction: 创意方向
            
        Returns:
            创建的笑话集元数据
        """
        import datetime
        
        # 创建目录
        collection_dir = self.jokes_dir / collection_id
        (collection_dir / "jokes").mkdir(parents=True, exist_ok=True)
        (collection_dir / "joke_summaries").mkdir(parents=True, exist_ok=True)
        
        # 创建元数据
        meta = {
            "id": collection_id,
            "title": title,
            "keywords": keywords,
            "creative_direction": creative_direction,
            "current_count": 0,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # 保存元数据
        meta_path = collection_dir / "meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        
        # 更新列表
        collections = self.list_collections()
        collections.append({
            "id": collection_id,
            "title": title,
            "created_at": meta["created_at"]
        })
        self.save_collection_list(collections)
        
        return meta
    
    def update_collection_meta(self, collection_id: str, updates: Dict) -> bool:
        """
        更新笑话集元数据
        
        Args:
            collection_id: 笑话集ID
            updates: 要更新的字段
            
        Returns:
            是否更新成功
        """
        meta_path = self.get_collection_meta_path(collection_id)
        if not meta_path.exists():
            return False
        
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            meta.update(updates)
            
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"更新元数据失败: {e}")
            return False
    
    def remove_collection(self, collection_id: str) -> bool:
        """删除笑话集"""
        # 从列表中移除
        collections = self.list_collections()
        collections = [c for c in collections if c.get("id") != collection_id]
        self.save_collection_list(collections)
        
        # 删除目录
        collection_dir = self.jokes_dir / collection_id
        if collection_dir.exists():
            shutil.rmtree(collection_dir)
            return True
        return False
    
    def collection_exists(self, collection_id: str) -> bool:
        """检查笑话集是否存在"""
        return self.get_collection_meta_path(collection_id).exists()
    
    # ==================== 笑话内容操作 ====================
    
    def save_joke_group(self, collection_id: str, joke_group: int, 
                        content: str, summary: Dict) -> bool:
        """
        保存一组笑话
        
        Args:
            collection_id: 笑话集ID
            joke_group: 组编号（第几组）
            content: 笑话内容（markdown格式）
            summary: 该组摘要
            
        Returns:
            是否保存成功
        """
        # 保存笑话内容
        joke_path = self.get_joke_path(collection_id, joke_group)
        joke_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(joke_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 保存摘要
        summary_path = self.get_joke_summary_path(collection_id, joke_group)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 更新元数据中的计数
        self.update_collection_meta(collection_id, {"current_count": joke_group})
        
        return True
    
    def read_joke_group(self, collection_id: str, joke_group: int) -> Optional[str]:
        """读取一组笑话内容"""
        joke_path = self.get_joke_path(collection_id, joke_group)
        if not joke_path.exists():
            return None
        
        with open(joke_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_joke_groups(self, collection_id: str) -> List[int]:
        """列出笑话集所有组编号"""
        jokes_dir = self.get_collection_jokes_dir(collection_id)
        if not jokes_dir.exists():
            return []
        
        groups = []
        for f in jokes_dir.glob("joke_*.md"):
            try:
                num = int(f.stem.split('_')[1])
                groups.append(num)
            except (IndexError, ValueError):
                continue
        
        groups.sort()
        return groups
    
    # ==================== 工具方法 ====================
    
    def read_json(self, relative_path: str) -> Optional[Any]:
        """读取 JSON 文件"""
        file_path = self.jokes_dir / relative_path
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取JSON失败 {file_path}: {e}")
            return None
    
    def write_json(self, relative_path: str, data: Any, atomic: bool = True) -> bool:
        """写入 JSON 文件"""
        file_path = self.jokes_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if atomic:
                temp_path = file_path.with_suffix('.tmp')
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                shutil.move(str(temp_path), str(file_path))
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"写入JSON失败 {file_path}: {e}")
            return False


# 全局实例
_joke_storage: Optional[JokeStorage] = None


def get_joke_storage() -> JokeStorage:
    """获取笑话存储实例"""
    global _joke_storage
    if _joke_storage is None:
        _joke_storage = JokeStorage()
    return _joke_storage


def reset_joke_storage():
    """重置存储实例（用于测试）"""
    global _joke_storage
    _joke_storage = None