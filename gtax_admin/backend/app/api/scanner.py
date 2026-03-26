"""
Market Scanner API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from app.services.scanner.market_scanner import market_scanner


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
    Scan markets and return top trading opportunities.
    
    This endpoint scans configured stocks/crypto pairs and ranks them
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


@router.get("/scan/{symbol}", response_model=SymbolAnalysis)
async def analyze_symbol(symbol: str):
    """
    Get detailed analysis for a specific symbol.
    
    Args:
        symbol: Stock or crypto symbol (e.g., 'AAPL', 'BTC-USD')
    """
    try:
        result = await market_scanner.get_symbol_analysis(symbol.upper())
        
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


@router.get("/scan/status")
async def scanner_status():
    """Get market scanner status."""
    return {
        "is_scanning": market_scanner.is_scanning,
        "symbols_count": len(market_scanner.symbols),
        "scan_interval": market_scanner.scan_interval,
        "last_results_count": len(market_scanner.last_scan_results),
        "last_scan_time": market_scanner.last_scan_results[0]['timestamp'] if market_scanner.last_scan_results else None
    }
