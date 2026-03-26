"""
WebSocket endpoints for real-time updates.
"""
import asyncio
import json
from typing import List, Dict, Any, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.services.scanner.market_scanner import market_scanner
from app.services.data.data_fetcher import data_fetcher


router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        self.subscriptions[websocket] = set()
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_subscribers(self, channel: str, message: dict):
        """Broadcast to connections subscribed to a specific channel."""
        disconnected = []
        for websocket, channels in self.subscriptions.items():
            if channel in channels or '*' in channels:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    def subscribe(self, websocket: WebSocket, channel: str):
        if websocket in self.subscriptions:
            self.subscriptions[websocket].add(channel)
    
    def unsubscribe(self, websocket: WebSocket, channel: str):
        if websocket in self.subscriptions:
            self.subscriptions[websocket].discard(channel)


manager = ConnectionManager()


@router.websocket("/live")
async def websocket_live(websocket: WebSocket):
    """
    WebSocket endpoint for live market data.
    
    Supports commands:
    - {"action": "subscribe", "channel": "scanner"}
    - {"action": "subscribe", "channel": "quotes", "symbols": ["AAPL", "GOOGL"]}
    - {"action": "unsubscribe", "channel": "scanner"}
    - {"action": "ping"}
    """
    await manager.connect(websocket)
    
    # Default subscriptions
    manager.subscribe(websocket, "scanner")
    
    try:
        # Start background tasks for this connection
        scanner_task = asyncio.create_task(
            send_scanner_updates(websocket)
        )
        
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()
            
            action = data.get("action")
            
            if action == "subscribe":
                channel = data.get("channel")
                if channel:
                    manager.subscribe(websocket, channel)
                    await manager.send_personal_message(
                        {"type": "subscribed", "channel": channel},
                        websocket
                    )
                    
                    # Start quote updates if subscribing to quotes
                    if channel == "quotes" and "symbols" in data:
                        asyncio.create_task(
                            send_quote_updates(websocket, data["symbols"])
                        )
            
            elif action == "unsubscribe":
                channel = data.get("channel")
                if channel:
                    manager.unsubscribe(websocket, channel)
                    await manager.send_personal_message(
                        {"type": "unsubscribed", "channel": channel},
                        websocket
                    )
            
            elif action == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": asyncio.get_event_loop().time()},
                    websocket
                )
            
            elif action == "get_scanner":
                results = market_scanner.get_last_results()
                await manager.send_personal_message(
                    {"type": "scanner", "data": results},
                    websocket
                )
            
            elif action == "get_quote":
                symbol = data.get("symbol")
                if symbol:
                    quote = await data_fetcher.get_realtime_quote(symbol)
                    await manager.send_personal_message(
                        {"type": "quote", "symbol": symbol, "data": quote},
                        websocket
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        scanner_task.cancel()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def send_scanner_updates(websocket: WebSocket):
    """Send scanner updates periodically."""
    while websocket in manager.active_connections:
        if "scanner" in manager.subscriptions.get(websocket, set()):
            results = market_scanner.get_last_results()
            if results:
                try:
                    await websocket.send_json({
                        "type": "scanner",
                        "data": results
                    })
                except Exception:
                    break
        
        await asyncio.sleep(30)  # Update every 30 seconds


async def send_quote_updates(websocket: WebSocket, symbols: List[str]):
    """Send quote updates for subscribed symbols."""
    while websocket in manager.active_connections:
        if "quotes" in manager.subscriptions.get(websocket, set()):
            quotes = await data_fetcher.get_multiple_quotes(symbols)
            if quotes:
                try:
                    await websocket.send_json({
                        "type": "quotes",
                        "data": quotes
                    })
                except Exception:
                    break
        
        await asyncio.sleep(5)  # Update every 5 seconds


@router.websocket("/signals")
async def websocket_signals(websocket: WebSocket):
    """
    WebSocket endpoint for real-time trading signals.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            action = data.get("action")
            
            if action == "get_signals":
                from app.services.ai.decision_engine import ai_decision_engine
                
                symbols = data.get("symbols", ["AAPL", "GOOGL", "MSFT"])
                signals = await ai_decision_engine.generate_bulk_signals(symbols)
                
                await manager.send_personal_message(
                    {
                        "type": "signals",
                        "data": [s.to_dict() for s in signals]
                    },
                    websocket
                )
            
            elif action == "ping":
                await manager.send_personal_message(
                    {"type": "pong"},
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Signals WebSocket error: {e}")
        manager.disconnect(websocket)
