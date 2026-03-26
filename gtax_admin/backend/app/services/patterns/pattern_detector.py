"""
Chart Pattern Detection Module.

Detects various chart patterns:
- Head & Shoulders
- Double Top/Bottom
- Breakouts
- Support/Resistance
- Triangles
- Flags and Pennants
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from scipy.signal import argrelextrema
from loguru import logger


class PatternDetector:
    """
    Detects chart patterns using rule-based algorithms.
    """
    
    def __init__(self):
        self.min_pattern_bars = 10
        self.extrema_order = 5
    
    def detect_all_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect all patterns in the given price data.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            List of detected patterns with details
        """
        if df is None or len(df) < self.min_pattern_bars * 2:
            return []
        
        patterns = []
        
        # Find local extrema
        highs, lows = self._find_extrema(df)
        
        # Detect various patterns
        patterns.extend(self._detect_head_and_shoulders(df, highs, lows))
        patterns.extend(self._detect_double_top_bottom(df, highs, lows))
        patterns.extend(self._detect_support_resistance(df, highs, lows))
        patterns.extend(self._detect_breakout(df))
        patterns.extend(self._detect_triangle(df, highs, lows))
        
        # Sort by confidence
        patterns.sort(key=lambda x: x['confidence'], reverse=True)
        
        return patterns
    
    def _find_extrema(
        self, 
        df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Find local highs and lows."""
        high_idx = argrelextrema(
            df['high'].values, 
            np.greater, 
            order=self.extrema_order
        )[0]
        
        low_idx = argrelextrema(
            df['low'].values, 
            np.less, 
            order=self.extrema_order
        )[0]
        
        return high_idx, low_idx
    
    def _detect_head_and_shoulders(
        self, 
        df: pd.DataFrame,
        high_idx: np.ndarray,
        low_idx: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Detect Head and Shoulders pattern.
        
        Pattern: Three peaks where the middle (head) is highest,
        and two outer peaks (shoulders) are roughly equal.
        """
        patterns = []
        
        if len(high_idx) < 3:
            return patterns
        
        # Look for head and shoulders (bearish)
        for i in range(len(high_idx) - 2):
            left_shoulder_idx = high_idx[i]
            head_idx = high_idx[i + 1]
            right_shoulder_idx = high_idx[i + 2]
            
            left_shoulder = df['high'].iloc[left_shoulder_idx]
            head = df['high'].iloc[head_idx]
            right_shoulder = df['high'].iloc[right_shoulder_idx]
            
            # Head should be higher than both shoulders
            if head > left_shoulder and head > right_shoulder:
                # Shoulders should be roughly equal (within 5%)
                shoulder_diff = abs(left_shoulder - right_shoulder) / max(left_shoulder, right_shoulder)
                
                if shoulder_diff < 0.05:
                    # Calculate neckline
                    neckline_lows = df['low'].iloc[left_shoulder_idx:right_shoulder_idx + 1]
                    neckline = neckline_lows.min()
                    
                    confidence = min(0.9, 0.6 + (0.05 - shoulder_diff) * 6)
                    
                    patterns.append({
                        'pattern_type': 'HEAD_AND_SHOULDERS',
                        'direction': 'BEARISH',
                        'confidence': round(confidence, 3),
                        'start_idx': int(left_shoulder_idx),
                        'end_idx': int(right_shoulder_idx),
                        'start_date': str(df.index[left_shoulder_idx]),
                        'end_date': str(df.index[right_shoulder_idx]),
                        'neckline': float(neckline),
                        'target_price': float(neckline - (head - neckline)),
                        'head_price': float(head),
                        'left_shoulder': float(left_shoulder),
                        'right_shoulder': float(right_shoulder),
                        'description': 'Bearish reversal pattern - potential downward movement'
                    })
        
        # Look for inverse head and shoulders (bullish)
        if len(low_idx) >= 3:
            for i in range(len(low_idx) - 2):
                left_shoulder_idx = low_idx[i]
                head_idx = low_idx[i + 1]
                right_shoulder_idx = low_idx[i + 2]
                
                left_shoulder = df['low'].iloc[left_shoulder_idx]
                head = df['low'].iloc[head_idx]
                right_shoulder = df['low'].iloc[right_shoulder_idx]
                
                # Head should be lower than both shoulders
                if head < left_shoulder and head < right_shoulder:
                    shoulder_diff = abs(left_shoulder - right_shoulder) / max(left_shoulder, right_shoulder)
                    
                    if shoulder_diff < 0.05:
                        neckline_highs = df['high'].iloc[left_shoulder_idx:right_shoulder_idx + 1]
                        neckline = neckline_highs.max()
                        
                        confidence = min(0.9, 0.6 + (0.05 - shoulder_diff) * 6)
                        
                        patterns.append({
                            'pattern_type': 'INVERSE_HEAD_AND_SHOULDERS',
                            'direction': 'BULLISH',
                            'confidence': round(confidence, 3),
                            'start_idx': int(left_shoulder_idx),
                            'end_idx': int(right_shoulder_idx),
                            'start_date': str(df.index[left_shoulder_idx]),
                            'end_date': str(df.index[right_shoulder_idx]),
                            'neckline': float(neckline),
                            'target_price': float(neckline + (neckline - head)),
                            'head_price': float(head),
                            'left_shoulder': float(left_shoulder),
                            'right_shoulder': float(right_shoulder),
                            'description': 'Bullish reversal pattern - potential upward movement'
                        })
        
        return patterns
    
    def _detect_double_top_bottom(
        self, 
        df: pd.DataFrame,
        high_idx: np.ndarray,
        low_idx: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Detect Double Top and Double Bottom patterns.
        """
        patterns = []
        tolerance = 0.03  # 3% tolerance
        
        # Double Top (bearish)
        if len(high_idx) >= 2:
            for i in range(len(high_idx) - 1):
                peak1_idx = high_idx[i]
                peak2_idx = high_idx[i + 1]
                
                peak1 = df['high'].iloc[peak1_idx]
                peak2 = df['high'].iloc[peak2_idx]
                
                # Peaks should be roughly equal
                peak_diff = abs(peak1 - peak2) / max(peak1, peak2)
                
                if peak_diff < tolerance:
                    # Find the trough between peaks
                    trough = df['low'].iloc[peak1_idx:peak2_idx + 1].min()
                    
                    confidence = min(0.85, 0.5 + (tolerance - peak_diff) * 10)
                    
                    patterns.append({
                        'pattern_type': 'DOUBLE_TOP',
                        'direction': 'BEARISH',
                        'confidence': round(confidence, 3),
                        'start_idx': int(peak1_idx),
                        'end_idx': int(peak2_idx),
                        'start_date': str(df.index[peak1_idx]),
                        'end_date': str(df.index[peak2_idx]),
                        'resistance_level': float(max(peak1, peak2)),
                        'support_level': float(trough),
                        'target_price': float(trough - (max(peak1, peak2) - trough)),
                        'description': 'Bearish reversal - two peaks at similar levels'
                    })
        
        # Double Bottom (bullish)
        if len(low_idx) >= 2:
            for i in range(len(low_idx) - 1):
                trough1_idx = low_idx[i]
                trough2_idx = low_idx[i + 1]
                
                trough1 = df['low'].iloc[trough1_idx]
                trough2 = df['low'].iloc[trough2_idx]
                
                trough_diff = abs(trough1 - trough2) / max(trough1, trough2)
                
                if trough_diff < tolerance:
                    peak = df['high'].iloc[trough1_idx:trough2_idx + 1].max()
                    
                    confidence = min(0.85, 0.5 + (tolerance - trough_diff) * 10)
                    
                    patterns.append({
                        'pattern_type': 'DOUBLE_BOTTOM',
                        'direction': 'BULLISH',
                        'confidence': round(confidence, 3),
                        'start_idx': int(trough1_idx),
                        'end_idx': int(trough2_idx),
                        'start_date': str(df.index[trough1_idx]),
                        'end_date': str(df.index[trough2_idx]),
                        'support_level': float(min(trough1, trough2)),
                        'resistance_level': float(peak),
                        'target_price': float(peak + (peak - min(trough1, trough2))),
                        'description': 'Bullish reversal - two troughs at similar levels'
                    })
        
        return patterns
    
    def _detect_support_resistance(
        self, 
        df: pd.DataFrame,
        high_idx: np.ndarray,
        low_idx: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Detect support and resistance levels.
        """
        patterns = []
        
        if len(df) < 20:
            return patterns
        
        current_price = df['close'].iloc[-1]
        
        # Find resistance levels (from recent highs)
        if len(high_idx) > 0:
            recent_highs = df['high'].iloc[high_idx[-5:]] if len(high_idx) >= 5 else df['high'].iloc[high_idx]
            
            # Cluster similar highs
            resistance_levels = self._cluster_levels(recent_highs.values)
            
            for level in resistance_levels:
                if level > current_price:
                    distance = (level - current_price) / current_price
                    confidence = max(0.3, 0.8 - distance * 2)
                    
                    patterns.append({
                        'pattern_type': 'RESISTANCE',
                        'direction': 'NEUTRAL',
                        'confidence': round(confidence, 3),
                        'start_date': str(df.index[0]),
                        'end_date': str(df.index[-1]),
                        'resistance_level': float(level),
                        'current_price': float(current_price),
                        'distance_percent': round(distance * 100, 2),
                        'description': f'Resistance level at {level:.2f}'
                    })
        
        # Find support levels (from recent lows)
        if len(low_idx) > 0:
            recent_lows = df['low'].iloc[low_idx[-5:]] if len(low_idx) >= 5 else df['low'].iloc[low_idx]
            
            support_levels = self._cluster_levels(recent_lows.values)
            
            for level in support_levels:
                if level < current_price:
                    distance = (current_price - level) / current_price
                    confidence = max(0.3, 0.8 - distance * 2)
                    
                    patterns.append({
                        'pattern_type': 'SUPPORT',
                        'direction': 'NEUTRAL',
                        'confidence': round(confidence, 3),
                        'start_date': str(df.index[0]),
                        'end_date': str(df.index[-1]),
                        'support_level': float(level),
                        'current_price': float(current_price),
                        'distance_percent': round(distance * 100, 2),
                        'description': f'Support level at {level:.2f}'
                    })
        
        return patterns
    
    def _cluster_levels(self, levels: np.ndarray, tolerance: float = 0.02) -> List[float]:
        """Cluster similar price levels."""
        if len(levels) == 0:
            return []
        
        sorted_levels = np.sort(levels)
        clusters = [[sorted_levels[0]]]
        
        for level in sorted_levels[1:]:
            if abs(level - np.mean(clusters[-1])) / np.mean(clusters[-1]) < tolerance:
                clusters[-1].append(level)
            else:
                clusters.append([level])
        
        # Return mean of each cluster
        return [np.mean(cluster) for cluster in clusters if len(cluster) >= 2]
    
    def _detect_breakout(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect breakout patterns.
        """
        patterns = []
        
        if len(df) < 20:
            return patterns
        
        # Use last 20 bars for range calculation
        lookback = min(20, len(df) - 1)
        range_high = df['high'].iloc[-lookback:-1].max()
        range_low = df['low'].iloc[-lookback:-1].min()
        
        current_close = df['close'].iloc[-1]
        current_high = df['high'].iloc[-1]
        current_low = df['low'].iloc[-1]
        
        avg_volume = df['volume'].iloc[-lookback:-1].mean() if 'volume' in df.columns else None
        current_volume = df['volume'].iloc[-1] if 'volume' in df.columns else None
        
        # Check for breakout above resistance
        if current_close > range_high:
            breakout_strength = (current_close - range_high) / range_high
            volume_ratio = current_volume / avg_volume if avg_volume and current_volume else 1
            
            confidence = min(0.9, 0.4 + breakout_strength * 5 + (volume_ratio - 1) * 0.1)
            
            patterns.append({
                'pattern_type': 'BREAKOUT_UP',
                'direction': 'BULLISH',
                'confidence': round(max(0.3, confidence), 3),
                'start_date': str(df.index[-lookback]),
                'end_date': str(df.index[-1]),
                'breakout_level': float(range_high),
                'current_price': float(current_close),
                'breakout_strength': round(breakout_strength * 100, 2),
                'volume_ratio': round(volume_ratio, 2) if volume_ratio else None,
                'target_price': float(current_close + (range_high - range_low)),
                'description': 'Bullish breakout above resistance'
            })
        
        # Check for breakdown below support
        if current_close < range_low:
            breakdown_strength = (range_low - current_close) / range_low
            volume_ratio = current_volume / avg_volume if avg_volume and current_volume else 1
            
            confidence = min(0.9, 0.4 + breakdown_strength * 5 + (volume_ratio - 1) * 0.1)
            
            patterns.append({
                'pattern_type': 'BREAKOUT_DOWN',
                'direction': 'BEARISH',
                'confidence': round(max(0.3, confidence), 3),
                'start_date': str(df.index[-lookback]),
                'end_date': str(df.index[-1]),
                'breakout_level': float(range_low),
                'current_price': float(current_close),
                'breakdown_strength': round(breakdown_strength * 100, 2),
                'volume_ratio': round(volume_ratio, 2) if volume_ratio else None,
                'target_price': float(current_close - (range_high - range_low)),
                'description': 'Bearish breakdown below support'
            })
        
        return patterns
    
    def _detect_triangle(
        self, 
        df: pd.DataFrame,
        high_idx: np.ndarray,
        low_idx: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Detect triangle patterns (ascending, descending, symmetric).
        """
        patterns = []
        
        if len(high_idx) < 3 or len(low_idx) < 3:
            return patterns
        
        # Get recent highs and lows
        recent_highs = [(idx, df['high'].iloc[idx]) for idx in high_idx[-4:]]
        recent_lows = [(idx, df['low'].iloc[idx]) for idx in low_idx[-4:]]
        
        if len(recent_highs) < 2 or len(recent_lows) < 2:
            return patterns
        
        # Calculate slopes
        high_slope = (recent_highs[-1][1] - recent_highs[0][1]) / (recent_highs[-1][0] - recent_highs[0][0])
        low_slope = (recent_lows[-1][1] - recent_lows[0][1]) / (recent_lows[-1][0] - recent_lows[0][0])
        
        # Determine triangle type
        current_price = df['close'].iloc[-1]
        
        if high_slope < -0.001 and low_slope > 0.001:
            # Symmetric triangle
            patterns.append({
                'pattern_type': 'SYMMETRIC_TRIANGLE',
                'direction': 'NEUTRAL',
                'confidence': 0.6,
                'start_date': str(df.index[min(recent_highs[0][0], recent_lows[0][0])]),
                'end_date': str(df.index[-1]),
                'current_price': float(current_price),
                'description': 'Symmetric triangle - breakout direction uncertain'
            })
        elif abs(high_slope) < 0.001 and low_slope > 0.001:
            # Ascending triangle (bullish)
            patterns.append({
                'pattern_type': 'ASCENDING_TRIANGLE',
                'direction': 'BULLISH',
                'confidence': 0.65,
                'start_date': str(df.index[min(recent_highs[0][0], recent_lows[0][0])]),
                'end_date': str(df.index[-1]),
                'resistance_level': float(recent_highs[-1][1]),
                'current_price': float(current_price),
                'description': 'Ascending triangle - bullish continuation pattern'
            })
        elif high_slope < -0.001 and abs(low_slope) < 0.001:
            # Descending triangle (bearish)
            patterns.append({
                'pattern_type': 'DESCENDING_TRIANGLE',
                'direction': 'BEARISH',
                'confidence': 0.65,
                'start_date': str(df.index[min(recent_highs[0][0], recent_lows[0][0])]),
                'end_date': str(df.index[-1]),
                'support_level': float(recent_lows[-1][1]),
                'current_price': float(current_price),
                'description': 'Descending triangle - bearish continuation pattern'
            })
        
        return patterns
    
    def get_pattern_score(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate an overall pattern score from detected patterns.
        
        Returns a score from -1 (very bearish) to 1 (very bullish).
        """
        if not patterns:
            return {'score': 0, 'confidence': 0, 'dominant_pattern': None}
        
        bullish_score = 0
        bearish_score = 0
        total_confidence = 0
        
        for pattern in patterns:
            confidence = pattern['confidence']
            total_confidence += confidence
            
            if pattern['direction'] == 'BULLISH':
                bullish_score += confidence
            elif pattern['direction'] == 'BEARISH':
                bearish_score += confidence
        
        if total_confidence == 0:
            return {'score': 0, 'confidence': 0, 'dominant_pattern': None}
        
        # Calculate net score
        net_score = (bullish_score - bearish_score) / total_confidence
        
        # Find dominant pattern
        dominant = max(patterns, key=lambda x: x['confidence'])
        
        return {
            'score': round(net_score, 3),
            'confidence': round(total_confidence / len(patterns), 3),
            'dominant_pattern': dominant['pattern_type'],
            'dominant_direction': dominant['direction'],
            'pattern_count': len(patterns)
        }


# Singleton instance
pattern_detector = PatternDetector()
