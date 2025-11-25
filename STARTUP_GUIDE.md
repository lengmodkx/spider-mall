# SpiderMail 启动指南

## 项目概述

SpiderMail 是一个电商数据爬虫项目，用于从淘宝和京东等平台提取产品和评论数据。项目已配置好数据库连接并可正常运行。

## 完成的配置

### ✅ 环境配置
- Python 3.12+ 虚拟环境设置
- 使用 uv 管理依赖包
- 所有必需依赖已安装

### ✅ 数据库配置
- **数据库类型**: PostgreSQL 14.19
- **配置方式**: 环境变量（安全）
- **状态**: ✅ 连接成功，表已创建
- **敏感信息**: 已从版本控制中移除

### ✅ 项目结构
```
spiderMail/
├── src/spidermail/          # 主要代码
│   ├── config/             # 配置文件
│   ├── database/           # 数据库连接和模型
│   ├── models/             # 数据模型
│   ├── spiders/            # 爬虫实现
│   ├── utils/              # 工具函数
│   ├── cli.py              # 命令行接口
│   └── scheduler.py        # 任务调度器
├── logs/                   # 日志目录
├── database/               # 数据库脚本
├── test_run.py            # 系统测试脚本
├── start_simple.py        # 简化启动脚本
└── STARTUP_GUIDE.md       # 本文件
```

## 如何使用项目

### 1. 系统状态检查

```bash
# 检查系统状态
uv run python start_simple.py status

# 运行完整测试
uv run python test_run.py
```

### 2. 测试爬虫功能

```bash
# 测试淘宝爬虫
uv run python start_simple.py test taobao

# 测试京东爬虫
uv run python start_simple.py test jd
```

### 3. 使用原始CLI（可能有编码问题）

原始CLI包含emoji字符，在某些Windows环境下可能显示异常，但功能正常：

```bash
# 查看配置（可能有编码问题）
uv run spidermail config

# 初始化数据库
uv run spidermail init-db

# 手动爬取数据
uv run spidermail crawl --platform taobao --category 手机 --pages 3

# 启动调度器
uv run spidermail start-scheduler
```

### 4. 编程方式使用

```python
import sys
sys.path.insert(0, 'src')

from spidermail.spiders.taobao_spider import TaobaoSpider
from spidermail.database.connection import db_manager

# 创建爬虫实例
spider = TaobaoSpider()

# 搜索产品
products = spider.search_products("手机", page=1)

# 数据库操作
with db_manager.get_session() as session:
    # 进行数据库操作
    pass
```

## 功能特性

### 🕷️ 爬虫功能
- **淘宝爬虫**: 搜索产品、提取评论
- **京东爬虫**: 搜索产品、提取评论
- **反反爬虫**: 用户代理轮换、请求延迟
- **错误重试**: 自动重试机制

### 💾 数据存储
- **产品信息**: 标题、价格、品牌、规格等
- **评论数据**: 评分、内容、时间等
- **价格历史**: 价格变化追踪
- **任务记录**: 爬取任务状态

### ⏰ 调度功能
- **定时任务**: 每日自动爬取
- **手动触发**: 按需执行爬取
- **失败重试**: 自动重试机制

## 配置说明

### 环境变量配置

为了安全起见，所有敏感配置信息现在都通过环境变量配置。数据库连接信息等敏感数据已从版本控制中移除。

#### 1. 复制环境配置文件
```bash
cp .env.example .env
```

#### 2. 编辑 .env 文件设置你的配置
```bash
# 数据库配置
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password_here

# 其他配置...
REQUEST_DELAY=1.0
LOG_LEVEL=INFO
# ... 更多配置选项
```

#### 3. 可用的环境变量
- **数据库**: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- **爬虫**: `REQUEST_DELAY`, `MAX_RETRIES`, `REQUEST_TIMEOUT`
- **平台**: `TAOBAO_BASE_URL`, `JD_BASE_URL`, `MOBILE_CATEGORY`
- **调度**: `SCHEDULE_ENABLED`, `CRAWL_TIME`, `TIMEZONE`
- **日志**: `LOG_LEVEL`, `LOG_FILE_PATH`

### 安全性
- ✅ `.env` 文件已在 `.gitignore` 中，不会被提交
- ✅ 所有敏感信息通过环境变量管理
- ✅ 提供了 `.env.example` 作为配置模板
- ✅ 默认值安全，不会暴露生产信息

### 爬虫配置
```python
spider:
  request_delay: 1.0          # 请求延迟（秒）
  max_retries: 3              # 最大重试次数
  timeout: 30                 # 请求超时时间
  concurrent_requests: 5      # 并发请求数
```

### 调度配置
```python
schedule:
  enabled: true               # 启用调度器
  crawl_time: "02:00"        # 每日爬取时间
  timezone: "Asia/Shanghai"   # 时区设置
```

## 故障排除

### 1. 编码问题
Windows下emoji字符显示异常是正常的，功能不受影响。使用 `start_simple.py` 可避免此问题。

### 2. 爬虫无数据
淘宝/京东有反爬虫机制，返回空数据是正常现象。可以尝试：
- 更换搜索关键词
- 调整请求参数
- 使用代理

### 3. 数据库连接失败
检查数据库配置和网络连接，确保：
- 数据库服务正常运行
- 网络连接通畅
- 用户名密码正确

## 下一步开发建议

1. **增强反爬虫能力**: 添加更多用户代理、代理池
2. **数据清洗**: 实现更好的数据清洗和验证
3. **API接口**: 添加REST API提供数据访问
4. **数据可视化**: 添加数据展示和分析功能
5. **分布式部署**: 支持多机器分布式爬取

## 技术栈

- **Python**: 3.12+
- **Web框架**: 无（爬虫项目）
- **数据库**: PostgreSQL 14.19
- **ORM**: SQLAlchemy
- **爬虫**: requests, BeautifulSoup4, selenium
- **调度**: schedule, celery
- **日志**: loguru
- **配置**: pydantic
- **包管理**: uv

---

**项目状态**: ✅ 已配置完成，可正常运行
**最后更新**: 2025-11-25