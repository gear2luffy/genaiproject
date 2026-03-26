"""
Backtesting API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime

from app.services.learning.learning_model import backtest_engine, ml_predictor
from app.core.config import settings


router = APIRouter()


class BacktestRequest(BaseModel):
    """Backtest configuration request."""
    symbols: List[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: Optional[float] = 100000.0
    strategy_params: Optional[dict] = None


class TrainRequest(BaseModel):
    """ML model training request."""
    symbols: List[str]
    model_type: str = "random_forest"


class BacktestResponse(BaseModel):
    """Backtest results response."""
    status: str
    symbols: List[str]
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_trades: int
    metrics: dict


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    Run backtest simulation on historical data.
    
    Tests the trading strategy on past data to evaluate performance.
    """
    try:
        results = await backtest_engine.run_backtest(
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy_params=request.strategy_params or {}
        )
        
        return BacktestResponse(
            status="success",
            symbols=results['symbols'],
            start_date=results['start_date'],
            end_date=results['end_date'],
            initial_capital=results['initial_capital'],
            final_capital=results['final_capital'],
            total_return=results['total_return'],
            total_trades=results['total_trades'],
            metrics=results['metrics']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest/detailed")
async def run_detailed_backtest(request: BacktestRequest):
    """
    Run backtest and return detailed results including equity curve and trades.
    """
    try:
        results = await backtest_engine.run_backtest(
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy_params=request.strategy_params or {}
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train_model(request: TrainRequest, background_tasks: BackgroundTasks):
    """
    Train ML model on historical data.
    
    This can take a while, so it runs in the background.
    """
    try:
        results = await ml_predictor.train_model(
            symbols=request.symbols,
            model_type=request.model_type
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict/{symbol}")
async def get_ml_prediction(
    symbol: str,
    model_type: str = Query(default="random_forest", description="Model type to use")
):
    """
    Get ML prediction for a symbol.
    
    Uses a trained model to predict the likely price direction.
    """
    try:
        result = await ml_predictor.predict(symbol.upper(), model_type)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """
    List available trained models.
    """
    from pathlib import Path
    
    model_dir = Path("models")
    models = []
    
    if model_dir.exists():
        for model_file in model_dir.glob("*.pkl"):
            models.append({
                'name': model_file.stem,
                'path': str(model_file),
                'size_kb': round(model_file.stat().st_size / 1024, 2)
            })
    
    return {
        'status': 'success',
        'loaded_models': list(ml_predictor.models.keys()),
        'available_models': models
    }
