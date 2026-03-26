"""
Trade Execution API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from app.services.trading.trade_executor import trade_executor, risk_manager


router = APIRouter()


class TradeRequest(BaseModel):
    """Trade execution request."""
    symbol: str
    side: str  # BUY or SELL
    quantity: Optional[float] = None
    risk_pct: float = 0.02
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    use_risk_management: bool = True


class TradeResponse(BaseModel):
    """Trade execution response."""
    status: str
    order: dict
    risk_management: dict


@router.post("/trade", response_model=TradeResponse)
async def execute_trade(request: TradeRequest):
    """
    Execute a trade (paper trading by default).
    
    If quantity is not provided, it will be calculated based on
    risk management parameters.
    """
    try:
        result = await trade_executor.execute_trade(
            symbol=request.symbol.upper(),
            side=request.side.upper(),
            quantity=request.quantity,
            risk_pct=request.risk_pct,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            use_risk_management=request.use_risk_management
        )
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result.get('message', 'Trade failed'))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio")
async def get_portfolio():
    """
    Get current portfolio state.
    
    Returns cash, positions, and performance metrics.
    """
    try:
        return trade_executor.get_portfolio()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_positions():
    """
    Get current open positions.
    """
    try:
        portfolio = trade_executor.get_portfolio()
        return {
            'status': 'success',
            'count': portfolio['positions_count'],
            'positions': portfolio['positions']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close/{symbol}")
async def close_position(symbol: str):
    """
    Close an entire position in a symbol.
    """
    try:
        positions = trade_executor.paper_engine.positions
        
        if symbol.upper() not in positions:
            raise HTTPException(status_code=404, detail=f"No position found for {symbol}")
        
        position = positions[symbol.upper()]
        
        result = await trade_executor.execute_trade(
            symbol=symbol.upper(),
            side='SELL',
            quantity=position.quantity,
            use_risk_management=False
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def get_orders():
    """
    Get all orders (filled and pending).
    """
    try:
        orders = trade_executor.paper_engine.orders
        return {
            'status': 'success',
            'count': len(orders),
            'orders': [order.to_dict() for order in orders.values()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades")
async def get_trade_history():
    """
    Get completed trade history.
    """
    try:
        trades = trade_executor.paper_engine.trade_history
        
        # Calculate aggregate stats
        if trades:
            total_pnl = sum(t['pnl'] for t in trades)
            winning = [t for t in trades if t['pnl'] > 0]
            losing = [t for t in trades if t['pnl'] < 0]
            win_rate = len(winning) / len(trades) * 100 if trades else 0
        else:
            total_pnl = 0
            win_rate = 0
            winning = []
            losing = []
        
        return {
            'status': 'success',
            'count': len(trades),
            'total_pnl': round(total_pnl, 2),
            'win_rate': round(win_rate, 2),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'trades': trades
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-positions")
async def update_positions():
    """
    Update positions with current prices and check stop loss / take profit.
    """
    try:
        result = await trade_executor.update_and_check_orders()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/position-size")
async def calculate_position_size(
    capital: float = Query(..., description="Total capital"),
    risk_pct: float = Query(0.02, description="Risk per trade (e.g., 0.02 for 2%)"),
    entry_price: float = Query(..., description="Entry price"),
    stop_loss: float = Query(..., description="Stop loss price")
):
    """
    Calculate optimal position size based on risk parameters.
    """
    try:
        shares = risk_manager.calculate_position_size(
            capital=capital,
            risk_per_trade=risk_pct,
            entry_price=entry_price,
            stop_loss=stop_loss
        )
        
        return {
            'shares': shares,
            'position_value': round(shares * entry_price, 2),
            'risk_amount': round(capital * risk_pct, 2),
            'risk_per_share': round(abs(entry_price - stop_loss), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/levels")
async def calculate_risk_levels(
    entry_price: float = Query(..., description="Entry price"),
    stop_loss_pct: float = Query(0.02, description="Stop loss percentage"),
    risk_reward: float = Query(2.0, description="Risk-reward ratio")
):
    """
    Calculate stop loss and take profit levels.
    """
    try:
        stop_loss = risk_manager.calculate_stop_loss(entry_price, stop_loss_pct)
        take_profit = risk_manager.calculate_take_profit(
            entry_price, stop_loss=stop_loss, risk_reward=risk_reward
        )
        
        return {
            'entry_price': entry_price,
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'risk_amount': round(entry_price - stop_loss, 2),
            'reward_amount': round(take_profit - entry_price, 2),
            'risk_pct': round((entry_price - stop_loss) / entry_price * 100, 2),
            'reward_pct': round((take_profit - entry_price) / entry_price * 100, 2),
            'risk_reward': risk_reward
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
