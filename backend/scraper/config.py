from pydantic_settings import BaseSettings
from pathlib import Path

# Get absolute path to backend directory
BACKEND_DIR = Path(__file__).parent.parent.absolute()
DB_PATH = BACKEND_DIR / "aideas_tracker.db"

class ScraperConfig(BaseSettings):
    """Configuration for AWS Skill Builder API scraper"""
    
    # Target URL (for reference)
    TARGET_URL: str = "https://builder.aws.com/learn/topics/aideas-2025?tab=article"
    
    # Rate limiting (seconds)
    REQUEST_DELAY: float = 1.0
    RETRY_DELAY: float = 5.0
    MAX_RETRIES: int = 3
    
    # User agent
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Engagement scoring weights
    LIKE_WEIGHT: float = 1.0
    COMMENT_WEIGHT: float = 1.0
    
    # Database (absolute path)
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

config = ScraperConfig()
print(f"[CONFIG] Database path: {config.DATABASE_URL}")  # Debug output

