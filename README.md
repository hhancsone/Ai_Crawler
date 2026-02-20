# EasyCrawler 智能新闻爬虫系统

一个功能强大的智能新闻爬虫系统，支持多种新闻源、定时任务、AI内容处理和数据导出。

![Vue](https://img.shields.io/badge/Vue-3.4+-42b883?style=flat&logo=vue.js)
![Python](https://img.shields.io/badge/Python-3.12+-3776ab?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat&logo=fastapi)

## 功能特性

### 🕷️ 快速爬取
- 输入任意新闻URL，系统自动识别新闻源
- 支持多种主流新闻网站一键爬取

### 🤖 AI 智能处理
- 集成多种AI模型（OpenAI、Claude、通义千问等）
- 支持内容摘要、翻译、润色等处理

### ⏰ 定时任务
- 创建一次性或周期性爬取任务
- 自定义执行时间和间隔

### 📊 数据管理
- 可视化结果管理界面
- 支持CSV格式数据导出

### 🌐 支持的新闻源

| 新闻源 | 分类 |
|--------|------|
| 网易新闻 | 时事、军事、社会、科技、娱乐、经济、教育、生活 |
| 搜狐新闻 | 时政、国际、财经、娱乐、体育等80+分类 |
| 新浪新闻 | 国际、国内、社会、科技、体育、娱乐、财经、教育、军事 |
| 腾讯新闻 | 经济、科技、娱乐、国际、军事、游戏、民生等 |
| 澎湃新闻 | 中国政库、舆论场、打虎记等100+分类 |
| IT之家 | 科技、数码、手机、电脑、软件、游戏、评测 |
| 腾讯体育 | NBA、CBA、足球、欧冠、英超、中超 |
| 中国日报 | 时政要闻、台海动态、国际资讯、财经、教育、体育 |

## 技术栈

### 前端
- **Vue 3** - 渐进式前端框架
- **Vue Router** - 路由管理
- **Tailwind CSS** - Utility-first CSS框架
- **Lucide Vue Next** - 图标库

### 后端
- **Python 3.12** - 核心语言
- **FastAPI** - 现代高性能Web框架
- **aiohttp** - 异步HTTP客户端
- **MySQL** - 关系型数据库
- **lxml** - XML/HTML解析库

## 项目结构

```
Ai_Crawler/
├── src/                      # 前端源码
│   ├── components/           # Vue组件
│   │   ├── Sidebar.vue       # 侧边栏导航
│   │   ├── NewTaskModal.vue  # 新建任务弹窗
│   │   └── Toast.vue         # 提示组件
│   ├── views/                # 页面视图
│   │   ├── Dashboard.vue     # 仪表盘
│   │   ├── Schedule.vue      # 快速爬取
│   │   ├── Rules.vue         # API管理
│   │   ├── Tasks.vue         # 任务管理
│   │   ├── Results.vue       # 结果管理
│   │   └── Help.vue          # 帮助中心
│   ├── utils/               # 工具函数
│   │   ├── constants.js     # 常量定义
│   │   └── formatDate.js   # 日期格式化
│   ├── App.vue              # 根组件
│   └── main.js              # 入口文件
│
├── backend/                  # 后端源码
│   ├── core/                # 核心模块
│   │   ├── base.py          # 爬虫基类
│   │   ├── database.py      # 数据库连接
│   │   └── logger_utils.py  # 日志工具
│   ├── spiders/             # 爬虫实现
│   │   ├── wangyi.py        # 网易新闻
│   │   ├── souhu.py         # 搜狐新闻
│   │   ├── xinlang.py       # 新浪新闻
│   │   ├── pengpai.py       # 澎湃新闻
│   │   ├── ithome.py        # IT之家
│   │   └── ...
│   ├── api.py               # API服务入口
│   └── main.py              # 主程序
│
├── .gitignore               # Git忽略配置
├── package.json             # 前端依赖
├── vite.config.js           # Vite配置
└── tailwind.config.js       # Tailwind配置
```

## 快速开始

### 环境要求
- Node.js 18+
- Python 3.12+
- MySQL 8.0+

### 1. 克隆项目

```bash
git clone <repository-url>
cd Ai_Crawler
```

### 2. 安装前端依赖

```bash
npm install
```

### 3. 配置后端

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，配置数据库连接
```

### 4. 初始化数据库

```sql
CREATE DATABASE article_spider CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 启动后端服务

```bash
cd backend
python api.py
```

后端服务将在 `http://localhost:8000` 启动

### 6. 启动前端开发服务器

```bash
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

## API 文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/tasks | 获取任务列表 |
| POST | /api/tasks | 创建新任务 |
| DELETE | /api/tasks/{id} | 删除任务 |
| GET | /api/results | 获取结果列表 |
| GET | /api/stats | 获取统计数据 |
| POST | /api/crawl-url | 爬取指定URL |
| POST | /api/chat | AI对话处理 |
| GET | /api/api-keys | 获取API密钥列表 |
| POST | /api/api-keys | 添加API密钥 |

## 使用指南

### 创建爬取任务
1. 点击左侧导航「任务管理」
2. 点击「新建任务」按钮
3. 填写任务名称、选择新闻源、设置爬取URL
4. 选择任务类型（一次性/定时）
5. 点击「创建并运行」

### 快速爬取
1. 点击左侧导航「快速爬取」
2. 输入或粘贴新闻URL
3. 点击「识别URL」自动识别新闻源
4. 在右侧选择AI模型进行处理

### 导出数据
1. 点击左侧导航「结果管理」
2. 使用筛选器选择特定数据
3. 点击「导出数据」按钮下载CSV文件

## 开发说明

### 添加新的新闻源

1. 在 `backend/spiders/` 目录下创建新的爬虫文件
2. 继承 `BaseSpider` 类
3. 实现 `get_news_list` 和 `get_article_content` 方法
4. 在 `api.py` 中注册新的爬虫

### 添加新的AI模型

1. 在前端 `utils/constants.js` 中添加模型配置
2. 后端实现对应的API调用逻辑

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
