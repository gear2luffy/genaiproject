"""
Trade Execution System.

Supports:
- Paper trading (simulated)
- Real trading (via broker APIs)
- Risk management (stop loss, take profit, position sizing)
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from loguru import logger
import asyncio

from app.core.config import settings
from app.services.data.data_fetcher import data_fetcher
from app.services.logging.trade_logger import trade_logger


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    PARTIAL = "PARTIAL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


@dataclass
class Order:
    """Trade order representation."""
    id: str
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    status: OrderStatus = OrderStatus.PENDING
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    filled_price: Optional[float] = None
    filled_quantity: float = 0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    is_paper: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': self.quantity,
            'order_type': self.order_type.value,
            'status': self.status.value,
            'limit_price': self.limit_price,
            'stop_price': self.stop_price,
            'filled_price': self.filled_price,
            'filled_quantity': self.filled_quantity,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'is_paper': self.is_paper,
            'created_at': self.created_at.isoformat(),
            'filled_at': self.filled_at.isoformat() if self.filled_at else None
        }


@dataclass
class Position:
    """Current position in a symbol."""
    symbol: str
    quantity: float
    average_cost: float
    current_price: float = 0
    market_value: float = 0
    unrealized_pnl: float = 0
    unrealized_pnl_pct: float = 0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    def update_price(self, price: float):
        self.current_price = price
        self.market_value = self.quantity * price
        self.unrealized_pnl = self.market_value - (self.quantity * self.average_cost)
        self.unrealized_pnl_pct = (price - self.average_cost) / self.average_cost if self.average_cost > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'average_cost': round(self.average_cost, 2),
            'current_price': round(self.current_price, 2),
            'market_value': round(self.market_value, 2),
            'unrealized_pnl': round(self.unrealized_pnl, 2),
            'unrealized_pnl_pct': round(self.unrealized_pnl_pct * 100, 2),
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit
        }


class PaperTradingEngine:
    """
    Paper trading engine for simulated trading.
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.trade_history: List[Dict[str, Any]] = []
        self.order_counter = 0
    
    def _generate_order_id(self) -> str:
        self.order_counter += 1
        return f"PAPER-{datetime.now().strftime('%Y%m%d')}-{self.order_counter:06d}"
    
    async def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Order:
        """
        Submit a paper trading order.
        """
        order_id = self._generate_order_id()
        
        order = Order(
            id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            is_paper=True
        )
        
        self.orders[order_id] = order
        
        # For market orders, execute immediately
        if order_type == OrderType.MARKET:
            await self._execute_order(order)
        
        return order
    
    async def _execute_order(self, order: Order) -> bool:
        """Execute an order at current market price."""
        quote = await data_fetcher.get_realtime_quote(order.symbol)
        
        if not quote or quote.get('price') is None:
            order.status = OrderStatus.REJECTED
            logger.error(f"Order {order.id} rejected: Could not get price for {order.symbol}")
            return False
        
        price = quote['price']
        total_cost = price * order.quantity
        
        if order.side == OrderSide.BUY:
            # Check if we have enough cash
            if total_cost > self.cash:
                order.status = OrderStatus.REJECTED
                logger.warning(f"Order {order.id} rejected: Insufficient funds")
                return False
            
            # Execute buy
            self.cash -= total_cost
            
            if order.symbol in self.positions:
                # Add to existing position
                pos = self.positions[order.symbol]
                total_quantity = pos.quantity + order.quantity
                pos.average_cost = (pos.average_cost * pos.quantity + total_cost) / total_quantity
                pos.quantity = total_quantity
            else:
                # New position
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    average_cost=price,
                    current_price=price,
                    stop_loss=order.stop_loss,
                    take_profit=order.take_profit
                )
            
            self.positions[order.symbol].update_price(price)
        
        else:  # SELL
            if order.symbol not in self.positions:
                order.status = OrderStatus.REJECTED
                logger.warning(f"Order {order.id} rejected: No position to sell")
                return False
            
            pos = self.positions[order.symbol]
            
            if order.quantity > pos.quantity:
                order.status = OrderStatus.REJECTED
                logger.warning(f"Order {order.id} rejected: Insufficient shares")
                return False
            
            # Execute sell
            self.cash += total_cost
            
            # Record PnL
            entry_cost = pos.average_cost * order.quantity
            pnl = total_cost - entry_cost
            
            self.trade_history.append({
                'symbol': order.symbol,
                'side': 'SELL',
                'quantity': order.quantity,
                'entry_price': pos.average_cost,
                'exit_price': price,
                'pnl': round(pnl, 2),
                'pnl_pct': round((price - pos.average_cost) / pos.average_cost * 100, 2),
                'timestamp': datetime.now().isoformat()
            })
            
            # Update or remove position
            pos.quantity -= order.quantity
            if pos.quantity <= 0:
                del self.positions[order.symbol]
            else:
                pos.update_price(price)
        
        # Mark order as filled
        order.status = OrderStatus.FILLED
        order.filled_price = price
        order.filled_quantity = order.quantity
        order.filled_at = datetime.now()
        
        logger.info(f"Order {order.id} filled: {order.side.value} {order.quantity} {order.symbol} @ {price}")
        
        return True
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        if order.status != OrderStatus.PENDING:
            return False
        
        order.status = OrderStatus.CANCELLED
        return True
    
    async def update_positions(self) -> Dict[str, Position]:
        """Update all positions with current prices."""
        for symbol, position in self.positions.items():
            quote = await data_fetcher.get_realtime_quote(symbol)
            if quote and quote.get('price'):
                position.update_price(quote['price'])
        
        return self.positions
    
    async def check_stop_loss_take_profit(self) -> List[Order]:
        """Check and execute stop loss / take profit orders."""
        executed_orders = []
        
        for symbol, position in list(self.positions.items()):
            quote = await data_fetcher.get_realtime_quote(symbol)
            
            if not quote or quote.get('price') is None:
                continue
            
            price = quote['price']
            position.update_price(price)
            
            # Check stop loss
            if position.stop_loss and price <= position.stop_loss:
                logger.info(f"Stop loss triggered for {symbol} at {price}")
                order = await self.submit_order(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    quantity=position.quantity,
                    order_type=OrderType.MARKET
                )
                executed_orders.append(order)
            
            # Check take profit
            elif position.take_profit and price >= position.take_profit:
                logger.info(f"Take profit triggered for {symbol} at {price}")
                order = await self.submit_order(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    quantity=position.quantity,
                    order_type=OrderType.MARKET
                )
                executed_orders.append(order)
        
        return executed_orders
    
    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value."""
        positions_value = sum(
            pos.market_value for pos in self.positions.values()
        )
        return self.cash + positions_value
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary."""
        portfolio_value = self.get_portfolio_value()
        total_pnl = portfolio_value - self.initial_capital
        
        return {
            'initial_capital': self.initial_capital,
            'cash': round(self.cash, 2),
            'positions_value': round(portfolio_value - self.cash, 2),
            'portfolio_value': round(portfolio_value, 2),
            'total_pnl': round(total_pnl, 2),
            'total_pnl_pct': round(total_pnl / self.initial_capital * 100, 2),
            'positions_count': len(self.positions),
            'trades_count': len(self.trade_history),
            'positions': [pos.to_dict() for pos in self.positions.values()],
            'recent_trades': self.trade_history[-10:]
        }


