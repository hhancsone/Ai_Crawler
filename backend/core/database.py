import aiomysql
import os
from typing import Optional
from core.logger_utils import logger


class MySQLManager:
    def __init__(
        self,
        host=None,
        port=None,
        user=None,
        password=None,
        database=None,
    ):
        self.host = host or os.getenv("DB_HOST", "localhost")
        self.port = int(port or os.getenv("DB_PORT", 3306))
        self.user = user or os.getenv("DB_USER", "root")
        self.password = password or os.getenv("DB_PASSWORD", "123456")
        self.database = database or os.getenv("DB_DATABASE", "article_spider")
        self.pool: Optional[aiomysql.Pool] = None

    async def create_pool(self):
        """创建连接池"""
        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.database,
            charset="utf8mb4",
            maxsize=10,
            minsize=1,
            autocommit=True,
        )

    async def close_pool(self):
        """关闭连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def execute(self, sql, params: tuple = ()):
        """执行SQL语句"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, params)
                return cursor.lastrowid

    async def fetchone(self, sql, params=None):
        """查询单条记录"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql, params or ())
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def fetchall(self, sql, params=None):
        """查询多条记录"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql, params or ())
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def init_tables(self):
        """初始化数据表"""
        check_table_sql = """
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s
            AND table_name = 'accounts_accountnews'
        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(check_table_sql, (self.database,))
                result = await cursor.fetchone()
                logger.info(f"检查表存在性结果: {result[0]}")
                if result[0] == 0:
                    create_table_sql = """
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
                        )
                    """
                    await cursor.execute(create_table_sql)
                    await cursor.execute("CREATE INDEX idx_title ON accounts_accountnews (title)")
                    await cursor.execute("CREATE INDEX idx_category ON accounts_accountnews (category)")
                    print("表 'accounts_accountnews' 已创建")
                else:
                    print("表 'accounts_accountnews' 已存在，跳过创建")
                
                try:
                    await cursor.execute("ALTER TABLE accounts_accountnews ADD COLUMN task_id INT")
                    print("添加 task_id 列成功")
                except Exception as e:
                    print(f"task_id 列可能已存在: {e}")
                
                check_api_table_sql = """
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                    AND table_name = 'ai_api_keys'
                """
                await cursor.execute(check_api_table_sql, (self.database,))
                result2 = await cursor.fetchone()
                logger.info(f"检查ai_api_keys表存在性结果: {result2[0]}")
                if result2[0] == 0:
                    create_api_table_sql = """
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
                        )
                    """
                    await cursor.execute(create_api_table_sql)
                    print("表 'ai_api_keys' 已创建")
                else:
                    print("表 'ai_api_keys' 已存在，跳过创建")
                
                try:
                    await cursor.execute("ALTER TABLE ai_api_keys ADD COLUMN prompt TEXT")
                    print("添加 prompt 列成功")
                except Exception as e:
                    print(f"prompt 列可能已存在: {e}")


db_manager = MySQLManager()
