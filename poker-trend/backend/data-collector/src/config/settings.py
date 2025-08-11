# -*- coding: utf-8 -*-
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Database URLs
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/poker_trend")
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://admin:password@localhost:27017/poker_trend?authSource=admin")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API Keys
    youtube_api_key: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    twitter_bearer_token: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")
    reddit_client_id: Optional[str] = os.getenv("REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = os.getenv("REDDIT_CLIENT_SECRET")
    
    # Collection Settings
    trend_check_interval: int = int(os.getenv("TREND_CHECK_INTERVAL", "300"))  # 5 minutes
    minimum_trend_score: float = float(os.getenv("MINIMUM_TREND_SCORE", "70.0"))
    trend_alert_threshold: float = float(os.getenv("TREND_ALERT_THRESHOLD", "85.0"))
    
    # Rate Limiting
    api_rate_limit: int = int(os.getenv("API_RATE_LIMIT", "100"))
    api_rate_window: int = int(os.getenv("API_RATE_WINDOW", "3600"))  # 1 hour
    
    # Collection Limits
    max_youtube_results: int = int(os.getenv("MAX_YOUTUBE_RESULTS", "50"))
    max_twitter_results: int = int(os.getenv("MAX_TWITTER_RESULTS", "100"))
    max_reddit_results: int = int(os.getenv("MAX_REDDIT_RESULTS", "25"))
    
    # Keywords for poker trend detection
    poker_keywords: list = [
        "poker", "wsop", "world series of poker", "pokerstars", "texas holdem",
        "omaha poker", "poker tournament", "poker strategy", "bluff", "all in",
        "poker hand", "royal flush", "straight flush", "full house", "flush",
        "straight", "three of a kind", "two pair", "pair", "high card",
        "daniel negreanu", "phil hellmuth", "doyle brunson", "phil ivey",
        "antonio esfandiari", "gus hansen", "poker face", "poker chips",
        "casino poker", "online poker", "live poker", "poker room",
        "poker cash game", "poker sit n go", "poker mtt", "poker final table"
    ]
    
    # Social media hashtags to monitor
    poker_hashtags: list = [
        "#poker", "#pokerstars", "#wsop", "#pokertournament", "#pokerlife",
        "#pokerstrategy", "#pokernews", "#pokerplayer", "#pokerpro",
        "#texasholdem", "#omaha", "#pokercash", "#pokermtt", "#pokersng",
        "#pokerface", "#allin", "#bluff", "#pokerhands", "#royalflush",
        "#pokeronline", "#livepoker", "#casinpoker", "#pokergame"
    ]
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        case_sensitive = False
        env_file = ".env"

# Create global settings instance
settings = Settings()