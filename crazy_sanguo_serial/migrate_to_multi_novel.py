#!/usr/bin/env python3
"""
数据迁移脚本
将旧的单小说数据迁移到新的多小说目录结构

使用方法:
    python migrate_to_multi_novel.py [--novel-id NAME]

迁移内容:
1. 将 meta.json 移动到 novels/{novel_id}/meta.json
2. 将 story_bible.json 移动到 novels/{novel_id}/story_bible.json
3. 将 characters.json 移动到 novels/{novel_id}/characters.json
4. 将 plot_state.json 移动到 novels/{novel_id}/plot_state.json
5. 将 arc_summaries.json 移动到 novels/{novel_id}/arc_summaries.json
6. 将 data/chapters/ 移动到 novels/{novel_id}/chapters/
7. 将 data/chapter_summaries/ 移动到 novels/{novel_id}/chapter_summaries/
8. 创建 novel-list.json
"""

import os
import sys
import shutil
import json
import argparse
from pathlib import Path

script_dir = Path(__file__).parent
BASE_DIR = script_dir.parent / "novel-reader"
NOVELS_DIR = BASE_DIR / "novels"


def parse_args():
    parser = argparse.ArgumentParser(description="迁移数据到多小说目录结构")
    parser.add_argument(
        "--novel-id",
        type=str,
        default="crazy_sanguo",
        help="小说ID（默认: crazy_sanguo）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅显示将要执行的操作，不实际执行"
    )
    return parser.parse_args()


def ensure_dirs(novel_id: str):
    """确保小说目录存在"""
    dirs = [
        NOVELS_DIR / novel_id,
        NOVELS_DIR / novel_id / "chapters",
        NOVELS_DIR / novel_id / "chapter_summaries",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def migrate_file(src: Path, dst: Path, dry_run: bool = False):
    """迁移单个文件"""
    if not src.exists():
        print(f"  ⏭️  跳过 (不存在): {src}")
        return False
    
    if dry_run:
        print(f"  📋 将移动: {src} -> {dst}")
        return True
    
    shutil.move(str(src), str(dst))
    print(f"  ✅ 已移动: {src.name}")
    return True


def migrate_novel_list(novel_id: str, story_title: str, story_subtitle: str, dry_run: bool = False):
    """更新小说列表"""
    list_file = NOVELS_DIR / "novel-list.json"
    
    if dry_run:
        if list_file.exists():
            print(f"  📋 将更新: {list_file}")
        else:
            print(f"  📋 将创建: {list_file}")
        return
    
    novels = []
    if list_file.exists():
        with open(list_file, 'r', encoding='utf-8') as f:
            novels = json.load(f)
    
    existing = any(n.get("id") == novel_id for n in novels)
    if not existing:
        import datetime
        novels.append({
            "id": novel_id,
            "title": story_title,
            "subtitle": story_subtitle,
            "created_at": datetime.datetime.now().isoformat()
        })
        with open(list_file, 'w', encoding='utf-8') as f:
            json.dump(novels, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 已更新小说列表")
    else:
        print(f"  ⏭️  小说已在列表中: {novel_id}")


def main():
    args = parse_args()
    novel_id = args.novel_id
    dry_run = args.dry_run
    
    print(f"\n🔄 数据迁移到多小说目录")
    print(f"   小说ID: {novel_id}")
    print(f"   模式: {'仅预览' if dry_run else '执行迁移'}")
    print("=" * 50)
    
    if not (BASE_DIR / "meta.json").exists() and not (BASE_DIR / "data").exists():
        print("❌ 未找到需要迁移的数据")
        sys.exit(1)
    
    ensure_dirs(novel_id)
    
    print("\n📁 迁移文件:")
    
    meta_file = BASE_DIR / "meta.json"
    if meta_file.exists():
        meta_data = json.load(open(meta_file, 'r', encoding='utf-8'))
        story_title = meta_data.get("story_title", "未知小说")
        story_subtitle = meta_data.get("story_subtitle", "")
    else:
        story_title = "未知小说"
        story_subtitle = ""
    
    migrate_file(meta_file, NOVELS_DIR / novel_id / "meta.json", dry_run)
    migrate_file(BASE_DIR / "story_bible.json", NOVELS_DIR / novel_id / "story_bible.json", dry_run)
    migrate_file(BASE_DIR / "characters.json", NOVELS_DIR / novel_id / "characters.json", dry_run)
    migrate_file(BASE_DIR / "plot_state.json", NOVELS_DIR / novel_id / "plot_state.json", dry_run)
    migrate_file(BASE_DIR / "arc_summaries.json", NOVELS_DIR / novel_id / "arc_summaries.json", dry_run)
    
    print("\n📁 迁移目录:")
    
    src_chapters = BASE_DIR / "data" / "chapters"
    dst_chapters = NOVELS_DIR / novel_id / "chapters"
    if src_chapters.exists():
        if dry_run:
            print(f"  📋 将移动目录: {src_chapters} -> {dst_chapters}")
        else:
            if dst_chapters.exists():
                shutil.rmtree(dst_chapters)
            shutil.move(str(src_chapters), str(dst_chapters))
            print(f"  ✅ 已移动章节目录")
    
    src_summaries = BASE_DIR / "data" / "chapter_summaries"
    dst_summaries = NOVELS_DIR / novel_id / "chapter_summaries"
    if src_summaries.exists():
        if dry_run:
            print(f"  📋 将移动目录: {src_summaries} -> {dst_summaries}")
        else:
            if dst_summaries.exists():
                shutil.rmtree(dst_summaries)
            shutil.move(str(src_summaries), str(dst_summaries))
            print(f"  ✅ 已移动摘要目录")
    
    migrate_novel_list(novel_id, story_title, story_subtitle, dry_run)
    
    if dry_run:
        print("\n⚠️  这是预览模式，未执行实际迁移")
        print("   移除 --dry-run 参数以执行迁移")
    else:
        print("\n✅ 迁移完成!")
        print(f"   小说数据已迁移到: {NOVELS_DIR / novel_id}")
    
    print()


if __name__ == '__main__':
    main()