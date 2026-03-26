# AI-Powered Autonomous Trading Platform - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Workflow](#workflow)
8. [Modules Documentation](#modules-documentation)
9. [API Reference](#api-reference)
10. [Frontend](#frontend)
11. [Trade Logging](#trade-logging)
12. [Risk Management](#risk-management)
13. [Troubleshooting](#troubleshooting)

---

## Overview

This platform is designed to operate **fully autonomously** - from stock selection to trade execution. Once started, it continuously:

1. **Scans markets** for trading opportunities
2. **Analyzes** using AI (technical indicators + chart patterns + news sentiment)
3. **Generates signals** with confidence scores
4. **Executes trades** when confidence exceeds threshold
5. **Manages positions** (stop-loss, take-profit)
6. **Logs everything** to Excel for review

### Key Features

- ✅ **Autonomous Operation** - Runs 24/7 without human intervention
- ✅ **AI Decision Engine** - Weighted scoring system combining multiple analysis methods
- ✅ **Multi-Asset Support** - Stocks and Cryptocurrencies
- ✅ **Risk Management** - Position sizing, stop-loss, take-profit
- ✅ **Paper Trading** - Test strategies without real money
- ✅ **Real Trading Ready** - Alpaca/Binance API integration
- ✅ **Excel Trade Logging** - Complete trade history with analysis data
- ✅ **Web Dashboard** - Real-time monitoring via React frontend
- ✅ **WebSocket Updates** - Live price and signal updates

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React)                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Dashboard │ │ Signals  │ │Portfolio │ │ Backtest │ │  Stock   │          │
│  │          │ │          │ │          │ │          │ │  Detail  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ REST API / WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    AUTONOMOUS TRADING ORCHESTRATOR                    │   │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │   │
│  │   │  Scan   │───▶│ Analyze │───▶│ Signal  │───▶│ Execute │         │   │
│  │   │ Markets │    │   AI    │    │Generate │    │  Trade  │         │   │
│  │   └─────────┘    └─────────┘    └─────────┘    └─────────┘         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │   Market     │ │    News      │ │    Chart     │ │      AI      │       │
│  │   Scanner    │ │  Sentiment   │ │   Patterns   │ │   Decision   │       │
│  │              │ │   Engine     │ │  Detection   │ │    Engine    │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│                                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │    Trade     │ │   Learning   │ │    Data      │ │    Excel     │       │
│  │   Executor   │ │    Model     │ │   Fetcher    │ │   Logger     │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
             ┌──────────┐    ┌──────────┐    ┌──────────┐
             │ Database │    │  Redis   │    │  Broker  │
             │ (SQLite/ │    │ (Cache)  │    │   APIs   │
             │ Postgres)│    │          │    │          │
             └──────────┘    └──────────┘    └──────────┘
```

---

## Technology Stack

### Backend Libraries

| Component | Library | Version | Purpose |
|-----------|---------|---------|---------|
| **Web Framework** | FastAPI | ≥0.104.0 | Async REST API with automatic OpenAPI docs |
| **ASGI Server** | Uvicorn | ≥0.24.0 | High-performance async server |
| **Database ORM** | SQLAlchemy | ≥2.0.0 | Async database operations |
| **Migrations** | Alembic | ≥1.12.0 | Database schema migrations |
| **PostgreSQL Driver** | asyncpg | ≥0.29.0 | Async PostgreSQL support |
| **SQLite Driver** | aiosqlite | ≥0.19.0 | Async SQLite for development |
| **Caching** | Redis | ≥5.0.0 | Market data caching |
| **Background Tasks** | Celery | ≥5.3.0 | Distributed task queue |
| **Logging** | Loguru | ≥0.7.0 | Structured logging |
| **Config** | Pydantic-Settings | ≥2.1.0 | Environment configuration |

### Data & Analysis Libraries

| Component | Library | Version | Purpose |
|-----------|---------|---------|---------|
| **Data Processing** | Pandas | ≥2.1.0 | DataFrame operations |
| **Numerical** | NumPy | ≥1.26.0 | Array computations |
| **Scientific** | SciPy | ≥1.11.0 | Statistical functions, peak detection |
| **Technical Analysis** | TA | ≥0.11.0 | Technical indicators (RSI, MACD, etc.) |
| **TA-Lib** | ta-lib | ≥0.4.28 | Advanced technical analysis |
| **Market Data** | yfinance | ≥0.2.31 | Yahoo Finance API for stock/crypto data |
| **Crypto Data** | CCXT | ≥4.1.0 | Cryptocurrency exchange connections |

### AI & Machine Learning Libraries

| Component | Library | Version | Purpose |
|-----------|---------|---------|---------|
| **ML Framework** | scikit-learn | ≥1.3.0 | Classification, regression algorithms |
| **Deep Learning** | TensorFlow | ≥2.15.0 | Neural networks (optional) |
| **Gradient Boosting** | XGBoost | ≥2.0.0 | Gradient boosting trees |
| **Light GBM** | LightGBM | ≥4.1.0 | Fast gradient boosting |
| **NLP** | NLTK | ≥3.8.0 | Natural language processing toolkit |
| **NLP Models** | spaCy | ≥3.7.0 | Industrial NLP |
| **Transformers** | transformers | ≥4.35.0 | Pre-trained language models |
| **Sentiment** | VADER | ≥3.3.2 | Social media/financial sentiment |
| **Sentiment** | TextBlob | ≥0.17.0 | Simple sentiment analysis |

### Trading & Execution Libraries

| Component | Library | Version | Purpose |
|-----------|---------|---------|---------|
| **Stock Broker** | Alpaca API | - | Paper/live stock trading |
| **Crypto Exchange** | Binance API | via CCXT | Cryptocurrency trading |
| **HTTP Client** | httpx | ≥0.25.0 | Async HTTP requests |
| **HTTP Client** | aiohttp | ≥3.9.0 | Alternative async HTTP |
| **News Feeds** | feedparser | ≥6.0.0 | RSS news parsing |

### Logging & Export Libraries

| Component | Library | Version | Purpose |
|-----------|---------|---------|---------|
| **Excel Export** | openpyxl | ≥3.1.0 | Trade log Excel files with formatting |

### Frontend Libraries

| Component | Library | Version | Purpose |
|-----------|---------|---------|---------|
| **Framework** | React | 18.x | UI component framework |
| **Language** | TypeScript | 5.x | Type safety |
| **Styling** | TailwindCSS | 3.x | Utility-first CSS framework |
| **Charts** | Chart.js | 4.x | Data visualization |
| **Charts** | react-chartjs-2 | 5.x | React Chart.js wrapper |
| **HTTP** | Axios | 1.x | API requests |
| **Routing** | React Router | 6.x | Client-side routing |
| **Icons** | Lucide React | - | Icon library |
| **Date** | date-fns | 2.x | Date formatting utilities |

---

## Project Structure

```
gtax_admin/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   │
│   │   ├── api/                       # API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auto_trading.py        # Autonomous trading control endpoints
│   │   │   ├── backtest.py            # Backtesting endpoints
│   │   │   ├── patterns.py            # Chart pattern detection endpoints
│   │   │   ├── scanner.py             # Market scanner endpoints
│   │   │   ├── sentiment.py           # News sentiment endpoints
│   │   │   ├── signals.py             # Trading signals endpoints
│   │   │   ├── trade_log.py           # Excel log endpoints
│   │   │   ├── trades.py              # Trade execution endpoints
│   │   │   └── websocket.py           # Real-time WebSocket updates
│   │   │
│   │   ├── core/                      # Core Configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py              # Application settings from env
│   │   │
│   │   ├── db/                        # Database Layer
│   │   │   ├── __init__.py
│   │   │   ├── database.py            # Database connection & sessions
│   │   │   └── models.py              # SQLAlchemy ORM models
│   │   │
│   │   └── services/                  # Business Logic Services
│   │       ├── __init__.py
│   │       │
│   │       ├── ai/                    # AI Decision Engine
│   │       │   ├── __init__.py
│   │       │   └── decision_engine.py # Weighted scoring AI system
│   │       │
│   │       ├── data/                  # Data Fetching
│   │       │   ├── __init__.py
│   │       │   └── data_fetcher.py    # Market data service (yfinance)
│   │       │
│   │       ├── learning/              # Machine Learning
│   │       │   ├── __init__.py
│   │       │   └── model_trainer.py   # Signal prediction model trainer
│   │       │
│   │       ├── logging/               # Trade Logging
│   │       │   ├── __init__.py
│   │       │   └── trade_logger.py    # Excel trade logger (openpyxl)
│   │       │
│   │       ├── orchestrator/          # Autonomous Trading
│   │       │   ├── __init__.py
│   │       │   └── trading_orchestrator.py  # Main autonomous loop
│   │       │
│   │       ├── patterns/              # Chart Patterns
│   │       │   ├── __init__.py
│   │       │   └── pattern_detector.py # Pattern recognition (scipy)
│   │       │
│   │       ├── scanner/               # Market Scanner
│   │       │   ├── __init__.py
│   │       │   └── market_scanner.py  # Opportunity scanner
│   │       │
│   │       ├── sentiment/             # News Sentiment
│   │       │   ├── __init__.py
│   │       │   └── news_analyzer.py   # Sentiment analysis (VADER)
│   │       │
│   │       └── trading/               # Trade Execution
│   │           ├── __init__.py
│   │           └── trade_executor.py  # Order execution & risk mgmt
│   │
│   ├── logs/
│   │   └── trades/                    # Excel trade logs location
│   │       └── trade_log_YYYY_MM.xlsx
│   │
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/                # Reusable UI components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── SignalCard.tsx
│   │   │   ├── StockChart.tsx
│   │   │   ├── PortfolioSummary.tsx
│   │   │   └── SentimentIndicator.tsx
│   │   │
│   │   ├── pages/                     # Page components
│   │   │   ├── Dashboard.tsx          # Main dashboard
│   │   │   ├── Signals.tsx            # Signal list page
│   │   │   ├── Portfolio.tsx          # Portfolio management
│   │   │   ├── Backtest.tsx           # Backtesting interface
│   │   │   └── StockDetail.tsx        # Individual stock analysis
│   │   │
│   │   ├── services/                  # API services
│   │   │   ├── api.ts                 # REST API client
│   │   │   └── websocket.ts           # WebSocket client
│   │   │
│   │   ├── types/                     # TypeScript definitions
│   │   │   └── index.ts
│   │   │
│   │   ├── App.tsx                    # Main app component
│   │   ├── index.tsx                  # Entry point
│   │   └── index.css                  # TailwindCSS imports
│   │
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── docker-compose.yml                 # Docker orchestration
├── DOCUMENTATION.md                   # This file
└── README.md                          # Quick start guide
```

---

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- Redis (optional, for caching)
- PostgreSQL (optional, SQLite works for development)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Running the Application

**Option 1: Manual Start**

```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

**Option 2: Docker Compose**

```bash
docker-compose up -d
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## Configuration

### Environment Variables (.env)

```env
# ═══════════════════════════════════════════════════════════════════
# APPLICATION SETTINGS
# ═══════════════════════════════════════════════════════════════════
APP_NAME=AI Trading Platform
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# ═══════════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
# SQLite (Development):
DATABASE_URL=sqlite+aiosqlite:///./trading.db

# PostgreSQL (Production):
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/tradingdb

# ═══════════════════════════════════════════════════════════════════
# REDIS CACHE (Optional)
# ═══════════════════════════════════════════════════════════════════
REDIS_URL=redis://localhost:6379/0

# ═══════════════════════════════════════════════════════════════════
# EXTERNAL API KEYS (Optional for paper trading)
# ═══════════════════════════════════════════════════════════════════
NEWS_API_KEY=your-newsapi-key
ALPHA_VANTAGE_KEY=your-alpha-vantage-key

# ═══════════════════════════════════════════════════════════════════
# TRADING BROKER APIS (For real trading)
# ═══════════════════════════════════════════════════════════════════
# Alpaca (Stocks)
ALPACA_API_KEY=your-alpaca-key
ALPACA_SECRET_KEY=your-alpaca-secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading

# Binance (Crypto)
BINANCE_API_KEY=your-binance-key
BINANCE_SECRET_KEY=your-binance-secret

# ═══════════════════════════════════════════════════════════════════
# AI DECISION ENGINE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
AI_TECHNICAL_WEIGHT=0.4      # 40% weight to technical analysis
AI_PATTERN_WEIGHT=0.3        # 30% weight to chart patterns
AI_SENTIMENT_WEIGHT=0.3      # 30% weight to news sentiment
AI_CONFIDENCE_THRESHOLD=0.65 # Minimum confidence to generate signal

# ═══════════════════════════════════════════════════════════════════
# AUTONOMOUS TRADING SETTINGS
# ═══════════════════════════════════════════════════════════════════
AUTO_START_TRADING=true      # Start trading automatically on startup
AUTO_TRADING_INTERVAL=300    # Market scan interval (seconds) - 5 min
AUTO_MAX_POSITIONS=5         # Maximum concurrent open positions
AUTO_CONFIDENCE_THRESHOLD=0.7 # Minimum confidence to auto-execute
AUTO_TRADE_24_7=true         # Trade outside market hours (for crypto)

# ═══════════════════════════════════════════════════════════════════
# RISK MANAGEMENT
# ═══════════════════════════════════════════════════════════════════
MAX_POSITION_SIZE=0.1        # 10% of portfolio per position maximum
DEFAULT_STOP_LOSS=0.02       # 2% stop loss from entry
DEFAULT_TAKE_PROFIT=0.05     # 5% take profit target

# ═══════════════════════════════════════════════════════════════════
# WATCHLIST SYMBOLS
# ═══════════════════════════════════════════════════════════════════
SCANNER_SYMBOLS=["AAPL","GOOGL","MSFT","AMZN","META","TSLA","NVDA","AMD","JPM","BAC","BTC-USD","ETH-USD","SOL-USD"]
```

---

## Workflow

### Complete Autonomous Trading Cycle

The system runs through these steps continuously:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        STEP 1: APPLICATION STARTUP                      │
├────────────────────────────────────────────────────────────────────────┤
│  What Happens:                                                          │
│  • FastAPI server starts on port 8000                                  │
│  • Database connection established and tables created                   │
│  • AutomatedTradingOrchestrator initializes                            │
│  • If AUTO_START_TRADING=true, trading loop begins immediately         │
│                                                                         │
│  Libraries Used: FastAPI, SQLAlchemy, asyncio, Loguru                  │
│  File: backend/app/main.py                                             │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   STEP 2: MARKET SCANNING (Every 5 minutes)            │
├────────────────────────────────────────────────────────────────────────┤
│  What Happens:                                                          │
│  • Fetches latest price data for all watchlist symbols                 │
│  • Calculates opportunity metrics:                                      │
│    - Price momentum (% change over periods)                            │
│    - Volume surge (current vs 20-day average)                          │
│    - Volatility (ATR-based)                                            │
│    - RSI levels (overbought/oversold)                                  │
│  • Ranks symbols by composite opportunity score                        │
│  • Selects top N symbols for detailed analysis                         │
│                                                                         │
│  Libraries Used: yfinance, pandas, numpy, ta                           │
│  File: backend/app/services/scanner/market_scanner.py                  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      STEP 3: TECHNICAL ANALYSIS                         │
├────────────────────────────────────────────────────────────────────────┤
│  What Happens (for each selected symbol):                               │
│                                                                         │
│  Indicators Calculated:                                                 │
│  ┌──────────────────┬─────────────────────────────────────────────┐   │
│  │ RSI (14)         │ <30 = Oversold (Bullish)                    │   │
│  │                  │ >70 = Overbought (Bearish)                  │   │
│  ├──────────────────┼─────────────────────────────────────────────┤   │
│  │ MACD             │ Line > Signal = Bullish                     │   │
│  │                  │ Line < Signal = Bearish                     │   │
│  ├──────────────────┼─────────────────────────────────────────────┤   │
│  │ Bollinger Bands  │ Price < Lower = Potential Buy               │   │
│  │                  │ Price > Upper = Potential Sell              │   │
│  ├──────────────────┼─────────────────────────────────────────────┤   │
│  │ Moving Averages  │ Price > SMA 50 > SMA 200 = Uptrend         │   │
│  │ (SMA 20/50/200)  │ Price < SMA 50 < SMA 200 = Downtrend       │   │
│  ├──────────────────┼─────────────────────────────────────────────┤   │
│  │ Volume           │ Above average = Confirmation                │   │
│  ├──────────────────┼─────────────────────────────────────────────┤   │
│  │ ATR (14)         │ Used for stop-loss calculation             │   │
│  └──────────────────┴─────────────────────────────────────────────┘   │
│                                                                         │
│  Output: Technical Score (0.0 to 1.0)                                  │
│                                                                         │
│  Libraries Used: ta, ta-lib, pandas, numpy                             │
│  File: backend/app/services/ai/decision_engine.py                      │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    STEP 4: CHART PATTERN DETECTION                      │
├────────────────────────────────────────────────────────────────────────┤
│  What Happens:                                                          │
│  • Analyzes price history to identify patterns                         │
│  • Uses peak/trough detection algorithm                                │
│                                                                         │
│  Patterns Detected:                                                     │
│  ┌──────────────────────┬──────────┬──────────────────────────────┐   │
│  │ Pattern              │ Type     │ Indication                   │   │
│  ├──────────────────────┼──────────┼──────────────────────────────┤   │
│  │ Double Bottom        │ Bullish  │ Reversal from downtrend      │   │
│  │ Double Top           │ Bearish  │ Reversal from uptrend        │   │
│  │ Head & Shoulders     │ Bearish  │ Strong reversal signal       │   │
│  │ Inverse H&S          │ Bullish  │ Strong reversal signal       │   │
│  │ Ascending Triangle   │ Bullish  │ Breakout continuation        │   │
│  │ Descending Triangle  │ Bearish  │ Breakdown continuation       │   │
│  │ Bull Flag            │ Bullish  │ Pullback in uptrend          │   │
│  │ Bear Flag            │ Bearish  │ Bounce in downtrend          │   │
│  │ Support Level        │ Neutral  │ Price floor                  │   │
│  │ Resistance Level     │ Neutral  │ Price ceiling                │   │
│  └──────────────────────┴──────────┴──────────────────────────────┘   │
│                                                                         │
│  Output: Pattern Score (0.0 to 1.0) + List of detected patterns        │
│                                                                         │
│  Libraries Used: numpy, scipy (argrelextrema for peaks/troughs)        │
│  File: backend/app/services/patterns/pattern_detector.py               │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   STEP 5: NEWS SENTIMENT ANALYSIS                       │
├────────────────────────────────────────────────────────────────────────┤
│  What Happens:                                                          │
│  1. Fetch recent news articles (last 24-48 hours)                      │
│     - NewsAPI for financial news                                       │
│     - RSS feeds from financial sites                                   │
│                                                                         │
│  2. Process each article:                                               │
│     - Extract headline and summary text                                │
│     - Clean and normalize text                                         │
│                                                                         │
│  3. Run sentiment analysis:                                             │
│     ┌────────────────────────────────────────────────────────────┐    │
│     │ VADER Sentiment Analyzer                                    │    │
│     │ • Optimized for social media and financial text            │    │
│     │ • Returns: compound score (-1 to +1)                       │    │
│     │ • Handles: negations, intensifiers, punctuation            │    │
│     ├────────────────────────────────────────────────────────────┤    │
│     │ TextBlob                                                    │    │
│     │ • General purpose sentiment                                │    │
│     │ • Returns: polarity (-1 to +1), subjectivity (0 to 1)     │    │
│     └────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  4. Aggregate scores:                                                   │
│     - Average VADER and TextBlob scores                                │
│     - Apply recency weighting (newer = higher weight)                  │
│     - Normalize to 0-1 scale                                           │
│                                                                         │
│  Score Interpretation:                                                  │
│  ┌────────────┬───────────────────┐                                    │
│  │ 0.0 - 0.3  │ Very Negative     │                                    │
│  │ 0.3 - 0.45 │ Negative          │                                    │
│  │ 0.45 - 0.55│ Neutral           │                                    │
│  │ 0.55 - 0.7 │ Positive          │                                    │
│  │ 0.7 - 1.0  │ Very Positive     │                                    │
│  └────────────┴───────────────────┘                                    │
│                                                                         │
│  Output: Sentiment Score (0.0 to 1.0)                                  │
│                                                                         │
│  Libraries Used: nltk, vaderSentiment, textblob, feedparser, httpx    │
│  File: backend/app/services/sentiment/news_analyzer.py                 │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      STEP 6: AI DECISION ENGINE                         │
├────────────────────────────────────────────────────────────────────────┤
│  What Happens:                                                          │
│  Combines all analysis scores using weighted average                   │
│                                                                         │
│  ╔════════════════════════════════════════════════════════════════╗   │
│  ║  COMPOSITE SCORE FORMULA:                                       ║   │
│  ║                                                                  ║   │
│  ║  Score = (Technical × 0.40) +                                   ║   │
│  ║          (Pattern × 0.30) +                                      ║   │
│  ║          (Sentiment × 0.30)                                      ║   │
│  ╚════════════════════════════════════════════════════════════════╝   │
│                                                                         │
│  Signal Generation Rules:                                               │
│  ┌─────────────────┬─────────────────┬────────────────────────────┐   │
│  │ Composite Score │ Technical Score │ Signal Generated           │   │
│  ├─────────────────┼─────────────────┼────────────────────────────┤   │
│  │ > 0.65          │ > 0.50          │ BUY (Strong bullish)       │   │
│  │ < 0.35          │ < 0.50          │ SELL (Strong bearish)      │   │
│  │ 0.35 - 0.65     │ any             │ HOLD (No action)           │   │
│  └─────────────────┴─────────────────┴────────────────────────────┘   │
│                                                                         │
│  Additional Outputs:                                                    │
│  • Confidence Score (how strong the signal is)                         │
│  • Target Price (based on ATR and resistance levels)                   │
│  • Stop Loss (based on ATR and support levels)                         │
│  • Detailed reasoning for the signal                                   │
│                                                                         │
│  Libraries Used: numpy, scikit-learn (optional ML enhancement)         │
│  File: backend/app/services/ai/decision_engine.py                      │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       STEP 7: TRADE EXECUTION                           │
├────────────────────────────────────────────────────────────────────────┤
│  What Happens:                                                          │
│  If Signal Confidence ≥ AUTO_CONFIDENCE_THRESHOLD (default 70%):       │
│                                                                         │
│  Pre-Trade Validation Checks:                                           │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ ✓ Symbol not already traded today                              │   │
│  │ ✓ Not exceeding max positions limit (default: 5)               │   │
│  │ ✓ Sufficient cash available                                    │   │
│  │ ✓ Position size within limits (max 10% of portfolio)           │   │
│  │ ✓ Within trading hours (if configured)                         │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Position Sizing (Risk-Based):                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ Risk Amount = Portfolio Value × Risk% (default 2%)             │   │
│  │             = $100,000 × 0.02 = $2,000                         │   │
│  │                                                                 │   │
│  │ Stop Loss = Entry Price - (ATR × 2)                            │   │
│  │           = $178.50 - ($1.88 × 2) = $174.74                    │   │
│  │                                                                 │   │
│  │ Shares = Risk Amount ÷ (Entry - Stop Loss)                     │   │
│  │        = $2,000 ÷ $3.76 = 531 shares                           │   │
│  │                                                                 │   │
│  │ Position Value Check = 531 × $178.50 = $94,783                 │   │
│  │ If > 10% of portfolio, reduce to 56 shares                     │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Order Execution:                                                       │
│  • Paper Trading: Simulated at current market price                    │
│  • Real Trading: Submit via Alpaca/Binance API                         │
│                                                                         │
│  Libraries Used: httpx, ccxt, asyncio                                  │
│  File: backend/app/services/trading/trade_executor.py                  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     STEP 8: EXCEL TRADE LOGGING                         │
├────────────────────────────────────────────────────────────────────────┤
│  What Happens:                                                          │
│  Every executed trade is logged to Excel with full details             │
│                                                                         │
│  Excel Columns Recorded:                                                │
│  ┌────────────────┬────────────────────────────────────────────────┐  │
│  │ Trade ID       │ PAPER-20260320-000001                          │  │
│  │ Date/Time      │ 2026-03-20 09:35:00                            │  │
│  │ Symbol         │ AAPL                                           │  │
│  │ Action         │ BUY                                            │  │
│  │ Quantity       │ 56                                             │  │
│  │ Entry Price    │ $178.50                                        │  │
│  │ Exit Price     │ (filled on position close)                     │  │
│  │ Stop Loss      │ $174.74                                        │  │
│  │ Take Profit    │ $187.43                                        │  │
│  │ Strategy       │ AI_COMPOSITE                                   │  │
│  │ Entry Reason   │ Strong technicals (72%); Bull flag (68%);     │  │
│  │                │ Positive sentiment (65%)                       │  │
│  │ Confidence     │ 71.2%                                          │  │
│  │ Technical Score│ 72.0%                                          │  │
│  │ Pattern Score  │ 68.0%                                          │  │
│  │ Sentiment Score│ 65.0%                                          │  │
│  │ P&L ($)        │ (calculated on exit)                           │  │
│  │ P&L (%)        │ (calculated on exit)                           │  │
│  │ Duration       │ (calculated on exit)                           │  │
│  │ Status         │ OPEN                                           │  │
│  │ Notes          │ Additional comments                            │  │
│  └────────────────┴────────────────────────────────────────────────┘  │
│                                                                         │
│  File Location: logs/trades/trade_log_YYYY_MM.xlsx                     │
│  (New file created monthly)                                            │
│                                                                         │
│  Libraries Used: openpyxl (with styling and formulas)                  │
│  File: backend/app/services/logging/trade_logger.py                    │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  STEP 9: POSITION MONITORING (Every 30s)                │
├────────────────────────────────────────────────────────────────────────┤
│  What Happens:                                                          │
│  For each open position, the system continuously:                      │
│                                                                         │
│  1. Fetches current market price                                       │
│  2. Updates unrealized P&L                                             │
│  3. Checks stop-loss trigger:                                          │
│     If current_price ≤ stop_loss → AUTO SELL                          │
│  4. Checks take-profit trigger:                                        │
│     If current_price ≥ take_profit → AUTO SELL                        │
│  5. Logs exit to Excel with final P&L                                  │
│                                                                         │
│  Libraries Used: yfinance, asyncio                                     │
│  File: backend/app/services/trading/trade_executor.py                  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        STEP 10: CYCLE REPEATS                           │
├────────────────────────────────────────────────────────────────────────┤
│  What Happens:                                                          │
│  • System waits for next scan interval (default: 5 minutes)            │
│  • Daily trade list resets at midnight (allows re-trading symbols)     │
│  • Loop continues 24/7 if AUTO_TRADE_24_7=true                         │
│  • Or only during market hours (9:30 AM - 4:00 PM ET) if false         │
│                                                                         │
│  The cycle repeats indefinitely until manually stopped via:            │
│  POST /api/auto/stop                                                   │
│                                                                         │
│  File: backend/app/services/orchestrator/trading_orchestrator.py       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Modules Documentation

### 1. Market Scanner

**File**: `backend/app/services/scanner/market_scanner.py`

**Purpose**: Continuously scans the market for trading opportunities.

**Key Functions**:
```python
# Scan all watchlist symbols
opportunities = await market_scanner.scan_markets()

# Get top ranked opportunities
top = await market_scanner.get_top_opportunities(limit=5)

# Analyze specific symbol
analysis = await market_scanner.analyze_symbol("AAPL")
```

**Opportunity Score Factors**:
- Momentum (price change %)
- Volume surge (vs average)
- Volatility (ATR-based)
- RSI extremes (oversold/overbought)

---

### 2. AI Decision Engine

**File**: `backend/app/services/ai/decision_engine.py`

**Purpose**: The brain - combines all analysis into actionable signals.

**Key Functions**:
```python
# Full analysis with signal generation
result = await ai_decision_engine.analyze(symbol="AAPL")

# Generate trading signal only
signal = await ai_decision_engine.generate_signal(symbol="AAPL")

# Technical analysis only
tech_score = ai_decision_engine.get_technical_score(ohlcv_data)
```

**Signal Output**:
```python
{
    "symbol": "AAPL",
    "signal_type": "BUY",
    "confidence": 0.72,
    "technical_score": 0.75,
    "pattern_score": 0.68,
    "sentiment_score": 0.65,
    "entry_price": 178.50,
    "stop_loss": 174.74,
    "target_price": 187.43,
    "reason": "Strong technicals; Bull flag pattern; Positive news sentiment"
}
```

---

### 3. Chart Pattern Detector

**File**: `backend/app/services/patterns/pattern_detector.py`

**Purpose**: Identifies chart patterns that predict price movements.

**Key Functions**:
```python
# Detect all patterns
patterns = await pattern_detector.detect_patterns("AAPL")

# Get pattern-based score
score = await pattern_detector.get_pattern_score("AAPL")
```

**Pattern Detection Algorithm**:
1. Find local peaks and troughs using `scipy.signal.argrelextrema`
2. Analyze peak/trough relationships for pattern signatures
3. Calculate pattern confidence based on formation quality

---

### 4. News Sentiment Analyzer

**File**: `backend/app/services/sentiment/news_analyzer.py`

**Purpose**: Analyzes news sentiment for trading decisions.

**Key Functions**:
```python
# Get sentiment analysis
sentiment = await news_analyzer.analyze_sentiment("AAPL")

# Get raw news articles
news = await news_analyzer.fetch_news("AAPL")
```

**Sentiment Pipeline**:
1. Fetch news from NewsAPI and RSS feeds
2. Extract and clean text
3. Run VADER sentiment analysis
4. Run TextBlob as secondary check
5. Average and normalize scores

---

### 5. Trade Executor

**File**: `backend/app/services/trading/trade_executor.py`

**Purpose**: Executes trades with risk management.

**Key Functions**:
```python
# Execute a trade
result = await trade_executor.execute_trade(
    symbol="AAPL",
    side="BUY",
    risk_pct=0.02,
    stop_loss=174.74,
    take_profit=187.43,
    strategy="AI_COMPOSITE",
    reason="Strong signal",
    signal_data=signal
)

# Get portfolio
portfolio = trade_executor.get_portfolio()

# Check stop loss / take profit
await trade_executor.update_and_check_orders()
```

---

### 6. Trading Orchestrator

**File**: `backend/app/services/orchestrator/trading_orchestrator.py`

**Purpose**: Coordinates autonomous trading loop.

**Configuration**:
```python
AutomatedTradingOrchestrator(
    scan_interval=300,           # Scan every 5 minutes
    position_check_interval=30,   # Check positions every 30 seconds
    max_positions=5,             # Max 5 concurrent positions
    min_confidence=0.70,         # Minimum 70% confidence to trade
    auto_execute=True,           # Auto-execute trades
    trading_hours_only=False     # Trade 24/7 (for crypto)
)
```

---

### 7. Excel Trade Logger

**File**: `backend/app/services/logging/trade_logger.py`

**Purpose**: Maintains detailed Excel trade logs.

**Key Functions**:
```python
# Log a trade entry
trade_logger.log_entry(
    trade_id="PAPER-20260320-000001",
    symbol="AAPL",
    action="BUY",
    quantity=56,
    entry_price=178.50,
    stop_loss=174.74,
    take_profit=187.43,
    strategy="AI_COMPOSITE",
    entry_reason="Strong technicals; Bull flag; Positive sentiment",
    signal_confidence=0.72,
    technical_score=0.75,
    pattern_score=0.68,
    sentiment_score=0.65
)

# Log a trade exit
trade_logger.log_exit(
    trade_id="PAPER-20260320-000001",
    exit_price=185.00,
    pnl=364.00,
    pnl_pct=3.64,
    exit_reason="Take profit triggered"
)

# Get summary statistics
summary = trade_logger.get_trade_summary()
```

---

## API Reference

### Autonomous Trading Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auto/status` | GET | Get orchestrator status and statistics |
| `/api/auto/start` | POST | Start autonomous trading |
| `/api/auto/stop` | POST | Stop autonomous trading |
| `/api/auto/configure` | POST | Update trading configuration |
| `/api/auto/run-cycle` | POST | Manually trigger one trading cycle |
| `/api/auto/pending-signals` | GET | Get signals awaiting execution |

### Trade Log Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/log/summary` | GET | Trade statistics (win rate, P&L) |
| `/api/log/open-trades` | GET | Currently open positions |
| `/api/log/download` | GET | Download Excel log file |
| `/api/log/info` | GET | Log file information |
| `/api/log/test` | POST | Create test log entry |

### Market Analysis Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scanner/scan` | POST | Scan markets for opportunities |
| `/api/scanner/opportunities` | GET | Get top opportunities |
| `/api/scanner/analyze/{symbol}` | GET | Analyze specific symbol |
| `/api/sentiment/{symbol}` | GET | Get sentiment analysis |
| `/api/patterns/{symbol}` | GET | Detect chart patterns |
| `/api/signals/generate` | POST | Generate trading signals |
| `/api/signals/history` | GET | Get signal history |

### Trading Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/trades/execute` | POST | Execute a trade manually |
| `/api/trades/portfolio` | GET | Get portfolio summary |
| `/api/trades/positions` | GET | Get open positions |
| `/api/trades/history` | GET | Get trade history |
| `/api/trades/close/{symbol}` | POST | Close specific position |

### Backtesting Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/backtest/run` | POST | Run historical backtest |
| `/api/backtest/results/{id}` | GET | Get backtest results |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws/prices` | Real-time price updates |
| `/ws/signals` | Real-time signal notifications |
| `/ws/trades` | Trade execution notifications |

---

## Trade Logging

### Excel File Structure

**File**: `logs/trades/trade_log_2026_03.xlsx`

**Sheets**:
1. **Trades** - All trade entries
2. **Summary** - Statistics with formulas

### Sample Trade Log Entry

| Column | Value |
|--------|-------|
| Trade ID | PAPER-20260320-000001 |
| Date/Time | 2026-03-20 09:35:00 |
| Symbol | AAPL |
| Action | BUY |
| Quantity | 56 |
| Entry Price | $178.50 |
| Exit Price | $185.00 |
| Stop Loss | $174.74 |
| Take Profit | $187.43 |
| Strategy | AI_COMPOSITE |
| Entry Reason | Strong technicals (72%); Bull flag detected (68%); Positive sentiment (65%) |
| Signal Confidence | 71.2% |
| Technical Score | 72.0% |
| Pattern Score | 68.0% |
| Sentiment Score | 65.0% |
| P&L ($) | $364.00 |
| P&L (%) | 3.64% |
| Trade Duration | 4h 45m |
| Status | CLOSED |

---

## Risk Management

### Position Sizing Algorithm

```python
def calculate_position_size(portfolio_value, risk_pct, entry_price, stop_loss):
    # Calculate maximum risk amount
    risk_amount = portfolio_value * risk_pct  # e.g., $100,000 * 0.02 = $2,000
    
    # Calculate price risk per share
    price_risk = abs(entry_price - stop_loss)  # e.g., $178.50 - $174.74 = $3.76
    
    # Calculate position size
    shares = risk_amount / price_risk  # e.g., $2,000 / $3.76 = 531 shares
    
    # Check maximum position size limit
    position_value = shares * entry_price  # e.g., 531 * $178.50 = $94,783
    max_position = portfolio_value * MAX_POSITION_SIZE  # e.g., $100,000 * 0.10 = $10,000
    
    if position_value > max_position:
        shares = max_position / entry_price  # e.g., $10,000 / $178.50 = 56 shares
    
    return shares
```

### Default Risk Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `risk_per_trade` | 2% | Maximum loss per trade |
| `DEFAULT_STOP_LOSS` | 2% | Stop loss distance from entry |
| `DEFAULT_TAKE_PROFIT` | 5% | Take profit target |
| `MAX_POSITION_SIZE` | 10% | Maximum portfolio % per position |
| `AUTO_MAX_POSITIONS` | 5 | Maximum concurrent positions |

---

## Troubleshooting

### Common Issues and Solutions

**1. "Import could not be resolved" in IDE**
```
This is normal - VS Code shows this before dependencies are installed.
Solution: pip install -r requirements.txt
```

**2. Trading not starting automatically**
```
Check these settings in .env:
- AUTO_START_TRADING=true
- View startup logs for errors
```

**3. No signals being generated**
```
Possible causes:
- AI_CONFIDENCE_THRESHOLD too high (try 0.60)
- Market data not fetching (check yfinance)
- No market hours if trading_hours_only=True
```

**4. Excel log file not created**
```
Solution:
pip install openpyxl
Check logs/trades/ directory permissions
```

**5. WebSocket connection failing**
```
Ensure backend is running on correct port
Check CORS_ORIGINS includes frontend URL
```

### Viewing Logs

**Application Logs**: Console output via Loguru
```bash
uvicorn app.main:app --log-level debug
```

**Trade Logs**: Excel files in `logs/trades/`

**API Request Logs**: Available in FastAPI debug mode

---

## Quick Reference Commands

```bash
# Start backend (development)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (development)
cd frontend
npm start

# Docker start
docker-compose up -d

# Docker stop
docker-compose down

# View API documentation
# Open: http://localhost:8000/docs

# Check trading status
curl http://localhost:8000/api/auto/status

# Start trading manually
curl -X POST http://localhost:8000/api/auto/start

# Stop trading
curl -X POST http://localhost:8000/api/auto/stop

# Download trade log
curl http://localhost:8000/api/log/download -o trade_log.xlsx
```

---

## Contact & Support

For issues and feature requests, please open a GitHub issue.

---

*Documentation last updated: March 2026*
