"""
Unified API - Scrapes, stores, and serves data in one process
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from datetime import datetime
import asyncio
import json
import os

from scraper.fetcher import ArticleFetcher
from scraper.parser import ArticleParser
from db.models import init_db
from db.operations import ArticleDB
from scraper.config import config

app = FastAPI(title="AIdeas 2025 Unified API")

# CORS - allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
SessionMaker = init_db(config.DATABASE_URL)

# Track last update time
last_update = None
is_updating = False


class ArticleResponse(BaseModel):
    content_id: str
    title: str
    author_name: str | None
    likes_count: int
    comments_count: int
    engagement_score: float
    article_url: str | None


class StatsResponse(BaseModel):
    total_articles: int
    total_likes: int
    total_comments: int
    last_updated: str | None
    is_updating: bool


def fetch_and_store():
    """Background task to fetch and store articles"""
    global last_update, is_updating
    
    try:
        is_updating = True
        print("\n🔄 Fetching latest data from AWS...")
        
        # Fetch articles
        fetcher = ArticleFetcher()
        raw_articles = fetcher.fetch_all_articles()
        fetcher.close()
        
        # Parse articles
        parsed_articles = ArticleParser.parse_articles(raw_articles)
        
        # Store in database
        session = SessionMaker()
        db = ArticleDB(session)
        
        for article_data in parsed_articles:
            db.upsert_article(article_data)
        
        session.close()
        
        last_update = datetime.utcnow().isoformat()
        print(f"✅ Updated {len(parsed_articles)} articles at {last_update}")
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
    finally:
        is_updating = False


@app.on_event("startup")
async def startup_event():
    """Fetch data on startup"""
    print("🚀 Starting unified API...")
    print("📥 Fetching initial data...")
    fetch_and_store()


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "AIdeas 2025 Unified API",
        "last_update": last_update,
        "is_updating": is_updating
    }


@app.get("/leaderboard", response_model=List[ArticleResponse])
def get_leaderboard(exclude_host: bool = True):
    """
    Get leaderboard (from database cache)
    
    Args:
        exclude_host: Exclude Ben Fowler (AWS host) articles from rankings
    """
    session = SessionMaker()
    db = ArticleDB(session)
    
    try:
        articles = db.get_leaderboard(limit=100, exclude_author="Ben Fowler" if exclude_host else None)
        return [ArticleResponse(**article.to_dict()) for article in articles]
    finally:
        session.close()


@app.get("/stats", response_model=StatsResponse)
def get_stats():
    """Get statistics"""
    session = SessionMaker()
    db = ArticleDB(session)
    
    try:
        stats = db.get_stats()
        return StatsResponse(
            **stats,
            last_updated=last_update,
            is_updating=is_updating
        )
    finally:
        session.close()


@app.post("/refresh")
def refresh_data(background_tasks: BackgroundTasks):
    """Trigger manual refresh"""
    if is_updating:
        return {"status": "already_updating", "message": "Update in progress"}
    
    background_tasks.add_task(fetch_and_store)
    return {"status": "started", "message": "Refresh started in background"}


@app.post("/cookies")
async def update_cookies(cookies_data: dict):
    """
    Update cookies from frontend
    Expects: {"cookies": [...]} (EditThisCookie format)
    """
    try:
        cookies_list = cookies_data.get("cookies", [])
        
        if not cookies_list or not isinstance(cookies_list, list):
            return {"status": "error", "message": "Invalid cookies format. Expected array of cookie objects."}
        
        # Validate cookie structure
        required_fields = ["name", "value", "domain"]
        for cookie in cookies_list:
            if not all(field in cookie for field in required_fields):
                return {"status": "error", "message": f"Cookie missing required fields: {required_fields}"}
        
        # Write to cookies.json
        cookies_path = Path(__file__).parent.parent / "cookies.json"
        with open(cookies_path, 'w') as f:
            json.dump(cookies_list, f, indent=2)
        
        return {
            "status": "success", 
            "message": f"Updated {len(cookies_list)} cookies. Refresh data to use new cookies.",
            "cookie_count": len(cookies_list)
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to update cookies: {str(e)}"}


@app.get("/cookies/status")
def check_cookies():
    """Check if cookies file exists and is valid"""
    try:
        cookies_path = Path(__file__).parent.parent / "cookies.json"
        
        if not cookies_path.exists():
            return {"status": "missing", "message": "No cookies.json found"}
        
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
        
        if not isinstance(cookies, list) or len(cookies) == 0:
            return {"status": "invalid", "message": "cookies.json is empty or invalid"}
        
        return {
            "status": "valid", 
            "message": f"Found {len(cookies)} cookies",
            "cookie_count": len(cookies)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
