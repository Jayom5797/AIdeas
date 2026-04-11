"""
SQLAlchemy database models
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Article(Base):
    """Article engagement data"""
    __tablename__ = 'articles'
    
    content_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    author_name = Column(String)
    author_alias = Column(String)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    published_at = Column(DateTime)
    article_url = Column(String)
    description = Column(Text)
    
    # Finals tracking
    is_finalist = Column(Boolean, default=False)

    # Tracking
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'content_id': self.content_id,
            'title': self.title,
            'author_name': self.author_name,
            'author_alias': self.author_alias,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'engagement_score': self.engagement_score,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'article_url': self.article_url,
            'description': self.description,
            'is_finalist': self.is_finalist,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }


class EngagementHistory(Base):
    """Historical snapshots of engagement metrics"""
    __tablename__ = 'engagement_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String, nullable=False, index=True)
    likes_count = Column(Integer)
    comments_count = Column(Integer)
    engagement_score = Column(Float)
    snapshot_at = Column(DateTime, default=datetime.utcnow, index=True)


def init_db(database_url: str):
    """Initialize database and return session maker"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    _migrate_add_is_finalist(engine)
    return sessionmaker(bind=engine)


def _migrate_add_is_finalist(engine):
    """Add is_finalist column if it doesn't exist (safe migration)."""
    with engine.connect() as conn:
        try:
            conn.execute(
                __import__('sqlalchemy').text(
                    "ALTER TABLE articles ADD COLUMN is_finalist BOOLEAN DEFAULT 0"
                )
            )
            conn.commit()
            print("[DB] Migrated: added is_finalist column")
        except Exception:
            pass  # Column already exists
