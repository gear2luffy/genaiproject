"""
Chart Pattern Detection API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from app.services.patterns.pattern_detector import pattern_detector
from app.services.data.data_fetcher import data_fetcher


router = APIRouter()


class PatternResult(BaseModel):
    """Individual pattern detection result."""
    pattern_type: str
    direction: str
    confidence: float
    start_date: str
    end_date: str
    description: str


class PatternResponse(BaseModel):
    """Pattern detection response for a symbol."""
    symbol: str
    pattern_count: int
    patterns: List[dict]
    pattern_score: dict
    timestamp: str


class BulkPatternResponse(BaseModel):
    """Bulk pattern detection response."""
    status: str
    count: int
    data: dict


@router.get("/patterns/{symbol}", response_model=PatternResponse)
async def get_symbol_patterns(
    symbol: str,
    period: str = Query(default="3mo", description="Data period: 1mo, 3mo, 6mo, 1y"),
    interval: str = Query(default="1d", description="Data interval: 1h, 1d, 1wk")
):
    """
    Detect chart patterns for a specific symbol.
    
    Returns detected patterns including:
    - Head & Shoulders
    - Double Top/Bottom
    - Breakouts
    - Support/Resistance levels
    - Triangle patterns
    """
    try:
        # Fetch price data
        df = await data_fetcher.get_stock_data(
            symbol.upper(), 
            period=period, 
            interval=interval
        )
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not fetch data for symbol: {symbol}"
            )
        
        # Detect patterns
        patterns = pattern_detector.detect_all_patterns(df)
        pattern_score = pattern_detector.get_pattern_score(patterns)
        
        return PatternResponse(
            symbol=symbol.upper(),
            pattern_count=len(patterns),
            patterns=patterns,
            pattern_score=pattern_score,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/{symbol}/summary")
async def get_pattern_summary(symbol: str):
    """
    Get a simplified pattern summary for a symbol.
    """
    try:
        df = await data_fetcher.get_stock_data(symbol.upper(), period="3mo", interval="1d")
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not fetch data for symbol: {symbol}"
            )
        
        patterns = pattern_detector.detect_all_patterns(df)
        pattern_score = pattern_detector.get_pattern_score(patterns)
        
        # Get top patterns by confidence
        top_patterns = sorted(patterns, key=lambda x: x['confidence'], reverse=True)[:3]
        
        return {
            'symbol': symbol.upper(),
            'score': pattern_score['score'],
            'confidence': pattern_score['confidence'],
            'dominant_pattern': pattern_score.get('dominant_pattern'),
            'dominant_direction': pattern_score.get('dominant_direction'),
            'top_patterns': [
                {
                    'type': p['pattern_type'],
                    'direction': p['direction'],
                    'confidence': p['confidence']
                }
                for p in top_patterns
            ],
            'timestamp': datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/{symbol}/support-resistance")
async def get_support_resistance(symbol: str):
    """
    Get support and resistance levels for a symbol.
    """
    try:
        df = await data_fetcher.get_stock_data(symbol.upper(), period="3mo", interval="1d")
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not fetch data for symbol: {symbol}"
            )
        
        patterns = pattern_detector.detect_all_patterns(df)
        
        # Filter for support/resistance patterns
        support_resistance = [
            p for p in patterns 
            if p['pattern_type'] in ['SUPPORT', 'RESISTANCE']
        ]
        
        support_levels = [
            p['support_level'] for p in support_resistance 
            if p['pattern_type'] == 'SUPPORT'
        ]
        
        resistance_levels = [
            p['resistance_level'] for p in support_resistance 
            if p['pattern_type'] == 'RESISTANCE'
        ]
        
        current_price = float(df['close'].iloc[-1])
        
        return {
            'symbol': symbol.upper(),
            'current_price': current_price,
            'support_levels': sorted(support_levels, reverse=True),
            'resistance_levels': sorted(resistance_levels),
            'nearest_support': max([s for s in support_levels if s < current_price], default=None),
            'nearest_resistance': min([r for r in resistance_levels if r > current_price], default=None),
            'timestamp': datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
