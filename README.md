# SpiderMail 🕷️📧

一个自动爬取淘宝、京东手机品类商品信息和评论数据的Python程序，并将数据存储到PostgreSQL数据库中。

## 功能特性

- 🛒 **多平台支持**: 同时支持淘宝和京东商品数据爬取
- 📊 **丰富数据**: 商品信息、价格历史、用户评论、评分等
- ⏰ **定时任务**: 每天自动执行爬取任务
- 🗄️ **数据存储**: PostgreSQL数据库存储，支持历史数据追踪
- 🔄 **数据清洗**: 自动数据验证、清洗和去重
- 📝 **详细日志**: 完整的操作日志记录
- 🛡️ **反爬策略**: 随机User-Agent、请求延迟、重试机制
- 🎯 **精准定位**: 专注于手机品类的深度数据采集

## 项目结构

```
spidermail/
├── src/spidermail/
│   ├── spiders/           # 爬虫模块
│   │   ├── base.py       # 基础爬虫类
│   │   ├── taobao_spider.py  # 淘宝爬虫
│   │   └── jd_spider.py      # 京东爬虫
│   ├── database/          # 数据库模块
│   │   └── connection.py # 数据库连接管理
│   ├── models/            # 数据模型
│   │   ├── product.py    # 商品模型
│   │   ├── review.py     # 评论模型
│   │   └── crawl_task.py # 爬取任务模型
│   ├── utils/             # 工具模块
│   │   ├── data_cleaner.py  # 数据清洗
│   │   ├── logger.py         # 日志配置
│   │   └── exceptions.py     # 自定义异常
│   ├── config/            # 配置模块
│   │   └── settings.py   # 配置管理
│   ├── scheduler.py       # 任务调度器
│   ├── cli.py            # 命令行界面
│   └── __init__.py
├── database/
│   └── schema.sql        # 数据库表结构
├── pyproject.toml        # 项目配置
├── .env.example          # 环境变量示例
├── README.md             # 项目说明
└── CLAUDE.md             # Claude Code 指导文件
```

## 快速开始

### 1. 环境要求

- Python 3.12+
- PostgreSQL 12+
- Redis (可选，用于缓存)

### 2. 安装项目

```bash
# 克隆项目
git clone <repository-url>
cd spidermail

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -e .
```

### 3. 配置数据库

```bash
# 创建PostgreSQL数据库
createdb spidermail

# 复制环境配置文件
cp .env.example .env

# 编辑.env文件，配置数据库连接信息
```

### 4. 初始化数据库

```bash
spidermail init-db
```

### 5. 测试爬虫功能

```bash
# 测试淘宝爬虫
spidermail test-spider --platform taobao --test-search

# 测试京东爬虫
spidermail test-spider --platform jd --test-search
```

### 6. 运行爬取任务

```bash
# 手动爬取
spidermail crawl --platform all --category 手机 --pages 3

# 启动定时任务
spidermail start-scheduler
```

## 命令行工具

SpiderMail提供了丰富的命令行工具：

### 数据库管理
```bash
# 初始化数据库表
spidermail init-db [--host HOST] [--port PORT] [--database DATABASE] [--username USERNAME]
```

### 爬取任务
```bash
# 手动爬取数据
spidermail crawl [--platform PLATFORM] [--category CATEGORY] [--pages PAGES]

# 测试爬虫
spidermail test-spider --platform PLATFORM [--test-search] [--test-reviews]
```

### 任务调度
```bash
# 启动定时调度器
spidermail start-scheduler
```

### 系统状态
```bash
# 查看系统状态
spidermail status

# 查看配置信息
spidermail config
```

## 数据库表结构

### products (商品表)
- 商品基本信息：标题、品牌、价格、销量、评分等
- 商品详情：图片、描述、规格参数、店铺信息等
- 状态和时间戳字段

### reviews (评论表)
- 评论基本信息：用户评分、评论内容、购买信息等
- 评论元数据：有用数、回复数、情感分析等
- 关联商品ID和平台信息

### price_history (价格历史表)
- 商品价格变化历史记录
- 支持价格趋势分析

### crawl_tasks (爬取任务表)
- 爬取任务执行记录
- 任务状态、执行结果、错误信息等

## 配置说明

### 环境变量配置

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=spidermail
DB_USER=postgres
DB_PASSWORD=your_password

# 爬虫配置
REQUEST_DELAY=1.0              # 请求延迟（秒）
MAX_RETRIES=3                  # 最大重试次数
CONCURRENT_REQUESTS=5          # 并发请求数

# 调度配置
SCHEDULE_ENABLED=true          # 是否启用定时任务
CRAWL_TIME=02:00              # 每日爬取时间
TIMEZONE=Asia/Shanghai        # 时区设置
```

### 自定义配置

可以通过修改 `src/spidermail/config/settings.py` 文件进行更详细的配置。

## 数据清洗和验证

系统包含完整的数据清洗功能：

1. **数据验证**: 使用Pydantic进行数据模型验证
2. **数据清洗**: 自动清理HTML标签、规范文本格式
3. **去重处理**: 基于商品ID和评论ID去重
4. **情感分析**: 简单的情感倾向分析
5. **关键词提取**: 从评论中提取关键词

## 日志记录

系统提供详细的日志记录：

- **控制台日志**: 实时显示运行状态
- **文件日志**: 保存详细的运行日志
- **错误日志**: 单独记录错误信息
- **日志轮转**: 自动轮转和压缩历史日志

日志位置: `logs/spidermail.log`

## 反爬策略

为了应对网站的反爬措施，系统实现了以下策略：

1. **随机User-Agent**: 轮换使用不同的浏览器标识
2. **请求延迟**: 模拟人工操作的随机延迟
3. **重试机制**: 失败请求的自动重试
4. **代理支持**: 支持代理池配置（可选）
5. **请求频率控制**: 控制并发请求数量

## 扩展和定制

### 添加新平台

1. 继承 `BaseSpider` 类
2. 实现必要的方法：`search_products`, `get_product_details`, `get_product_reviews`
3. 在调度器中注册新的爬虫

### 添加新字段

1. 修改数据库模型 (`models/`)
2. 更新数据清洗逻辑 (`utils/data_cleaner.py`)
3. 重新生成数据库表结构

## 性能优化

1. **数据库索引**: 在关键字段上建立索引
2. **连接池**: 使用数据库连接池管理连接
3. **批量操作**: 批量插入和更新数据
4. **缓存机制**: Redis缓存热点数据

## 注意事项

1. **合法使用**: 请遵守网站的使用条款和robots.txt
2. **请求频率**: 不要设置过高的请求频率
3. **数据隐私**: 评论中的用户信息已经脱敏处理
4. **系统资源**: 爬取大量数据时注意系统资源消耗

## 故障排除

### 常见问题

1. **数据库连接失败**: 检查数据库配置和网络连接
2. **爬取失败**: 检查网络连接和目标网站可访问性
3. **数据保存失败**: 检查数据库表结构和权限
4. **调度器停止**: 检查日志文件查看错误信息

### 日志分析

通过查看日志文件可以诊断问题：

```bash
# 查看最新日志
tail -f logs/spidermail.log

# 查看错误日志
tail -f logs/error.log
```

## 开发和贡献

欢迎提交问题和改进建议！

### 开发环境设置

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
flake8 src/
```

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

## 联系方式

如有问题或建议，请通过Issue或Pull Request联系。

---

**免责声明**: 本工具仅用于合法的数据收集和分析目的。使用者需要自行确保遵守目标网站的使用条款和相关法律法规。