class RiskManager:
    """
    Risk management utilities.
    """
    
    @staticmethod
    def calculate_position_size(
        capital: float,
        risk_per_trade: float,
        entry_price: float,
        stop_loss: float
    ) -> float:
        """
        Calculate position size based on risk.
        
        Args:
            capital: Total capital
            risk_per_trade: Percentage of capital to risk (e.g., 0.02 for 2%)
            entry_price: Entry price
            stop_loss: Stop loss price
        
        Returns:
            Number of shares to buy
        """
        risk_amount = capital * risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk <= 0:
            return 0
        
        shares = risk_amount / price_risk
        return round(shares, 2)
    
    @staticmethod
    def calculate_stop_loss(
        entry_price: float,
        stop_loss_pct: float = None,
        atr: float = None,
        atr_multiplier: float = 2.0
    ) -> float:
        """
        Calculate stop loss price.
        
        Uses either percentage-based or ATR-based stop loss.
        """
        if atr:
            return entry_price - (atr * atr_multiplier)
        
        stop_loss_pct = stop_loss_pct or settings.DEFAULT_STOP_LOSS
        return entry_price * (1 - stop_loss_pct)
    
    @staticmethod
    def calculate_take_profit(
        entry_price: float,
        take_profit_pct: float = None,
        risk_reward: float = 2.0,
        stop_loss: float = None
    ) -> float:
        """
        Calculate take profit price.
        
        Uses either percentage or risk-reward ratio.
        """
        if stop_loss:
            risk = entry_price - stop_loss
            return entry_price + (risk * risk_reward)
        
        take_profit_pct = take_profit_pct or settings.DEFAULT_TAKE_PROFIT
        return entry_price * (1 + take_profit_pct)
    
    @staticmethod
    def check_max_position_size(
        position_value: float,
        portfolio_value: float,
        max_position_pct: float = None
    ) -> bool:
        """Check if position size exceeds maximum allowed."""
        max_pct = max_position_pct or settings.MAX_POSITION_SIZE
        return (position_value / portfolio_value) <= max_pct


