"""
Database operations for article storage and retrieval
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from .models import Article, EngagementHistory


class ArticleDB:
    """Database operations for articles"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def upsert_article(self, article_data: Dict) -> Article:
        """
        Insert or update article
        Creates historical snapshot if engagement changed
        
        Args:
            article_data: Parsed article dictionary
            
        Returns:
            Article model instance
        """
        content_id = article_data['content_id']
        existing = self.session.query(Article).filter_by(content_id=content_id).first()
        
        if existing:
            # Check if engagement changed
            engagement_changed = (
                existing.likes_count != article_data['likes_count'] or
                existing.comments_count != article_data['comments_count']
            )
            
            if engagement_changed:
                # Create historical snapshot
                self._create_snapshot(existing)
            
            # Update existing
            for key, value in article_data.items():
                setattr(existing, key, value)
            existing.last_updated = datetime.utcnow()
            article = existing
        else:
            # Create new
            article = Article(**article_data)
            self.session.add(article)
        
        self.session.commit()
        return article
    
    def _create_snapshot(self, article: Article):
        """Create historical snapshot of engagement metrics"""
        snapshot = EngagementHistory(
            content_id=article.content_id,
            likes_count=article.likes_count,
            comments_count=article.comments_count,
            engagement_score=article.engagement_score,
        )
        self.session.add(snapshot)
    
    def get_leaderboard(
        self, 
        limit: int = 100, 
        sort_by: str = 'engagement_score',
        exclude_author: str | None = None
    ) -> List[Article]:
        """
        Get ranked articles
        
        Args:
            limit: Maximum number of articles to return
            sort_by: Field to sort by (engagement_score, likes_count, comments_count)
            exclude_author: Author name to exclude (e.g., "Ben Fowler" for host articles)
            
        Returns:
            List of Article instances sorted by specified metric
        """
        query = self.session.query(Article)
        
        # Exclude specific author if specified
        if exclude_author:
            query = query.filter(Article.author_name != exclude_author)
        
        if sort_by == 'likes_count':
            query = query.order_by(Article.likes_count.desc())
        elif sort_by == 'comments_count':
            query = query.order_by(Article.comments_count.desc())
        else:
            query = query.order_by(Article.engagement_score.desc())
        
        return query.limit(limit).all()
    
    def get_article(self, content_id: str) -> Optional[Article]:
        """Get single article by ID"""
        return self.session.query(Article).filter_by(content_id=content_id).first()
    
    def get_engagement_history(
        self, 
        content_id: str, 
        limit: int = 50
    ) -> List[EngagementHistory]:
        """Get historical engagement data for an article"""
        return (
            self.session.query(EngagementHistory)
            .filter_by(content_id=content_id)
            .order_by(EngagementHistory.snapshot_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_stats(self) -> Dict:
        """Get overall statistics"""
        total_articles = self.session.query(Article).count()
        total_likes = self.session.query(Article).with_entities(
            Article.likes_count
        ).all()
        total_comments = self.session.query(Article).with_entities(
            Article.comments_count
        ).all()
        
        return {
            'total_articles': total_articles,
            'total_likes': sum(l[0] for l in total_likes),
            'total_comments': sum(c[0] for c in total_comments),
        }
    
    def search_by_title(self, query: str) -> List[Article]:
        """Search articles by title (case-insensitive)"""
        return (
            self.session.query(Article)
            .filter(Article.title.ilike(f'%{query}%'))
            .order_by(Article.engagement_score.desc())
            .all()
        )
