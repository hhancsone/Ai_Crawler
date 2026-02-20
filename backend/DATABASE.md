# 数据库表结构

## ai_api_keys - AI API密钥管理表

```sql
CREATE TABLE ai_api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    api_type VARCHAR(50) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    api_base VARCHAR(255),
    model VARCHAR(100),
    prompt TEXT,
    status SMALLINT DEFAULT 1,
    is_default SMALLINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| id | INT | 自增 | 主键 |
| name | VARCHAR(100) | NOT NULL | API名称 |
| api_type | VARCHAR(50) | NOT NULL | API类型 (openai/deepseek/claude等) |
| api_key | VARCHAR(255) | NOT NULL | API密钥 |
| api_base | VARCHAR(255) | NULL | API地址 (可选) |
| model | VARCHAR(100) | NULL | 模型名称 |
| prompt | TEXT | NULL | 系统提示词 |
| status | SMALLINT | 1 | 状态 (1=启用, 0=禁用) |
| is_default | SMALLINT | 0 | 是否默认 (1=默认, 0=非默认) |
| created_at | TIMESTAMP | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

---

## accounts_accountnews - 新闻文章表

```sql
CREATE TABLE accounts_accountnews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    article_url VARCHAR(255) NOT NULL UNIQUE,
    cover_url VARCHAR(255),
    content TEXT,
    date_str DATETIME,
    source VARCHAR(100),
    author VARCHAR(100),
    img_list JSON,
    status SMALLINT DEFAULT 0,
    platform_data JSON,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_title ON accounts_accountnews (title);
CREATE INDEX idx_category ON accounts_accountnews (category);
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| id | INT | 自增 | 主键 |
| title | VARCHAR(255) | NOT NULL | 文章标题 |
| article_url | VARCHAR(255) | NOT NULL, UNIQUE | 文章URL |
| cover_url | VARCHAR(255) | NULL | 封面图URL |
| content | TEXT | NULL | 文章内容 |
| date_str | DATETIME | NULL | 发布日期 |
| source | VARCHAR(100) | NULL | 新闻源 |
| author | VARCHAR(100) | NULL | 作者 |
| img_list | JSON | NULL | 图片列表 |
| status | SMALLINT | 0 | 状态 |
| platform_data | JSON | NULL | 平台数据 |
| category | VARCHAR(100) | NULL | 分类 |
| created_at | TIMESTAMP | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

---

## API接口

### AI API密钥管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/api-keys | 获取所有API密钥 |
| POST | /api/api-keys | 添加API密钥 |
| PUT | /api/api-keys/{id} | 更新API密钥 |
| DELETE | /api/api-keys/{id} | 删除API密钥 |
| GET | /api/api-keys/{id} | 获取单个API密钥 |
