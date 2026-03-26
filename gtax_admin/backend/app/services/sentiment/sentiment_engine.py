"""
News Sentiment Analysis Engine.
"""
import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import httpx
from loguru import logger

from app.core.config import settings


class NewsFetcher:
    """Service for fetching news from various sources."""
    
    def __init__(self):
        self.news_api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
    
    async def fetch_news_api(
        self, 
        query: str, 
        days_back: int = 7,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI."""
        if not self.news_api_key:
            logger.warning("NewsAPI key not configured, using mock data")
            return self._get_mock_news(query)
        
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'publishedAt',
            'pageSize': page_size,
            'apiKey': self.news_api_key,
            'language': 'en'
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/everything",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                return [
                    {
                        'title': article['title'],
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'source': article['source']['name'],
                        'url': article['url'],
                        'published_at': article['publishedAt'],
                        'query': query
                    }
                    for article in data.get('articles', [])
                ]
        except Exception as e:
            logger.error(f"Error fetching news for {query}: {e}")
            return self._get_mock_news(query)
    
    def _get_mock_news(self, query: str) -> List[Dict[str, Any]]:
        """Return mock news data for development."""
        mock_articles = [
            {
                'title': f'{query} shows strong momentum amid market rally',
                'description': f'{query} stock has been gaining traction with positive investor sentiment.',
                'content': f'{query} demonstrates resilient performance with trading volume increasing significantly.',
                'source': 'Financial Times',
                'url': 'https://example.com/news/1',
                'published_at': datetime.now().isoformat(),
                'query': query
            },
            {
                'title': f'Analysts upgrade {query} rating to buy',
                'description': f'Multiple analysts have revised their outlook on {query} positively.',
                'content': f'Wall Street analysts are bullish on {query} citing strong fundamentals.',
                'source': 'Bloomberg',
                'url': 'https://example.com/news/2',
                'published_at': (datetime.now() - timedelta(hours=6)).isoformat(),
                'query': query
            },
            {
                'title': f'{query} faces headwinds from regulatory concerns',
                'description': f'Regulatory scrutiny could impact {query} short-term performance.',
                'content': f'{query} may experience volatility due to pending regulatory decisions.',
                'source': 'Reuters',
                'url': 'https://example.com/news/3',
                'published_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'query': query
            }
        ]
        return mock_articles
    
    async def fetch_for_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Fetch news for a specific stock symbol."""
        # Map symbol to company name for better results
        symbol_names = {
            'AAPL': 'Apple',
            'GOOGL': 'Google Alphabet',
            'MSFT': 'Microsoft',
            'AMZN': 'Amazon',
            'META': 'Meta Facebook',
            'TSLA': 'Tesla',
            'NVDA': 'Nvidia',
            'AMD': 'AMD',
            'BTC-USD': 'Bitcoin',
            'ETH-USD': 'Ethereum'
        }
        
        query = symbol_names.get(symbol, symbol)
        return await self.fetch_news_api(query)


class SentimentAnalyzer:
    """
    Sentiment analysis using multiple approaches:
    - VADER (rule-based)
    - TextBlob (pattern-based)
    - Transformers (if available)
    """
    
    def __init__(self):
        self._setup_analyzers()
    
    def _setup_analyzers(self):
        """Initialize sentiment analyzers."""
        # VADER
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader = SentimentIntensityAnalyzer()
        except ImportError:
            logger.warning("VADER not available")
            self.vader = None
        
        # TextBlob
        try:
            from textblob import TextBlob
            self.textblob_available = True
        except ImportError:
            logger.warning("TextBlob not available")
            self.textblob_available = False
        
        # Financial sentiment keywords
        self.positive_words = {
            'bullish', 'surge', 'rally', 'growth', 'profit', 'gain', 'upgrade',
            'breakthrough', 'success', 'record', 'outperform', 'beat', 'strong',
            'positive', 'momentum', 'opportunity', 'innovative', 'leading'
        }
        
        self.negative_words = {
            'bearish', 'crash', 'decline', 'loss', 'downgrade', 'risk', 'concern',
            'warning', 'lawsuit', 'investigation', 'weak', 'miss', 'underperform',
            'negative', 'volatility', 'uncertainty', 'slowdown', 'layoff'
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using multiple methods.
        
        Returns:
            Dict with sentiment label, score (-1 to 1), and confidence
        """
        if not text or not text.strip():
            return {
                'sentiment': 'NEUTRAL',
                'score': 0.0,
                'confidence': 0.0,
                'details': {}
            }
        
        scores = []
        details = {}
        
        # Clean text
        text = self._clean_text(text)
        
        # VADER analysis
        if self.vader:
            vader_scores = self.vader.polarity_scores(text)
            vader_compound = vader_scores['compound']
            scores.append(vader_compound)
            details['vader'] = vader_scores
        
        # TextBlob analysis
        if self.textblob_available:
            from textblob import TextBlob
            blob = TextBlob(text)
            textblob_score = blob.sentiment.polarity
            scores.append(textblob_score)
            details['textblob'] = {
                'polarity': textblob_score,
                'subjectivity': blob.sentiment.subjectivity
            }
        
        # Financial keyword analysis
        keyword_score = self._keyword_analysis(text)
        scores.append(keyword_score)
        details['keywords'] = keyword_score
        
        # Calculate final score
        if scores:
            final_score = sum(scores) / len(scores)
        else:
            final_score = 0.0
        
        # Determine sentiment label
        if final_score > 0.2:
            sentiment = 'POSITIVE'
        elif final_score < -0.2:
            sentiment = 'NEGATIVE'
        else:
            sentiment = 'NEUTRAL'
        
        # Calculate confidence
        confidence = min(abs(final_score) * 1.5, 1.0)
        
        return {
            'sentiment': sentiment,
            'score': round(final_score, 4),
            'confidence': round(confidence, 4),
            'details': details
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean text for analysis."""
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text.lower()
    
    def _keyword_analysis(self, text: str) -> float:
        """Analyze sentiment based on financial keywords."""
        text_lower = text.lower()
        words = set(text_lower.split())
        
        positive_count = len(words.intersection(self.positive_words))
        negative_count = len(words.intersection(self.negative_words))
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total


class NewsSentimentEngine:
    """
    Main sentiment analysis engine combining news fetching and analysis.
    """
    
    def __init__(self):
        self.fetcher = NewsFetcher()
        self.analyzer = SentimentAnalyzer()
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_sentiment_for_symbol(
        self, 
        symbol: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get aggregated sentiment for a symbol.
        
        Returns:
            Dict with overall sentiment and individual news items
        """
        # Check cache
        cache_key = symbol
        if use_cache and cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.now().timestamp() - cached['timestamp'] < self.cache_ttl:
                return cached['data']
        
        # Fetch news
        news_items = await self.fetcher.fetch_for_symbol(symbol)
        
        if not news_items:
            return {
                'symbol': symbol,
                'sentiment': 'NEUTRAL',
                'score': 0.0,
                'confidence': 0.0,
                'news_count': 0,
                'news_items': [],
                'timestamp': datetime.now().isoformat()
            }
        
        # Analyze each news item
        analyzed_items = []
        scores = []
        
        for item in news_items:
            text = f"{item['title']} {item.get('description', '')} {item.get('content', '')}"
            analysis = self.analyzer.analyze_text(text)
            
            analyzed_items.append({
                'title': item['title'],
                'source': item['source'],
                'url': item.get('url'),
                'published_at': item['published_at'],
                'sentiment': analysis['sentiment'],
                'score': analysis['score'],
                'confidence': analysis['confidence']
            })
            
            scores.append(analysis['score'])
        
        # Calculate aggregate
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score > 0.15:
            overall_sentiment = 'POSITIVE'
        elif avg_score < -0.15:
            overall_sentiment = 'NEGATIVE'
        else:
            overall_sentiment = 'NEUTRAL'
        
        result = {
            'symbol': symbol,
            'sentiment': overall_sentiment,
            'score': round(avg_score, 4),
            'confidence': round(min(abs(avg_score) * 2, 1.0), 4),
            'news_count': len(analyzed_items),
            'positive_count': sum(1 for i in analyzed_items if i['sentiment'] == 'POSITIVE'),
            'negative_count': sum(1 for i in analyzed_items if i['sentiment'] == 'NEGATIVE'),
            'neutral_count': sum(1 for i in analyzed_items if i['sentiment'] == 'NEUTRAL'),
            'news_items': analyzed_items,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache result
        self.cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now().timestamp()
        }
        
        return result
    
    async def get_bulk_sentiment(
        self, 
        symbols: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Get sentiment for multiple symbols concurrently."""
        tasks = [self.get_sentiment_for_symbol(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        return {
            symbol: result 
            for symbol, result in zip(symbols, results)
        }


# Singleton instance
news_sentiment_engine = NewsSentimentEngine()
