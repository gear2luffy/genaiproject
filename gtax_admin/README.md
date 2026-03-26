# AI Trading Platform

An intelligent, **fully autonomous** trading system that automatically selects stocks/assets, analyzes them using chart patterns + technical indicators, incorporates news sentiment, and executes trades based on AI decisions - **all without human intervention**.

> 📖 **For complete documentation with workflow diagrams and library details, see [DOCUMENTATION.md](DOCUMENTATION.md)**

## ✨ Key Highlights

- 🤖 **Fully Autonomous** - Starts trading automatically, runs 24/7
- 📊 **AI-Powered Decisions** - Weighted scoring: Technical (40%) + Patterns (30%) + Sentiment (30%)
- 📝 **Excel Trade Logging** - Every trade logged with full analysis data
- 💰 **Risk Management** - Position sizing, stop-loss, take-profit built-in
- 📈 **Multi-Asset** - Stocks and Cryptocurrencies supported

## 🏗️ Project Structure

```
gtax_admin/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # REST API routes
│   │   ├── core/              # Core configuration
│   │   ├── db/                # Database models & connection
│   │   ├── services/          # Business logic services
│   │   │   ├── ai/            # AI Decision Engine
│   │   │   ├── data/          # Data fetching services
│   │   │   ├── scanner/       # Market Scanner
│   │   │   ├── sentiment/     # News Sentiment Analysis (VADER, TextBlob)
│   │   │   ├── patterns/      # Chart Pattern Detection (scipy)
│   │   │   ├── learning/      # ML Learning Model
│   │   │   ├── logging/       # Excel Trade Logger (openpyxl)
│   │   │   ├── orchestrator/  # Autonomous Trading Controller
│   │   │   └── trading/       # Trade Execution & Risk Management
│   │   └── utils/             # Utility functions
│   ├── logs/trades/           # Excel trade log files
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React.js Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   └── types/             # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── DOCUMENTATION.md           # Complete documentation
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL (or SQLite for development)

### Development Setup

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm start
```

3. **Using Docker**
```bash
docker-compose up --build
```

## 📌 Features

### 1. Autonomous Trading Orchestrator ⭐ NEW
- **Auto-starts** on application launch
- Runs complete trading pipeline automatically
- Configurable scan intervals (default: 5 minutes)
- 24/7 operation support for crypto
- API controls: start, stop, configure

### 2. Market Scanner
- Scans multiple stocks/crypto pairs continuously
- Filters by volume spikes, volatility, trend strength
- Ranks top trading opportunities

### 3. News Sentiment Analysis
- Fetches news from NewsAPI, RSS feeds
- NLP-based sentiment analysis using **VADER** and **TextBlob**
- Assigns sentiment score per stock (0-1 scale)

### 4. Chart Pattern Detection
- Detects: Head & Shoulders, Double Top/Bottom, Triangles, Flags
- Identifies Support/Resistance levels
- Uses **scipy** peak detection algorithms

### 5. AI Decision Engine
- Combines chart patterns, technical indicators, sentiment
- **Weighted formula**: Technical (40%) + Patterns (30%) + Sentiment (30%)
- Outputs Buy/Sell/Hold with confidence score

### 6. Excel Trade Logging ⭐ NEW
- Automatic logging of every trade to Excel
- Records: Entry reason, AI scores, P&L, duration
- Monthly files in `logs/trades/`
- Download via API endpoint

### 7. Risk Management
- Position sizing based on risk percentage
- Automatic stop-loss calculation (ATR-based)
- Take-profit targets with risk-reward ratio
- Maximum position limits

### 8. Trade Execution
- Paper trading mode (default)
- Real trading integration (Alpaca, Binance)
- Risk management: Stop loss, Take profit, Position sizing

## 🔗 API Endpoints

### Autonomous Trading Control
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auto/status` | GET | Get trading status |
| `/api/auto/start` | POST | Start autonomous trading |
| `/api/auto/stop` | POST | Stop autonomous trading |
| `/api/auto/configure` | POST | Update configuration |

### Trade Logging
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/log/summary` | GET | Trade statistics |
| `/api/log/download` | GET | Download Excel file |
| `/api/log/open-trades` | GET | Currently open trades |

### Market Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scanner/scan` | POST | Returns top stocks to trade |
| `/api/sentiment/{symbol}` | GET | Sentiment per stock |
| `/api/patterns/{symbol}` | GET | Detected chart patterns |
| `/api/signals/generate` | POST | AI trading decisions |

### Trading
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/trades/execute` | POST | Execute trade |
| `/api/trades/portfolio` | GET | Get portfolio |
| `/api/backtest/run` | POST | Run simulation |
| `/ws/prices` | WebSocket | Live market updates |

## 📊 Tech Stack

### Backend
- **Framework**: FastAPI, Uvicorn
- **Database**: SQLAlchemy, PostgreSQL/SQLite
- **Caching**: Redis, Celery

### Data & Analysis
- **Market Data**: yfinance, CCXT
- **Technical Analysis**: ta, ta-lib, pandas, numpy
- **Pattern Detection**: scipy (peak detection)

### AI & Sentiment
- **Sentiment**: VADER, TextBlob
- **NLP**: NLTK, spaCy
- **ML**: scikit-learn, XGBoost

### Logging & Export
- **Excel**: openpyxl (trade logging)
- **Logging**: Loguru

### Frontend
- **Framework**: React 18, TypeScript
- **Styling**: TailwindCSS
- **Charts**: Chart.js, react-chartjs-2
- **HTTP**: Axios

### Infrastructure
- **Containerization**: Docker, Docker Compose

## 📄 License

MIT License

---

## 🚦 Autonomous Trading Quick Start

Once the backend starts, trading begins automatically! Control via:

```bash
# Check status
curl http://localhost:8000/api/auto/status

# Stop trading
curl -X POST http://localhost:8000/api/auto/stop

# Start trading
curl -X POST http://localhost:8000/api/auto/start

# Download trade log
curl http://localhost:8000/api/log/download -o trades.xlsx
```

**Configuration** (in `.env`):
```
AUTO_START_TRADING=true
AUTO_TRADING_INTERVAL=300
AUTO_MAX_POSITIONS=5
AUTO_CONFIDENCE_THRESHOLD=0.7
```

---

*For complete workflow diagrams and library documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)*
