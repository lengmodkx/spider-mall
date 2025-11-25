# UV 使用指南

## 什么是 UV？

UV 是一个超快的 Python 包和项目管理器，用 Rust 编写。它可以替代 pip、pip-tools 和 virtualenv。

## UV 已安装

你的系统已经安装了 UV：
- 版本：0.8.15
- 安装路径：已在系统 PATH 中

## UV 优势

1. **速度极快**：比 pip 快 10-100 倍
2. **依赖管理**：自动处理依赖冲突
3. **虚拟环境**：自动创建和管理虚拟环境
4. **缓存机制**：智能包缓存，节省下载时间
5. **锁定文件**：确保环境一致性

## 在 SpiderMail 项目中使用 UV

### 1. 安装依赖

```bash
# 进入项目目录
cd D:\develop\project\python\spiderMail

# 同步所有依赖（包括开发依赖）
uv sync

# 只安装生产依赖
uv sync --no-dev

# 添加新依赖
uv add requests beautifulsoup4

# 添加开发依赖
uv add --dev pytest black
```

### 2. 运行命令

```bash
# 运行主程序
uv run spidermail --help

# 运行脚本
uv run python example.py

# 运行测试
uv run pytest

# 运行代码格式化
uv run black src/

# 运行类型检查
uv run mypy src/
```

### 3. 虚拟环境管理

```bash
# UV 自动管理虚拟环境，无需手动操作

# 查看虚拟环境信息
uv venv --help

# 重新创建虚拟环境
uv sync --reinstall
```

### 4. 开发工作流

```bash
# 1. 克隆或进入项目
cd spidermail

# 2. 安装所有依赖
uv sync

# 3. 激活环境（可选，uv run 会自动处理）
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 4. 运行开发命令
uv run python example.py
uv run pytest
uv run black src/
```

### 5. 项目初始化（如果开始新项目）

```bash
# 创建新项目
uv init my-new-project
cd my-new-project

# 添加依赖
uv add requests
uv add --dev pytest

# 运行代码
uv run python main.py
```

## UV 常用命令

### 基本命令

```bash
# 检查 UV 版本
uv --version

# 查看帮助
uv --help

# 同步项目依赖
uv sync

# 添加包
uv add package_name

# 添加开发包
uv add --dev package_name

# 移除包
uv remove package_name

# 更新包
uv lock --upgrade
```

### 运行命令

```bash
# 在项目环境中运行命令
uv run python script.py
uv run pytest
uv run black .
uv run mypy src/

# 执行脚本文件
uv run script.py [args]
```

### 依赖管理

```bash
# 查看已安装的包
uv pip list

# 查看依赖树
uv pip tree

# 生成锁定文件
uv lock

# 验证锁定文件
uv lock --check
```

## 配置文件

### pyproject.toml 配置

项目的 `pyproject.toml` 文件已经配置好了 UV：

```toml
[project]
name = "spidermail"
version = "0.1.0"
dependencies = [
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    # ... 其他依赖
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "mypy>=1.5.0",
    # ... 其他开发依赖
]
```

## SpiderMail 项目使用 UV 的完整流程

### 1. 设置开发环境

```bash
# 进入项目目录
cd D:\develop\project\python\spiderMail

# 安装所有依赖
uv sync

# 查看项目状态
uv run spidermail status
```

### 2. 开发和测试

```bash
# 运行示例代码
uv run python example.py

# 测试爬虫功能
uv run spidermail test-spider --platform taobao --test-search

# 手动爬取数据
uv run spidermail crawl --platform all --category 手机 --pages 1

# 代码格式化
uv run black src/ --check

# 类型检查
uv run mypy src/
```

### 3. 部署和维护

```bash
# 检查依赖更新
uv pip list --outdated

# 更新依赖
uv lock --upgrade

# 重新安装依赖
uv sync --reinstall

# 清理缓存
uv cache clean
```

## 性能优势

UV 相比传统 pip 的性能提升：

1. **安装速度**：10-100倍更快的包安装
2. **依赖解析**：毫秒级的依赖冲突解决
3. **缓存机制**：全局缓存，避免重复下载
4. **并行下载**：同时下载多个包
5. **增量更新**：只下载有变化的包

## 故障排除

### 常见问题

1. **UV 命令不存在**
   ```bash
   # 确保 UV 在 PATH 中
   uv --version
   ```

2. **依赖冲突**
   ```bash
   # 清理并重新安装
   uv sync --reinstall
   ```

3. **缓存问题**
   ```bash
   # 清理缓存
   uv cache clean
   ```

4. **权限问题（Windows）**
   ```bash
   # 使用管理员权限运行 PowerShell 或 CMD
   ```

### 环境变量配置

```bash
# 设置 UV 缓存目录（可选）
export UV_CACHE_DIR="D:\uv-cache"

# 设置包索引（可选）
export UV_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple/"
```

## 最佳实践

1. **始终使用 `uv sync`** 而不是手动安装依赖
2. **定期运行 `uv lock --upgrade`** 更新依赖
3. **使用 `--dev` 标志** 区分生产和开发依赖
4. **提交 `uv.lock` 文件** 到版本控制
5. **定期清理缓存** 释放磁盘空间

## 替代工具对比

| 功能 | UV | Pip | Poetry |
|------|-----|-----|--------|
| 速度 | 🚀 极快 | 🐢 慢 | 🚀 快 |
| 依赖解析 | ⚡ 毫秒级 | 🐌 分钟级 | ⚡ 快 |
| 虚拟环境 | ✅ 自动 | ❌ 手动 | ✅ 自动 |
| 锁定文件 | ✅ uv.lock | ❌ 无 | ✅ poetry.lock |
| 缓存 | ✅ 智能 | ❌ 基础 | ✅ 智能 |

现在你可以在 SpiderMail 项目中享受 UV 带来的极速开发体验！