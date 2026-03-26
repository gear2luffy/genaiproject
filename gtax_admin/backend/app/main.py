"""
Main FastAPI application for AI Trading Platform.

This application starts automatically and runs the full trading pipeline:
- Market scanning
- AI signal generation  
- Automated trade execution
- Position monitoring
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.db.database import init_db, close_db
from app.api import scanner, sentiment, patterns, signals, trades, backtest, websocket, auto_trading, trade_log


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 Starting AI Trading Platform...")
    logger.info("=" * 60)
    
    await init_db()
    logger.info("✅ Database initialized")
    
    # Import orchestrator
    from app.services.orchestrator.trading_orchestrator import trading_orchestrator
    
    # Start the automated trading system
    orchestrator_task = None
    if settings.AUTO_START_TRADING:
        logger.info("🤖 Auto-starting automated trading system...")
        orchestrator_task = asyncio.create_task(trading_orchestrator.start())
    else:
        logger.info("⏸️ Automated trading NOT auto-started (call /api/auto/start to begin)")
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 Shutting down AI Trading Platform...")
    
    # Stop orchestrator
    if trading_orchestrator.is_running:
        trading_orchestrator.stop()
    
    if orchestrator_task:
        orchestrator_task.cancel()
        try:
            await orchestrator_task
        except asyncio.CancelledError:
            pass
    
    await close_db()
    logger.info("✅ Shutdown complete")
    logger.info("=" * 60)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="An intelligent trading system with AI-powered analysis",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auto_trading.router, prefix="/api", tags=["Automated Trading"])
app.include_router(trade_log.router, prefix="/api", tags=["Trade Log"])
app.include_router(scanner.router, prefix="/api", tags=["Scanner"])
app.include_router(sentiment.router, prefix="/api", tags=["Sentiment"])
app.include_router(patterns.router, prefix="/api", tags=["Patterns"])
app.include_router(signals.router, prefix="/api", tags=["Signals"])
app.include_router(trades.router, prefix="/api", tags=["Trades"])
app.include_router(backtest.router, prefix="/api", tags=["Backtest"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "scanner": "running",
            "sentiment": "available",
            "patterns": "available",
            "ai_engine": "available"
        }
    }
