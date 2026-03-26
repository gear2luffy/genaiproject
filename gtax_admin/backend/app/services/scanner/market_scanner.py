"""
Market Scanner service for identifying trading opportunities.
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from loguru import logger

from app.core.config import settings
from app.services.data.data_fetcher import data_fetcher
from app.services.data.technical_indicators import TechnicalIndicators


class MarketScanner:
    """
    Scans markets to identify top trading opportunities.
    
    Filters assets based on:
    - Volume spikes
    - Volatility
    - Trend strength
    - Technical indicators
    """
    
    def __init__(self):
        self.symbols = settings.SCANNER_SYMBOLS
        self.scan_interval = settings.SCANNER_INTERVAL
        self.top_n = settings.SCANNER_TOP_N
        self.last_scan_results: List[Dict[str, Any]] = []
        self.is_scanning = False
        self._callbacks = []
    
    def add_callback(self, callback):
        """Add callback for scan results updates."""
        self._callbacks.append(callback)
    
    async def _notify_callbacks(self, results: List[Dict[str, Any]]):
        """Notify all callbacks with scan results."""
        for callback in self._callbacks:
            try:
                await callback(results)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    async def analyze_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a single symbol for trading opportunity.
        
        Returns:
            Analysis results including scores and indicators
        """
        try:
            # Fetch price data
            df = await data_fetcher.get_stock_data(symbol, period="1mo", interval="1h")
            
            if df is None or df.empty or len(df) < 50:
                return None
            
            # Calculate technical indicators
            df = TechnicalIndicators.calculate_all(df)
            
            # Get current quote
            quote = await data_fetcher.get_realtime_quote(symbol)
            
            latest = df.iloc[-1]
            
            # Calculate various scores
            volume_score = self._calculate_volume_score(df)
            volatility_score = self._calculate_volatility_score(df)
            trend_score = self._calculate_trend_score(df)
            technical = TechnicalIndicators.get_technical_score(df)
            
            # Overall opportunity score
            opportunity_score = (
                volume_score * 0.2 +
                volatility_score * 0.2 +
                trend_score * 0.3 +
                abs(technical['score']) * 0.3
            )
            
            return {
                'symbol': symbol,
                'price': quote.get('price') if quote else float(latest['close']),
                'change_percent': quote.get('change_percent', 0) if quote else 0,
                'volume': int(latest.get('volume', 0)),
                'volume_score': round(volume_score, 3),
                'volatility_score': round(volatility_score, 3),
                'trend_score': round(trend_score, 3),
                'technical_score': technical['score'],
                'technical_signals': technical['signals'],
                'opportunity_score': round(opportunity_score, 3),
                'rsi': round(latest.get('rsi', 0), 2) if pd.notna(latest.get('rsi')) else None,
                'macd': round(latest.get('macd', 0), 4) if pd.notna(latest.get('macd')) else None,
                'adx': round(latest.get('adx', 0), 2) if pd.notna(latest.get('adx')) else None,
                'sma_20': round(latest.get('sma_20', 0), 2) if pd.notna(latest.get('sma_20')) else None,
                'sma_50': round(latest.get('sma_50', 0), 2) if pd.notna(latest.get('sma_50')) else None,
                'bollinger_upper': round(latest.get('bollinger_upper', 0), 2) if pd.notna(latest.get('bollinger_upper')) else None,
                'bollinger_lower': round(latest.get('bollinger_lower', 0), 2) if pd.notna(latest.get('bollinger_lower')) else None,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def _calculate_volume_score(self, df: pd.DataFrame) -> float:
        """Calculate volume score (0-1) based on recent volume vs average."""
        if 'volume' not in df.columns or df['volume'].isna().all():
            return 0.5
        
        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        current_volume = df['volume'].iloc[-1]
        
        if pd.isna(avg_volume) or avg_volume == 0:
            return 0.5
        
        ratio = current_volume / avg_volume
        # Normalize: ratio of 2+ = score of 1.0
        score = min(ratio / 2, 1.0)
        return score
    
    def _calculate_volatility_score(self, df: pd.DataFrame) -> float:
        """Calculate volatility score (0-1)."""
        if 'atr' not in df.columns:
            df['atr'] = TechnicalIndicators.calculate_atr(
                df['high'], df['low'], df['close']
            )
        
        atr = df['atr'].iloc[-1]
        close = df['close'].iloc[-1]
        
        if pd.isna(atr) or close == 0:
            return 0.5
        
        # ATR as percentage of price
        atr_pct = (atr / close) * 100
        
        # Normalize: 2-5% ATR is ideal (score of 0.7-1.0)
        if atr_pct < 1:
            score = atr_pct * 0.5
        elif atr_pct < 5:
            score = 0.5 + (atr_pct - 1) * 0.125
        else:
            score = 1.0 - min((atr_pct - 5) * 0.1, 0.3)
        
        return max(0, min(score, 1.0))
    
    def _calculate_trend_score(self, df: pd.DataFrame) -> float:
        """Calculate trend strength score (0-1)."""
        if 'adx' not in df.columns:
            df['adx'] = TechnicalIndicators.calculate_adx(
                df['high'], df['low'], df['close']
            )
        
        adx = df['adx'].iloc[-1]
        
        if pd.isna(adx):
            return 0.5
        
        # ADX > 25 indicates strong trend
        # Normalize to 0-1 score
        score = min(adx / 50, 1.0)
        return score
    
    async def scan_all(self) -> List[Dict[str, Any]]:
        """
        Scan all configured symbols and rank by opportunity.
        
        Returns:
            List of top trading opportunities sorted by score
        """
        logger.info(f"Scanning {len(self.symbols)} symbols...")
        
        # Analyze all symbols concurrently
        tasks = [self.analyze_symbol(symbol) for symbol in self.symbols]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results and sort by opportunity score
        valid_results = [r for r in results if r is not None]
        sorted_results = sorted(
            valid_results, 
            key=lambda x: x['opportunity_score'], 
            reverse=True
        )
        
        # Get top N
        top_results = sorted_results[:self.top_n]
        
        self.last_scan_results = top_results
        logger.info(f"Scan complete. Top {len(top_results)} opportunities identified.")
        
        return top_results
    
    async def start_scanning(self):
        """Start continuous market scanning."""
        self.is_scanning = True
        logger.info("Starting continuous market scanning...")
        
        while self.is_scanning:
            try:
                results = await self.scan_all()
                await self._notify_callbacks(results)
            except Exception as e:
                logger.error(f"Scan error: {e}")
            
            await asyncio.sleep(self.scan_interval)
    
    def stop_scanning(self):
        """Stop continuous market scanning."""
        self.is_scanning = False
        logger.info("Market scanning stopped.")
    
    def get_last_results(self) -> List[Dict[str, Any]]:
        """Get results from the last scan."""
        return self.last_scan_results
    
    async def get_symbol_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get detailed analysis for a specific symbol."""
        return await self.analyze_symbol(symbol)


# Singleton instance
market_scanner = MarketScanner()
