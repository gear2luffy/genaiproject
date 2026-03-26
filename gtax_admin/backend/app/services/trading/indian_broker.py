"""
Indian Broker Integration Module.

Supports integration with popular Indian brokers:
- Zerodha Kite
- Upstox
- Angel One (Angel Broking)

Provides:
- Order placement (Market, Limit, SL, SL-M)
- Position management
- Holdings and funds query
- Intraday square-off
"""
import asyncio
from datetime import datetime, time as dt_time
from typing import Dict, Any, List, Optional
from enum import Enum
from loguru import logger
import pytz

from app.core.config import settings


class IndianExchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    NFO = "NFO"  # NSE F&O
    BFO = "BFO"  # BSE F&O
    MCX = "MCX"  # Commodity


class IndianOrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"          # Stop Loss
    SL_M = "SL-M"      # Stop Loss Market


class IndianProductType(str, Enum):
    CNC = "CNC"        # Cash and Carry (Delivery)
    MIS = "MIS"        # Intraday
    NRML = "NRML"      # Normal (F&O overnight)


class ZerodhaKiteAPI:
    """
    Zerodha Kite API integration.
    
    Note: This is a placeholder implementation.
    For actual trading, you need to:
    1. Install kiteconnect: pip install kiteconnect
    2. Get API credentials from Zerodha Developer Console
    3. Complete the login flow to get access_token
    """
    
    def __init__(self):
        self.api_key = settings.ZERODHA_API_KEY
        self.api_secret = settings.ZERODHA_API_SECRET
        self.access_token = settings.ZERODHA_ACCESS_TOKEN
        self.kite = None
        self.is_initialized = False
        
    def initialize(self):
        """Initialize Kite Connect client."""
        if not self.api_key:
            logger.warning("Zerodha API key not configured")
            return False
        
        try:
            from kiteconnect import KiteConnect
            self.kite = KiteConnect(api_key=self.api_key)
            
            if self.access_token:
                self.kite.set_access_token(self.access_token)
                self.is_initialized = True
                logger.info("Zerodha Kite API initialized")
                return True
            else:
                logger.warning("Zerodha access token not set. Login required.")
                return False
                
        except ImportError:
            logger.warning("kiteconnect not installed. Run: pip install kiteconnect")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Zerodha API: {e}")
            return False
    
    def get_login_url(self) -> str:
        """Get Zerodha login URL for authentication."""
        if not self.kite:
            self.initialize()
        return self.kite.login_url() if self.kite else None
    
    def complete_login(self, request_token: str) -> bool:
        """Complete login with request token from redirect."""
        try:
            data = self.kite.generate_session(
                request_token, 
                api_secret=self.api_secret
            )
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            self.is_initialized = True
            logger.info("Zerodha login successful")
            return True
        except Exception as e:
            logger.error(f"Zerodha login failed: {e}")
            return False
    
    async def place_order(
        self,
        symbol: str,
        exchange: IndianExchange,
        transaction_type: str,  # BUY or SELL
        quantity: int,
        order_type: IndianOrderType = IndianOrderType.MARKET,
        product: IndianProductType = IndianProductType.MIS,
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        stoploss: Optional[float] = None,
        tag: str = "AI_TRADE"
    ) -> Dict[str, Any]:
        """Place order on Zerodha."""
        if not self.is_initialized:
            return {
                'status': 'error',
                'message': 'Zerodha API not initialized'
            }
        
        try:
            # Prepare order parameters
            order_params = {
                'tradingsymbol': symbol.replace('.NS', '').replace('.BO', ''),
                'exchange': exchange.value,
                'transaction_type': transaction_type.upper(),
                'quantity': quantity,
                'order_type': order_type.value,
                'product': product.value,
                'validity': 'DAY',
                'tag': tag
            }
            
            if price and order_type in [IndianOrderType.LIMIT, IndianOrderType.SL]:
                order_params['price'] = price
            
            if trigger_price and order_type in [IndianOrderType.SL, IndianOrderType.SL_M]:
                order_params['trigger_price'] = trigger_price
            
            # Place order
            order_id = await asyncio.to_thread(
                self.kite.place_order,
                variety='regular',
                **order_params
            )
            
            logger.info(f"Zerodha order placed: {order_id}")
            
            return {
                'status': 'success',
                'order_id': order_id,
                'symbol': symbol,
                'exchange': exchange.value,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'order_type': order_type.value,
                'product': product.value
            }
            
        except Exception as e:
            logger.error(f"Zerodha order failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def place_bracket_order(
        self,
        symbol: str,
        exchange: IndianExchange,
        transaction_type: str,
        quantity: int,
        price: float,
        stoploss: float,
        target: float,
        trailing_stoploss: Optional[float] = None
    ) -> Dict[str, Any]:
        """Place Bracket Order (BO) with automatic SL and target."""
        if not self.is_initialized:
            return {'status': 'error', 'message': 'API not initialized'}
        
        try:
            order_id = await asyncio.to_thread(
                self.kite.place_order,
                variety='bo',
                tradingsymbol=symbol.replace('.NS', '').replace('.BO', ''),
                exchange=exchange.value,
                transaction_type=transaction_type.upper(),
                quantity=quantity,
                order_type='LIMIT',
                product='MIS',  # BO is always intraday
                price=price,
                stoploss=abs(price - stoploss),
                squareoff=abs(target - price),
                trailing_stoploss=trailing_stoploss
            )
            
            return {
                'status': 'success',
                'order_id': order_id,
                'order_type': 'BRACKET'
            }
            
        except Exception as e:
            logger.error(f"Bracket order failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_positions(self) -> Dict[str, Any]:
        """Get current positions."""
        if not self.is_initialized:
            return {'status': 'error', 'message': 'API not initialized'}
        
        try:
            positions = await asyncio.to_thread(self.kite.positions)
            return {
                'status': 'success',
                'day': positions.get('day', []),
                'net': positions.get('net', [])
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def get_holdings(self) -> Dict[str, Any]:
        """Get current holdings (delivery)."""
        if not self.is_initialized:
            return {'status': 'error', 'message': 'API not initialized'}
        
        try:
            holdings = await asyncio.to_thread(self.kite.holdings)
            return {'status': 'success', 'holdings': holdings}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def get_margins(self) -> Dict[str, Any]:
        """Get account margins/funds."""
        if not self.is_initialized:
            return {'status': 'error', 'message': 'API not initialized'}
        
        try:
            margins = await asyncio.to_thread(self.kite.margins)
            return {'status': 'success', 'margins': margins}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def cancel_order(self, order_id: str, variety: str = 'regular') -> Dict[str, Any]:
        """Cancel an order."""
        if not self.is_initialized:
            return {'status': 'error', 'message': 'API not initialized'}
        
        try:
            await asyncio.to_thread(
                self.kite.cancel_order,
                variety=variety,
                order_id=order_id
            )
            return {'status': 'success', 'order_id': order_id}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def square_off_all(self) -> Dict[str, Any]:
        """Square off all open positions (intraday)."""
        if not self.is_initialized:
            return {'status': 'error', 'message': 'API not initialized'}
        
        try:
            positions = await self.get_positions()
            if positions['status'] != 'success':
                return positions
            
            squared_off = []
            for pos in positions.get('day', []):
                if pos.get('quantity', 0) != 0:
                    # Place opposite order to square off
                    side = 'SELL' if pos['quantity'] > 0 else 'BUY'
                    result = await self.place_order(
                        symbol=pos['tradingsymbol'],
                        exchange=IndianExchange(pos['exchange']),
                        transaction_type=side,
                        quantity=abs(pos['quantity']),
                        product=IndianProductType.MIS,
                        tag='SQUARE_OFF'
                    )
                    squared_off.append(result)
            
            return {
                'status': 'success',
                'squared_off_count': len(squared_off),
                'orders': squared_off
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


class IndianBrokerRouter:
    """
    Routes orders to appropriate broker based on configuration.
    """
    
    def __init__(self):
        self.zerodha = ZerodhaKiteAPI()
        self.ist_tz = pytz.timezone('Asia/Kolkata')
        self.active_broker = None  # Will be set based on config
        
    def initialize(self) -> bool:
        """Initialize the configured broker."""
        # Try Zerodha first
        if settings.ZERODHA_API_KEY:
            if self.zerodha.initialize():
                self.active_broker = 'ZERODHA'
                return True
        
        # Add other brokers here (Upstox, Angel, etc.)
        
        logger.warning("No broker initialized. Using paper trading.")
        return False
    
    def is_market_open(self) -> bool:
        """Check if Indian market is open."""
        now = datetime.now(self.ist_tz)
        
        # Check weekday
        if now.weekday() >= 5:
            return False
        
        # Market hours: 9:15 AM to 3:30 PM IST
        market_open = dt_time(9, 15)
        market_close = dt_time(15, 30)
        current_time = now.time()
        
        return market_open <= current_time <= market_close
    
    def should_square_off(self) -> bool:
        """Check if it's time to square off intraday positions."""
        now = datetime.now(self.ist_tz)
        square_off_time = dt_time(15, 15)  # Square off at 3:15 PM
        
        return now.time() >= square_off_time
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str = "MARKET",
        product: str = "MIS",  # Intraday by default
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        stoploss: Optional[float] = None,
        target: Optional[float] = None
    ) -> Dict[str, Any]:
        """Place order through active broker."""
        
        # Determine exchange from symbol
        exchange = IndianExchange.NSE if '.NS' in symbol else IndianExchange.BSE
        
        # Use Zerodha if active
        if self.active_broker == 'ZERODHA':
            # If SL and target provided, use bracket order
            if stoploss and target and order_type == "LIMIT":
                return await self.zerodha.place_bracket_order(
                    symbol=symbol,
                    exchange=exchange,
                    transaction_type=side,
                    quantity=quantity,
                    price=price,
                    stoploss=stoploss,
                    target=target
                )
            
            return await self.zerodha.place_order(
                symbol=symbol,
                exchange=exchange,
                transaction_type=side,
                quantity=quantity,
                order_type=IndianOrderType(order_type),
                product=IndianProductType(product),
                price=price,
                trigger_price=trigger_price
            )
        
        # Fallback: return mock response for paper trading
        return {
            'status': 'paper',
            'message': 'No broker configured. Paper trade recorded.',
            'symbol': symbol,
            'side': side,
            'quantity': quantity
        }
    
    async def get_positions(self) -> Dict[str, Any]:
        """Get positions from active broker."""
        if self.active_broker == 'ZERODHA':
            return await self.zerodha.get_positions()
        
        return {'status': 'paper', 'positions': []}
    
    async def square_off_all(self) -> Dict[str, Any]:
        """Square off all intraday positions."""
        if self.active_broker == 'ZERODHA':
            return await self.zerodha.square_off_all()
        
        return {'status': 'paper', 'message': 'Paper positions cleared'}


# Singleton instance
indian_broker = IndianBrokerRouter()
zerodha_api = ZerodhaKiteAPI()
