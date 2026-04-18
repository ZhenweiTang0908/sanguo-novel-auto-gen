# 🏯 疯狂三国连载器

> 当罗贯中的棺材板压不住的时候...

一个自动化的魔改三国长篇连载生成器。基于阿里云百炼 qwen-turbo 模型，每次运行可自动从现有章节后继续生成新内容。

## ✨ 特性

- 🎲 **极度魔改**：赛博朋克 + 量子兵法 + 修仙机甲 + 丧尸儒学...
- 🔗 **长篇连续**：自动维护角色状态、伏笔、世界观
- 🧠 **智能记忆**：分层压缩机制，支持超长篇连载
- 🎯 **章节衔接**：确保新章节自然承接上文
- 💡 **创意注入**：每章都有新创意，避免重复
- 📊 **状态可视化**：实时显示当前故事状态

## 📁 项目结构

```
crazy_sanguo_serial/
├── main.py              # 主入口
├── config.py            # 配置管理
├── llm_client.py        # LLM 客户端
├── storage.py           # 数据持久化
├── story_state.py       # 故事状态管理
├── prompt_builder.py    # Prompt 构建器
├── summarizer.py        # 摘要生成器
├── chapter_writer.py    # 章节写作逻辑
├── requirements.txt     # 依赖
└── README.md           # 本文件
```

### 数据目录结构

```
data/
├── meta.json            # 元信息（当前章数等）
├── story_bible.json     # 世界观设定
├── characters.json      # 角色状态
├── plot_state.json      # 主线/伏笔/创意记录
├── arc_summaries.json   # 分卷摘要
├── chapters/           # 章节正文
│   ├── chapter_001.md
│   └── ...
└── chapter_summaries/   # 单章摘要
    ├── chapter_001.json
    └── ...
```

## 🚀 安装与运行

### 1. 安装依赖

```bash
cd crazy_sanguo_serial
pip install -r requirements.txt
```

### 2. 设置环境变量

**必须设置** `DASHSCOPE_API_KEY`：

```bash
# Linux/macOS
export DASHSCOPE_API_KEY='your-api-key-here'

# Windows (PowerShell)
$env:DASHSCOPE_API_KEY='your-api-key-here'
```

或者直接在命令行运行：

```bash
DASHSCOPE_API_KEY='your-key' python main.py
```

### 3. 运行

```bash
# 首次运行（自动初始化故事宇宙）
python main.py

# 查看当前状态
python main.py --status

# 生成 3 章新内容
python main.py --chapters 3

# 生成 5 章，设置目标字数
python main.py --chapters 5 --chapter-length 2500

# 高温模式（更有创意但可能更不稳定）
python main.py --chapters 3 --temperature 1.1

# 重新初始化故事（慎用！）
python main.py --init
```

## 🎮 使用方式

### 交互模式

```bash
python main.py
```

会显示当前状态，然后你可以：
1. 生成新章节
2. 重新初始化故事
3. 退出

### 命令行模式

```bash
# 生成 1 章
python main.py -c 1

# 生成 3 章
python main.py --chapters 3

# 指定章节长度
python main.py -c 2 -l 2500
```

## ⚙️ 配置

在 `config.py` 中可以调整：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `llm.temperature` | 0.8 | 生成温度 |
| `llm.max_tokens_chapter` | 3500 | 章节最大 token 数 |
| `chapter.default_length` | 2000 | 默认目标字数 |
| `chapter.arc_trigger` | 5 | 多少章触发分卷摘要 |

## 🧠 核心机制

### 分层记忆压缩

为了支持超长篇连载，系统采用分层压缩：

1. **总设定摘要**：始终完整保留
2. **分卷摘要**：每 5 章合并一次
3. **章节摘要**：保留最近 3 章
4. **结尾片段**：保留最后 1 章结尾

### 章节衔接包

每次写新章节前，系统会自动构建：
- 上一章结尾关键段落
- 当前场景位置
- 主要视角角色
- 角色即时目标
- 当前紧张点
- 必须回应的钩子

### 创意注入器

系统会为每章生成 1-2 个创意候选，包括：
- 人物身份颠倒
- 历史事件反向
- 科技/修仙系统突变
- 势力阵营洗牌
- 记忆篡改
- 平行宇宙碰撞
- 等等...

## 📝 写作风格

- 荒诞史诗 + 热血邪典 + 黑色幽默
- 网文节奏：快节奏、高潮迭起
- 每章必须有推进、有爆点、有结尾钩子
- 文风癫狂但逻辑自洽

## 🔧 开发

### 运行测试

```bash
python -c "from main import *; print('OK')"
```

### 查看日志

```bash
python main.py -c 1 -v
```

## ⚠️ 注意事项

1. API Key 不可硬编码，必须通过环境变量设置
2. 每次 API 调用会消耗 Token，请注意账户余额
3. 重新初始化会清空所有章节和设定
4. 建议定期备份 `data/` 目录

## 📜 License

MIT License - 可以自由使用、修改、分发。

---

**疯狂三国 · 魔改演义** - 让我们一起癫狂！
