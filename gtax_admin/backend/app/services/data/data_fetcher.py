"""
Data fetching service for market data.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
import yfinance as yf
from loguru import logger

from app.core.config import settings


class DataFetcher:
    """Service for fetching market data from various sources."""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 60  # seconds
    
    async def get_stock_data(
        self, 
        symbol: str, 
        period: str = "1mo",
        interval: str = "1h"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical stock/crypto data.
        
        Args:
            symbol: Stock or crypto symbol (e.g., 'AAPL', 'BTC-USD')
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Check cache
            cache_key = f"{symbol}_{period}_{interval}"
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                if datetime.now().timestamp() - cached['timestamp'] < self.cache_ttl:
                    return cached['data']
            
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            df = await asyncio.to_thread(
                ticker.history, period=period, interval=interval
            )
            
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Standardize column names
            df.columns = [col.lower() for col in df.columns]
            df = df.rename(columns={'stock splits': 'splits'})
            
            # Cache the data
            self.cache[cache_key] = {
                'data': df,
                'timestamp': datetime.now().timestamp()
            }
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    async def get_realtime_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            info = await asyncio.to_thread(lambda: ticker.info)
            
            return {
                'symbol': symbol,
                'price': info.get('regularMarketPrice', info.get('currentPrice')),
                'change': info.get('regularMarketChange'),
                'change_percent': info.get('regularMarketChangePercent'),
                'volume': info.get('regularMarketVolume'),
                'high': info.get('regularMarketDayHigh'),
                'low': info.get('regularMarketDayLow'),
                'open': info.get('regularMarketOpen'),
                'previous_close': info.get('regularMarketPreviousClose'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get quotes for multiple symbols concurrently."""
        tasks = [self.get_realtime_quote(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        quotes = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, dict):
                quotes[symbol] = result
            else:
                logger.error(f"Failed to get quote for {symbol}: {result}")
        
        return quotes
    
    async def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get detailed stock information."""
        try:
            ticker = yf.Ticker(symbol)
            info = await asyncio.to_thread(lambda: ticker.info)
            
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'avg_volume': info.get('averageVolume'),
                'description': info.get('longBusinessSummary', '')[:500]
            }
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            return None


# Singleton instance
data_fetcher = DataFetcher()
