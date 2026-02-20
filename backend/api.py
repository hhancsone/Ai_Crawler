import asyncio
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Dict, Optional

import uvicorn
from core.database import db_manager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.logger_utils import logger

load_dotenv()

# Task models
class TaskCreate(BaseModel):
    name: str
    source: str
    categories: List[str] = []
    categoryCounts: Dict[str, int] = {}
    rate: str
    count: int = 10

class Task(BaseModel):
    id: int
    name: str
    source: str
    sourceName: str
    categories: List[str] = []
    categoryCounts: Dict[str, int] = {}
    rate: str
    rateSeconds: int
    count: int = 10
    countSeconds: int = 0
    status: str
    createdAt: str
    dataCount: int

class Result(BaseModel):
    id: int
    title: str
    source: str
    category: str
    author: Optional[str] = None
    publishTime: Optional[str] = None
    createdAt: str
    content: Optional[str] = None
    article_url: Optional[str] = None
    taskId: Optional[int] = None
    taskName: Optional[str] = None
    imgList: Optional[str] = None
    coverUrl: Optional[str] = None

# In-memory task storage
tasks: List[Task] = []
next_task_id = 1

# Rate to seconds mapping
RATE_MAP = {
    "fast": 60,
    "normal": 180,
    "slow": 300
}

# News source mapping
NEWS_SOURCES = {
    "wangyi": "网易新闻",
    "souhu": "搜狐新闻",
    "xinlang": "新浪新闻",
    "pengpai": "澎湃新闻",
    "ithome": "IT之家",
    "tengxunxinwen": "腾讯新闻",
    "tengxuntiyu": "腾讯体育",
    "zhongguoribao": "中国日报"
}

# Active crawling tasks
active_crawlers = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.header("API 服务启动")
    
    # Initialize database connection
    db_manager.host = os.getenv("DB_HOST", "localhost")
    db_manager.port = int(os.getenv("DB_PORT", 3306))
    db_manager.user = os.getenv("DB_USER", "root")
    db_manager.password = os.getenv("DB_PASSWORD", "123456")
    db_manager.database = os.getenv("DB_DATABASE", "article_spider")
    
    try:
        # First try to create database if not exists
        import aiomysql
        temp_pool = await aiomysql.create_pool(
            host=db_manager.host,
            port=db_manager.port,
            user=db_manager.user,
            password=db_manager.password,
            autocommit=True
        )
        async with temp_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_manager.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        temp_pool.close()
        await temp_pool.wait_closed()
        
        # Then connect to the database
        await db_manager.create_pool()
        await db_manager.init_tables()
        logger.success("数据库连接池已创建")
    except Exception as e:
        logger.warning(f"数据库连接失败: {e}，API 将以有限功能运行")
    
    yield
    
    # Shutdown
    await db_manager.close_pool()
    logger.info("API 服务已关闭")


app = FastAPI(title="EasyCrawler API", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "time": datetime.now().isoformat()}

# Task APIs
@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    return tasks

