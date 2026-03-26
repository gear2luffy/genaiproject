"""
Support and Resistance Level Calculator for Indian Stocks.

Advanced support/resistance detection using multiple methods:
- Pivot Points (Standard, Fibonacci, Camarilla)
- Historical highs and lows
- Volume Profile Support/Resistance
- Moving Average based levels
- Fibonacci Retracement
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from scipy.signal import argrelextrema
from loguru import logger


class SupportResistanceCalculator:
    """
    Multi-method support and resistance level calculator.
    """
    
    def __init__(self):
        self.lookback_period = 50
        self.cluster_tolerance = 0.015  # 1.5% tolerance for clustering
        
    def calculate_all_levels(
        self, 
        df: pd.DataFrame,
        current_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate support/resistance levels using all methods.
        """
        if df is None or len(df) < 20:
            return {
                'support_levels': [],
                'resistance_levels': [],
                'pivot_levels': {},
                'fibonacci_levels': {},
                'nearest_support': None,
                'nearest_resistance': None
            }
        
        # Get current price
        current_price = current_price or float(df['close'].iloc[-1])
        
        # Calculate using different methods
        historical_levels = self._calculate_historical_levels(df)
        pivot_levels = self._calculate_pivot_points(df)
        fib_levels = self._calculate_fibonacci_levels(df)
        ma_levels = self._calculate_ma_levels(df)
        
        # Combine all levels
        all_support = []
        all_resistance = []
        
        # Add historical levels
        all_support.extend(historical_levels.get('support', []))
        all_resistance.extend(historical_levels.get('resistance', []))
        
        # Add pivot levels
        for level in ['s1', 's2', 's3']:
            if pivot_levels.get(level):
                all_support.append(pivot_levels[level])
        for level in ['r1', 'r2', 'r3']:
            if pivot_levels.get(level):
                all_resistance.append(pivot_levels[level])
        
        # Add Fibonacci levels
        for label, level in fib_levels.items():
            if level < current_price:
                all_support.append(level)
            else:
                all_resistance.append(level)
        
        # Add MA levels
        for ma_level in ma_levels:
            if ma_level < current_price:
                all_support.append(ma_level)
            else:
                all_resistance.append(ma_level)
        
        # Cluster similar levels
        support_clusters = self._cluster_levels(
            [l for l in all_support if l < current_price]
        )
        resistance_clusters = self._cluster_levels(
            [l for l in all_resistance if l > current_price]
        )
        
        # Sort and get nearest
        support_clusters.sort(reverse=True)  # Highest support first (nearest)
        resistance_clusters.sort()  # Lowest resistance first (nearest)
        
        return {
            'current_price': current_price,
            'support_levels': support_clusters[:5],  # Top 5 supports
            'resistance_levels': resistance_clusters[:5],  # Top 5 resistances
            'pivot_levels': pivot_levels,
            'fibonacci_levels': fib_levels,
            'ma_levels': ma_levels,
            'nearest_support': support_clusters[0] if support_clusters else None,
            'nearest_resistance': resistance_clusters[0] if resistance_clusters else None,
            'support_distance_percent': round(
                ((current_price - support_clusters[0]) / current_price) * 100, 2
            ) if support_clusters else None,
            'resistance_distance_percent': round(
                ((resistance_clusters[0] - current_price) / current_price) * 100, 2
            ) if resistance_clusters else None
        }
    
    def _calculate_historical_levels(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """Calculate support/resistance from historical highs/lows."""
        support = []
        resistance = []
        
        # Find local extrema
        high_idx = argrelextrema(df['high'].values, np.greater, order=5)[0]
        low_idx = argrelextrema(df['low'].values, np.less, order=5)[0]
        
        # Get recent highs and lows
        for idx in high_idx[-10:]:
            resistance.append(float(df['high'].iloc[idx]))
        
        for idx in low_idx[-10:]:
            support.append(float(df['low'].iloc[idx]))
        
        # Add 52-week high/low if available
        if len(df) >= 252:
            resistance.append(float(df['high'].iloc[-252:].max()))
            support.append(float(df['low'].iloc[-252:].min()))
        else:
            resistance.append(float(df['high'].max()))
            support.append(float(df['low'].min()))
        
        return {'support': support, 'resistance': resistance}
    
    def _calculate_pivot_points(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Standard Pivot Points.
        PP = (H + L + C) / 3
        """
        # Use previous day/candle for pivot calculation
        prev_high = float(df['high'].iloc[-2])
        prev_low = float(df['low'].iloc[-2])
        prev_close = float(df['close'].iloc[-2])
        
        # Standard Pivot Points
        pp = (prev_high + prev_low + prev_close) / 3
        
        s1 = (2 * pp) - prev_high
        s2 = pp - (prev_high - prev_low)
        s3 = prev_low - 2 * (prev_high - pp)
        
        r1 = (2 * pp) - prev_low
        r2 = pp + (prev_high - prev_low)
        r3 = prev_high + 2 * (pp - prev_low)
        
        return {
            'pp': round(pp, 2),
            's1': round(s1, 2),
            's2': round(s2, 2),
            's3': round(s3, 2),
            'r1': round(r1, 2),
            'r2': round(r2, 2),
            'r3': round(r3, 2)
        }
    
    def _calculate_fibonacci_levels(
        self, 
        df: pd.DataFrame,
        lookback: int = 50
    ) -> Dict[str, float]:
        """
        Calculate Fibonacci Retracement levels.
        """
        lookback = min(lookback, len(df) - 1)
        
        high = df['high'].iloc[-lookback:].max()
        low = df['low'].iloc[-lookback:].min()
        diff = high - low
        
        # Standard Fibonacci levels
        fib_levels = {
            'level_0': round(high, 2),           # 0%
            'level_236': round(high - (diff * 0.236), 2),  # 23.6%
            'level_382': round(high - (diff * 0.382), 2),  # 38.2%
            'level_500': round(high - (diff * 0.5), 2),    # 50%
            'level_618': round(high - (diff * 0.618), 2),  # 61.8%
            'level_786': round(high - (diff * 0.786), 2),  # 78.6%
            'level_1000': round(low, 2),          # 100%
            # Extensions
            'level_1272': round(low - (diff * 0.272), 2),  # 127.2%
            'level_1618': round(low - (diff * 0.618), 2),  # 161.8%
        }
        
        return fib_levels
    
    def _calculate_ma_levels(self, df: pd.DataFrame) -> List[float]:
        """Calculate Moving Average based support/resistance."""
        ma_levels = []
        
        # Key moving averages
        ma_periods = [20, 50, 100, 200]
        
        for period in ma_periods:
            if len(df) >= period:
                ma = df['close'].rolling(window=period).mean().iloc[-1]
                if not pd.isna(ma):
                    ma_levels.append(round(float(ma), 2))
        
        return ma_levels
    
    def _cluster_levels(self, levels: List[float]) -> List[float]:
        """Cluster similar price levels together."""
        if not levels:
            return []
        
        sorted_levels = sorted(levels)
        clusters = [[sorted_levels[0]]]
        
        for level in sorted_levels[1:]:
            # Check if level is within tolerance of current cluster mean
            if abs(level - np.mean(clusters[-1])) / np.mean(clusters[-1]) < self.cluster_tolerance:
                clusters[-1].append(level)
            else:
                clusters.append([level])
        
        # Return mean of each cluster, weighted by count
        result = []
        for cluster in clusters:
            if len(cluster) >= 1:
                # More touches = stronger level
                strength = len(cluster)
                mean_level = round(np.mean(cluster), 2)
                result.append(mean_level)
        
        return result
    
    def get_trading_signal(
        self,
        current_price: float,
        support_levels: List[float],
        resistance_levels: List[float]
    ) -> Dict[str, Any]:
        """
        Generate trading signal based on support/resistance proximity.
        """
        if not support_levels or not resistance_levels:
            return {
                'signal': 'HOLD',
                'confidence': 0.3,
                'reason': 'Insufficient support/resistance data'
            }
        
        nearest_support = support_levels[0] if support_levels else None
        nearest_resistance = resistance_levels[0] if resistance_levels else None
        
        # Calculate distances
        support_distance = ((current_price - nearest_support) / current_price * 100) if nearest_support else 10
        resistance_distance = ((nearest_resistance - current_price) / current_price * 100) if nearest_resistance else 10
        
        # Risk/Reward ratio
        risk_reward = resistance_distance / support_distance if support_distance > 0 else 0
        
        # Generate signal
        if support_distance < 1.0:  # Very close to support
            signal = 'BUY'
            confidence = 0.7 + min(0.2, risk_reward * 0.1)
            reason = f'Price near support ({support_distance:.2f}% above). R:R = {risk_reward:.2f}'
        elif resistance_distance < 1.0:  # Very close to resistance
            signal = 'SELL'
            confidence = 0.6
            reason = f'Price near resistance ({resistance_distance:.2f}% below)'
        elif risk_reward >= 2.0 and support_distance < 3.0:  # Good Risk/Reward
            signal = 'BUY'
            confidence = 0.6 + min(0.2, (risk_reward - 2) * 0.05)
            reason = f'Favorable R:R = {risk_reward:.2f}'
        else:
            signal = 'HOLD'
            confidence = 0.5
            reason = f'No clear S/R signal. Support: {support_distance:.2f}%, Resistance: {resistance_distance:.2f}%'
        
        return {
            'signal': signal,
            'confidence': round(min(0.95, confidence), 2),
            'reason': reason,
            'risk_reward_ratio': round(risk_reward, 2),
            'support_distance_percent': round(support_distance, 2),
            'resistance_distance_percent': round(resistance_distance, 2),
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'stop_loss_suggestion': nearest_support * 0.995 if nearest_support else None,  # 0.5% below support
            'target_price_suggestion': nearest_resistance * 0.995 if nearest_resistance else None  # Just below resistance
        }


class CamarillaPivots:
    """
    Calculate Camarilla Pivot Points (popular for intraday trading).
    """
    
    @staticmethod
    def calculate(prev_high: float, prev_low: float, prev_close: float) -> Dict[str, float]:
        """
        Calculate Camarilla pivot points.
        Good for intraday range trading.
        """
        range_val = prev_high - prev_low
        
        # Support levels
        s1 = prev_close - (range_val * 1.1 / 12)
        s2 = prev_close - (range_val * 1.1 / 6)
        s3 = prev_close - (range_val * 1.1 / 4)
        s4 = prev_close - (range_val * 1.1 / 2)
        
        # Resistance levels
        r1 = prev_close + (range_val * 1.1 / 12)
        r2 = prev_close + (range_val * 1.1 / 6)
        r3 = prev_close + (range_val * 1.1 / 4)
        r4 = prev_close + (range_val * 1.1 / 2)
        
        return {
            's1': round(s1, 2),
            's2': round(s2, 2),
            's3': round(s3, 2),  # Key level - buy if price bounces
            's4': round(s4, 2),  # Strong support
            'r1': round(r1, 2),
            'r2': round(r2, 2),
            'r3': round(r3, 2),  # Key level - sell if price rejects
            'r4': round(r4, 2),  # Strong resistance
        }
    
    @staticmethod
    def get_intraday_signal(
        current_price: float,
        pivots: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Generate intraday trading signal from Camarilla pivots.
        """
        s3, s4 = pivots['s3'], pivots['s4']
        r3, r4 = pivots['r3'], pivots['r4']
        
        if current_price < s4:
            return {
                'signal': 'BUY',
                'strategy': 'CAMARILLA_S4_BREAKOUT',
                'confidence': 0.7,
                'reason': 'Price below S4 - strong buy signal',
                'target': s3,
                'stop_loss': current_price * 0.99
            }
        elif current_price < s3:
            return {
                'signal': 'BUY',
                'strategy': 'CAMARILLA_S3_BOUNCE',
                'confidence': 0.65,
                'reason': 'Price between S3-S4 - bounce trade',
                'target': (pivots['r1'] + pivots['r2']) / 2,
                'stop_loss': s4
            }
        elif current_price > r4:
            return {
                'signal': 'SELL',
                'strategy': 'CAMARILLA_R4_BREAKOUT',
                'confidence': 0.7,
                'reason': 'Price above R4 - strong sell signal',
                'target': r3,
                'stop_loss': current_price * 1.01
            }
        elif current_price > r3:
            return {
                'signal': 'SELL',
                'strategy': 'CAMARILLA_R3_REJECTION',
                'confidence': 0.65,
                'reason': 'Price between R3-R4 - rejection trade',
                'target': (pivots['s1'] + pivots['s2']) / 2,
                'stop_loss': r4
            }
        else:
            return {
                'signal': 'HOLD',
                'strategy': 'CAMARILLA_RANGE',
                'confidence': 0.5,
                'reason': 'Price within S3-R3 range - wait for breakout',
                'target': None,
                'stop_loss': None
            }


# Singleton instance
support_resistance_calculator = SupportResistanceCalculator()
camarilla_pivots = CamarillaPivots()
