"""
WebSocket endpoints for real-time communication.

Demonstrates:
- WebSocket connections
- Connection management
- Broadcasting messages
- Authentication over WebSocket
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from fastapi.websockets import WebSocketState

from app.core.security import security_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ConnectionManager:
    """
    WebSocket connection manager.
    
    Manages active WebSocket connections and provides
    methods for sending messages to connected clients.
    
    Demonstrates:
    - Class-based connection management
    - Broadcasting patterns
    - Room-based messaging
    """
    
    def __init__(self) -> None:
        """Initialize connection manager."""
        # General connections: {user_id: websocket}
        self.active_connections: Dict[int, WebSocket] = {}
        
        # Room-based connections: {room_id: [websocket, ...]}
        self.rooms: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        """
        Accept and store a WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            user_id: The user's ID
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info("WebSocket connected", user_id=user_id)
    
    def disconnect(self, user_id: int) -> None:
        """
        Remove a WebSocket connection.
        
        Args:
            user_id: The user's ID
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info("WebSocket disconnected", user_id=user_id)
    
    async def send_personal_message(
        self,
        message: dict,
        user_id: int
    ) -> bool:
        """
        Send a message to a specific user.
        
        Args:
            message: The message to send
            user_id: The recipient's user ID
            
        Returns:
            bool: True if message was sent
        """
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
                return True
        return False
    
    async def broadcast(self, message: dict, exclude_user: Optional[int] = None) -> int:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: The message to broadcast
            exclude_user: Optional user ID to exclude
            
        Returns:
            int: Number of clients that received the message
        """
        sent_count = 0
        disconnected = []
        
        for user_id, websocket in self.active_connections.items():
            if user_id == exclude_user:
                continue
            
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json(message)
                    sent_count += 1
            except Exception:
                disconnected.append(user_id)
        
        # Clean up disconnected
        for user_id in disconnected:
            self.disconnect(user_id)
        
        return sent_count
    
    async def join_room(self, websocket: WebSocket, room_id: str) -> None:
        """
        Add a websocket to a room.
        
        Args:
            websocket: The WebSocket connection
            room_id: The room identifier
        """
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        self.rooms[room_id].append(websocket)
    
    async def leave_room(self, websocket: WebSocket, room_id: str) -> None:
        """
        Remove a websocket from a room.
        
        Args:
            websocket: The WebSocket connection
            room_id: The room identifier
        """
        if room_id in self.rooms:
            if websocket in self.rooms[room_id]:
                self.rooms[room_id].remove(websocket)
            if not self.rooms[room_id]:
                del self.rooms[room_id]
    
    async def broadcast_to_room(
        self,
        message: dict,
        room_id: str,
        exclude: Optional[WebSocket] = None
    ) -> int:
        """
        Broadcast message to all connections in a room.
        
        Args:
            message: The message to broadcast
            room_id: The room identifier
            exclude: Optional websocket to exclude
            
        Returns:
            int: Number of clients that received the message
        """
        if room_id not in self.rooms:
            return 0
        
        sent_count = 0
        disconnected = []
        
        for websocket in self.rooms[room_id]:
            if websocket == exclude:
                continue
            
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json(message)
                    sent_count += 1
            except Exception:
                disconnected.append(websocket)
        
        # Clean up disconnected
        for ws in disconnected:
            await self.leave_room(ws, room_id)
        
        return sent_count


# Global connection manager instance
manager = ConnectionManager()


async def get_user_from_token(token: str) -> Optional[int]:
    """
    Validate token and extract user ID.
    
    Args:
        token: JWT token
        
    Returns:
        Optional[int]: User ID if valid, None otherwise
    """
    payload = security_service.decode_token(token)
    if payload and payload.get("type") == "access":
        try:
            return int(payload.get("sub", 0))
        except (ValueError, TypeError):
            return None
    return None


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token")
):
    """
    Main WebSocket endpoint for real-time communication.
    
    Connect with: ws://host/api/v1/ws/connect?token=<jwt_token>
    
    Message format (JSON):
    {
        "type": "message|join_room|leave_room|ping",
        "data": {...},
        "room": "optional_room_id"
    }
    
    Args:
        websocket: The WebSocket connection
        token: JWT access token for authentication
    """
    # Authenticate
    user_id = await get_user_from_token(token)
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Connect
    await manager.connect(websocket, user_id)
    
    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "message": "Successfully connected",
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                continue
            
            msg_type = message.get("type", "message")
            
            if msg_type == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif msg_type == "join_room":
                # Join a room
                room_id = message.get("room")
                if room_id:
                    await manager.join_room(websocket, room_id)
                    await websocket.send_json({
                        "type": "room_joined",
                        "room": room_id
                    })
                    # Notify room members
                    await manager.broadcast_to_room(
                        {
                            "type": "user_joined",
                            "user_id": user_id,
                            "room": room_id,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        room_id,
                        exclude=websocket
                    )
            
            elif msg_type == "leave_room":
                # Leave a room
                room_id = message.get("room")
                if room_id:
                    await manager.leave_room(websocket, room_id)
                    await websocket.send_json({
                        "type": "room_left",
                        "room": room_id
                    })
            
            elif msg_type == "room_message":
                # Send message to room
                room_id = message.get("room")
                if room_id:
                    await manager.broadcast_to_room(
                        {
                            "type": "room_message",
                            "from_user": user_id,
                            "room": room_id,
                            "data": message.get("data", {}),
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        room_id
                    )
            
            elif msg_type == "direct_message":
                # Send direct message to user
                to_user = message.get("to_user")
                if to_user:
                    sent = await manager.send_personal_message(
                        {
                            "type": "direct_message",
                            "from_user": user_id,
                            "data": message.get("data", {}),
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        to_user
                    )
                    await websocket.send_json({
                        "type": "message_sent" if sent else "user_offline",
                        "to_user": to_user
                    })
            
            elif msg_type == "broadcast":
                # Broadcast to all (could be restricted to admins)
                await manager.broadcast(
                    {
                        "type": "broadcast",
                        "from_user": user_id,
                        "data": message.get("data", {}),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude_user=user_id
                )
            
            else:
                # Echo back unknown message types
                await websocket.send_json({
                    "type": "echo",
                    "original": message,
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        # Broadcast disconnect notification if needed
        await manager.broadcast({
            "type": "user_disconnected",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error("WebSocket error", user_id=user_id, error=str(e))
        manager.disconnect(user_id)


@router.websocket("/notifications")
async def notifications_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token")
):
    """
    WebSocket endpoint for receiving notifications.
    
    This is a simpler endpoint that only sends notifications
    to the connected user (no sending from client).
    
    Args:
        websocket: The WebSocket connection
        token: JWT access token
    """
    # Authenticate
    user_id = await get_user_from_token(token)
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await websocket.accept()
    
    logger.info("Notifications WebSocket connected", user_id=user_id)
    
    try:
        while True:
            # Keep connection alive, just handle pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        logger.info("Notifications WebSocket disconnected", user_id=user_id)
