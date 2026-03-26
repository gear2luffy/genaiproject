"""
News Sentiment Analysis Engine for Indian Stock Market.

Enhanced sentiment analysis for Indian stocks with:
- Indian financial news sources (Economic Times, MoneyControl, etc.)
- Company-specific news mapping for NSE/BSE stocks
- Financial keyword analysis
- Multi-method sentiment scoring
"""
import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import httpx
from loguru import logger

from app.core.config import settings


class IndianNewsFetcher:
    """Service for fetching news from Indian financial sources."""
    
    def __init__(self):
        self.news_api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        
        # Indian stock symbol to company name mapping
        self.symbol_names = {
            # NIFTY 50 Stocks
            'RELIANCE.NS': 'Reliance Industries',
            'TCS.NS': 'Tata Consultancy Services TCS',
            'HDFCBANK.NS': 'HDFC Bank',
            'INFY.NS': 'Infosys',
            'ICICIBANK.NS': 'ICICI Bank',
            'HINDUNILVR.NS': 'Hindustan Unilever HUL',
            'ITC.NS': 'ITC Limited',
            'SBIN.NS': 'State Bank of India SBI',
            'BHARTIARTL.NS': 'Bharti Airtel',
            'KOTAKBANK.NS': 'Kotak Mahindra Bank',
            'LT.NS': 'Larsen and Toubro L&T',
            'BAJFINANCE.NS': 'Bajaj Finance',
            'ASIANPAINT.NS': 'Asian Paints',
            'AXISBANK.NS': 'Axis Bank',
            'MARUTI.NS': 'Maruti Suzuki',
            'HCLTECH.NS': 'HCL Technologies',
            'SUNPHARMA.NS': 'Sun Pharmaceutical',
            'TITAN.NS': 'Titan Company',
            'ULTRACEMCO.NS': 'UltraTech Cement',
            'WIPRO.NS': 'Wipro',
            'NESTLEIND.NS': 'Nestle India',
            'ONGC.NS': 'Oil and Natural Gas Corporation ONGC',
            'NTPC.NS': 'NTPC Limited',
            'POWERGRID.NS': 'Power Grid Corporation',
            'TATAMOTORS.NS': 'Tata Motors',
            # Bank Nifty Stocks
            'BANKBARODA.NS': 'Bank of Baroda',
            'PNB.NS': 'Punjab National Bank PNB',
            'IDFCFIRSTB.NS': 'IDFC First Bank',
            'INDUSINDBK.NS': 'IndusInd Bank',
            'FEDERALBNK.NS': 'Federal Bank',
            # Other popular stocks
            'TATASTEEL.NS': 'Tata Steel',
            'ADANIENT.NS': 'Adani Enterprises',
            'ADANIPORTS.NS': 'Adani Ports',
            'JSWSTEEL.NS': 'JSW Steel',
            'HINDALCO.NS': 'Hindalco Industries',
            'COALINDIA.NS': 'Coal India',
            'VEDL.NS': 'Vedanta Limited',
            'ZOMATO.NS': 'Zomato',
            'PAYTM.NS': 'Paytm One97',
            'DELHIVERY.NS': 'Delhivery',
            # Legacy US symbols for backward compatibility
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
    
    async def fetch_news_api(
        self, 
        query: str, 
        days_back: int = 3,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI with Indian source preference."""
        if not self.news_api_key:
            logger.warning("NewsAPI key not configured, using mock data")
            return self._get_mock_indian_news(query)
        
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Add India-specific context to query
        india_query = f"{query} stock NSE BSE India"
        
        params = {
            'q': india_query,
            'from': from_date,
            'sortBy': 'publishedAt',
            'pageSize': page_size,
            'apiKey': self.news_api_key,
            'language': 'en',
            'domains': ','.join(settings.INDIAN_NEWS_SOURCES)
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/everything",
                    params=params,
                    timeout=15.0
                )
                response.raise_for_status()
                data = response.json()
                
                articles = [
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
                
                # If no articles found with domains, try without
                if not articles:
                    params.pop('domains', None)
                    response = await client.get(
                        f"{self.base_url}/everything",
                        params=params,
                        timeout=15.0
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    articles = [
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
                
                return articles
                
        except Exception as e:
            logger.error(f"Error fetching news for {query}: {e}")
            return self._get_mock_indian_news(query)
    
    def _get_mock_indian_news(self, query: str) -> List[Dict[str, Any]]:
        """Return mock Indian news data for development."""
        company = query.replace('.NS', '').replace('.BO', '')
        
        mock_articles = [
            {
                'title': f'{company} reports strong Q3 results, stock rallies',
                'description': f'{company} has delivered better-than-expected quarterly earnings, driving positive sentiment.',
                'content': f'{company} stock witnessed strong buying interest after the company reported robust quarterly results. Analysts remain bullish on the counter.',
                'source': 'Economic Times',
                'url': 'https://economictimes.indiatimes.com/markets/1',
                'published_at': datetime.now().isoformat(),
                'query': query
            },
            {
                'title': f'FIIs increase stake in {company}, signal confidence',
                'description': f'Foreign institutional investors have been accumulating {company} shares in recent weeks.',
                'content': f'FII interest in {company} has increased significantly. The stock is expected to perform well in the coming sessions.',
                'source': 'MoneyControl',
                'url': 'https://moneycontrol.com/news/2',
                'published_at': (datetime.now() - timedelta(hours=6)).isoformat(),
                'query': query
            },
            {
                'title': f'{company} announces expansion plans, stock in focus',
                'description': f'{company} is planning to expand its operations which could boost revenue growth.',
                'content': f'{company} management has outlined aggressive expansion plans for the next fiscal year. Markets remain watchful.',
                'source': 'LiveMint',
                'url': 'https://livemint.com/market/3',
                'published_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'query': query
            },
            {
                'title': f'Market outlook: {company} among top picks by brokerages',
                'description': f'Multiple brokerages have listed {company} as their top pick for the quarter.',
                'content': f'Leading domestic and international brokerages have given buy ratings to {company} citing strong fundamentals.',
                'source': 'Business Standard',
                'url': 'https://business-standard.com/article/4',
                'published_at': (datetime.now() - timedelta(days=1, hours=12)).isoformat(),
                'query': query
            }
        ]
        return mock_articles
    
    async def fetch_for_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Fetch news for a specific Indian stock symbol."""
        query = self.symbol_names.get(symbol, symbol.replace('.NS', '').replace('.BO', ''))
        return await self.fetch_news_api(query)
    
    async def fetch_market_news(self) -> List[Dict[str, Any]]:
        """Fetch general Indian market news."""
        queries = [
            "Nifty 50 stock market India",
            "Sensex BSE India",
            "Indian stock market today",
            "RBI monetary policy India"
        ]
        
        all_news = []
        for query in queries[:2]:  # Limit to avoid rate limits
            news = await self.fetch_news_api(query, days_back=1, page_size=5)
            all_news.extend(news)
        
        return all_news


class IndianSentimentAnalyzer:
    """
    Enhanced sentiment analysis for Indian financial news.
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
        
        # Indian financial sentiment keywords
        self.positive_words = {
            # General positive
            'bullish', 'surge', 'rally', 'growth', 'profit', 'gain', 'upgrade',
            'breakthrough', 'success', 'record', 'outperform', 'beat', 'strong',
            'positive', 'momentum', 'opportunity', 'innovative', 'leading',
            # Indian market specific
            'nifty', 'sensex', 'fii', 'dii', 'accumulate', 'overweight',
            'target price', 'upside', 'breakout', 'volume spike', 'buy',
            'robust', 'stellar', 'impressive', 'recommend', 'investing',
            'returns', 'dividend', 'bonus', 'split', 'buyback',
            # Sector specific
            'ipo', 'listing gain', 'market cap', 'all-time high', 'new high',
            '52-week high', 'rbi support', 'rate cut', 'reform'
        }
        
        self.negative_words = {
            # General negative
            'bearish', 'crash', 'decline', 'loss', 'downgrade', 'risk', 'concern',
            'warning', 'lawsuit', 'investigation', 'weak', 'miss', 'underperform',
            'negative', 'volatility', 'uncertainty', 'slowdown', 'layoff',
            # Indian market specific
            'fii selling', 'outflow', 'correction', 'sell-off', 'underweight',
            'downside', 'breakdown', 'target cut', 'reduce', 'avoid',
            'caution', 'fragile', 'disappointing', 'miss estimates',
            # Sector specific
            'scam', 'fraud', 'default', 'npa', 'bad loan', 'sebi investigation',
            '52-week low', 'rate hike', 'inflation', 'recession'
        }
        
        # Strong signal words (weighted higher)
        self.strong_positive = {'breakout', 'rally', 'surge', 'buy', 'upgrade', 'record', 'stellar'}
        self.strong_negative = {'crash', 'scam', 'fraud', 'sell', 'downgrade', 'avoid', 'default'}
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using multiple methods.
        """
        if not text or not text.strip():
            return {
                'sentiment': 'NEUTRAL',
                'score': 0.0,
                'confidence': 0.0,
                'details': {}
            }
        
        scores = []
        weights = []
        details = {}
        
        # Clean text
        text = self._clean_text(text)
        
        # VADER analysis (weight: 0.35)
        if self.vader:
            vader_scores = self.vader.polarity_scores(text)
            vader_compound = vader_scores['compound']
            scores.append(vader_compound)
            weights.append(0.35)
            details['vader'] = vader_scores
        
        # TextBlob analysis (weight: 0.25)
        if self.textblob_available:
            from textblob import TextBlob
            blob = TextBlob(text)
            textblob_score = blob.sentiment.polarity
            scores.append(textblob_score)
            weights.append(0.25)
            details['textblob'] = {
                'polarity': textblob_score,
                'subjectivity': blob.sentiment.subjectivity
            }
        
        # Financial keyword analysis (weight: 0.40)
        keyword_score, keyword_details = self._keyword_analysis(text)
        scores.append(keyword_score)
        weights.append(0.40)
        details['keywords'] = keyword_details
        
        # Calculate weighted final score
        if scores and weights:
            total_weight = sum(weights)
            final_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
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
        text = re.sub(r'[^\w\s.,!?%-]', '', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text.lower()
    
    def _keyword_analysis(self, text: str) -> tuple:
        """Analyze sentiment based on financial keywords with weights."""
        text_lower = text.lower()
        words = set(text_lower.split())
        
        positive_count = 0
        negative_count = 0
        
        # Check for word matches with weights
        for word in words:
            if word in self.strong_positive:
                positive_count += 2  # Double weight
            elif word in self.positive_words:
                positive_count += 1
            
            if word in self.strong_negative:
                negative_count += 2  # Double weight
            elif word in self.negative_words:
                negative_count += 1
        
        # Check for phrase matches
        for phrase in ['all-time high', '52-week high', 'fii buying', 'strong results']:
            if phrase in text_lower:
                positive_count += 2
        
        for phrase in ['52-week low', 'fii selling', 'miss estimates', 'sebi notice']:
            if phrase in text_lower:
                negative_count += 2
        
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
        else:
            score = (positive_count - negative_count) / total
        
        details = {
            'positive_count': positive_count,
            'negative_count': negative_count,
            'score': round(score, 4)
        }
        
        return score, details


class NewsSentimentEngine:
    """
    Main sentiment analysis engine for Indian stocks.
    Combines news fetching and multi-method sentiment analysis.
    """
    
    def __init__(self):
        self.fetcher = IndianNewsFetcher()
        self.analyzer = IndianSentimentAnalyzer()
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_sentiment_for_symbol(
        self, 
        symbol: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get aggregated sentiment for an Indian stock symbol.
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
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'news_items': [],
                'trading_signal': 'HOLD',
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
        
        # Calculate aggregate with recency weighting
        weighted_scores = []
        for i, score in enumerate(scores):
            # More recent news gets higher weight
            weight = 1.0 - (i * 0.1)  # First article: 1.0, second: 0.9, etc.
            weight = max(0.5, weight)
            weighted_scores.append(score * weight)
        
        avg_score = sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0
        
        if avg_score > 0.15:
            overall_sentiment = 'POSITIVE'
        elif avg_score < -0.15:
            overall_sentiment = 'NEGATIVE'
        else:
            overall_sentiment = 'NEUTRAL'
        
        # Determine trading signal based on sentiment
        positive_count = sum(1 for i in analyzed_items if i['sentiment'] == 'POSITIVE')
        negative_count = sum(1 for i in analyzed_items if i['sentiment'] == 'NEGATIVE')
        
        if positive_count >= 3 and positive_count > negative_count * 2:
            trading_signal = 'BUY'
            signal_strength = 'STRONG'
        elif positive_count > negative_count:
            trading_signal = 'BUY'
            signal_strength = 'MODERATE'
        elif negative_count >= 3 and negative_count > positive_count * 2:
            trading_signal = 'SELL'
            signal_strength = 'STRONG'
        elif negative_count > positive_count:
            trading_signal = 'SELL'
            signal_strength = 'MODERATE'
        else:
            trading_signal = 'HOLD'
            signal_strength = 'NEUTRAL'
        
        result = {
            'symbol': symbol,
            'sentiment': overall_sentiment,
            'score': round(avg_score, 4),
            'confidence': round(min(abs(avg_score) * 2, 1.0), 4),
            'news_count': len(analyzed_items),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': sum(1 for i in analyzed_items if i['sentiment'] == 'NEUTRAL'),
            'news_items': analyzed_items,
            'trading_signal': trading_signal,
            'signal_strength': signal_strength,
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
    
    async def get_market_sentiment(self) -> Dict[str, Any]:
        """Get overall Indian market sentiment."""
        news_items = await self.fetcher.fetch_market_news()
        
        if not news_items:
            return {
                'market': 'INDIA',
                'sentiment': 'NEUTRAL',
                'score': 0.0,
                'timestamp': datetime.now().isoformat()
            }
        
        scores = []
        for item in news_items:
            text = f"{item['title']} {item.get('description', '')}"
            analysis = self.analyzer.analyze_text(text)
            scores.append(analysis['score'])
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score > 0.1:
            overall = 'BULLISH'
        elif avg_score < -0.1:
            overall = 'BEARISH'
        else:
            overall = 'NEUTRAL'
        
        return {
            'market': 'INDIA',
            'sentiment': overall,
            'score': round(avg_score, 4),
            'news_count': len(news_items),
            'timestamp': datetime.now().isoformat()
        }


# Backward compatible alias
NewsFetcher = IndianNewsFetcher
SentimentAnalyzer = IndianSentimentAnalyzer

# Singleton instance
news_sentiment_engine = NewsSentimentEngine()
