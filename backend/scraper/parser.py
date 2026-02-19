"""
Parses raw API response into structured article data
"""
from typing import Dict, List
from datetime import datetime
from .config import config


class ArticleParser:
    """Parses article data from API response"""
    
    @staticmethod
    def parse_article(raw_article: Dict) -> Dict:
        """
        Extract relevant fields from raw API response
        
        Args:
            raw_article: Raw article dict from API
            
        Returns:
            Cleaned article dict with engagement metrics
        """
        # Extract author info
        author = raw_article.get('author', {})
        author_name = author.get('preferredName') or author.get('alias', 'Unknown')
        
        # Extract engagement metrics
        likes = raw_article.get('likesCount', 0)
        comments = raw_article.get('commentsCount', 0)
        
        # Calculate engagement score
        engagement_score = (
            likes * config.LIKE_WEIGHT + 
            comments * config.COMMENT_WEIGHT
        )
        
        # Extract timestamps
        published_at = raw_article.get('lastPublishedAt')
        published_date = None
        if published_at:
            # Convert milliseconds timestamp to datetime
            published_date = datetime.fromtimestamp(published_at / 1000)
        
        # Build article URL
        content_id = raw_article.get('contentId', '')
        article_url = f"https://builder.aws.com{content_id}" if content_id else None
        
        return {
            'content_id': content_id,
            'title': raw_article.get('title', 'Untitled'),
            'author_name': author_name,
            'author_alias': author.get('alias'),
            'likes_count': likes,
            'comments_count': comments,
            'engagement_score': engagement_score,
            'published_at': published_date,
            'article_url': article_url,
            'description': raw_article.get('contentTypeSpecificResponse', {})
                                      .get('article', {})
                                      .get('description', ''),
        }
    
    @staticmethod
    def parse_articles(raw_articles: List[Dict]) -> List[Dict]:
        """
        Parse multiple articles
        
        Args:
            raw_articles: List of raw article dicts
            
        Returns:
            List of parsed article dicts
        """
        parsed = []
        for raw in raw_articles:
            try:
                parsed.append(ArticleParser.parse_article(raw))
            except Exception as e:
                print(f"⚠️ Failed to parse article: {e}")
                continue
        
        return parsed
