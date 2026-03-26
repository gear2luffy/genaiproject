"""
Core configuration settings for the AI Trading Platform.
Configured for Indian Stock Market (NSE/BSE) with Intraday Trading.
"""
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App Settings
    APP_NAME: str = "AI Trading Platform - India"
    APP_VERSION: str = "2.0.0"
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
    
    # Indian Broker API Keys (Zerodha Kite)
    ZERODHA_API_KEY: Optional[str] = None
    ZERODHA_API_SECRET: Optional[str] = None
    ZERODHA_ACCESS_TOKEN: Optional[str] = None
    ZERODHA_REQUEST_TOKEN: Optional[str] = None
    
    # Upstox API Keys (Alternative Indian Broker)
    UPSTOX_API_KEY: Optional[str] = None
    UPSTOX_API_SECRET: Optional[str] = None
    UPSTOX_ACCESS_TOKEN: Optional[str] = None
    
    # Angel One API Keys (Alternative Indian Broker)
    ANGEL_API_KEY: Optional[str] = None
    ANGEL_CLIENT_ID: Optional[str] = None
    ANGEL_PASSWORD: Optional[str] = None
    ANGEL_TOTP_SECRET: Optional[str] = None
    
    # Legacy US Market Keys (for international trading)
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"
    
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None
    
    # Market Selection
    MARKET: str = "INDIA"  # INDIA, US, CRYPTO
    EXCHANGE: str = "NSE"  # NSE, BSE for India
    
    # AI Model Settings - Enhanced for multi-factor analysis
    AI_TECHNICAL_WEIGHT: float = 0.25
    AI_PATTERN_WEIGHT: float = 0.25
    AI_SENTIMENT_WEIGHT: float = 0.25
    AI_SUPPORT_RESISTANCE_WEIGHT: float = 0.25
    AI_CONFIDENCE_THRESHOLD: float = 0.65
    
    # Indian Stock Market Scanner Settings (NSE/BSE)
    SCANNER_SYMBOLS: List[str] = Field(default=[
        # NIFTY 50 Top Stocks
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
        "LT.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "AXISBANK.NS", "MARUTI.NS",
        "HCLTECH.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS",
        "NESTLEIND.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TATAMOTORS.NS",
        # Bank NIFTY Stocks
        "BANKBARODA.NS", "PNB.NS", "IDFCFIRSTB.NS", "INDUSINDBK.NS", "FEDERALBNK.NS",
        # High Volume Intraday Stocks
        "TATASTEEL.NS", "ADANIENT.NS", "ADANIPORTS.NS", "JSWSTEEL.NS", "HINDALCO.NS",
        "COALINDIA.NS", "VEDL.NS", "ZOMATO.NS", "PAYTM.NS", "DELHIVERY.NS"
    ])
    
    # Intraday Scanner Symbols (High liquidity stocks for day trading)
    INTRADAY_SYMBOLS: List[str] = Field(default=[
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "SBIN.NS", "BAJFINANCE.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "AXISBANK.NS",
        "KOTAKBANK.NS", "LT.NS", "MARUTI.NS", "ADANIENT.NS", "ADANIPORTS.NS",
        "HINDALCO.NS", "JSWSTEEL.NS", "ONGC.NS", "NTPC.NS", "ZOMATO.NS"
    ])
    
    SCANNER_INTERVAL: int = 60  # seconds
    SCANNER_TOP_N: int = 10
    
    # Intraday Trading Settings
    INTRADAY_START_TIME: str = "09:15"  # IST
    INTRADAY_END_TIME: str = "15:15"    # IST (Square off before 15:30)
    INTRADAY_SQUARE_OFF_TIME: str = "15:15"  # Auto square off all positions
    INTRADAY_MAX_TRADES_PER_DAY: int = 10
    INTRADAY_MIN_GAP_BETWEEN_TRADES: int = 5  # minutes
    
    # Risk Management - Indian Market
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio per trade
    DEFAULT_STOP_LOSS: float = 0.015  # 1.5% (tighter for intraday)
    DEFAULT_TAKE_PROFIT: float = 0.03  # 3% (reasonable intraday target)
    INTRADAY_STOP_LOSS: float = 0.01  # 1% for intraday trades
    INTRADAY_TAKE_PROFIT: float = 0.02  # 2% for intraday trades
    MAX_DAILY_LOSS: float = 0.03  # Stop trading if 3% portfolio loss
    TRAILING_STOP_PERCENT: float = 0.005  # 0.5% trailing stop
    
    # Position Sizing
    USE_VOLATILITY_POSITION_SIZING: bool = True
    DEFAULT_QUANTITY_INR: float = 50000  # Default position size in INR
    
    # Autonomous Trading Settings
    AUTO_START_TRADING: bool = True  # Start trading automatically on app startup
    AUTO_TRADING_INTERVAL: int = 180  # Scan interval in seconds (3 minutes for intraday)
    AUTO_MAX_POSITIONS: int = 5  # Maximum concurrent open positions
    AUTO_CONFIDENCE_THRESHOLD: float = 0.70  # Minimum confidence to execute trade
    AUTO_TRADE_24_7: bool = False  # Indian market hours only
    
    # Trading Hours (Indian Market - IST)
    MARKET_OPEN_HOUR: int = 9
    MARKET_OPEN_MINUTE: int = 15
    MARKET_CLOSE_HOUR: int = 15
    MARKET_CLOSE_MINUTE: int = 30
    
    # News Sentiment Settings - Indian Sources
    INDIAN_NEWS_SOURCES: List[str] = Field(default=[
        "economictimes.indiatimes.com",
        "moneycontrol.com",
        "livemint.com",
        "business-standard.com",
        "financialexpress.com",
        "zeebiz.com"
    ])
    
    # Pattern Detection Settings
    PATTERN_MIN_CONFIDENCE: float = 0.60
    SUPPORT_RESISTANCE_LOOKBACK: int = 50  # bars to look back
    
    # Signal Combination Settings
    MIN_BULLISH_SIGNALS: int = 3  # Minimum bullish signals needed to buy
    MIN_BEARISH_SIGNALS: int = 3  # Minimum bearish signals needed to sell
    
    # Backtesting
    BACKTEST_START_DATE: str = "2023-01-01"
    BACKTEST_END_DATE: str = "2024-01-01"
    BACKTEST_INITIAL_CAPITAL: float = 500000.0  # 5 Lakh INR
    
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
