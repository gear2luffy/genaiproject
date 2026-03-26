"""
News Sentiment API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from app.services.sentiment.sentiment_engine import news_sentiment_engine
from app.core.config import settings


router = APIRouter()


class NewsItem(BaseModel):
    """Individual news item with sentiment."""
    title: str
    source: str
    url: Optional[str]
    published_at: str
    sentiment: str
    score: float
    confidence: float


class SentimentResponse(BaseModel):
    """Sentiment analysis response for a symbol."""
    symbol: str
    sentiment: str
    score: float
    confidence: float
    news_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    news_items: List[NewsItem]
    timestamp: str


class BulkSentimentResponse(BaseModel):
    """Bulk sentiment response."""
    status: str
    count: int
    data: dict


@router.get("/news-sentiment/{symbol}", response_model=SentimentResponse)
async def get_symbol_sentiment(
    symbol: str,
    refresh: bool = Query(default=False, description="Force refresh data")
):
    """
    Get news sentiment analysis for a specific symbol.
    
    Analyzes recent news articles and returns:
    - Overall sentiment (POSITIVE/NEGATIVE/NEUTRAL)
    - Sentiment score (-1 to 1)
    - Individual news items with their sentiment
    """
    try:
        result = await news_sentiment_engine.get_sentiment_for_symbol(
            symbol.upper(),
            use_cache=not refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news-sentiment", response_model=BulkSentimentResponse)
async def get_bulk_sentiment(
    symbols: str = Query(
        default=None,
        description="Comma-separated list of symbols"
    )
):
    """
    Get sentiment for multiple symbols.
    
    If no symbols provided, uses default scanner symbols.
    """
    try:
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
        else:
            symbol_list = settings.SCANNER_SYMBOLS[:5]  # Default to first 5
        
        results = await news_sentiment_engine.get_bulk_sentiment(symbol_list)
        
        return BulkSentimentResponse(
            status="success",
            count=len(results),
            data=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news-sentiment/{symbol}/summary")
async def get_sentiment_summary(symbol: str):
    """
    Get a simplified sentiment summary for a symbol.
    
    Returns just the key metrics without full news items.
    """
    try:
        result = await news_sentiment_engine.get_sentiment_for_symbol(symbol.upper())
        
        return {
            'symbol': result['symbol'],
            'sentiment': result['sentiment'],
            'score': result['score'],
            'confidence': result['confidence'],
            'news_count': result['news_count'],
            'summary': f"{result['positive_count']} positive, {result['negative_count']} negative, {result['neutral_count']} neutral",
            'timestamp': result['timestamp']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