class TradeExecutor:
    """
    Main trade execution coordinator.
    
    Routes orders to appropriate execution engine (paper or real).
    """
    
    def __init__(self):
        self.paper_engine = PaperTradingEngine()
        self.risk_manager = RiskManager()
        self.use_paper_trading = True  # Default to paper trading
    
    async def execute_trade(
        self,
        symbol: str,
        side: str,
        quantity: Optional[float] = None,
        risk_pct: float = 0.02,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        use_risk_management: bool = True,
        strategy: str = "AI_COMPOSITE",
        reason: str = "",
        signal_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a trade with optional risk management.
        
        Args:
            symbol: Stock/crypto symbol
            side: BUY or SELL
            quantity: Number of units (auto-calculated if None)
            risk_pct: Risk percentage per trade
            stop_loss: Stop loss price
            take_profit: Take profit price
            use_risk_management: Whether to use risk management
            strategy: Trading strategy name for logging
            reason: Reason for the trade for logging
            signal_data: AI signal data with scores
        """
        # Get current price
        quote = await data_fetcher.get_realtime_quote(symbol)
        
        if not quote or quote.get('price') is None:
            return {
                'status': 'error',
                'message': f'Could not get price for {symbol}'
            }
        
        price = quote['price']
        
        # Calculate position size if not provided
        if quantity is None and use_risk_management:
            if stop_loss is None:
                stop_loss = self.risk_manager.calculate_stop_loss(price)
            
            quantity = self.risk_manager.calculate_position_size(
                capital=self.paper_engine.cash,
                risk_per_trade=risk_pct,
                entry_price=price,
                stop_loss=stop_loss
            )
        
        if quantity is None or quantity <= 0:
            return {
                'status': 'error',
                'message': 'Invalid quantity'
            }
        
        # Calculate stop loss and take profit if not provided
        if stop_loss is None:
            stop_loss = self.risk_manager.calculate_stop_loss(price)
        
        if take_profit is None:
            take_profit = self.risk_manager.calculate_take_profit(
                price, stop_loss=stop_loss
            )
        
        # Execute order
        order_side = OrderSide.BUY if side.upper() == 'BUY' else OrderSide.SELL
        
        order = await self.paper_engine.submit_order(
            symbol=symbol,
            side=order_side,
            quantity=quantity,
            order_type=OrderType.MARKET,
            stop_loss=stop_loss if order_side == OrderSide.BUY else None,
            take_profit=take_profit if order_side == OrderSide.BUY else None
        )
        
        # Log trade to Excel
        if order.status == OrderStatus.FILLED:
            try:
                # Calculate P&L for sells
                pnl = None
                pnl_pct = None
                if order_side == OrderSide.SELL and self.paper_engine.trade_history:
                    last_trade = self.paper_engine.trade_history[-1]
                    if last_trade.get('symbol') == symbol:
                        pnl = last_trade.get('pnl')
                        pnl_pct = last_trade.get('pnl_pct')
                
                trade_logger.log_trade(
                    trade_id=order.id,
                    symbol=symbol,
                    action=side.upper(),
                    quantity=quantity,
                    price=order.filled_price,
                    strategy=strategy,
                    reason=reason,
                    signal_data=signal_data,
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )
            except Exception as e:
                logger.error(f"Failed to log trade to Excel: {e}")
        
        return {
            'status': 'success' if order.status == OrderStatus.FILLED else 'error',
            'order': order.to_dict(),
            'risk_management': {
                'stop_loss': round(stop_loss, 2),
                'take_profit': round(take_profit, 2),
                'risk_pct': risk_pct
            },
            'logged_to_excel': order.status == OrderStatus.FILLED
        }
    
    def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio state."""
        return self.paper_engine.get_portfolio_summary()
    
    async def update_and_check_orders(self) -> Dict[str, Any]:
        """Update positions and check stop loss / take profit."""
        await self.paper_engine.update_positions()
        executed = await self.paper_engine.check_stop_loss_take_profit()
        
        return {
            'positions_updated': len(self.paper_engine.positions),
            'orders_executed': len(executed),
            'executed_orders': [o.to_dict() for o in executed]
        }


# Singleton instances
trade_executor = TradeExecutor()
risk_manager = RiskManager()
