"""
Core configuration settings for the AI Trading Platform.
"""
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App Settings
    APP_NAME: str = "AI Trading Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./trading.db"
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Keys
    NEWS_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_KEY: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    
    # Trading API Keys (for real trading - optional)
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"  # Paper trading by default
    
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None
    
    # AI Model Settings
    AI_TECHNICAL_WEIGHT: float = 0.4
    AI_PATTERN_WEIGHT: float = 0.3
    AI_SENTIMENT_WEIGHT: float = 0.3
    AI_CONFIDENCE_THRESHOLD: float = 0.65
    
    # Market Scanner Settings
    SCANNER_SYMBOLS: List[str] = Field(default=[
        "AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "NVDA", "AMD",
        "JPM", "BAC", "GS", "V", "MA", "PYPL",
        "BTC-USD", "ETH-USD", "SOL-USD"
    ])
    SCANNER_INTERVAL: int = 60  # seconds
    SCANNER_TOP_N: int = 10
    
    # Risk Management
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio
    DEFAULT_STOP_LOSS: float = 0.02  # 2%
    DEFAULT_TAKE_PROFIT: float = 0.05  # 5%
    
    # Autonomous Trading Settings
    AUTO_START_TRADING: bool = True  # Start trading automatically on app startup
    AUTO_TRADING_INTERVAL: int = 300  # Scan interval in seconds (5 minutes)
    AUTO_MAX_POSITIONS: int = 5  # Maximum concurrent open positions
    AUTO_CONFIDENCE_THRESHOLD: float = 0.7  # Minimum confidence to execute trade
    AUTO_TRADE_24_7: bool = True  # Trade outside market hours (crypto)
    
    # Backtesting
    BACKTEST_START_DATE: str = "2023-01-01"
    BACKTEST_END_DATE: str = "2024-01-01"
    BACKTEST_INITIAL_CAPITAL: float = 100000.0
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
