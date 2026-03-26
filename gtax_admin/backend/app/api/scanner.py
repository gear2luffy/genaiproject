"""
Market Scanner API endpoints for Indian Stocks.
Includes both positional and intraday scanning.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from app.services.scanner.market_scanner import market_scanner
from app.services.scanner.intraday_scanner import intraday_scanner


router = APIRouter()


class ScanResult(BaseModel):
    """Scan result response model."""
    symbol: str
    price: Optional[float]
    change_percent: Optional[float]
    volume: Optional[int]
    volume_score: float
    volatility_score: float
    trend_score: float
    technical_score: float
    technical_signals: List
    opportunity_score: float
    rsi: Optional[float]
    macd: Optional[float]
    adx: Optional[float]
    sma_20: Optional[float]
    sma_50: Optional[float]
    bollinger_upper: Optional[float]
    bollinger_lower: Optional[float]
    timestamp: str


class ScanResponse(BaseModel):
    """Response model for scan endpoint."""
    status: str
    count: int
    data: List[ScanResult]


class IntradayScanResult(BaseModel):
    """Intraday scan result."""
    symbol: str
    current_price: float
    change_percent: float
    gap_data: Optional[Dict[str, Any]]
    volume_data: Optional[Dict[str, Any]]
    orb_data: Optional[Dict[str, Any]]
    vwap_data: Optional[Dict[str, Any]]
    momentum_data: Optional[Dict[str, Any]]
    intraday_score: float
    signal: str
    signal_strength: float
    time_to_square_off: int
    timestamp: str


class IntradayResponse(BaseModel):
    """Response for intraday scan."""
    status: str
    market_open: bool
    trading_allowed: bool
    count: int
    data: List[Dict[str, Any]]


class SymbolAnalysis(BaseModel):
    """Detailed symbol analysis response."""
    symbol: str
    price: Optional[float]
    change_percent: Optional[float]
    volume: Optional[int]
    volume_score: float
    volatility_score: float
    trend_score: float
    technical_score: float
    technical_signals: List
    opportunity_score: float
    rsi: Optional[float]
    macd: Optional[float]
    adx: Optional[float]
    sma_20: Optional[float]
    sma_50: Optional[float]
    bollinger_upper: Optional[float]
    bollinger_lower: Optional[float]
    timestamp: str


@router.get("/scan", response_model=ScanResponse)
async def scan_markets(
    top_n: int = Query(default=10, ge=1, le=50, description="Number of top stocks to return"),
    refresh: bool = Query(default=False, description="Force refresh data")
):
    """
    Scan Indian markets (NSE/BSE) and return top trading opportunities.
    
    This endpoint scans configured Indian stocks and ranks them
    based on volume, volatility, trend strength, and technical indicators.
    """
    try:
        if refresh or not market_scanner.last_scan_results:
            results = await market_scanner.scan_all()
        else:
            results = market_scanner.get_last_results()
        
        return ScanResponse(
            status="success",
            count=len(results[:top_n]),
            data=results[:top_n]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intraday", response_model=IntradayResponse)
async def scan_intraday(
    top_n: int = Query(default=10, ge=1, le=20, description="Number of top stocks to return"),
    refresh: bool = Query(default=True, description="Force refresh data")
):
    """
    Scan Indian stocks for intraday trading opportunities.
    
    Analyzes:
    - Gap up/down from previous close
    - Volume surge detection
    - Opening Range Breakout (ORB)
    - VWAP crossover signals
    - Momentum indicators
    
    Returns actionable BUY/SELL signals with confidence scores.
    """
    try:
        # Check market status
        market_open = intraday_scanner.is_market_open()
        trading_allowed = intraday_scanner.is_trading_allowed()
        
        if not market_open:
            return IntradayResponse(
                status="market_closed",
                market_open=False,
                trading_allowed=False,
                count=0,
                data=[]
            )
        
        results = await intraday_scanner.scan_all()
        
        return IntradayResponse(
            status="success",
            market_open=market_open,
            trading_allowed=trading_allowed,
            count=len(results[:top_n]),
            data=results[:top_n]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intraday/gaps")
async def get_gap_report():
    """
    Get pre-market gap analysis for all configured stocks.
    
    Shows stocks with significant gap up/down from previous close,
    which often present intraday trading opportunities.
    """
    try:
        gaps = await intraday_scanner.get_gap_report()
        
        return {
            "status": "success",
            "market_open": intraday_scanner.is_market_open(),
            "count": len(gaps),
            "gap_up": [g for g in gaps if g.get('gap_type') == 'UP'],
            "gap_down": [g for g in gaps if g.get('gap_type') == 'DOWN'],
            "data": gaps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intraday/volume-surgers")
async def get_volume_surgers():
    """
    Get stocks with unusual volume activity.
    
    Identifies stocks trading with significantly higher volume
    than their 20-day average, which often indicates strong momentum.
    """
    try:
        surgers = await intraday_scanner.get_volume_surgers()
        
        return {
            "status": "success",
            "market_open": intraday_scanner.is_market_open(),
            "count": len(surgers),
            "data": surgers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intraday/{symbol}")
async def analyze_intraday_symbol(symbol: str):
    """
    Get detailed intraday analysis for a specific stock.
    
    Args:
        symbol: NSE/BSE stock symbol (e.g., 'RELIANCE.NS')
    """
    try:
        result = await intraday_scanner.scan_single_stock(symbol.upper())
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not analyze symbol: {symbol}"
            )
        
        return {
            "status": "success",
            "market_open": intraday_scanner.is_market_open(),
            "trading_allowed": intraday_scanner.is_trading_allowed(),
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan/{symbol}", response_model=SymbolAnalysis)
async def analyze_symbol(symbol: str):
    """
    Get detailed analysis for a specific symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS', 'TCS.NS')
    """
    try:
        result = await market_scanner.analyze_symbol(symbol.upper())
        
        if result is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not analyze symbol: {symbol}"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def scanner_status():
    """Get market scanner status for Indian markets."""
    return {
        "market": "INDIA",
        "exchange": "NSE/BSE",
        "is_scanning": market_scanner.is_scanning,
        "intraday_market_open": intraday_scanner.is_market_open(),
        "intraday_trading_allowed": intraday_scanner.is_trading_allowed(),
        "time_to_square_off_minutes": intraday_scanner.time_to_square_off(),
        "positional_symbols_count": len(market_scanner.symbols),
        "intraday_symbols_count": len(intraday_scanner.symbols),
        "scan_interval": market_scanner.scan_interval,
        "last_results_count": len(market_scanner.last_scan_results),
        "last_scan_time": market_scanner.last_scan_results[0]['timestamp'] if market_scanner.last_scan_results else None
    }
