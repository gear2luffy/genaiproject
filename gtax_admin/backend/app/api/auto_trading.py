"""
Automated Trading API endpoints.

Control the autonomous trading system.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.orchestrator.trading_orchestrator import trading_orchestrator


router = APIRouter()


class OrchestratorConfig(BaseModel):
    """Configuration for the trading orchestrator."""
    auto_execute: Optional[bool] = None
    max_positions: Optional[int] = None
    min_confidence: Optional[float] = None
    risk_per_trade: Optional[float] = None
    signal_interval: Optional[int] = None
    trading_hours_only: Optional[bool] = None


@router.get("/auto/status")
async def get_orchestrator_status():
    """
    Get the current status of the automated trading system.
    
    Returns running state, statistics, pending signals, and portfolio status.
    """
    return trading_orchestrator.get_status()


@router.post("/auto/start")
async def start_orchestrator():
    """
    Start the automated trading system.
    
    The system will automatically:
    - Scan markets for opportunities
    - Generate AI trading signals
    - Execute trades based on signals
    - Monitor positions for stop loss/take profit
    """
    if trading_orchestrator.is_running:
        return {
            "status": "already_running",
            "message": "Automated trading is already running"
        }
    
    import asyncio
    asyncio.create_task(trading_orchestrator.start())
    
    return {
        "status": "started",
        "message": "Automated trading system started",
        "config": {
            "auto_execute": trading_orchestrator.auto_execute,
            "max_positions": trading_orchestrator.max_positions,
            "min_confidence": trading_orchestrator.min_confidence,
            "signal_interval": trading_orchestrator.signal_interval
        }
    }


@router.post("/auto/stop")
async def stop_orchestrator():
    """
    Stop the automated trading system.
    
    Open positions will remain open until manually closed or stop loss/take profit is hit.
    """
    if not trading_orchestrator.is_running:
        return {
            "status": "not_running",
            "message": "Automated trading is not running"
        }
    
    trading_orchestrator.stop()
    
    return {
        "status": "stopped",
        "message": "Automated trading system stopped",
        "stats": trading_orchestrator.stats
    }


@router.post("/auto/configure")
async def configure_orchestrator(config: OrchestratorConfig):
    """
    Configure the automated trading system parameters.
    
    Changes take effect on the next trading cycle.
    """
    if config.auto_execute is not None:
        trading_orchestrator.auto_execute = config.auto_execute
    
    if config.max_positions is not None:
        trading_orchestrator.max_positions = config.max_positions
    
    if config.min_confidence is not None:
        trading_orchestrator.min_confidence = config.min_confidence
    
    if config.risk_per_trade is not None:
        trading_orchestrator.risk_per_trade = config.risk_per_trade
    
    if config.signal_interval is not None:
        trading_orchestrator.signal_interval = config.signal_interval
    
    if config.trading_hours_only is not None:
        trading_orchestrator.trading_hours_only = config.trading_hours_only
    
    return {
        "status": "configured",
        "message": "Configuration updated",
        "config": {
            "auto_execute": trading_orchestrator.auto_execute,
            "max_positions": trading_orchestrator.max_positions,
            "min_confidence": trading_orchestrator.min_confidence,
            "risk_per_trade": trading_orchestrator.risk_per_trade,
            "signal_interval": trading_orchestrator.signal_interval,
            "trading_hours_only": trading_orchestrator.trading_hours_only
        }
    }


@router.post("/auto/run-cycle")
async def run_single_cycle():
    """
    Run a single trading cycle manually.
    
    Useful for testing or manual intervention.
    """
    try:
        await trading_orchestrator.run_trading_cycle()
        return {
            "status": "success",
            "message": "Trading cycle completed",
            "stats": trading_orchestrator.stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto/pending-signals")
async def get_pending_signals():
    """
    Get pending signals that haven't been executed.
    
    Only populated when auto_execute is disabled.
    """
    return {
        "count": len(trading_orchestrator.pending_signals),
        "signals": trading_orchestrator.pending_signals
    }


@router.post("/auto/execute-pending")
async def execute_pending_signals():
    """
    Execute all pending signals.
    
    Use when auto_execute is disabled and you want to manually approve execution.
    """
    executed = []
    
    for signal in trading_orchestrator.pending_signals:
        result = await trading_orchestrator.execute_signal(signal)
        if result:
            executed.append(signal['symbol'])
    
    trading_orchestrator.pending_signals = []
    
    return {
        "status": "success",
        "executed": executed,
        "count": len(executed)
    }
