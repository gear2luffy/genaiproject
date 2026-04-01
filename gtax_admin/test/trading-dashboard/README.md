# Trading Dashboard

A full-stack trading dashboard application built with Go (backend), React (frontend), and PostgreSQL (database), containerized with Docker.

## Features

- **JWT Authentication**: Secure login/registration system
- **Dashboard**: Overview of trending stocks, top gainers, and top losers
- **Stock Search**: Search for stocks by symbol or name
- **Historical Data**: View price trends for the last 1 day, 1 week, 30 days, or 60 days
- **Interactive Charts**: Visualize price movements with responsive charts
- **Price Tables**: Detailed historical price data in tabular format
- **Market Data Pipeline**: Backend automatically fetches and stores market data

## Tech Stack

- **Backend**: Go (Golang) with Gin framework
- **Frontend**: React with Chart.js
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  PostgreSQL │
│   (React)   │     │    (Go)     │     │  Database   │
│   Port 3000 │     │  Port 8080  │     │  Port 5432  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Alpha Vantage│
                    │     API     │
                    └─────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed on your machine

### Running the Application

1. Clone the repository or navigate to the project directory:
```bash
cd trading-dashboard
```

2. Start all services with a single command:
```bash
docker-compose up --build
```

3. Wait for the services to start (this may take a few minutes on first run)

4. Access the application:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8080
   - **Health Check**: http://localhost:8080/health

### First-time Use

1. Open http://localhost:3000 in your browser
2. Click "Sign Up" to create a new account
3. Enter your name, email, and password (min 6 characters)
4. You'll be automatically logged in and redirected to the dashboard

## API Endpoints

### Authentication
- `POST /api/register` - Register a new user
- `POST /api/login` - Login and receive JWT token
- `GET /api/user` - Get current user info (protected)

### Market Data
- `GET /api/stocks/search?q=query` - Search stocks (protected)
- `GET /api/stocks/:symbol` - Get stock details (protected)
- `GET /api/stocks/:symbol/prices?days=30` - Get price history (protected)
- `GET /api/dashboard/summary` - Get dashboard data (protected)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Stocks Table
```sql
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'stock',
    exchange VARCHAR(50),
    sector VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Price History Table
```sql
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    open_price DECIMAL(15, 4),
    high_price DECIMAL(15, 4),
    low_price DECIMAL(15, 4),
    close_price DECIMAL(15, 4) NOT NULL,
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date)
);
```

## Project Structure

```
trading-dashboard/
├── backend/
│   ├── cmd/
│   │   └── server/
│   │       └── main.go
│   ├── internal/
│   │   ├── database/
│   │   │   ├── connection.go
│   │   │   └── migrations.go
│   │   ├── handlers/
│   │   │   ├── auth_handler.go
│   │   │   └── market_handler.go
│   │   ├── middleware/
│   │   │   └── middleware.go
│   │   ├── models/
│   │   │   └── models.go
│   │   ├── repository/
│   │   │   ├── user_repository.go
│   │   │   ├── stock_repository.go
│   │   │   └── price_repository.go
│   │   └── services/
│   │       ├── auth_service.go
│   │       └── market_service.go
│   ├── Dockerfile
│   └── go.mod
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── StockChart.js
│   │   │   └── PriceTable.js
│   │   ├── context/
│   │   │   └── AuthContext.js
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   └── Dashboard.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Configuration

### Environment Variables

#### Backend
| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | localhost |
| `DB_PORT` | PostgreSQL port | 5432 |
| `DB_USER` | Database user | postgres |
| `DB_PASSWORD` | Database password | postgres |
| `DB_NAME` | Database name | trading_db |
| `JWT_SECRET` | Secret key for JWT tokens | (default provided) |
| `PORT` | Backend server port | 8080 |
| `ALPHA_VANTAGE_API_KEY` | API key for real market data | (optional) |

#### Frontend
| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | http://localhost:8080/api |

## Market Data

By default, the application uses simulated market data for demonstration purposes. The simulated data:
- Generates realistic price movements based on actual stock base prices
- Creates 60 days of historical data for each stock
- Updates periodically

### Using Real Market Data

To use real market data from Alpha Vantage:

1. Get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Add the API key to `docker-compose.yml`:
```yaml
backend:
  environment:
    ALPHA_VANTAGE_API_KEY: your-api-key-here
```
3. Restart the services

Note: The free tier has a limit of 5 API calls per minute and 500 per day.

## Development

### Running Backend Locally

```bash
cd backend
go mod download
DB_HOST=localhost DB_PORT=5432 DB_USER=postgres DB_PASSWORD=postgres DB_NAME=trading_db go run cmd/server/main.go
```

### Running Frontend Locally

```bash
cd frontend
npm install
npm start
```

## Stopping the Application

```bash
docker-compose down
```

To also remove the database volume:
```bash
docker-compose down -v
```

## Troubleshooting

### Database connection issues
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check logs: `docker-compose logs db`

### Backend not starting
- Wait for database to be ready (it has a health check)
- Check logs: `docker-compose logs backend`

### Frontend not loading
- Ensure backend is running
- Check browser console for errors
- Verify API URL configuration

## License

MIT
