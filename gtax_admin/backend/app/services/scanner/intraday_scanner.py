"""
Intraday Stock Scanner for Indian Market (NSE/BSE).

Specialized scanner for identifying intraday trading opportunities:
- Pre-market gap analysis
- Volume surge detection
- Opening range breakout
- VWAP analysis
- Momentum stocks
- News-driven movers
"""
import asyncio
from datetime import datetime, time as dt_time, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from loguru import logger
import pytz

from app.core.config import settings
from app.services.data.data_fetcher import data_fetcher
from app.services.data.technical_indicators import TechnicalIndicators


class IntradayScanner:
    """
    Intraday scanner for Indian stock market.
    
    Features:
    - Gap up/down detection
    - Volume spike identification
    - Opening Range Breakout (ORB)
    - VWAP crossover signals
    - Momentum ranking
    - Real-time filtering
    """
    
    def __init__(self):
        self.symbols = settings.INTRADAY_SYMBOLS
        self.ist_tz = pytz.timezone('Asia/Kolkata')
        self.market_open = dt_time(9, 15)
        self.market_close = dt_time(15, 30)
        self.square_off_time = dt_time(15, 15)
        self.scan_results: List[Dict[str, Any]] = []
        self.orb_levels: Dict[str, Dict[str, float]] = {}  # {symbol: {high, low, range}}
        
        # Intraday filters
        self.min_volume_ratio = 1.5  # Minimum volume vs 20-day average
        self.min_price = 100  # Minimum stock price in INR
        self.max_price = 5000  # Maximum stock price in INR
        self.min_gap_percent = 0.5  # Minimum gap % to consider
        self.orb_period_minutes = 15  # First 15 min for ORB
        
    def is_market_open(self) -> bool:
        """Check if Indian market is currently open."""
        now = datetime.now(self.ist_tz)
        current_time = now.time()
        
        # Check if weekday
        if now.weekday() >= 5:
            return False
            
        return self.market_open <= current_time <= self.market_close
    
    def is_trading_allowed(self) -> bool:
        """Check if new trades should be initiated."""
        now = datetime.now(self.ist_tz)
        current_time = now.time()
        
        # No new trades after square off time
        if current_time >= self.square_off_time:
            return False
            
        # No trades in first 5 minutes (market volatility)
        market_open_plus_5 = dt_time(9, 20)
        if current_time < market_open_plus_5:
            return False
            
        return self.is_market_open()
    
    def time_to_square_off(self) -> int:
        """Get minutes remaining until square off."""
        now = datetime.now(self.ist_tz)
        current_time = now.time()
        
        square_off_dt = datetime.combine(now.date(), self.square_off_time)
        current_dt = datetime.combine(now.date(), current_time)
        
        remaining = (square_off_dt - current_dt).total_seconds() / 60
        return max(0, int(remaining))
    
    async def calculate_gap(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Calculate pre-market gap for a stock."""
        try:
            # Get previous day data
            df = await data_fetcher.get_stock_data(symbol, period="5d", interval="1d")
            
            if df is None or len(df) < 2:
                return None
            
            prev_close = df['close'].iloc[-2]
            current_open = df['open'].iloc[-1]
            
            gap_amount = current_open - prev_close
            gap_percent = (gap_amount / prev_close) * 100
            
            gap_type = "UP" if gap_percent > 0 else "DOWN" if gap_percent < 0 else "FLAT"
            
            return {
                'symbol': symbol,
                'prev_close': float(prev_close),
                'current_open': float(current_open),
                'gap_amount': float(gap_amount),
                'gap_percent': round(gap_percent, 2),
                'gap_type': gap_type
            }
            
        except Exception as e:
            logger.error(f"Error calculating gap for {symbol}: {e}")
            return None
    
    async def analyze_volume_surge(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Detect unusual volume activity."""
        try:
            df = await data_fetcher.get_stock_data(symbol, period="1mo", interval="1d")
            
            if df is None or len(df) < 20:
                return None
            
            # Calculate 20-day average volume
            avg_volume = df['volume'].iloc[:-1].tail(20).mean()
            current_volume = df['volume'].iloc[-1]
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            return {
                'symbol': symbol,
                'current_volume': int(current_volume),
                'avg_volume': int(avg_volume),
                'volume_ratio': round(volume_ratio, 2),
                'is_surge': volume_ratio >= self.min_volume_ratio
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume for {symbol}: {e}")
            return None
    
    async def calculate_orb_levels(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Calculate Opening Range Breakout levels.
        Uses first 15-30 minutes high/low as breakout levels.
        """
        try:
            # Get intraday data with 5-min intervals
            df = await data_fetcher.get_stock_data(symbol, period="1d", interval="5m")
            
            if df is None or len(df) < 3:
                return None
            
            # Get first 3 candles (15 minutes) for ORB
            opening_range = df.head(3)
            orb_high = opening_range['high'].max()
            orb_low = opening_range['low'].min()
            orb_range = orb_high - orb_low
            orb_mid = (orb_high + orb_low) / 2
            
            # Current price
            current_price = df['close'].iloc[-1]
            
            # Determine position relative to ORB
            if current_price > orb_high:
                orb_signal = "BREAKOUT_UP"
            elif current_price < orb_low:
                orb_signal = "BREAKOUT_DOWN"
            else:
                orb_signal = "INSIDE_RANGE"
            
            # Store ORB levels
            self.orb_levels[symbol] = {
                'high': float(orb_high),
                'low': float(orb_low),
                'mid': float(orb_mid),
                'range': float(orb_range)
            }
            
            return {
                'symbol': symbol,
                'orb_high': float(orb_high),
                'orb_low': float(orb_low),
                'orb_range': float(orb_range),
                'orb_range_percent': round((orb_range / orb_mid) * 100, 2),
                'current_price': float(current_price),
                'orb_signal': orb_signal
            }
            
        except Exception as e:
            logger.error(f"Error calculating ORB for {symbol}: {e}")
            return None
    
    async def calculate_vwap(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Calculate Volume Weighted Average Price for intraday.
        """
        try:
            df = await data_fetcher.get_stock_data(symbol, period="1d", interval="5m")
            
            if df is None or len(df) < 5:
                return None
            
            # Calculate VWAP
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            
            current_price = df['close'].iloc[-1]
            current_vwap = vwap.iloc[-1]
            
            # Distance from VWAP
            vwap_distance = ((current_price - current_vwap) / current_vwap) * 100
            
            # Determine signal
            if current_price > current_vwap * 1.005:  # 0.5% above VWAP
                vwap_signal = "BULLISH"
            elif current_price < current_vwap * 0.995:  # 0.5% below VWAP
                vwap_signal = "BEARISH"
            else:
                vwap_signal = "NEUTRAL"
            
            return {
                'symbol': symbol,
                'vwap': round(float(current_vwap), 2),
                'current_price': round(float(current_price), 2),
                'vwap_distance_percent': round(vwap_distance, 2),
                'vwap_signal': vwap_signal
            }
            
        except Exception as e:
            logger.error(f"Error calculating VWAP for {symbol}: {e}")
            return None
    
    async def calculate_momentum_score(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Calculate intraday momentum score.
        """
        try:
            # Get intraday data
            df = await data_fetcher.get_stock_data(symbol, period="1d", interval="5m")
            
            if df is None or len(df) < 10:
                return None
            
            # Calculate indicators
            df = TechnicalIndicators.calculate_all(df)
            
            latest = df.iloc[-1]
            
            # Price momentum (rate of change)
            roc_5 = ((df['close'].iloc[-1] - df['close'].iloc[-6]) / df['close'].iloc[-6]) * 100
            roc_10 = ((df['close'].iloc[-1] - df['close'].iloc[-11]) / df['close'].iloc[-11]) * 100 if len(df) > 10 else 0
            
            # RSI for overbought/oversold
            rsi = latest.get('rsi', 50)
            
            # MACD momentum
            macd = latest.get('macd', 0)
            macd_signal = latest.get('macd_signal', 0)
            macd_histogram = macd - macd_signal if macd and macd_signal else 0
            
            # Calculate momentum score (0-100)
            momentum_score = 50  # Start neutral
            
            # ROC contribution (±20)
            momentum_score += min(20, max(-20, roc_5 * 4))
            
            # RSI contribution (±15)
            if rsi > 70:
                momentum_score += 15
            elif rsi < 30:
                momentum_score -= 15
            else:
                momentum_score += (rsi - 50) * 0.3
            
            # MACD contribution (±15)
            if macd_histogram > 0:
                momentum_score += min(15, macd_histogram * 10)
            else:
                momentum_score += max(-15, macd_histogram * 10)
            
            # Normalize to 0-100
            momentum_score = max(0, min(100, momentum_score))
            
            # Determine signal
            if momentum_score >= 65:
                signal = "STRONG_BULLISH"
            elif momentum_score >= 55:
                signal = "BULLISH"
            elif momentum_score <= 35:
                signal = "STRONG_BEARISH"
            elif momentum_score <= 45:
                signal = "BEARISH"
            else:
                signal = "NEUTRAL"
            
            return {
                'symbol': symbol,
                'momentum_score': round(momentum_score, 2),
                'roc_5m': round(roc_5, 2),
                'roc_10m': round(roc_10, 2),
                'rsi': round(rsi, 2) if not pd.isna(rsi) else None,
                'macd_histogram': round(macd_histogram, 4) if macd_histogram else None,
                'momentum_signal': signal
            }
            
        except Exception as e:
            logger.error(f"Error calculating momentum for {symbol}: {e}")
            return None
    
    async def scan_single_stock(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Comprehensive intraday scan for a single stock.
        """
        try:
            # Run all analyses in parallel
            gap_task = self.calculate_gap(symbol)
            volume_task = self.analyze_volume_surge(symbol)
            orb_task = self.calculate_orb_levels(symbol)
            vwap_task = self.calculate_vwap(symbol)
            momentum_task = self.calculate_momentum_score(symbol)
            
            gap, volume, orb, vwap, momentum = await asyncio.gather(
                gap_task, volume_task, orb_task, vwap_task, momentum_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            for result in [gap, volume, orb, vwap, momentum]:
                if isinstance(result, Exception):
                    logger.error(f"Error in intraday scan for {symbol}: {result}")
            
            if not isinstance(gap, dict) or not isinstance(volume, dict):
                return None
            
            # Get current quote
            quote = await data_fetcher.get_realtime_quote(symbol)
            current_price = quote.get('price', 0) if quote else 0
            
            # Filter by price range
            if not (self.min_price <= current_price <= self.max_price):
                return None
            
            # Calculate overall intraday score
            intraday_score = self._calculate_intraday_score(gap, volume, orb, vwap, momentum)
            
            # Determine trading signal
            signal, signal_strength = self._determine_intraday_signal(
                gap, volume, orb, vwap, momentum, intraday_score
            )
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'change_percent': quote.get('change_percent', 0) if quote else 0,
                'gap_data': gap if isinstance(gap, dict) else None,
                'volume_data': volume if isinstance(volume, dict) else None,
                'orb_data': orb if isinstance(orb, dict) else None,
                'vwap_data': vwap if isinstance(vwap, dict) else None,
                'momentum_data': momentum if isinstance(momentum, dict) else None,
                'intraday_score': round(intraday_score, 2),
                'signal': signal,
                'signal_strength': round(signal_strength, 2),
                'time_to_square_off': self.time_to_square_off(),
                'timestamp': datetime.now(self.ist_tz).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")
            return None
    
    def _calculate_intraday_score(
        self,
        gap: Optional[Dict],
        volume: Optional[Dict],
        orb: Optional[Dict],
        vwap: Optional[Dict],
        momentum: Optional[Dict]
    ) -> float:
        """Calculate overall intraday opportunity score."""
        score = 50  # Start neutral
        
        # Gap contribution (±15)
        if isinstance(gap, dict):
            gap_pct = abs(gap.get('gap_percent', 0))
            if gap_pct >= 2:
                score += 15 if gap.get('gap_type') == 'UP' else -10
            elif gap_pct >= 1:
                score += 10 if gap.get('gap_type') == 'UP' else -5
        
        # Volume contribution (±15)
        if isinstance(volume, dict):
            vol_ratio = volume.get('volume_ratio', 1)
            if vol_ratio >= 3:
                score += 15
            elif vol_ratio >= 2:
                score += 10
            elif vol_ratio >= 1.5:
                score += 5
        
        # ORB contribution (±10)
        if isinstance(orb, dict):
            orb_signal = orb.get('orb_signal', '')
            if orb_signal == 'BREAKOUT_UP':
                score += 10
            elif orb_signal == 'BREAKOUT_DOWN':
                score -= 5
        
        # VWAP contribution (±10)
        if isinstance(vwap, dict):
            vwap_signal = vwap.get('vwap_signal', '')
            if vwap_signal == 'BULLISH':
                score += 10
            elif vwap_signal == 'BEARISH':
                score -= 5
        
        # Momentum contribution (based on momentum score)
        if isinstance(momentum, dict):
            mom_score = momentum.get('momentum_score', 50)
            score += (mom_score - 50) * 0.3
        
        return max(0, min(100, score))
    
    def _determine_intraday_signal(
        self,
        gap: Optional[Dict],
        volume: Optional[Dict],
        orb: Optional[Dict],
        vwap: Optional[Dict],
        momentum: Optional[Dict],
        intraday_score: float
    ) -> Tuple[str, float]:
        """Determine trading signal based on all factors."""
        bullish_signals = 0
        bearish_signals = 0
        confidence = 0.5
        
        # Check gap
        if isinstance(gap, dict):
            gap_pct = gap.get('gap_percent', 0)
            if gap_pct >= 1:
                bullish_signals += 1
                confidence += 0.1
            elif gap_pct <= -1:
                bearish_signals += 1
        
        # Check volume
        if isinstance(volume, dict) and volume.get('is_surge', False):
            confidence += 0.05  # Volume confirms any signal
        
        # Check ORB
        if isinstance(orb, dict):
            if orb.get('orb_signal') == 'BREAKOUT_UP':
                bullish_signals += 1
                confidence += 0.1
            elif orb.get('orb_signal') == 'BREAKOUT_DOWN':
                bearish_signals += 1
        
        # Check VWAP
        if isinstance(vwap, dict):
            if vwap.get('vwap_signal') == 'BULLISH':
                bullish_signals += 1
                confidence += 0.05
            elif vwap.get('vwap_signal') == 'BEARISH':
                bearish_signals += 1
        
        # Check Momentum
        if isinstance(momentum, dict):
            mom_signal = momentum.get('momentum_signal', '')
            if 'BULLISH' in mom_signal:
                bullish_signals += 1
                confidence += 0.1 if 'STRONG' in mom_signal else 0.05
            elif 'BEARISH' in mom_signal:
                bearish_signals += 1
        
        # Determine final signal
        min_signals_required = settings.MIN_BULLISH_SIGNALS
        
        if bullish_signals >= min_signals_required and bullish_signals > bearish_signals:
            signal = "BUY"
            confidence = min(0.95, confidence + (intraday_score - 50) * 0.01)
        elif bearish_signals >= min_signals_required and bearish_signals > bullish_signals:
            signal = "SELL"
            confidence = min(0.95, confidence)
        else:
            signal = "HOLD"
            confidence = 0.5
        
        return signal, confidence
    
    async def scan_all(self) -> List[Dict[str, Any]]:
        """
        Scan all configured intraday symbols.
        """
        if not self.is_market_open():
            logger.warning("Indian market is closed. Intraday scan skipped.")
            return []
        
        logger.info(f"🔍 Scanning {len(self.symbols)} symbols for intraday opportunities...")
        
        # Scan all symbols concurrently
        tasks = [self.scan_single_stock(symbol) for symbol in self.symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid results
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result.get('signal') != 'HOLD':
                valid_results.append(result)
        
        # Sort by intraday score
        sorted_results = sorted(
            valid_results,
            key=lambda x: x.get('intraday_score', 0),
            reverse=True
        )
        
        # Get top opportunities
        top_results = sorted_results[:settings.SCANNER_TOP_N]
        
        self.scan_results = top_results
        logger.info(f"✅ Intraday scan complete. Found {len(top_results)} opportunities.")
        
        return top_results
    
    async def get_gap_report(self) -> List[Dict[str, Any]]:
        """Get gap up/down report for all stocks."""
        logger.info("📊 Generating gap report...")
        
        tasks = [self.calculate_gap(symbol) for symbol in self.symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        gap_reports = []
        for result in results:
            if isinstance(result, dict):
                if abs(result.get('gap_percent', 0)) >= self.min_gap_percent:
                    gap_reports.append(result)
        
        # Sort by gap percent (descending)
        gap_reports.sort(key=lambda x: abs(x.get('gap_percent', 0)), reverse=True)
        
        return gap_reports
    
    async def get_volume_surgers(self) -> List[Dict[str, Any]]:
        """Get stocks with unusual volume."""
        logger.info("📈 Finding volume surgers...")
        
        tasks = [self.analyze_volume_surge(symbol) for symbol in self.symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        surgers = []
        for result in results:
            if isinstance(result, dict) and result.get('is_surge', False):
                surgers.append(result)
        
        # Sort by volume ratio (descending)
        surgers.sort(key=lambda x: x.get('volume_ratio', 0), reverse=True)
        
        return surgers


# Singleton instance
intraday_scanner = IntradayScanner()
