"""
Trade Log API Endpoints.

Provides endpoints to view and manage the Excel trade log.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any
from pathlib import Path

from app.services.logging.trade_logger import trade_logger


router = APIRouter()


@router.get("/log/summary")
async def get_trade_log_summary() -> Dict[str, Any]:
    """
    Get summary statistics from the trade log.
    
    Returns:
        Trade statistics including win rate, total P&L, etc.
    """
    summary = trade_logger.get_trade_summary()
    
    if not summary:
        return {
            'status': 'no_data',
            'message': 'No trades logged yet or Excel logging disabled'
        }
    
    return {
        'status': 'success',
        'summary': summary
    }


@router.get("/log/open-trades")
async def get_open_trades() -> Dict[str, Any]:
    """
    Get all currently open trades from the log.
    
    Returns:
        List of open trades with entry details
    """
    open_trades = trade_logger.get_open_trades()
    
    return {
        'status': 'success',
        'count': len(open_trades),
        'trades': open_trades
    }


@router.get("/log/download")
async def download_trade_log():
    """
    Download the current month's trade log Excel file.
    
    Returns:
        Excel file download
    """
    if not trade_logger.current_file or not trade_logger.current_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Trade log file not found. No trades have been logged yet."
        )
    
    return FileResponse(
        path=str(trade_logger.current_file),
        filename=trade_logger.current_file.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/log/info")
async def get_log_info() -> Dict[str, Any]:
    """
    Get information about the trade log file.
    
    Returns:
        Log file path and status
    """
    from app.services.logging.trade_logger import OPENPYXL_AVAILABLE
    
    return {
        'excel_logging_enabled': OPENPYXL_AVAILABLE,
        'log_directory': str(trade_logger.log_dir),
        'current_file': str(trade_logger.current_file) if trade_logger.current_file else None,
        'file_exists': trade_logger.current_file.exists() if trade_logger.current_file else False
    }


@router.post("/log/test")
async def test_log_entry() -> Dict[str, Any]:
    """
    Create a test entry in the trade log (for debugging).
    
    Returns:
        Result of the test log entry
    """
    import uuid
    
    result = trade_logger.log_trade(
        trade_id=f"TEST-{uuid.uuid4().hex[:8].upper()}",
        symbol="TEST",
        action="BUY",
        quantity=100,
        price=150.00,
        strategy="TEST_STRATEGY",
        reason="Test entry for verification",
        signal_data={
            'confidence': 0.85,
            'technical_score': 0.75,
            'pattern_score': 0.80,
            'sentiment_score': 0.90
        },
        stop_loss=145.00,
        take_profit=160.00,
        notes="This is a test trade entry"
    )
    
    return {
        'status': 'success' if result else 'failed',
        'message': 'Test trade logged to Excel' if result else 'Failed to log test trade',
        'log_file': str(trade_logger.current_file) if trade_logger.current_file else None
    }
