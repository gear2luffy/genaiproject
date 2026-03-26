"""
Tests for the AI Trading Platform.
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.anyio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


@pytest.mark.anyio
async def test_scanner_status():
    """Test scanner status endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/scan/status")
        assert response.status_code == 200
        data = response.json()
        assert "symbols_count" in data


class TestTechnicalIndicators:
    """Tests for technical indicators."""
    
    def test_calculate_sma(self):
        import pandas as pd
        from app.services.data.technical_indicators import TechnicalIndicators
        
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        sma = TechnicalIndicators.calculate_sma(data, 3)
        
        assert sma.iloc[-1] == 9.0  # (8 + 9 + 10) / 3
    
    def test_calculate_rsi(self):
        import pandas as pd
        import numpy as np
        from app.services.data.technical_indicators import TechnicalIndicators
        
        # Create sample data with clear trend
        data = pd.Series(np.linspace(100, 150, 30))
        rsi = TechnicalIndicators.calculate_rsi(data, 14)
        
        # In an uptrend, RSI should be above 50
        assert rsi.iloc[-1] > 50


class TestSentimentAnalyzer:
    """Tests for sentiment analyzer."""
    
    def test_positive_sentiment(self):
        from app.services.sentiment.sentiment_engine import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("Stock is surging with strong bullish momentum and record profits")
        
        assert result["sentiment"] == "POSITIVE"
        assert result["score"] > 0
    
    def test_negative_sentiment(self):
        from app.services.sentiment.sentiment_engine import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("Market crash warning as stock declines sharply with major losses")
        
        assert result["sentiment"] == "NEGATIVE"
        assert result["score"] < 0
    
    def test_neutral_sentiment(self):
        from app.services.sentiment.sentiment_engine import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("The stock traded today with normal volume")
        
        # Score should be close to 0 for neutral text
        assert abs(result["score"]) < 0.3


class TestPatternDetector:
    """Tests for pattern detector."""
    
    def test_support_resistance_detection(self):
        import pandas as pd
        import numpy as np
        from app.services.patterns.pattern_detector import PatternDetector
        
        # Create sample OHLCV data
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        close = 100 + np.cumsum(np.random.randn(100) * 2)
        high = close + np.abs(np.random.randn(100))
        low = close - np.abs(np.random.randn(100))
        
        df = pd.DataFrame({
            'open': close - 0.5,
            'high': high,
            'low': low,
            'close': close,
            'volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)
        
        detector = PatternDetector()
        patterns = detector.detect_all_patterns(df)
        
        # Should detect some patterns
        assert isinstance(patterns, list)


class TestRiskManager:
    """Tests for risk manager."""
    
    def test_position_size_calculation(self):
        from app.services.trading.trade_executor import RiskManager
        
        shares = RiskManager.calculate_position_size(
            capital=100000,
            risk_per_trade=0.02,
            entry_price=100,
            stop_loss=95
        )
        
        # Risk amount = 100000 * 0.02 = 2000
        # Risk per share = 100 - 95 = 5
        # Position size = 2000 / 5 = 400
        assert shares == 400
    
    def test_stop_loss_calculation(self):
        from app.services.trading.trade_executor import RiskManager
        
        stop_loss = RiskManager.calculate_stop_loss(
            entry_price=100,
            stop_loss_pct=0.02
        )
        
        assert stop_loss == 98.0
    
    def test_take_profit_calculation(self):
        from app.services.trading.trade_executor import RiskManager
        
        take_profit = RiskManager.calculate_take_profit(
            entry_price=100,
            stop_loss=95,
            risk_reward=2.0
        )
        
        # Risk = 100 - 95 = 5
        # Reward = 5 * 2 = 10
        # Target = 100 + 10 = 110
        assert take_profit == 110.0
