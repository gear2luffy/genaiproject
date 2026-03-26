"""
SQLAlchemy models for the AI Trading Platform.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.database import Base


class TradeSignal(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class TradeStatus(str, enum.Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class SentimentType(str, enum.Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class Stock(Base):
    """Stock/Asset information."""
    __tablename__ = "stocks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    market_cap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_crypto: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_data: Mapped[List["PriceData"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    signals: Mapped[List["Signal"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    news_items: Mapped[List["NewsItem"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    patterns: Mapped[List["Pattern"]] = relationship(back_populates="stock", cascade="all, delete-orphan")


class PriceData(Base):
    """Historical price data."""
    __tablename__ = "price_data"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)
    
    # Technical Indicators (cached)
    rsi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    macd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    macd_signal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ema_12: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ema_26: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sma_20: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sma_50: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bollinger_upper: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bollinger_lower: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    atr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    stock: Mapped["Stock"] = relationship(back_populates="price_data")


class Signal(Base):
    """AI-generated trading signals."""
    __tablename__ = "signals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    signal_type: Mapped[TradeSignal] = mapped_column(Enum(TradeSignal))
    confidence: Mapped[float] = mapped_column(Float)
    
    # Component scores
    technical_score: Mapped[float] = mapped_column(Float)
    pattern_score: Mapped[float] = mapped_column(Float)
    sentiment_score: Mapped[float] = mapped_column(Float)
    
    # Additional info
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price_at_signal: Mapped[float] = mapped_column(Float)
    target_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    stop_loss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    stock: Mapped["Stock"] = relationship(back_populates="signals")
    trades: Mapped[List["Trade"]] = relationship(back_populates="signal")


class Trade(Base):
    """Trade execution records."""
    __tablename__ = "trades"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    signal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("signals.id"), nullable=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    
    side: Mapped[str] = mapped_column(String(10))  # BUY or SELL
    quantity: Mapped[float] = mapped_column(Float)
    entry_price: Mapped[float] = mapped_column(Float)
    exit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    status: Mapped[TradeStatus] = mapped_column(Enum(TradeStatus), default=TradeStatus.PENDING)
    is_paper: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Risk management
    stop_loss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    take_profit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Results
    pnl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pnl_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # External reference
    external_order_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    signal: Mapped[Optional["Signal"]] = relationship(back_populates="trades")


class NewsItem(Base):
    """News articles and their sentiment."""
    __tablename__ = "news_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stock_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stocks.id"), nullable=True, index=True)
    
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(100))
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    
    # Sentiment analysis
    sentiment: Mapped[SentimentType] = mapped_column(Enum(SentimentType))
    sentiment_score: Mapped[float] = mapped_column(Float)  # -1 to 1
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    stock: Mapped[Optional["Stock"]] = relationship(back_populates="news_items")


class Pattern(Base):
    """Detected chart patterns."""
    __tablename__ = "patterns"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    
    pattern_type: Mapped[str] = mapped_column(String(100))  # e.g., "HEAD_AND_SHOULDERS", "DOUBLE_TOP"
    direction: Mapped[str] = mapped_column(String(20))  # BULLISH, BEARISH
    confidence: Mapped[float] = mapped_column(Float)
    
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    
    support_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resistance_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Pattern-specific data
    pattern_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    stock: Mapped["Stock"] = relationship(back_populates="patterns")


class BacktestResult(Base):
    """Backtesting results."""
    __tablename__ = "backtest_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    
    # Configuration
    symbols: Mapped[List[str]] = mapped_column(JSON)
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    initial_capital: Mapped[float] = mapped_column(Float)
    strategy_params: Mapped[dict] = mapped_column(JSON)
    
    # Results
    final_capital: Mapped[float] = mapped_column(Float)
    total_return: Mapped[float] = mapped_column(Float)
    total_trades: Mapped[int] = mapped_column(Integer)
    winning_trades: Mapped[int] = mapped_column(Integer)
    losing_trades: Mapped[int] = mapped_column(Integer)
    win_rate: Mapped[float] = mapped_column(Float)
    
    # Metrics
    sharpe_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sortino_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_drawdown: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    profit_factor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Detailed results
    equity_curve: Mapped[List[dict]] = mapped_column(JSON)
    trade_history: Mapped[List[dict]] = mapped_column(JSON)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Portfolio(Base):
    """Portfolio positions and holdings."""
    __tablename__ = "portfolio"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    quantity: Mapped[float] = mapped_column(Float)
    average_cost: Mapped[float] = mapped_column(Float)
    current_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    market_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unrealized_pnl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    is_paper: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