@app.post("/api/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    global next_task_id
    
    source_name = NEWS_SOURCES.get(task.source, task.source)
    rate_seconds = RATE_MAP.get(task.rate, 180)
    task_count = task.count if task.count else 10
    
    new_task = Task(
        id=next_task_id,
        name=task.name,
        source=task.source,
        sourceName=source_name,
        categories=task.categories,
        categoryCounts=task.categoryCounts,
        rate=task.rate,
        rateSeconds=rate_seconds,
        count=task_count,
        status="running",
        createdAt=datetime.now().isoformat(),
        dataCount=0
    )
    
    tasks.append(new_task)
    next_task_id += 1
    
    # Start crawling in background
    asyncio.create_task(run_spider_task(new_task))
    
    return new_task

async def run_spider_task(task: Task):
    """Background task to run the spider"""
    try:
        # Import spiders dynamically
        from spiders.ithome import ITHome
        from spiders.pengpai import PengPai
        from spiders.wangyi import WangYi
        from spiders.souhu import SouHu
        from spiders.tengxunxinwen import TenXuNews
        from spiders.tengxuntiyu import TenXun
        from spiders.xinlang import XinLangGuoJi
        from spiders.zhongguoribao import ChineseDayNews
        
        spider_map = {
            "ithome": ITHome,
            "pengpai": PengPai,
            "wangyi": WangYi,
            "souhu": SouHu,
            "tengxunxinwen": TenXuNews,
            "tengxuntiyu": TenXun,
            "xinlang": XinLangGuoJi,
            "zhongguoribao": ChineseDayNews
        }
        
        spider_class = spider_map.get(task.source)
        if not spider_class:
            task.status = "failed"
            return
        
        categories = task.categories if task.categories else ["新闻"]
        total_saved = 0
        
        for cat in categories:
            spider = spider_class()
            spider.category = cat
            spider.task_id = task.id
            count_for_cat = task.categoryCounts.get(cat, task.count) if task.categoryCounts else task.count
            saved_count = await spider.crawl_and_save(limit=count_for_cat)
            total_saved += saved_count
        
        # Update task
        for t in tasks:
            if t.id == task.id:
                t.status = "completed"
                t.dataCount = total_saved
                break
        
        logger.success(f"任务 {task.name} 完成，保存了 {total_saved} 篇文章")
        
    except Exception as e:
        logger.error(f"任务 {task.name} 失败: {e}")
        for t in tasks:
            if t.id == task.id:
                t.status = "failed"
                break

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    global tasks
    try:
        async with db_manager.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM accounts_accountnews WHERE task_id = %s", (task_id,))
                await conn.commit()
    except Exception as e:
        logger.error(f"删除任务结果失败: {e}")
    
    tasks = [t for t in tasks if t.id != task_id]
    return {"success": True}

@app.post("/api/tasks/{task_id}/run")
async def run_task(task_id: int):
    task = next((t for t in tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "running"
    asyncio.create_task(run_spider_task(task))
    return {"success": True}

# Result APIs
@app.get("/api/results", response_model=List[Result])
async def get_results(source: Optional[str] = None, category: Optional[str] = None, limit: int = 100):
    try:
        async with db_manager.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "SELECT id, title, source, category, date_str, author, created_at, content, article_url, task_id, cover_url, img_list FROM accounts_accountnews WHERE 1=1"
                params = []
                
                if source:
                    query += " AND source = %s"
                    params.append(source)
                if category:
                    query += " AND category = %s"
                    params.append(category)
                
                query += f" ORDER BY created_at DESC LIMIT {limit}"
                
                await cursor.execute(query, params)
                rows = await cursor.fetchall()
                
                results = []
                for row in rows:
                    task_id = row[9] if len(row) > 9 else None
                    task_name = None
                    if task_id:
                        for t in tasks:
                            if t.id == task_id:
                                task_name = t.name
                                break
                    results.append(Result(
                        id=row[0],
                        title=row[1] or "",
                        source=row[2] or "",
                        category=row[3] or "",
                        author=row[5],
                        publishTime=str(row[4]) if row[4] else None,
                        createdAt=str(row[6]) if row[6] else "",
                        content=row[7] if len(row) > 7 else None,
                        article_url=row[8] if len(row) > 8 else None,
                        taskId=task_id,
                        taskName=task_name,
                        coverUrl=row[10] if len(row) > 10 else None,
                        imgList=row[11] if len(row) > 11 else None
                    ))
                
                return results
    except Exception as e:
        logger.error(f"获取结果失败: {e}")
        return []

@app.delete("/api/results/{result_id}")
async def delete_result(result_id: int):
    try:
        async with db_manager.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM accounts_accountnews WHERE id = %s", (result_id,))
                await conn.commit()
                return {"success": True}
    except Exception as e:
        logger.error(f"删除结果失败: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/stats")
async def get_stats():
    try:
        async with db_manager.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Total count
                await cursor.execute("SELECT COUNT(*) FROM accounts_accountnews")
                total = (await cursor.fetchone())[0]
                
                # Count by source
                await cursor.execute("SELECT source, COUNT(*) FROM accounts_accountnews GROUP BY source")
                by_source = {row[0]: row[1] for row in await cursor.fetchall()}
                
                # Recent count (last 24 hours)
                await cursor.execute("SELECT COUNT(*) FROM accounts_accountnews WHERE created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)")
                recent = (await cursor.fetchone())[0]
                
                return {
                    "total": total,
                    "bySource": by_source,
                    "recent24h": recent,
                    "tasks": len(tasks),
                    "runningTasks": len([t for t in tasks if t.status == "running"])
                }
    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        return {
            "total": 0,
            "bySource": {},
            "recent24h": 0,
            "tasks": len(tasks),
            "runningTasks": len([t for t in tasks if t.status == "running"])
        }

# Crawl single URL API
@app.post("/api/crawl-url")
async def crawl_url(request: Dict):
    url = request.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    try:
        # Import spiders dynamically
        from spiders.ithome import ITHome
        from spiders.pengpai import PengPai
        from spiders.wangyi import WangYi
        from spiders.souhu import SouHu
        from spiders.tengxunxinwen import TenXuNews
        from spiders.tengxuntiyu import TenXun
        from spiders.xinlang import XinLangGuoJi
        from spiders.zhongguoribao import ChineseDayNews
        
        # Determine which spider to use based on URL
        if "163.com" in url or "wangyi" in url.lower():
            spider_class = WangYi
        elif "sohu.com" in url:
            spider_class = SouHu
        elif "sina" in url:
            spider_class = XinLangGuoJi
        elif "thepaper.cn" in url or "pengpai" in url.lower():
            spider_class = PengPai
        elif "ithome" in url.lower():
            spider_class = ITHome
        elif "qq.com" in url:
            if "sports" in url:
                spider_class = TenXun
            else:
                spider_class = TenXuNews
        elif "chinadaily" in url:
            spider_class = ChineseDayNews
        else:
            # Try all spiders until one works
            spider_classes = [WangYi, SouHu, XinLangGuoJi, PengPai, ITHome, TenXuNews, TenXun, ChineseDayNews]
            spider_class = None
            
            for sc in spider_classes:
                try:
                    spider = sc()
                    if hasattr(spider, 'get_news_info'):
                        result = await spider.get_news_info({"article_url": url}, category="通用")
                        if result:
                            spider_class = sc
                            break
                except Exception:
                    continue
            
            if not spider_class:
                raise HTTPException(status_code=400, detail="Unsupported URL, cannot find matching spider")
        
        # Create spider instance and get news info
        spider = spider_class()
        
        # Try to get news info
        item = {"article_url": url, "title": "", "cover_url": "", "category": "通用"}
        
        result = await spider.get_news_info(item, category="通用")
        
        if result:
            return {
                "success": True,
                "data": result
            }
        else:
            # If detailed crawl fails, return basic info
            return {
                "success": True,
                "data": {
                    "title": "无法获取详情",
                    "article_url": url,
                    "article_info": "该页面无法被爬取或内容解析失败",
                    "cover_url": "",
                    "date_str": ""
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"爬取URL失败: {e}")
        raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")

@app.get("/api/download-image")
async def download_image(url: str):
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    content_type = response.headers.get('Content-Type', 'image/jpeg')
                    from fastapi.responses import Response
                    return Response(content=content, media_type=content_type)
                else:
                    raise HTTPException(status_code=400, detail="Failed to download image")
    except Exception as e:
        logger.error(f"下载图片失败: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

class ApiKey(BaseModel):
    id: Optional[int] = None
    name: str
    api_type: str
    api_key: str
    api_base: Optional[str] = None
    model: Optional[str] = None
    prompt: Optional[str] = None
    status: int = 1
    is_default: int = 0

class ChatRequest(BaseModel):
    api_key_id: int
    message: str

class ChatResponse(BaseModel):
    success: bool
    data: Optional[str] = None
    detail: Optional[str] = None

async def get_api_config(api_key_id: int):
    row = await db_manager.fetchone("SELECT * FROM ai_api_keys WHERE id = %s AND status = 1", (api_key_id,))
    if not row:
        return None
    return row

async def call_openai_api(api_key: str, base_url: str, model: str, messages: list) -> str:
    import requests
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API返回错误: {response.status_code} - {response.text}")
    except Exception as e:
        raise Exception(f"API调用失败: {str(e)}")

async def call_deepseek_api(api_key: str, model: str, messages: list) -> str:
    import requests
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API返回错误: {response.status_code} - {response.text}")
    except Exception as e:
        raise Exception(f"API调用失败: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        api_config = await get_api_config(request.api_key_id)
        if not api_config:
            return ChatResponse(success=False, detail="API密钥不存在或已禁用")
        
        api_type = api_config["api_type"].lower()
        api_key = api_config["api_key"]
        model = api_config.get("model") or "gpt-3.5-turbo"
        
        messages = []
        if api_config.get("prompt"):
            messages.append({"role": "system", "content": api_config["prompt"]})
        messages.append({"role": "user", "content": request.message})
        
        result = ""
        if api_type == "openai":
            base_url = api_config["api_base"] or "https://api.openai.com/v1"
            result = await call_openai_api(api_key, base_url, model, messages)
        elif api_type == "deepseek":
            result = await call_deepseek_api(api_key, model, messages)
        else:
            if api_config["api_base"]:
                result = await call_openai_api(api_key, api_config["api_base"], model, messages)
            else:
                return ChatResponse(success=False, detail=f"不支持的API类型: {api_type}")
        
        return ChatResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"聊天失败: {e}")
        return ChatResponse(success=False, detail=str(e))

@app.get("/api/api-keys", response_model=List[Dict])
async def get_api_keys():
    try:
        rows = await db_manager.fetchall("SELECT * FROM ai_api_keys ORDER BY created_at DESC")
        return rows
    except Exception as e:
        logger.error(f"获取API密钥列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/api-keys")
async def create_api_key(api_key: ApiKey):
    try:
        if api_key.is_default == 1:
            await db_manager.execute("UPDATE ai_api_keys SET is_default = 0")
        
        sql = """
            INSERT INTO ai_api_keys (name, api_type, api_key, api_base, model, prompt, status, is_default)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        await db_manager.execute(sql, (
            api_key.name, api_key.api_type, api_key.api_key, 
            api_key.api_base, api_key.model, api_key.prompt,
            api_key.status, api_key.is_default
        ))
        return {"success": True, "message": "API密钥添加成功"}
    except Exception as e:
        logger.error(f"添加API密钥失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/api-keys/{api_key_id}")
async def update_api_key(api_key_id: int, api_key: ApiKey):
    try:
        if api_key.is_default == 1:
            await db_manager.execute("UPDATE ai_api_keys SET is_default = 0")
        
        sql = """
            UPDATE ai_api_keys 
            SET name=%s, api_type=%s, api_key=%s, api_base=%s, model=%s, prompt=%s, status=%s, is_default=%s
            WHERE id=%s
        """
        await db_manager.execute(sql, (
            api_key.name, api_key.api_type, api_key.api_key,
            api_key.api_base, api_key.model, api_key.prompt, api_key.status, api_key.is_default, api_key_id
        ))
        return {"success": True, "message": "API密钥更新成功"}
    except Exception as e:
        logger.error(f"更新API密钥失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/api-keys/{api_key_id}")
async def delete_api_key(api_key_id: int):
    try:
        await db_manager.execute("DELETE FROM ai_api_keys WHERE id = %s", (api_key_id,))
        return {"success": True, "message": "API密钥删除成功"}
    except Exception as e:
        logger.error(f"删除API密钥失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/api-keys/{api_key_id}")
async def get_api_key(api_key_id: int):
    try:
        row = await db_manager.fetchone("SELECT * FROM ai_api_keys WHERE id = %s", (api_key_id,))
        if not row:
            raise HTTPException(status_code=404, detail="API密钥不存在")
        return row
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取API密钥失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
