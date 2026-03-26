"""
AI Decision Engine Module for Indian Stock Market.

Combines multiple signals to generate trading decisions:
- Technical indicators (RSI, MACD, EMA, etc.)
- Chart patterns (Head & Shoulders, Double Top/Bottom, etc.)
- Support/Resistance levels
- News sentiment (from Indian financial news)

Outputs Buy/Sell/Hold with confidence score and reasoning.
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
from app.services.patterns.support_resistance import support_resistance_calculator, CamarillaPivots
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
    support_resistance_score: float
    price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    reasoning: List[str]
    timestamp: str
    # Enhanced fields for Indian market
    support_levels: List[float] = None
    resistance_levels: List[float] = None
    pivot_levels: Dict[str, float] = None
    news_sentiment: str = None
    dominant_pattern: str = None
    risk_reward_ratio: float = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'signal': self.signal.value,
            'confidence': self.confidence,
            'technical_score': self.technical_score,
            'pattern_score': self.pattern_score,
            'sentiment_score': self.sentiment_score,
            'support_resistance_score': self.support_resistance_score,
            'price': self.price,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'reasoning': self.reasoning,
            'timestamp': self.timestamp,
            'support_levels': self.support_levels,
            'resistance_levels': self.resistance_levels,
            'pivot_levels': self.pivot_levels,
            'news_sentiment': self.news_sentiment,
            'dominant_pattern': self.dominant_pattern,
            'risk_reward_ratio': self.risk_reward_ratio
        }


class AIDecisionEngine:
    """
    AI-powered trading decision engine for Indian stocks.
    
    Combines multiple analysis components with configurable weights
    to generate trading signals with high confidence.
    """
    
    def __init__(
        self,
        technical_weight: float = None,
        pattern_weight: float = None,
        sentiment_weight: float = None,
        support_resistance_weight: float = None,
        confidence_threshold: float = None
    ):
        self.technical_weight = technical_weight or settings.AI_TECHNICAL_WEIGHT
        self.pattern_weight = pattern_weight or settings.AI_PATTERN_WEIGHT
        self.sentiment_weight = sentiment_weight or settings.AI_SENTIMENT_WEIGHT
        self.support_resistance_weight = support_resistance_weight or settings.AI_SUPPORT_RESISTANCE_WEIGHT
        self.confidence_threshold = confidence_threshold or settings.AI_CONFIDENCE_THRESHOLD
        
        # Normalize weights
        total = (self.technical_weight + self.pattern_weight + 
                 self.sentiment_weight + self.support_resistance_weight)
        self.technical_weight /= total
        self.pattern_weight /= total
        self.sentiment_weight /= total
        self.support_resistance_weight /= total
    
    async def generate_signal(
        self, 
        symbol: str,
        include_sentiment: bool = True,
        is_intraday: bool = False
    ) -> TradingSignal:
        """
        Generate comprehensive trading signal for an Indian stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            include_sentiment: Whether to include news sentiment analysis
            is_intraday: If True, use intraday parameters (tighter stops)
        
        Returns:
            TradingSignal with recommendation and complete analysis
        """
        logger.info(f"🧠 Generating signal for {symbol} (intraday={is_intraday})")
        reasoning = []
        
        # 1. Fetch and analyze technical indicators
        technical_score, technical_reasons = await self._analyze_technical(symbol, is_intraday)
        reasoning.extend(technical_reasons)
        
        # 2. Detect and analyze chart patterns
        pattern_score, pattern_reasons, dominant_pattern = await self._analyze_patterns(symbol)
        reasoning.extend(pattern_reasons)
        
        # 3. Analyze support/resistance levels
        sr_score, sr_reasons, sr_data = await self._analyze_support_resistance(symbol)
        reasoning.extend(sr_reasons)
        
        # 4. Analyze news sentiment (if enabled)
        if include_sentiment:
            sentiment_score, sentiment_reasons, news_sentiment = await self._analyze_sentiment(symbol)
            reasoning.extend(sentiment_reasons)
        else:
            sentiment_score = 0
            news_sentiment = 'NEUTRAL'
            # Adjust weights when sentiment is excluded
            total_non_sentiment = self.technical_weight + self.pattern_weight + self.support_resistance_weight
            self.technical_weight = 0.40
            self.pattern_weight = 0.30
            self.support_resistance_weight = 0.30
            self.sentiment_weight = 0
        
        # 5. Calculate combined score with all factors
        combined_score = (
            technical_score * self.technical_weight +
            pattern_score * self.pattern_weight +
            sentiment_score * self.sentiment_weight +
            sr_score * self.support_resistance_weight
        )
        
        # 6. Count bullish/bearish signals
        bullish_signals = 0
        bearish_signals = 0
        
        if technical_score > 0.3: bullish_signals += 1
        elif technical_score < -0.3: bearish_signals += 1
        
        if pattern_score > 0.3: bullish_signals += 1
        elif pattern_score < -0.3: bearish_signals += 1
        
        if sentiment_score > 0.3: bullish_signals += 1
        elif sentiment_score < -0.3: bearish_signals += 1
        
        if sr_score > 0.3: bullish_signals += 1
        elif sr_score < -0.3: bearish_signals += 1
        
        # 7. Determine signal and confidence with consensus requirement
        signal, confidence = self._determine_signal_with_consensus(
            combined_score, bullish_signals, bearish_signals
        )
        
        # 8. Get current price and calculate smart targets
        quote = await data_fetcher.get_realtime_quote(symbol)
        current_price = quote.get('price', 0) if quote else 0
        
        target_price, stop_loss, risk_reward = self._calculate_smart_targets(
            current_price, signal, combined_score, sr_data, is_intraday
        )
        
        # Add final reasoning summary
        reasoning.append(
            f"📊 Final: Combined score {combined_score:.3f}, "
            f"Bullish signals: {bullish_signals}, Bearish signals: {bearish_signals}"
        )
        reasoning.append(
            f"✅ Signal: {signal.value} with {confidence:.1%} confidence"
        )
        
        return TradingSignal(
            symbol=symbol,
            signal=signal,
            confidence=round(confidence, 4),
            technical_score=round(technical_score, 4),
            pattern_score=round(pattern_score, 4),
            sentiment_score=round(sentiment_score, 4),
            support_resistance_score=round(sr_score, 4),
            price=current_price,
            target_price=round(target_price, 2) if target_price else None,
            stop_loss=round(stop_loss, 2) if stop_loss else None,
            reasoning=reasoning,
            timestamp=datetime.now().isoformat(),
            support_levels=sr_data.get('support_levels', []),
            resistance_levels=sr_data.get('resistance_levels', []),
            pivot_levels=sr_data.get('pivot_levels'),
            news_sentiment=news_sentiment,
            dominant_pattern=dominant_pattern,
            risk_reward_ratio=round(risk_reward, 2) if risk_reward else None
        )
    
    async def _analyze_technical(
        self, 
        symbol: str,
        is_intraday: bool = False
    ) -> Tuple[float, List[str]]:
        """Analyze technical indicators with emphasis on key signals."""
        reasoning = []
        
        try:
            # Use shorter timeframe for intraday
            period = "5d" if is_intraday else "1mo"
            interval = "5m" if is_intraday else "1h"
            
            df = await data_fetcher.get_stock_data(symbol, period=period, interval=interval)
            
            if df is None or df.empty or len(df) < 20:
                reasoning.append("📈 Technical: Insufficient data")
                return 0, reasoning
            
            df = TechnicalIndicators.calculate_all(df)
            technical = TechnicalIndicators.get_technical_score(df)
            
            score = technical['score']
            latest = df.iloc[-1]
            
            # Key indicator readings
            rsi = latest.get('rsi', 50)
            macd = latest.get('macd', 0)
            macd_signal = latest.get('macd_signal', 0)
            
            # RSI analysis
            if not np.isnan(rsi):
                if rsi < 30:
                    reasoning.append(f"📈 Technical: RSI oversold ({rsi:.1f})")
                elif rsi > 70:
                    reasoning.append(f"📈 Technical: RSI overbought ({rsi:.1f})")
                else:
                    reasoning.append(f"📈 Technical: RSI neutral ({rsi:.1f})")
            
            # MACD analysis
            if not np.isnan(macd) and not np.isnan(macd_signal):
                if macd > macd_signal:
                    reasoning.append(f"📈 Technical: MACD bullish crossover")
                else:
                    reasoning.append(f"📈 Technical: MACD bearish")
            
            # Add top indicator signals
            for indicator, signal_type, weight in technical['signals'][:2]:
                reasoning.append(f"📈 Technical: {indicator} → {signal_type}")
            
            return score, reasoning
            
        except Exception as e:
            logger.error(f"Technical analysis error for {symbol}: {e}")
            reasoning.append(f"📈 Technical: Analysis error - {str(e)[:50]}")
            return 0, reasoning
    
    async def _analyze_patterns(
        self, 
        symbol: str
    ) -> Tuple[float, List[str], Optional[str]]:
        """Analyze chart patterns and return score, reasoning, and dominant pattern."""
        reasoning = []
        dominant_pattern = None
        
        try:
            df = await data_fetcher.get_stock_data(symbol, period="3mo", interval="1d")
            
            if df is None or df.empty or len(df) < 30:
                reasoning.append("📊 Patterns: Insufficient data")
                return 0, reasoning, None
            
            patterns = pattern_detector.detect_all_patterns(df)
            pattern_score = pattern_detector.get_pattern_score(patterns)
            
            score = pattern_score['score']
            
            if pattern_score.get('dominant_pattern'):
                dominant_pattern = pattern_score['dominant_pattern']
                reasoning.append(
                    f"📊 Patterns: {dominant_pattern} "
                    f"({pattern_score['dominant_direction']})"
                )
            
            if patterns:
                top_pattern = patterns[0]
                reasoning.append(
                    f"📊 Patterns: {top_pattern['pattern_type']} "
                    f"confidence {top_pattern['confidence']:.1%}"
                )
                
                # Check for specific pattern implications
                if top_pattern['pattern_type'] in ['BREAKOUT_UP', 'INVERSE_HEAD_AND_SHOULDERS', 'DOUBLE_BOTTOM']:
                    reasoning.append(f"📊 Patterns: Bullish setup confirmed")
                elif top_pattern['pattern_type'] in ['BREAKOUT_DOWN', 'HEAD_AND_SHOULDERS', 'DOUBLE_TOP']:
                    reasoning.append(f"📊 Patterns: Bearish setup confirmed")
            else:
                reasoning.append("📊 Patterns: No significant patterns detected")
            
            return score, reasoning, dominant_pattern
            
        except Exception as e:
            logger.error(f"Pattern analysis error for {symbol}: {e}")
            reasoning.append("📊 Patterns: Analysis error")
            return 0, reasoning, None
    
    async def _analyze_support_resistance(
        self, 
        symbol: str
    ) -> Tuple[float, List[str], Dict[str, Any]]:
        """Analyze support/resistance levels."""
        reasoning = []
        sr_data = {}
        
        try:
            df = await data_fetcher.get_stock_data(symbol, period="3mo", interval="1d")
            
            if df is None or df.empty:
                reasoning.append("🎯 S/R: Insufficient data")
                return 0, reasoning, sr_data
            
            # Calculate all levels
            levels = support_resistance_calculator.calculate_all_levels(df)
            sr_data = levels
            
            current_price = levels.get('current_price', 0)
            
            # Get trading signal from S/R
            sr_signal = support_resistance_calculator.get_trading_signal(
                current_price,
                levels.get('support_levels', []),
                levels.get('resistance_levels', [])
            )
            
            # Convert signal to score (-1 to 1)
            if sr_signal['signal'] == 'BUY':
                score = sr_signal['confidence']
            elif sr_signal['signal'] == 'SELL':
                score = -sr_signal['confidence']
            else:
                score = 0
            
            # Add reasoning
            if levels.get('nearest_support'):
                reasoning.append(
                    f"🎯 S/R: Support at ₹{levels['nearest_support']:.2f} "
                    f"({levels.get('support_distance_percent', 0):.1f}% below)"
                )
            
            if levels.get('nearest_resistance'):
                reasoning.append(
                    f"🎯 S/R: Resistance at ₹{levels['nearest_resistance']:.2f} "
                    f"({levels.get('resistance_distance_percent', 0):.1f}% above)"
                )
            
            if sr_signal.get('risk_reward_ratio'):
                reasoning.append(
                    f"🎯 S/R: Risk/Reward = {sr_signal['risk_reward_ratio']:.2f}"
                )
            
            reasoning.append(f"🎯 S/R: {sr_signal['reason']}")
            
            return score, reasoning, sr_data
            
        except Exception as e:
            logger.error(f"S/R analysis error for {symbol}: {e}")
            reasoning.append("🎯 S/R: Analysis error")
            return 0, reasoning, {}
    
    async def _analyze_sentiment(
        self, 
        symbol: str
    ) -> Tuple[float, List[str], str]:
        """Analyze news sentiment for Indian stocks."""
        reasoning = []
        news_sentiment = 'NEUTRAL'
        
        try:
            sentiment = await news_sentiment_engine.get_sentiment_for_symbol(symbol)
            
            score = sentiment['score']
            news_sentiment = sentiment['sentiment']
            
            reasoning.append(
                f"📰 Sentiment: {sentiment['sentiment']} "
                f"(score: {score:.3f}, {sentiment['news_count']} articles)"
            )
            
            # Trading signal from sentiment
            if sentiment.get('trading_signal'):
                reasoning.append(
                    f"📰 Sentiment: Trading signal → {sentiment['trading_signal']} "
                    f"({sentiment.get('signal_strength', 'MODERATE')})"
                )
            
            if sentiment['positive_count'] > sentiment['negative_count']:
                reasoning.append(
                    f"📰 Sentiment: Positive news dominates "
                    f"({sentiment['positive_count']} vs {sentiment['negative_count']})"
                )
            elif sentiment['negative_count'] > sentiment['positive_count']:
                reasoning.append(
                    f"📰 Sentiment: Negative news dominates "
                    f"({sentiment['negative_count']} vs {sentiment['positive_count']})"
                )
            
            return score, reasoning, news_sentiment
            
        except Exception as e:
            logger.error(f"Sentiment analysis error for {symbol}: {e}")
            reasoning.append("📰 Sentiment: Analysis error")
            return 0, reasoning, 'NEUTRAL'
    
    def _determine_signal_with_consensus(
        self, 
        combined_score: float,
        bullish_signals: int,
        bearish_signals: int
    ) -> Tuple[SignalType, float]:
        """
        Determine trading signal requiring consensus from multiple factors.
        """
        abs_score = abs(combined_score)
        min_signals = settings.MIN_BULLISH_SIGNALS
        
        # Calculate base confidence
        confidence = min(0.95, 0.3 + abs_score * 0.7)
        
        # Determine signal with consensus requirement
        if combined_score > 0.15 and bullish_signals >= min_signals:
            signal = SignalType.BUY
            # Boost confidence if strong consensus
            if bullish_signals == 4:
                confidence = min(0.95, confidence + 0.15)
            elif bullish_signals == 3:
                confidence = min(0.90, confidence + 0.10)
        elif combined_score < -0.15 and bearish_signals >= min_signals:
            signal = SignalType.SELL
            if bearish_signals == 4:
                confidence = min(0.95, confidence + 0.15)
            elif bearish_signals == 3:
                confidence = min(0.90, confidence + 0.10)
        else:
            signal = SignalType.HOLD
            confidence = max(0.3, confidence - 0.2)
        
        # Apply confidence threshold
        if confidence < self.confidence_threshold:
            signal = SignalType.HOLD
        
        return signal, confidence
    
    def _calculate_smart_targets(
        self, 
        current_price: float,
        signal: SignalType,
        score: float,
        sr_data: Dict[str, Any],
        is_intraday: bool = False
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate smart targets using support/resistance levels.
        """
        if current_price <= 0 or signal == SignalType.HOLD:
            return None, None, None
        
        # Get S/R levels
        support_levels = sr_data.get('support_levels', [])
        resistance_levels = sr_data.get('resistance_levels', [])
        
        # Use intraday or positional parameters
        if is_intraday:
            default_sl = settings.INTRADAY_STOP_LOSS
            default_tp = settings.INTRADAY_TAKE_PROFIT
        else:
            default_sl = settings.DEFAULT_STOP_LOSS
            default_tp = settings.DEFAULT_TAKE_PROFIT
        
        if signal == SignalType.BUY:
            # Target: nearest resistance or default take profit
            if resistance_levels:
                target_price = resistance_levels[0] * 0.995  # Just below resistance
            else:
                target_price = current_price * (1 + default_tp)
            
            # Stop loss: below nearest support or default
            if support_levels:
                stop_loss = support_levels[0] * 0.995  # Just below support
            else:
                stop_loss = current_price * (1 - default_sl)
        else:  # SELL
            # For shorts or exit signals
            if support_levels:
                target_price = support_levels[0] * 1.005  # Just above support
            else:
                target_price = current_price * (1 - default_tp)
            
            if resistance_levels:
                stop_loss = resistance_levels[0] * 1.005
            else:
                stop_loss = current_price * (1 + default_sl)
        
        # Calculate risk/reward ratio
        if signal == SignalType.BUY:
            potential_gain = target_price - current_price
            potential_loss = current_price - stop_loss
        else:
            potential_gain = current_price - target_price
            potential_loss = stop_loss - current_price
        
        risk_reward = (potential_gain / potential_loss) if potential_loss > 0 else 0
        
        return target_price, stop_loss, risk_reward
    
    async def generate_bulk_signals(
        self, 
        symbols: List[str],
        include_sentiment: bool = True,
        is_intraday: bool = False
    ) -> List[TradingSignal]:
        """Generate signals for multiple symbols."""
        import asyncio
        
        tasks = [
            self.generate_signal(symbol, include_sentiment, is_intraday) 
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
    
    def rank_signals(
        self, 
        signals: List[TradingSignal]
    ) -> List[TradingSignal]:
        """Rank signals by quality (confidence * risk_reward)."""
        def signal_quality(s: TradingSignal) -> float:
            rr = s.risk_reward_ratio or 1.0
            return s.confidence * min(rr, 3.0)  # Cap R:R contribution at 3
        
        return sorted(signals, key=signal_quality, reverse=True)


# Singleton instance
ai_decision_engine = AIDecisionEngine()
