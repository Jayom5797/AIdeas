"""
Fetches article data from AWS Skill Builder API using cookies
Simple HTTP requests - no browser automation
"""
import requests
import json
import os
import time
from typing import List, Dict, Optional
from pathlib import Path
from .config import config


class ArticleFetcher:
    """Fetches articles from AWS Skill Builder API using session cookies"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT,
            'Accept': 'application/json',
        })
        self._load_cookies()
    
    def _load_cookies(self):
        """Load cookies from cookies.json, falling back to COOKIES_JSON env var"""
        cookies_path = Path(__file__).parent.parent / "cookies.json"

        # If file missing, try to restore from environment variable
        if not cookies_path.exists():
            cookies_env = os.environ.get("COOKIES_JSON")
            if cookies_env:
                print("🍪 Restoring cookies from COOKIES_JSON environment variable...")
                with open(cookies_path, 'w') as f:
                    f.write(cookies_env)
            else:
                raise FileNotFoundError(
                    f"cookies.json not found at {cookies_path}. Please export cookies using EditThisCookie extension."
                )
        
        print("🍪 Loading cookies from cookies.json...")
        
        with open(cookies_path, 'r') as f:
            cookies_list = json.load(f)
        
        # Convert EditThisCookie format to requests format
        for cookie in cookies_list:
            self.session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                path=cookie.get('path', '/'),
            )
        
        print(f"✓ Loaded {len(cookies_list)} cookies")
    
    def fetch_all_articles(self) -> List[Dict]:
        """
        Fetch all articles with pagination support
        
        Returns:
            List of article dictionaries with engagement metrics (deduplicated)
        """
        articles = []
        seen_ids = set()
        next_token = None
        page = 1
        consecutive_empty = 0
        
        while True:
            print(f"📥 Fetching page {page}...")
            
            try:
                page_data = self._fetch_page(next_token)
                
                if not page_data or 'feedContents' not in page_data:
                    print("⚠️ No data returned")
                    break
                
                page_articles = page_data['feedContents']
                
                # DEBUG: Print first article structure on page 1
                if page == 1 and len(page_articles) > 0:
                    print(f"🔍 DEBUG - First article keys: {list(page_articles[0].keys())}")
                    print(f"🔍 DEBUG - Sample article: {json.dumps(page_articles[0], indent=2)[:500]}")
                
                # Deduplicate articles by ID
                new_articles = []
                for article in page_articles:
                    article_id = article.get('id') or article.get('contentId') or article.get('articleId')
                    if article_id and article_id not in seen_ids:
                        seen_ids.add(article_id)
                        new_articles.append(article)
                    elif not article_id:
                        print(f"⚠️ Article missing ID: {article.get('title', 'NO TITLE')[:50]}")
                
                # Track consecutive empty pages
                if len(new_articles) == 0:
                    consecutive_empty += 1
                    if len(page_articles) > 0:
                        print(f"⚠️ Page had {len(page_articles)} articles but all were duplicates (consecutive empty: {consecutive_empty})")
                    else:
                        print(f"⚠️ Empty page (consecutive empty: {consecutive_empty})")
                    
                    # Stop after 2 consecutive empty pages
                    if consecutive_empty >= 2:
                        print("✓ Stopping: 2 consecutive pages with no new articles")
                        break
                else:
                    consecutive_empty = 0  # Reset counter
                    articles.extend(new_articles)
                    print(f"✓ Fetched {len(new_articles)} new articles (total unique: {len(articles)})")
                
                # Check for pagination
                next_token = page_data.get('nextToken')
                if not next_token:
                    print("✓ Reached last page (no nextToken)")
                    break
                
                page += 1
                time.sleep(config.REQUEST_DELAY)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error fetching page {page}: {e}")
                break
        
        print(f"\n📊 Deduplication stats: {len(articles)} unique articles from {len(seen_ids)} total IDs")
        return articles
    
    def _fetch_page(self, next_token: Optional[str] = None) -> Dict:
        """
        Fetch a single page of articles
        
        Args:
            next_token: Pagination token from previous response
            
        Returns:
            API response dictionary
        """
        url = "https://api.builder.aws.com/cs/content/tag"
        params = {
            'contentType': 'ARTICLE',
            'tagName': 'aideas-2025',
        }
        
        if next_token:
            params['nextToken'] = next_token
        
        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 401:
                    raise Exception(
                        "Authentication failed. Cookies may have expired. "
                        "Please re-export cookies using EditThisCookie extension."
                    )
                
                response.raise_for_status()
                return response.json()
                
            except requests.RequestException as e:
                if attempt < config.MAX_RETRIES - 1:
                    print(f"⚠️ Attempt {attempt + 1} failed, retrying in {config.RETRY_DELAY}s...")
                    time.sleep(config.RETRY_DELAY)
                else:
                    raise Exception(f"Failed after {config.MAX_RETRIES} attempts: {e}")
    
    def close(self):
        """Close the session"""
        self.session.close()
