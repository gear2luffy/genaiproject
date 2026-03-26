"""
Technical indicators calculation service.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from loguru import logger


class TechnicalIndicators:
    """Service for calculating technical indicators."""
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average."""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average."""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index."""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(
        data: pd.Series, 
        fast_period: int = 12, 
        slow_period: int = 26, 
        signal_period: int = 9
    ) -> Dict[str, pd.Series]:
        """Moving Average Convergence Divergence."""
        ema_fast = data.ewm(span=fast_period, adjust=False).mean()
        ema_slow = data.ewm(span=slow_period, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series, 
        period: int = 20, 
        std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """Bollinger Bands."""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        return {
            'middle': sma,
            'upper': sma + (std * std_dev),
            'lower': sma - (std * std_dev)
        }
    
    @staticmethod
    def calculate_atr(
        high: pd.Series, 
        low: pd.Series, 
        close: pd.Series, 
        period: int = 14
    ) -> pd.Series:
        """Average True Range."""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def calculate_stochastic(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> Dict[str, pd.Series]:
        """Stochastic Oscillator."""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()
        
        return {'k': k, 'd': d}
    
    @staticmethod
    def calculate_adx(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Average Directional Index."""
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.ewm(span=period, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(span=period, adjust=False).mean()
        
        return adx
    
    @staticmethod
    def calculate_volume_profile(
        close: pd.Series,
        volume: pd.Series,
        period: int = 20
    ) -> Dict[str, Any]:
        """Calculate volume profile metrics."""
        avg_volume = volume.rolling(window=period).mean()
        volume_ratio = volume / avg_volume
        
        return {
            'avg_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'is_volume_spike': volume_ratio > 2.0
        }
    
    @classmethod
    def calculate_all(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators for a DataFrame."""
        result = df.copy()
        
        # Moving Averages
        result['sma_20'] = cls.calculate_sma(df['close'], 20)
        result['sma_50'] = cls.calculate_sma(df['close'], 50)
        result['ema_12'] = cls.calculate_ema(df['close'], 12)
        result['ema_26'] = cls.calculate_ema(df['close'], 26)
        
        # RSI
        result['rsi'] = cls.calculate_rsi(df['close'])
        
        # MACD
        macd = cls.calculate_macd(df['close'])
        result['macd'] = macd['macd']
        result['macd_signal'] = macd['signal']
        result['macd_histogram'] = macd['histogram']
        
        # Bollinger Bands
        bb = cls.calculate_bollinger_bands(df['close'])
        result['bollinger_upper'] = bb['upper']
        result['bollinger_middle'] = bb['middle']
        result['bollinger_lower'] = bb['lower']
        
        # ATR
        result['atr'] = cls.calculate_atr(df['high'], df['low'], df['close'])
        
        # Stochastic
        stoch = cls.calculate_stochastic(df['high'], df['low'], df['close'])
        result['stoch_k'] = stoch['k']
        result['stoch_d'] = stoch['d']
        
        # ADX
        result['adx'] = cls.calculate_adx(df['high'], df['low'], df['close'])
        
        # Volume analysis
        if 'volume' in df.columns:
            vol_profile = cls.calculate_volume_profile(df['close'], df['volume'])
            result['avg_volume'] = vol_profile['avg_volume']
            result['volume_ratio'] = vol_profile['volume_ratio']
        
        return result
    
    @classmethod
    def get_technical_score(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate overall technical score from indicators.
        
        Returns a score from -1 (very bearish) to 1 (very bullish).
        """
        if df.empty or len(df) < 50:
            return {'score': 0, 'signals': [], 'confidence': 0}
        
        signals = []
        scores = []
        
        latest = df.iloc[-1]
        
        # RSI Analysis
        rsi = latest.get('rsi')
        if pd.notna(rsi):
            if rsi < 30:
                signals.append(('RSI', 'OVERSOLD', 0.7))
                scores.append(0.7)
            elif rsi > 70:
                signals.append(('RSI', 'OVERBOUGHT', -0.7))
                scores.append(-0.7)
            elif rsi < 50:
                signals.append(('RSI', 'BEARISH', -0.2))
                scores.append(-0.2)
            else:
                signals.append(('RSI', 'BULLISH', 0.2))
                scores.append(0.2)
        
        # MACD Analysis
        macd = latest.get('macd')
        macd_signal = latest.get('macd_signal')
        if pd.notna(macd) and pd.notna(macd_signal):
            if macd > macd_signal:
                signals.append(('MACD', 'BULLISH_CROSSOVER', 0.6))
                scores.append(0.6)
            else:
                signals.append(('MACD', 'BEARISH_CROSSOVER', -0.6))
                scores.append(-0.6)
        
        # Moving Average Analysis
        close = latest.get('close')
        sma_20 = latest.get('sma_20')
        sma_50 = latest.get('sma_50')
        
        if pd.notna(close) and pd.notna(sma_20):
            if close > sma_20:
                signals.append(('SMA20', 'ABOVE', 0.4))
                scores.append(0.4)
            else:
                signals.append(('SMA20', 'BELOW', -0.4))
                scores.append(-0.4)
        
        if pd.notna(sma_20) and pd.notna(sma_50):
            if sma_20 > sma_50:
                signals.append(('SMA_CROSS', 'GOLDEN', 0.5))
                scores.append(0.5)
            else:
                signals.append(('SMA_CROSS', 'DEATH', -0.5))
                scores.append(-0.5)
        
        # Bollinger Bands Analysis
        bb_upper = latest.get('bollinger_upper')
        bb_lower = latest.get('bollinger_lower')
        
        if pd.notna(close) and pd.notna(bb_upper) and pd.notna(bb_lower):
            if close >= bb_upper:
                signals.append(('BOLLINGER', 'OVERBOUGHT', -0.5))
                scores.append(-0.5)
            elif close <= bb_lower:
                signals.append(('BOLLINGER', 'OVERSOLD', 0.5))
                scores.append(0.5)
        
        # ADX Trend Strength
        adx = latest.get('adx')
        if pd.notna(adx):
            if adx > 25:
                signals.append(('ADX', 'STRONG_TREND', 0.3))
            else:
                signals.append(('ADX', 'WEAK_TREND', 0.0))
        
        # Calculate final score
        if scores:
            final_score = np.mean(scores)
            confidence = min(abs(final_score) + 0.3, 1.0)
        else:
            final_score = 0
            confidence = 0
        
        return {
            'score': round(final_score, 3),
            'signals': signals,
            'confidence': round(confidence, 3)
        }


# Singleton instance
technical_indicators = TechnicalIndicators()
