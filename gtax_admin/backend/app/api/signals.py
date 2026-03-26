"""
AI Signals API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from app.services.ai.decision_engine import ai_decision_engine, SignalType
from app.core.config import settings


router = APIRouter()


class SignalResponse(BaseModel):
    """Trading signal response."""
    symbol: str
    signal: str
    confidence: float
    technical_score: float
    pattern_score: float
    sentiment_score: float
    price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    reasoning: List[str]
    timestamp: str


class BulkSignalResponse(BaseModel):
    """Bulk signal response."""
    status: str
    count: int
    actionable_count: int
    signals: List[dict]


class SignalConfigRequest(BaseModel):
    """Request to customize signal generation weights."""
    technical_weight: float = 0.4
    pattern_weight: float = 0.3
    sentiment_weight: float = 0.3
    confidence_threshold: float = 0.65


@router.get("/signals/{symbol}", response_model=SignalResponse)
async def get_symbol_signal(
    symbol: str,
    include_sentiment: bool = Query(
        default=True, 
        description="Include news sentiment analysis"
    )
):
    """
    Get AI trading signal for a specific symbol.
    
    Combines:
    - Technical indicators (40%)
    - Chart patterns (30%)
    - News sentiment (30%)
    
    Returns BUY/SELL/HOLD with confidence score and reasoning.
    """
    try:
        signal = await ai_decision_engine.generate_signal(
            symbol.upper(),
            include_sentiment=include_sentiment
        )
        return signal.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals", response_model=BulkSignalResponse)
async def get_bulk_signals(
    symbols: str = Query(
        default=None,
        description="Comma-separated list of symbols"
    ),
    actionable_only: bool = Query(
        default=False,
        description="Return only BUY/SELL signals above threshold"
    ),
    include_sentiment: bool = Query(
        default=True,
        description="Include news sentiment analysis"
    )
):
    """
    Get AI trading signals for multiple symbols.
    
    If no symbols provided, uses top scanner results.
    """
    try:
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
        else:
            symbol_list = settings.SCANNER_SYMBOLS[:5]
        
        signals = await ai_decision_engine.generate_bulk_signals(
            symbol_list,
            include_sentiment=include_sentiment
        )
        
        if actionable_only:
            signals = ai_decision_engine.get_actionable_signals(signals)
        
        signal_dicts = [s.to_dict() for s in signals]
        actionable = [s for s in signals if s.signal != SignalType.HOLD]
        
        return BulkSignalResponse(
            status="success",
            count=len(signals),
            actionable_count=len(actionable),
            signals=signal_dicts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/signals/custom/{symbol}")
async def get_custom_signal(
    symbol: str,
    config: SignalConfigRequest,
    include_sentiment: bool = Query(default=True)
):
    """
    Get AI signal with custom weights.
    
    Allows customizing the weight of each analysis component.
    """
    try:
        # Create engine with custom config
        from app.services.ai.decision_engine import AIDecisionEngine
        
        custom_engine = AIDecisionEngine(
            technical_weight=config.technical_weight,
            pattern_weight=config.pattern_weight,
            sentiment_weight=config.sentiment_weight,
            confidence_threshold=config.confidence_threshold
        )
        
        signal = await custom_engine.generate_signal(
            symbol.upper(),
            include_sentiment=include_sentiment
        )
        
        return {
            **signal.to_dict(),
            'weights_used': {
                'technical': config.technical_weight,
                'pattern': config.pattern_weight,
                'sentiment': config.sentiment_weight
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/{symbol}/breakdown")
async def get_signal_breakdown(symbol: str):
    """
    Get detailed breakdown of all components contributing to the signal.
    """
    try:
        signal = await ai_decision_engine.generate_signal(symbol.upper())
        
        return {
            'symbol': signal.symbol,
            'final_signal': signal.signal.value,
            'final_confidence': signal.confidence,
            'components': {
                'technical': {
                    'score': signal.technical_score,
                    'weight': settings.AI_TECHNICAL_WEIGHT,
                    'contribution': signal.technical_score * settings.AI_TECHNICAL_WEIGHT
                },
                'patterns': {
                    'score': signal.pattern_score,
                    'weight': settings.AI_PATTERN_WEIGHT,
                    'contribution': signal.pattern_score * settings.AI_PATTERN_WEIGHT
                },
                'sentiment': {
                    'score': signal.sentiment_score,
                    'weight': settings.AI_SENTIMENT_WEIGHT,
                    'contribution': signal.sentiment_score * settings.AI_SENTIMENT_WEIGHT
                }
            },
            'combined_score': (
                signal.technical_score * settings.AI_TECHNICAL_WEIGHT +
                signal.pattern_score * settings.AI_PATTERN_WEIGHT +
                signal.sentiment_score * settings.AI_SENTIMENT_WEIGHT
            ),
            'reasoning': signal.reasoning,
            'targets': {
                'entry_price': signal.price,
                'target_price': signal.target_price,
                'stop_loss': signal.stop_loss
            },
            'timestamp': signal.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
