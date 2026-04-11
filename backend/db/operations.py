"""
Database operations for article storage and retrieval
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from .models import Article, EngagementHistory

# Hardcoded set of finalist content IDs (from the top-50 announcement article)
FINALIST_CONTENT_IDS = {
    "39w2EpJsgvWLg1yI3DNXfdX24tt", "39pQRgWDhijhuAlgN7PGgKgRoKm",
    "3A22NGhiEao2qxdd2Np4qCzahUV", "3AbGElqMID1VIAquwTZjF0hZ8ho",
    "39vKKkxvVQH1vM8dGpasINKy4Ea", "3BA1XmppjtA03RMR591vsCUxyIZ",
    "3AKpV9GGYD2hH94y8sZmvM3qqbF", "2rlJyjfEaINU6vttnDCoKWioK7j",
    "3AuhVCPW5dZn3fiUJ7fwhQyOzuO", "3ApXZirCDBgcUwz2Wtq9XJelthn",
    "3A0qTVUBzVuln6qahlkE0qX5yw0", "3AQbVLbWi70kMFoB92BwMT6EWj9",
    "3AqocXTWi2lWGnSkv2IBSMWxuuZ", "39pMA9C7qgjaIBqKJ0iAdQh2YmK",
    "3AQEpG9RlAFKgKkfOejDaja2TkX", "3AtCnJBSAWMDPwwjZiKLb3966Gp",
    "2zkFqqTTTB259ZesLX6l9ZbAqjD", "3AfHeBvpSunQSXvPDwSWoGbIkY3",
    "3A5ZGagjs9NfS76srn6yf0jAxNQ", "3AuHojv2cAq5mta6yC3BL9xKQxk",
    "3ArXiTl1piZMjDvsLN7gzeaSm2h", "3AYky649pvTCo3t2c74mCOyleM9",
    "39cMiFMTs7dRujnZnJd6Rw0oqkE", "3AW1kUcDD5MrziiX2z6mCplwNcp",
    "39n0dA4R4kJaFnRt95Aarx8Lq2Q", "39rLlWN6eOiGKB3qWDZyOPqKYjh",
    "3AwnvXYA2wZh1jN7WpG2FM6wgIF", "3AUHZSGL7l0rIvdqL154lhZKGTG",
    "3AZ5MKTeFiz6gT5ETAOMsIw3Vf8", "3ACtQwpKbT8jju0A0QaiMAKalnl",
    "3Aw69ASEjk9q2Tb1oavrKMotRWz", "3AeXqXKHOhdK9wMUwgK7IVYYV6O",
    "3Au9FCd7zZXkZWcx4JNZF718VQJ", "39qTnLaOki9b8RyT8MXOrg7Fns6",
    "3AuDbQhLBCgNjQo1vtdDbVXC0c1", "39nhcXonZOuxaH48n0TzrZDPwoK",
    "3AhXKEDLAm6Hu7DZ8gaOxQsDCKs", "3ASNW5iP8qrd7wARCBZYBwp2OCz",
    "3AsfNNuL0H583VpiKKoyZyyMf5E", "39nfgkz3wQ5tMWufutneVaoYfrk",
    "3Ae5pVpDymo5OF3oo3Ayl9eICdd", "3AvWRbIIAfakGmO0JQOx4m3StUy",
    "3Atk3LZRvgmQNhtaQnDJqtxYIW6", "3Anluy9p9fwbBgQKjQn9zvhMqmC",
    "3AuERXnLd33364Vev1HdG49CvzH", "3Au3F8dVsVAd4h3A9Un5tI2b6ji",
    "3AN8yefCK4HLdu8bscRMqt5ldLv", "39l2TayUzpddaEpCePLFw8Vt7Vl",
    "39hDgbnVoDjOhrR9yek4LyCuAPM", "3Au5CFfGzb4WZiSPREr50tVNzhA",
}


def is_finalist_article(content_id: str, title: str) -> bool:
    """Determine if an article belongs to a finalist based on content ID or title prefix."""
    if content_id in FINALIST_CONTENT_IDS:
        return True
    if title and title.startswith("AIdeas Finalist:"):
        return True
    return False


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

        # Determine finalist status
        article_data['is_finalist'] = is_finalist_article(
            content_id, article_data.get('title', '')
        )
        
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
        limit: Optional[int] = 100, 
        sort_by: str = 'engagement_score',
        exclude_author: str | None = None,
        finalist_only: bool = False,
    ) -> List[Article]:
        query = self.session.query(Article)
        
        if exclude_author:
            query = query.filter(Article.author_name != exclude_author)
        
        if finalist_only:
            query = query.filter(Article.is_finalist == True)  # noqa: E712
        
        if sort_by == 'likes_count':
            query = query.order_by(Article.likes_count.desc())
        elif sort_by == 'comments_count':
            query = query.order_by(Article.comments_count.desc())
        else:
            query = query.order_by(Article.engagement_score.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
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
