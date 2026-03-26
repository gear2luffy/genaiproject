"""
AI Decision Engine Module.

Combines multiple signals to generate trading decisions:
- Technical indicators (RSI, MACD, EMA, etc.)
- Chart patterns
- News sentiment

Outputs Buy/Sell/Hold with confidence score.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from loguru import logger
import numpy as np

from app.core.config import settings
from app.services.data.data_fetcher import data_fetcher
from app.services.data.technical_indicators import TechnicalIndicators
from app.services.patterns.pattern_detector import pattern_detector
from app.services.sentiment.sentiment_engine import news_sentiment_engine


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class TradingSignal:
    """Trading signal with all components."""
    symbol: str
    signal: SignalType
    confidence: float
    technical_score: float
    pattern_score: float
    sentiment_score: float
    price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    reasoning: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'signal': self.signal.value,
            'confidence': self.confidence,
            'technical_score': self.technical_score,
            'pattern_score': self.pattern_score,
            'sentiment_score': self.sentiment_score,
            'price': self.price,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'reasoning': self.reasoning,
            'timestamp': self.timestamp
        }


class AIDecisionEngine:
    """
    AI-powered trading decision engine.
    
    Combines multiple analysis components with configurable weights
    to generate trading signals.
    """
    
    def __init__(
        self,
        technical_weight: float = None,
        pattern_weight: float = None,
        sentiment_weight: float = None,
        confidence_threshold: float = None
    ):
        self.technical_weight = technical_weight or settings.AI_TECHNICAL_WEIGHT
        self.pattern_weight = pattern_weight or settings.AI_PATTERN_WEIGHT
        self.sentiment_weight = sentiment_weight or settings.AI_SENTIMENT_WEIGHT
        self.confidence_threshold = confidence_threshold or settings.AI_CONFIDENCE_THRESHOLD
        
        # Normalize weights
        total = self.technical_weight + self.pattern_weight + self.sentiment_weight
        self.technical_weight /= total
        self.pattern_weight /= total
        self.sentiment_weight /= total
    
    async def generate_signal(
        self, 
        symbol: str,
        include_sentiment: bool = True
    ) -> TradingSignal:
        """
        Generate trading signal for a symbol.
        
        Args:
            symbol: Stock or crypto symbol
            include_sentiment: Whether to include news sentiment analysis
        
        Returns:
            TradingSignal with recommendation and details
        """
        logger.info(f"Generating signal for {symbol}")
        reasoning = []
        
        # 1. Fetch and analyze technical indicators
        technical_score, technical_reasons = await self._analyze_technical(symbol)
        reasoning.extend(technical_reasons)
        
        # 2. Detect and analyze chart patterns
        pattern_score, pattern_reasons = await self._analyze_patterns(symbol)
        reasoning.extend(pattern_reasons)
        
        # 3. Analyze news sentiment (optional)
        if include_sentiment:
            sentiment_score, sentiment_reasons = await self._analyze_sentiment(symbol)
            reasoning.extend(sentiment_reasons)
        else:
            sentiment_score = 0
            # Adjust weights when sentiment is excluded
            self.technical_weight = 0.6
            self.pattern_weight = 0.4
            self.sentiment_weight = 0
        
        # 4. Calculate combined score
        combined_score = (
            technical_score * self.technical_weight +
            pattern_score * self.pattern_weight +
            sentiment_score * self.sentiment_weight
        )
        
        # 5. Determine signal and confidence
        signal, confidence = self._determine_signal(combined_score)
        
        # 6. Get current price and calculate targets
        quote = await data_fetcher.get_realtime_quote(symbol)
        current_price = quote.get('price', 0) if quote else 0
        
        target_price, stop_loss = self._calculate_targets(
            current_price, signal, combined_score
        )
        
        # Add final reasoning
        reasoning.append(
            f"Combined score: {combined_score:.3f} -> {signal.value} with {confidence:.1%} confidence"
        )
        
        return TradingSignal(
            symbol=symbol,
            signal=signal,
            confidence=round(confidence, 4),
            technical_score=round(technical_score, 4),
            pattern_score=round(pattern_score, 4),
            sentiment_score=round(sentiment_score, 4),
            price=current_price,
            target_price=round(target_price, 2) if target_price else None,
            stop_loss=round(stop_loss, 2) if stop_loss else None,
            reasoning=reasoning,
            timestamp=datetime.now().isoformat()
        )
    
    async def _analyze_technical(
        self, 
        symbol: str
    ) -> Tuple[float, List[str]]:
        """Analyze technical indicators."""
        reasoning = []
        
        try:
            df = await data_fetcher.get_stock_data(symbol, period="1mo", interval="1h")
            
            if df is None or df.empty:
                reasoning.append("Technical: Insufficient data")
                return 0, reasoning
            
            df = TechnicalIndicators.calculate_all(df)
            technical = TechnicalIndicators.get_technical_score(df)
            
            score = technical['score']
            
            # Add reasoning for key signals
            for indicator, signal_type, weight in technical['signals'][:3]:
                reasoning.append(f"Technical: {indicator} is {signal_type}")
            
            return score, reasoning
            
        except Exception as e:
            logger.error(f"Technical analysis error for {symbol}: {e}")
            reasoning.append(f"Technical: Analysis error")
            return 0, reasoning
    
    async def _analyze_patterns(
        self, 
        symbol: str
    ) -> Tuple[float, List[str]]:
        """Analyze chart patterns."""
        reasoning = []
        
        try:
            df = await data_fetcher.get_stock_data(symbol, period="3mo", interval="1d")
            
            if df is None or df.empty:
                reasoning.append("Patterns: Insufficient data")
                return 0, reasoning
            
            patterns = pattern_detector.detect_all_patterns(df)
            pattern_score = pattern_detector.get_pattern_score(patterns)
            
            score = pattern_score['score']
            
            if pattern_score.get('dominant_pattern'):
                reasoning.append(
                    f"Patterns: {pattern_score['dominant_pattern']} "
                    f"({pattern_score['dominant_direction']})"
                )
            
            if patterns:
                top_pattern = patterns[0]
                reasoning.append(
                    f"Patterns: Top pattern confidence {top_pattern['confidence']:.1%}"
                )
            else:
                reasoning.append("Patterns: No significant patterns detected")
            
            return score, reasoning
            
        except Exception as e:
            logger.error(f"Pattern analysis error for {symbol}: {e}")
            reasoning.append("Patterns: Analysis error")
            return 0, reasoning
    
    async def _analyze_sentiment(
        self, 
        symbol: str
    ) -> Tuple[float, List[str]]:
        """Analyze news sentiment."""
        reasoning = []
        
        try:
            sentiment = await news_sentiment_engine.get_sentiment_for_symbol(symbol)
            
            score = sentiment['score']
            
            reasoning.append(
                f"Sentiment: {sentiment['sentiment']} "
                f"(score: {score:.3f}, {sentiment['news_count']} articles)"
            )
            
            if sentiment['positive_count'] > sentiment['negative_count']:
                reasoning.append(
                    f"Sentiment: More positive ({sentiment['positive_count']}) "
                    f"than negative ({sentiment['negative_count']}) news"
                )
            elif sentiment['negative_count'] > sentiment['positive_count']:
                reasoning.append(
                    f"Sentiment: More negative ({sentiment['negative_count']}) "
                    f"than positive ({sentiment['positive_count']}) news"
                )
            
            return score, reasoning
            
        except Exception as e:
            logger.error(f"Sentiment analysis error for {symbol}: {e}")
            reasoning.append("Sentiment: Analysis error")
            return 0, reasoning
    
    def _determine_signal(
        self, 
        combined_score: float
    ) -> Tuple[SignalType, float]:
        """Determine trading signal and confidence from combined score."""
        
        # Score ranges: -1 (very bearish) to 1 (very bullish)
        abs_score = abs(combined_score)
        
        # Calculate confidence
        # Higher absolute score = higher confidence
        confidence = min(0.95, 0.3 + abs_score * 0.7)
        
        # Determine signal
        if combined_score > 0.2:
            signal = SignalType.BUY
        elif combined_score < -0.2:
            signal = SignalType.SELL
        else:
            signal = SignalType.HOLD
            confidence = max(0.3, confidence - 0.2)  # Lower confidence for HOLD
        
        # Apply confidence threshold
        if confidence < self.confidence_threshold:
            signal = SignalType.HOLD
        
        return signal, confidence
    
    def _calculate_targets(
        self, 
        current_price: float,
        signal: SignalType,
        score: float
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate target price and stop loss."""
        
        if current_price <= 0 or signal == SignalType.HOLD:
            return None, None
        
        # Use ATR-based targets (simplified)
        # In production, use actual ATR from technical analysis
        volatility_factor = 0.02 + abs(score) * 0.03  # 2-5%
        
        if signal == SignalType.BUY:
            target_price = current_price * (1 + settings.DEFAULT_TAKE_PROFIT)
            stop_loss = current_price * (1 - settings.DEFAULT_STOP_LOSS)
        else:  # SELL
            target_price = current_price * (1 - settings.DEFAULT_TAKE_PROFIT)
            stop_loss = current_price * (1 + settings.DEFAULT_STOP_LOSS)
        
        return target_price, stop_loss
    
    async def generate_bulk_signals(
        self, 
        symbols: List[str],
        include_sentiment: bool = True
    ) -> List[TradingSignal]:
        """Generate signals for multiple symbols."""
        import asyncio
        
        tasks = [
            self.generate_signal(symbol, include_sentiment) 
            for symbol in symbols
        ]
        
        signals = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_signals = []
        for symbol, signal in zip(symbols, signals):
            if isinstance(signal, TradingSignal):
                valid_signals.append(signal)
            else:
                logger.error(f"Signal generation failed for {symbol}: {signal}")
        
        return valid_signals
    
    def get_actionable_signals(
        self, 
        signals: List[TradingSignal]
    ) -> List[TradingSignal]:
        """Filter for actionable BUY/SELL signals above confidence threshold."""
        return [
            s for s in signals 
            if s.signal != SignalType.HOLD 
            and s.confidence >= self.confidence_threshold
        ]


# Singleton instance
ai_decision_engine = AIDecisionEngine()
