"""
Autonomous Trading Orchestrator.

This module orchestrates the entire automated trading pipeline:
1. Scan markets for opportunities
2. Analyze with technical indicators, patterns, and sentiment
3. Generate AI trading signals
4. Execute trades automatically based on signals
5. Manage positions (stop loss, take profit)

Runs continuously without human intervention.
"""
import asyncio
from datetime import datetime, time as dt_time
from typing import Dict, Any, List, Optional
from loguru import logger

from app.core.config import settings
from app.services.scanner.market_scanner import market_scanner
from app.services.ai.decision_engine import ai_decision_engine, SignalType
from app.services.trading.trade_executor import trade_executor, OrderSide


class AutomatedTradingOrchestrator:
    """
    Fully automated trading system that runs the complete pipeline.
    
    Features:
    - Continuous market scanning
    - Automatic signal generation
    - Auto-execution of trades based on AI decisions
    - Position management (stop loss/take profit monitoring)
    - Trading hours awareness
    - Risk management enforcement
    """
    
    def __init__(
        self,
        scan_interval: int = None,           # Scan interval in seconds
        signal_interval: int = None,         # Generate signals every N seconds
        position_check_interval: int = 30,   # Check positions every 30 seconds
        auto_execute: bool = True,           # Auto-execute trades
        max_positions: int = None,           # Maximum concurrent positions
        min_confidence: float = None,        # Minimum confidence to trade
        risk_per_trade: float = 0.02,        # 2% risk per trade
        trading_hours_only: bool = None      # Trade only during market hours (set False for 24/7 crypto)
    ):
        # Use settings from config or provided values
        self.scan_interval = scan_interval or settings.AUTO_TRADING_INTERVAL
        self.signal_interval = signal_interval or settings.AUTO_TRADING_INTERVAL
        self.position_check_interval = position_check_interval
        self.auto_execute = auto_execute
        self.max_positions = max_positions or settings.AUTO_MAX_POSITIONS
        self.min_confidence = min_confidence or settings.AUTO_CONFIDENCE_THRESHOLD
        self.risk_per_trade = risk_per_trade
        self.trading_hours_only = trading_hours_only if trading_hours_only is not None else (not settings.AUTO_TRADE_24_7)
        
        self.is_running = False
        self.last_scan_time: Optional[datetime] = None
        self.last_signal_time: Optional[datetime] = None
        self.pending_signals: List[Dict[str, Any]] = []
        self.executed_today: List[str] = []  # Symbols traded today
        
        # Statistics
        self.stats = {
            'scans_completed': 0,
            'signals_generated': 0,
            'trades_executed': 0,
            'trades_skipped': 0,
            'errors': 0,
            'start_time': None
        }
    
    def is_trading_hours(self) -> bool:
        """Check if current time is within trading hours."""
        if not self.trading_hours_only:
            return True  # Trade 24/7 (good for crypto)
        
        now = datetime.utcnow()
        
        # Skip weekends
        if now.weekday() >= 5:
            return False
        
        # US Market hours: 9:30 AM - 4:00 PM EST (14:30 - 21:00 UTC)
        market_open = dt_time(14, 30)
        market_close = dt_time(21, 0)
        current_time = now.time()
        
        return market_open <= current_time <= market_close
    
    async def scan_markets(self) -> List[Dict[str, Any]]:
        """Scan markets for trading opportunities."""
        try:
            logger.info("🔍 Scanning markets for opportunities...")
            results = await market_scanner.scan_all()
            self.last_scan_time = datetime.now()
            self.stats['scans_completed'] += 1
            logger.info(f"✅ Scan complete. Found {len(results)} candidates.")
            return results
        except Exception as e:
            logger.error(f"❌ Market scan error: {e}")
            self.stats['errors'] += 1
            return []
    
    async def generate_signals(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Generate AI trading signals for symbols."""
        try:
            logger.info(f"🧠 Generating AI signals for {len(symbols)} symbols...")
            
            signals = await ai_decision_engine.generate_bulk_signals(
                symbols,
                include_sentiment=True
            )
            
            # Filter for actionable signals
            actionable = [
                s for s in signals 
                if s.signal != SignalType.HOLD 
                and s.confidence >= self.min_confidence
            ]
            
            self.last_signal_time = datetime.now()
            self.stats['signals_generated'] += len(actionable)
            
            logger.info(f"✅ Generated {len(actionable)} actionable signals from {len(signals)} analyzed.")
            
            return [s.to_dict() for s in actionable]
        except Exception as e:
            logger.error(f"❌ Signal generation error: {e}")
            self.stats['errors'] += 1
            return []
    
    async def execute_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a trading signal."""
        symbol = signal['symbol']
        signal_type = signal['signal']
        confidence = signal['confidence']
        
        # Check if already traded today
        if symbol in self.executed_today:
            logger.info(f"⏭️ Skipping {symbol} - already traded today")
            self.stats['trades_skipped'] += 1
            return None
        
        # Check max positions for BUY signals
        current_positions = len(trade_executor.paper_engine.positions)
        if signal_type == 'BUY' and current_positions >= self.max_positions:
            logger.info(f"⏭️ Skipping {symbol} BUY - max positions ({self.max_positions}) reached")
            self.stats['trades_skipped'] += 1
            return None
        
        # Check if we have position to sell
        if signal_type == 'SELL' and symbol not in trade_executor.paper_engine.positions:
            logger.info(f"⏭️ Skipping {symbol} SELL - no position to close")
            self.stats['trades_skipped'] += 1
            return None
        
        try:
            logger.info(f"🚀 Executing {signal_type} for {symbol} (confidence: {confidence:.1%})")
            
            # Prepare signal data for logging
            signal_data = {
                'confidence': confidence,
                'technical_score': signal.get('technical_score', 0),
                'pattern_score': signal.get('pattern_score', 0),
                'sentiment_score': signal.get('sentiment_score', 0),
                'reason': signal.get('reason', ''),
                'strategy': signal.get('strategy', 'AI_COMPOSITE')
            }
            
            # Build entry reason from signal components
            entry_reason = signal.get('reason', '')
            if not entry_reason:
                reasons = []
                if signal.get('technical_score', 0) > 0.6:
                    reasons.append(f"Strong technicals ({signal.get('technical_score', 0):.0%})")
                if signal.get('pattern_score', 0) > 0.5:
                    reasons.append(f"Pattern detected ({signal.get('pattern_score', 0):.0%})")
                if signal.get('sentiment_score', 0) > 0.5:
                    reasons.append(f"Positive sentiment ({signal.get('sentiment_score', 0):.0%})")
                entry_reason = "; ".join(reasons) if reasons else f"AI Signal confidence: {confidence:.0%}"
            
            if signal_type == 'SELL':
                # Close entire position
                position = trade_executor.paper_engine.positions[symbol]
                result = await trade_executor.execute_trade(
                    symbol=symbol,
                    side='SELL',
                    quantity=position.quantity,
                    use_risk_management=False,
                    strategy=signal.get('strategy', 'AI_COMPOSITE'),
                    reason=entry_reason,
                    signal_data=signal_data
                )
            else:
                # BUY with risk management
                result = await trade_executor.execute_trade(
                    symbol=symbol,
                    side='BUY',
                    risk_pct=self.risk_per_trade,
                    stop_loss=signal.get('stop_loss'),
                    take_profit=signal.get('target_price'),
                    use_risk_management=True,
                    strategy=signal.get('strategy', 'AI_COMPOSITE'),
                    reason=entry_reason,
                    signal_data=signal_data
                )
            
            if result.get('status') == 'success':
                self.executed_today.append(symbol)
                self.stats['trades_executed'] += 1
                logger.info(f"✅ Trade executed: {signal_type} {symbol}")
                return result
            else:
                logger.warning(f"⚠️ Trade failed: {result.get('message')}")
                self.stats['trades_skipped'] += 1
                return None
                
        except Exception as e:
            logger.error(f"❌ Trade execution error for {symbol}: {e}")
            self.stats['errors'] += 1
            return None
    
    async def check_positions(self) -> Dict[str, Any]:
        """Check and manage open positions (stop loss, take profit)."""
        try:
            result = await trade_executor.update_and_check_orders()
            
            if result.get('orders_executed', 0) > 0:
                logger.info(f"📊 Position check: {result['orders_executed']} orders triggered")
            
            return result
        except Exception as e:
            logger.error(f"❌ Position check error: {e}")
            self.stats['errors'] += 1
            return {'error': str(e)}
    
    async def run_trading_cycle(self):
        """Run one complete trading cycle."""
        logger.info("=" * 50)
        logger.info(f"🔄 Starting trading cycle at {datetime.now().isoformat()}")
        
        # Check trading hours
        if not self.is_trading_hours():
            logger.info("⏰ Outside trading hours - skipping cycle")
            return
        
        # Step 1: Scan markets
        scan_results = await self.scan_markets()
        
        if not scan_results:
            logger.info("📭 No scan results - ending cycle")
            return
        
        # Get top symbols from scan
        top_symbols = [r['symbol'] for r in scan_results[:10]]
        
        # Step 2: Generate signals
        signals = await self.generate_signals(top_symbols)
        
        if not signals:
            logger.info("📭 No actionable signals - ending cycle")
            return
        
        # Step 3: Execute signals (if auto-execute enabled)
        if self.auto_execute:
            for signal in signals:
                await self.execute_signal(signal)
                await asyncio.sleep(1)  # Small delay between trades
        else:
            logger.info(f"📋 {len(signals)} signals generated (auto-execute disabled)")
            self.pending_signals = signals
        
        # Step 4: Check existing positions
        await self.check_positions()
        
        # Log portfolio status
        portfolio = trade_executor.get_portfolio()
        logger.info(f"💰 Portfolio: ${portfolio['portfolio_value']:,.2f} | "
                   f"Cash: ${portfolio['cash']:,.2f} | "
                   f"Positions: {portfolio['positions_count']} | "
                   f"P&L: {portfolio['total_pnl_pct']:.2f}%")
    
    async def position_monitor_loop(self):
        """Continuously monitor positions for stop loss/take profit."""
        logger.info("👀 Starting position monitor...")
        
        while self.is_running:
            try:
                if self.is_trading_hours():
                    await self.check_positions()
            except Exception as e:
                logger.error(f"Position monitor error: {e}")
            
            await asyncio.sleep(self.position_check_interval)
    
    async def trading_loop(self):
        """Main trading loop."""
        logger.info("📈 Starting main trading loop...")
        
        while self.is_running:
            try:
                await self.run_trading_cycle()
            except Exception as e:
                logger.error(f"Trading cycle error: {e}")
                self.stats['errors'] += 1
            
            await asyncio.sleep(self.signal_interval)
    
    async def start(self):
        """Start the automated trading system."""
        if self.is_running:
            logger.warning("Trading system already running")
            return
        
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        logger.info("=" * 60)
        logger.info("🤖 AUTOMATED TRADING SYSTEM STARTING")
        logger.info("=" * 60)
        logger.info(f"⚙️ Configuration:")
        logger.info(f"   - Auto-execute: {self.auto_execute}")
        logger.info(f"   - Max positions: {self.max_positions}")
        logger.info(f"   - Min confidence: {self.min_confidence:.0%}")
        logger.info(f"   - Risk per trade: {self.risk_per_trade:.0%}")
        logger.info(f"   - Signal interval: {self.signal_interval}s")
        logger.info(f"   - Trading hours only: {self.trading_hours_only}")
        logger.info("=" * 60)
        
        # Reset daily tracking
        self.executed_today = []
        
        # Run initial cycle immediately
        await self.run_trading_cycle()
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self.trading_loop()),
            asyncio.create_task(self.position_monitor_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Trading tasks cancelled")
    
    def stop(self):
        """Stop the automated trading system."""
        self.is_running = False
        logger.info("🛑 Automated trading system stopped")
        self.print_stats()
    
    def print_stats(self):
        """Print trading statistics."""
        runtime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else None
        
        logger.info("=" * 60)
        logger.info("📊 TRADING SESSION STATISTICS")
        logger.info("=" * 60)
        logger.info(f"   Runtime: {runtime}")
        logger.info(f"   Scans completed: {self.stats['scans_completed']}")
        logger.info(f"   Signals generated: {self.stats['signals_generated']}")
        logger.info(f"   Trades executed: {self.stats['trades_executed']}")
        logger.info(f"   Trades skipped: {self.stats['trades_skipped']}")
        logger.info(f"   Errors: {self.stats['errors']}")
        
        portfolio = trade_executor.get_portfolio()
        logger.info(f"   Final portfolio value: ${portfolio['portfolio_value']:,.2f}")
        logger.info(f"   Total P&L: ${portfolio['total_pnl']:,.2f} ({portfolio['total_pnl_pct']:.2f}%)")
        logger.info("=" * 60)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        portfolio = trade_executor.get_portfolio()
        
        return {
            'is_running': self.is_running,
            'auto_execute': self.auto_execute,
            'last_scan': self.last_scan_time.isoformat() if self.last_scan_time else None,
            'last_signal': self.last_signal_time.isoformat() if self.last_signal_time else None,
            'pending_signals': len(self.pending_signals),
            'executed_today': self.executed_today,
            'stats': self.stats,
            'portfolio': portfolio,
            'config': {
                'max_positions': self.max_positions,
                'min_confidence': self.min_confidence,
                'risk_per_trade': self.risk_per_trade,
                'signal_interval': self.signal_interval,
                'trading_hours_only': self.trading_hours_only
            }
        }


# Singleton instance
trading_orchestrator = AutomatedTradingOrchestrator(
    scan_interval=60,
    signal_interval=300,  # Run full cycle every 5 minutes
    position_check_interval=30,
    auto_execute=True,  # Enable automatic trade execution
    max_positions=5,
    min_confidence=0.65,
    risk_per_trade=0.02,
    trading_hours_only=False  # Trade 24/7 (supports crypto)
)
